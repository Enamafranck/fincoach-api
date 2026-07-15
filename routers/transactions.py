"""
Router pour la gestion des transactions, historique et objectifs CRUD
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from config import supabase, logger
from datetime import date, timedelta

router = APIRouter(prefix="/api", tags=["Transactions & Objectifs"])


class ObjectifCreate(BaseModel):
    utilisateur_id: str
    nom: str
    montant_cible: float
    frequence: Optional[str] = "mensuel"


class AbonnementRequest(BaseModel):
    utilisateur_id: str


@router.get("/transactions/stats/{utilisateur_id}")
def obtenir_statistiques_compteurs(utilisateur_id: str):
    """
    - Entrées   = dépôts effectués
    - Sorties   = retraits EXÉCUTÉS uniquement (pas ceux en carence)
    - Solde net = Entrées - Sorties - Argent en objectifs
    """
    try:
        liste_depots = supabase.table("cotisations")\
            .select("*")\
            .eq("utilisateur_id", utilisateur_id)\
            .eq("statut", "effectuee")\
            .eq("type", "mise_de_cote")\
            .execute().data or []

        # ✅ Seuls les retraits réellement exécutés comptent dans les sorties
        # (ceux en_attente_carence n'ont pas encore quitté le système)
        liste_retraits = supabase.table("retraits")\
            .select("*")\
            .eq("utilisateur_id", utilisateur_id)\
            .eq("statut", "execute")\
            .execute().data or []

        liste_objectifs = supabase.table("objectifs")\
            .select("montant_actuel")\
            .eq("utilisateur_id", utilisateur_id)\
            .execute().data or []

        entrees_totales     = sum(int(float(c["montant"])) for c in liste_depots)
        sorties_totales     = sum(int(float(r["montant"])) for r in liste_retraits)
        argent_en_objectifs = sum(int(float(o["montant_actuel"])) for o in liste_objectifs)

        solde_net = entrees_totales - sorties_totales - argent_en_objectifs

        taux_epargne = 0
        if entrees_totales > 0:
            taux_epargne = (argent_en_objectifs / entrees_totales) * 100

        return {
            "entrees_totales"     : entrees_totales,
            "sorties_totales"     : sorties_totales,
            "solde_disponible_net": solde_net,
            "efficacite_epargne"  : f"{round(min(100, max(0, taux_epargne)), 2)}%"
        }

    except Exception as e:
        logger.exception(f"❌ [ERREUR STATS] : {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors du calcul des indicateurs.")


@router.get("/transactions/historique/{utilisateur_id}")
def historique_global(utilisateur_id: str):
    try:
        transactions = supabase.table("transactions")\
            .select("*")\
            .eq("utilisateur_id", utilisateur_id)\
            .order("date", desc=True)\
            .limit(30)\
            .execute().data or []

        cotisations = supabase.table("cotisations")\
            .select("*")\
            .eq("utilisateur_id", utilisateur_id)\
            .eq("statut", "effectuee")\
            .order("created_at", desc=True)\
            .limit(30)\
            .execute().data or []

        retraits = supabase.table("retraits")\
            .select("*")\
            .eq("utilisateur_id", utilisateur_id)\
            .order("created_at", desc=True)\
            .limit(30)\
            .execute().data or []

        historique = []

        for t in transactions:
            historique.append({
                "id"       : t["id"],
                "type"     : "transaction",
                "sens"     : t["type"],
                "montant"  : int(float(t["montant"])),
                "categorie": t.get("categorie", "Autre"),
                "label"    : t.get("categorie", "Transaction"),
                "date"     : t.get("date", ""),
            })

        for c in cotisations:
            historique.append({
                "id"       : c["id"],
                "type"     : "cotisation",
                "sens"     : "entree",
                "montant"  : int(float(c["montant"])),
                "categorie": c.get("type", "epargne"),
                "label"    : "Mise de côté" if c.get("type") == "mise_de_cote" else "Cotisation objectif",
                "date"     : str(c.get("created_at", ""))[:10],
            })

        for r in retraits:
            # ✅ Catégorie explicite pour permettre à l'analyse des sorties de les compter
            est_solde_libre = not r.get("objectif_id")
            historique.append({
                "id"       : r["id"],
                "type"     : "retrait",
                "sens"     : "sortie",
                "montant"  : int(float(r["montant"])),
                "categorie": "Retrait solde libre" if est_solde_libre else "Retrait objectif",
                "label"    : ("Retrait solde libre" if est_solde_libre else "Retrait objectif")
                             + (" (anticipé)" if r.get("anticipe") else ""),
                "date"     : str(r.get("date") or r.get("created_at", ""))[:10],
            })

        historique.sort(key=lambda x: x["date"], reverse=True)
        return {"historique": historique[:50]}

    except Exception as e:
        logger.exception(f"❌ [ERREUR HISTORIQUE] : {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur historique.")


@router.post("/objectifs", status_code=status.HTTP_201_CREATED)
def creer_objectif(obj: ObjectifCreate):
    try:
        data_to_insert = {
            "utilisateur_id": obj.utilisateur_id,
            "nom": obj.nom,
            "montant_cible": obj.montant_cible,
            "frequence": obj.frequence,
            "statut": "actif",
            "couleur_statut": "vert",
            "montant_actuel": 0
        }
        response = supabase.table("objectifs").insert(data_to_insert).execute()
        return {"status": "success", "data": response.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création objectif : {str(e)}")


# ⚠️ Routes desactiver/reactiver RETIRÉES — elles utilisaient un statut "inactif" en
# conflit avec "en_pause" utilisé par /api/objectifs/{id}/toggle-statut (retraits.py).
# Le frontend n'utilise que toggle-statut : garder les deux systèmes créait des
# objectifs invisibles avec un statut orphelin, ce qui faussait les compteurs.


@router.delete("/objectifs/{objectif_id}")
def supprimer_objectif(objectif_id: str, user_id: str):
    """
    Supprime l'objectif, reverse l'argent cotisé au solde principal.
    ✅ BUG CORRIGÉ : le paramètre s'appelait "utilisateur_id" alors que le frontend
    envoie "?user_id=..." — mismatch qui faisait échouer silencieusement la requête
    (422 Unprocessable Entity). Renommé en "user_id" pour correspondre au frontend.
    """
    try:
        res = supabase.table("objectifs")\
            .select("*")\
            .eq("id", objectif_id)\
            .eq("utilisateur_id", user_id)\
            .execute()

        if not res.data:
            raise HTTPException(status_code=404, detail="Objectif introuvable.")

        objectif = res.data[0]
        montant_a_reverser = int(float(objectif["montant_actuel"]))

        if montant_a_reverser > 0:
            user_res = supabase.table("utilisateurs")\
                .select("solde_libre")\
                .eq("id", user_id)\
                .execute()

            if not user_res.data:
                raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

            nouveau_solde = int(float(user_res.data[0]["solde_libre"])) + montant_a_reverser

            supabase.table("utilisateurs").update({
                "solde_libre": nouveau_solde
            }).eq("id", user_id).execute()

            supabase.table("transactions").insert({
                "utilisateur_id": user_id,
                "montant": montant_a_reverser,
                "type": "depot",
                "categorie": "Clôture Objectif",
                "texte_brut": f"Fonds récupérés suite à la clôture de l'objectif : {objectif['nom']}"
            }).execute()

        supabase.table("cotisations")\
            .delete()\
            .eq("objectif_id", objectif_id)\
            .execute()

        supabase.table("objectifs")\
            .delete()\
            .eq("id", objectif_id)\
            .execute()

        return {
            "message"           : "Objectif supprimé ✅",
            "montant_reverse"   : montant_a_reverser,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"❌ [ERREUR SUPPRESSION OBJECTIF] : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ── ABONNEMENT ──

@router.get("/abonnements/statut/{utilisateur_id}")
def verifier_abonnement(utilisateur_id: str):
    try:
        abonnement = supabase.table("abonnements")\
            .select("*")\
            .eq("utilisateur_id", utilisateur_id)\
            .eq("statut", "actif")\
            .order("date_fin", desc=True)\
            .limit(1)\
            .execute().data

        if not abonnement:
            return {"actif": False, "jours_restants": 0, "message": "Aucun abonnement actif."}

        ab = abonnement[0]
        date_fin = date.fromisoformat(ab["date_fin"])
        jours_restants = (date_fin - date.today()).days

        if jours_restants < 0:
            supabase.table("abonnements").update({"statut": "expire"}).eq("id", ab["id"]).execute()
            return {"actif": False, "jours_restants": 0, "message": "Abonnement expiré."}

        # ✅ Notification si expiration proche
        if 0 <= jours_restants <= 5:
            try:
                from routers.notifications import creer_notification
                creer_notification(
                    utilisateur_id, 
                    "abonnement_expire",
                    "Ton abonnement expire bientôt",
                    f"Il te reste {jours_restants} jour(s). Renouvelle pour garder l'accès au Coach IA."
                )
            except Exception as e:
                print(f"Info: Notification non envoyée ({e})")

        return {"actif": True, "jours_restants": jours_restants, "date_fin": ab["date_fin"]}

    except Exception as e:
        print(f"❌ [ERREUR VÉRIF ABONNEMENT] : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/abonnements/essai-gratuit")
def creer_essai_gratuit(req: AbonnementRequest):
    try:
        existant = supabase.table("abonnements")\
            .select("id")\
            .eq("utilisateur_id", req.utilisateur_id)\
            .execute().data

        if existant:
            return {"message": "Abonnement déjà existant, essai gratuit non applicable."}

        date_debut = date.today()
        date_fin   = date_debut + timedelta(days=30)

        supabase.table("abonnements").insert({
            "utilisateur_id" : req.utilisateur_id,
            "montant"        : 0,
            "date_debut"     : date_debut.isoformat(),
            "date_fin"       : date_fin.isoformat(),
            "statut"         : "actif",
        }).execute()

        return {"message": "Essai gratuit de 30 jours activé 🎉", "date_fin": date_fin.isoformat()}

    except Exception as e:
        logger.exception(f"❌ [ERREUR ESSAI GRATUIT] : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/abonnements/activer")
def activer_abonnement(req: AbonnementRequest):
    try:
        date_debut = date.today()
        date_fin   = date_debut + timedelta(days=30)

        supabase.table("abonnements").update({
            "statut": "expire"
        }).eq("utilisateur_id", req.utilisateur_id).eq("statut", "actif").execute()

        supabase.table("abonnements").insert({
            "utilisateur_id" : req.utilisateur_id,
            "montant"        : 500,
            "date_debut"     : date_debut.isoformat(),
            "date_fin"       : date_fin.isoformat(),
            "statut"         : "actif",
        }).execute()

        supabase.table("caisse_admin").insert({
            "source"         : "abonnement",
            "montant"        : 500,
            "utilisateur_id" : req.utilisateur_id,
            "date"           : date_debut.isoformat(),
        }).execute()

        return {"message": "Abonnement activé ✅", "date_fin": date_fin.isoformat()}

    except Exception as e:
        logger.exception(f"❌ [ERREUR ACTIVATION ABONNEMENT] : {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))