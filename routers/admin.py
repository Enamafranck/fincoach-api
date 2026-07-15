"""
Router pour les routes d'administration FinCoach
"""
from datetime import date
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config import supabase

router = APIRouter(prefix="/api/admin", tags=["Administration"])


class RetraitAdminRequest(BaseModel):
    montant: float
    moyen_paiement: str | None = None  # 'mtn' | 'orange' | 'carte'
    numero: str | None = None


@router.get("/debug/structure-utilisateurs")
def debug_structure_utilisateurs():
    try:
        sample = supabase.table("utilisateurs").select("*").limit(1).execute().data
        if not sample:
            return {"message": "Aucun utilisateur dans la base", "colonnes": []}
        return {
            "message": "Structure de la table utilisateurs",
            "colonnes": list(sample[0].keys()),
            "exemple": sample[0]
        }
    except Exception as e:
        return {"error": str(e), "message": "Erreur lors de la récupération de la structure"}


@router.get("/stats")
def obtenir_statistiques_globales():
    """
    ✅ CORRIGÉ : structure de réponse à plat pour matcher DashboardAdmin.jsx
    (stats.total_users, stats.abonnes_actifs, stats.revenus_mois,
     stats.total_penalites, stats.solde_caisse_admin)
    """
    try:
        try:
            users_response = supabase.table("utilisateurs").select("id").execute()
            nb_utilisateurs = len(users_response.data) if users_response.data else 0
        except Exception as e:
            print(f"Erreur comptage utilisateurs: {e}")
            nb_utilisateurs = 0

        try:
            abonnements_response = supabase.table("abonnements")\
                .select("id").eq("statut", "actif").execute()
            nb_abonnes = len(abonnements_response.data) if abonnements_response.data else 0
        except Exception as e:
            print(f"Info: Table abonnements non disponible ({e})")
            nb_abonnes = 0

        # ✅ NOUVEAU : revenus du mois = abonnements + pénalités créés ce mois
        try:
            from datetime import date
            debut_mois = date.today().replace(day=1).isoformat()

            abonnements_mois = supabase.table("abonnements")\
                .select("montant, date_debut")\
                .gte("date_debut", debut_mois)\
                .execute().data or []
            revenus_abonnements = sum(int(float(a.get("montant", 0) or 0)) for a in abonnements_mois)

            caisse_mois = supabase.table("caisse_admin")\
                .select("montant, date")\
                .gte("date", debut_mois)\
                .execute().data or []
            revenus_caisse_mois = sum(int(float(c.get("montant", 0) or 0)) for c in caisse_mois)

            # On prend caisse_admin comme source unique (elle contient déjà abonnements + pénalités)
            revenus_mois = revenus_caisse_mois
        except Exception as e:
            print(f"Info: Erreur calcul revenus mois ({e})")
            revenus_mois = 0

        try:
            caisse_response = supabase.table("caisse_admin").select("montant").execute()
            caisse_data = caisse_response.data if caisse_response.data else []
            montant_caisse_admin = sum(int(float(c.get("montant", 0) or 0)) for c in caisse_data)
        except Exception as e:
            print(f"Info: Table caisse_admin non disponible ({e})")
            montant_caisse_admin = 0

        try:
            # La colonne "penalite" est réutilisée pour stocker les frais fixes (200 FCFA),
            # uniquement sur les retraits réellement exécutés
            retraits_response = supabase.table("retraits")\
                .select("penalite")\
                .eq("statut", "execute")\
                .execute()
            retraits = retraits_response.data if retraits_response.data else []
            montant_total_frais_retrait = sum(int(float(r.get("penalite", 0) or 0)) for r in retraits)
        except Exception as e:
            print(f"Info: Table retraits non disponible ({e})")
            montant_total_frais_retrait = 0

        # ✅ Clés à plat, exactement celles attendues par le frontend
        return {
            "total_users"           : nb_utilisateurs,
            "abonnes_actifs"        : nb_abonnes,
            "revenus_mois"          : revenus_mois,
            "total_frais_retrait"   : montant_total_frais_retrait,  # ✅ renommé
            "solde_caisse_admin"    : montant_caisse_admin,
        }
    except Exception as e:
        print(f"❌ [ERREUR STATS ADMIN] : {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur stats admin : {str(e)}")


@router.get("/utilisateurs")
def lister_utilisateurs():
    """
    Liste tous les utilisateurs en combinant :
    - Supabase Auth (supabase.auth.admin.list_users())
    - Table utilisateurs
    - Objectifs
    - Abonnements
    """
    try:
        # ✅ Récupération des emails via l'API Admin Auth de Supabase
        emails_par_id = {}
        try:
            auth_response = supabase.auth.admin.list_users()

            # Gestion des différents formats de retour selon la version de gotrue
            liste_users = auth_response if isinstance(auth_response, list) else getattr(auth_response, 'users', [])

            for auth_user in liste_users:
                user_id = getattr(auth_user, 'id', None) or auth_user.get('id') if isinstance(auth_user, dict) else None
                email = getattr(auth_user, 'email', None) or auth_user.get('email') if isinstance(auth_user, dict) else None
                if user_id and email:
                    emails_par_id[str(user_id)] = email

            print(f"✅ {len(emails_par_id)} emails récupérés via auth.admin")

        except Exception as e:
            print(f"❌ [ERREUR EMAILS AUTH.ADMIN] Type: {type(e).__name__} — Message: {str(e)}")

        # Récupérer la table utilisateurs (infos supplémentaires)
        utilisateurs_response = supabase.table("utilisateurs").select("*").execute()
        utilisateurs = utilisateurs_response.data if utilisateurs_response.data else []

        if not utilisateurs:
            return {"total": 0, "utilisateurs": []}

        # Récupérer tous les objectifs
        try:
            objectifs_response = supabase.table("objectifs")\
                .select("utilisateur_id, montant_actuel").execute()
            tous_objectifs = objectifs_response.data if objectifs_response.data else []
        except Exception as e:
            print(f"Info: Erreur récupération objectifs ({e})")
            tous_objectifs = []

        objectifs_par_user = {}
        for obj in tous_objectifs:
            user_id = obj.get("utilisateur_id")
            if user_id:
                objectifs_par_user.setdefault(user_id, []).append(obj)

        # Récupérer les abonnements actifs
        try:
            abonnements_response = supabase.table("abonnements")\
                .select("utilisateur_id").eq("statut", "actif").execute()
            users_avec_abonnement = {a["utilisateur_id"] for a in (abonnements_response.data or [])}
        except Exception as e:
            print(f"Info: Erreur récupération abonnements ({e})")
            users_avec_abonnement = set()

        # Enrichir chaque utilisateur
        for user in utilisateurs:
            user_id = user.get("id")
            objectifs_user = objectifs_par_user.get(user_id, [])

            user["nb_objectifs"] = len(objectifs_user)
            user["montant_epargne"] = sum(
                int(float(o.get("montant_actuel", 0) or 0)) for o in objectifs_user
            )
            user["abonnement_actif"] = user_id in users_avec_abonnement

            if "solde_libre" in user and user["solde_libre"] is not None:
                user["solde_libre"] = int(float(user["solde_libre"]))
            else:
                user["solde_libre"] = 0

            # ✅ Utiliser l'email récupéré via Auth, sinon fallback
            if user_id in emails_par_id:
                user["email"] = emails_par_id[user_id]
            elif not user.get("email"):
                user["email"] = f"user{user_id[:8]}@fincoach.cm"

            if not user.get("prenom"):
                user["prenom"] = user.get("email", "Utilisateur").split("@")[0]

        return {"total": len(utilisateurs), "utilisateurs": utilisateurs}

    except Exception as e:
        print(f"❌ [ERREUR LISTE UTILISATEURS] : {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur liste utilisateurs : {str(e)}")


@router.get("/caisse")
def details_caisse_admin():
    """
    ✅ CORRIGÉ : clé "historique" au lieu de "dernieres_entrees"
    pour matcher dataCaisse.historique dans le frontend.
    """
    try:
        caisse = supabase.table("caisse_admin")\
            .select("*").order("date", desc=True).execute().data or []

        montant_total = sum(int(float(c.get("montant", 0))) for c in caisse)

        return {
            "montant_total": montant_total,
            "nb_entrees": len(caisse),
            "historique": caisse,
        }

    except Exception as e:
        print(f"❌ [ERREUR CAISSE ADMIN] : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur caisse admin : {str(e)}")


@router.get("/utilisateurs/{utilisateur_id}")
def details_utilisateur(utilisateur_id: str):
    try:
        user = supabase.table("utilisateurs")\
            .select("*").eq("id", utilisateur_id).single().execute().data

        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur introuvable")

        objectifs = supabase.table("objectifs")\
            .select("*").eq("utilisateur_id", utilisateur_id).execute().data or []
        cotisations = supabase.table("cotisations")\
            .select("*").eq("utilisateur_id", utilisateur_id).execute().data or []
        retraits = supabase.table("retraits")\
            .select("*").eq("utilisateur_id", utilisateur_id).execute().data or []

        return {
            "utilisateur": user,
            "objectifs": objectifs,
            "statistiques": {
                "nb_objectifs": len(objectifs),
                "nb_cotisations": len(cotisations),
                "nb_retraits": len(retraits),
                "montant_epargne": sum(int(float(o.get("montant_actuel", 0))) for o in objectifs),
                "montant_cotise": sum(int(float(c.get("montant", 0))) for c in cotisations if c.get("statut") == "effectuee"),
                "montant_retire": sum(int(float(r.get("montant", 0))) for r in retraits)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [ERREUR DÉTAILS UTILISATEUR] : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur détails utilisateur : {str(e)}")


# ✅ NOUVELLES ROUTES — le frontend appelait déjà ces URLs, elles n'existaient pas
@router.patch("/utilisateurs/{utilisateur_id}/desactiver")
def desactiver_utilisateur(utilisateur_id: str):
    try:
        result = supabase.table("utilisateurs")\
            .update({"role": "desactive"}).eq("id", utilisateur_id).execute()
        return {"message": "Utilisateur désactivé ✅", "utilisateur": result.data[0] if result.data else None}
    except Exception as e:
        print(f"❌ [ERREUR DÉSACTIVATION] : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur désactivation : {str(e)}")


@router.patch("/utilisateurs/{utilisateur_id}/activer")
def activer_utilisateur(utilisateur_id: str):
    try:
        result = supabase.table("utilisateurs")\
            .update({"role": "user"}).eq("id", utilisateur_id).execute()
        return {"message": "Utilisateur réactivé ✅", "utilisateur": result.data[0] if result.data else None}
    except Exception as e:
        print(f"❌ [ERREUR RÉACTIVATION] : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur réactivation : {str(e)}")


@router.post("/retrait")
def retrait_caisse_admin(req: RetraitAdminRequest):
    """
    ✅ NOUVELLE ROUTE — retrait des fonds de la caisse admin vers Mobile Money.
    Enregistre une ligne négative dans caisse_admin pour tracer la sortie.
    """
    try:
        caisse = supabase.table("caisse_admin").select("montant").execute().data or []
        solde_actuel = sum(int(float(c.get("montant", 0))) for c in caisse)

        if req.montant > solde_actuel:
            raise HTTPException(status_code=400, detail="Solde insuffisant dans la caisse.")

        if not req.moyen_paiement:
            raise HTTPException(status_code=400, detail="Choisis un moyen de paiement (MTN, Orange ou carte).")
        if not req.numero:
            raise HTTPException(status_code=400, detail="Le numéro de téléphone ou de carte est requis.")

        supabase.table("caisse_admin").insert({
            "source"        : "retrait_admin",
            "montant"       : -int(req.montant),  # ligne négative = sortie de caisse
            "utilisateur_id": None,
            "date"          : date.today().isoformat(),
            "moyen_paiement": req.moyen_paiement,
            "numero"        : req.numero,
        }).execute()

        return {"message": "Retrait effectué avec succès ✅", "montant": req.montant}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [ERREUR RETRAIT ADMIN] : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur retrait : {str(e)}")


@router.delete("/utilisateurs/{utilisateur_id}")
def supprimer_utilisateur(utilisateur_id: str):
    try:
        supabase.table("utilisateurs").delete().eq("id", utilisateur_id).execute()
        return {"message": "Utilisateur supprimé ✅"}
    except Exception as e:
        print(f"❌ [ERREUR SUPPRESSION UTILISATEUR] : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur suppression : {str(e)}")