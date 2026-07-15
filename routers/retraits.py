"""
Router pour la gestion des retraits et transferts d'objectifs
✅ Nouveau système : plus de pénalité en % — frais fixes de 200 FCFA sur tout retrait.
✅ Délai de carence de 24h obligatoire pour tout retrait anticipé (objectif non atteint),
   avec un nudge du Coach IA au moment de la demande (géré côté frontend).
"""
from datetime import date, datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config import supabase, logger
from routers.notifications import creer_notification

router = APIRouter(prefix="/api", tags=["Retraits"])

FRAIS_RETRAIT = 200  # ✅ frais fixe unique, plus de pourcentage
DELAI_CARENCE_HEURES = 24


# ── MODÈLES ──
class RetraitRequest(BaseModel):
    user_id: str
    objectif_id: str
    montant_demande: int


class TransfertObjectifRequest(BaseModel):
    user_id: str
    objectif_id: str
    montant: int


class RetraitSoldeLibreRequest(BaseModel):
    user_id: str
    montant: int


class ConfirmerRetraitRequest(BaseModel):
    user_id: str


# ── ROUTES ──
@router.post("/retraits/effectuer")
def effectuer_retrait(req: RetraitRequest):
    """
    - Objectif atteint  → retrait immédiat, 200 FCFA de frais fixes
    - Objectif non atteint → mise en carence 24h avant de pouvoir confirmer,
      toujours 200 FCFA de frais (prélevés à la confirmation, pas à la demande)
    """
    try:
        objectif = supabase.from_("objectifs")\
            .select("*")\
            .eq("id", req.objectif_id)\
            .eq("utilisateur_id", req.user_id)\
            .single()\
            .execute().data

        if not objectif:
            raise HTTPException(status_code=404, detail="Objectif introuvable.")

        montant_actuel  = int(float(objectif["montant_actuel"]))
        montant_cible   = int(float(objectif["montant_cible"]))
        statut_objectif = objectif["statut"]

        if req.montant_demande <= 0:
            raise HTTPException(status_code=400, detail="Le montant doit être supérieur à 0.")

        if req.montant_demande > montant_actuel:
            raise HTTPException(
                status_code=400,
                detail=f"Montant insuffisant. Disponible : {montant_actuel} FCFA."
            )

        if req.montant_demande <= FRAIS_RETRAIT:
            raise HTTPException(
                status_code=400,
                detail=f"Le montant doit être supérieur aux frais de retrait ({FRAIS_RETRAIT} FCFA)."
            )

        nouveau_montant_actuel = montant_actuel - req.montant_demande
        nouveau_statut         = "actif" if nouveau_montant_actuel < montant_cible else "atteint"

        # ✅ Dans tous les cas, l'argent est immédiatement réservé (sorti de l'objectif)
        # pour empêcher qu'il serve deux fois (double dépense pendant la carence)
        supabase.from_("objectifs").update({
            "montant_actuel": nouveau_montant_actuel,
            "statut"        : nouveau_statut,
            "couleur_statut": "vert" if nouveau_statut == "atteint" else "orange",
        }).eq("id", req.objectif_id).execute()

        # ── CAS 1 : Objectif atteint → retrait immédiat ──
        if statut_objectif == "atteint":
            montant_net = req.montant_demande - FRAIS_RETRAIT

            profil = supabase.from_("utilisateurs")\
                .select("solde_libre")\
                .eq("id", req.user_id)\
                .single()\
                .execute().data

            nouveau_solde = int(float(profil["solde_libre"])) + montant_net

            supabase.from_("utilisateurs").update({
                "solde_libre": nouveau_solde
            }).eq("id", req.user_id).execute()

            supabase.from_("retraits").insert({
                "utilisateur_id": req.user_id,
                "objectif_id"   : req.objectif_id,
                "montant"       : req.montant_demande,
                "date"          : date.today().isoformat(),
                "anticipe"      : False,
                "penalite"      : FRAIS_RETRAIT,  # ✅ colonne réutilisée pour stocker les frais fixes
                "statut"        : "execute",
            }).execute()

            return {
                "message"          : "Retrait effectué avec succès ✅",
                "type_retrait"     : "normal",
                "carence"          : False,
                "montant_demande"  : req.montant_demande,
                "frais"            : FRAIS_RETRAIT,
                "montant_net"      : montant_net,
                "nouveau_solde"    : nouveau_solde,
                "objectif_restant" : nouveau_montant_actuel,
            }

        # ── CAS 2 : Retrait anticipé → carence 24h ──
        date_disponible = datetime.now(timezone.utc) + timedelta(hours=DELAI_CARENCE_HEURES)

        retrait_insere = supabase.from_("retraits").insert({
            "utilisateur_id" : req.user_id,
            "objectif_id"    : req.objectif_id,
            "montant"        : req.montant_demande,
            "date"           : date.today().isoformat(),
            "anticipe"       : True,
            "penalite"       : FRAIS_RETRAIT,
            "statut"         : "en_attente_carence",
            "date_disponible": date_disponible.isoformat(),
        }).execute()

        retrait_id = retrait_insere.data[0]["id"] if retrait_insere.data else None

        creer_notification(
            req.user_id, "retrait_carence",
            "⏳ Retrait en attente",
            f"Ton retrait de {req.montant_demande} FCFA sur « {objectif['nom']} » sera disponible dans 24h, le temps d'une pause pour réfléchir."
        )

        return {
            "message"          : "Retrait anticipé enregistré — délai de 24h avant confirmation.",
            "type_retrait"     : "anticipe",
            "carence"          : True,
            "retrait_id"       : retrait_id,
            "montant_demande"  : req.montant_demande,
            "frais"            : FRAIS_RETRAIT,
            "date_disponible"  : date_disponible.isoformat(),
            "objectif_restant" : nouveau_montant_actuel,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ [ERREUR RETRAIT] : %s", str(e))
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/retraits/{retrait_id}/confirmer")
def confirmer_retrait(retrait_id: str, req: ConfirmerRetraitRequest):
    """
    Finalise un retrait anticipé après expiration du délai de carence de 24h.
    Applique les 200 FCFA de frais et crédite le solde libre.
    """
    try:
        retrait = supabase.from_("retraits")\
            .select("*")\
            .eq("id", retrait_id)\
            .eq("utilisateur_id", req.user_id)\
            .single()\
            .execute().data

        if not retrait:
            raise HTTPException(status_code=404, detail="Retrait introuvable.")

        if retrait["statut"] == "execute":
            raise HTTPException(status_code=400, detail="Ce retrait a déjà été exécuté.")

        if retrait["statut"] == "annule":
            raise HTTPException(status_code=400, detail="Ce retrait a été annulé.")

        date_disponible = datetime.fromisoformat(retrait["date_disponible"])
        maintenant = datetime.now(timezone.utc)

        if maintenant < date_disponible:
            heures_restantes = round((date_disponible - maintenant).total_seconds() / 3600, 1)
            raise HTTPException(
                status_code=400,
                detail=f"Encore en délai de carence. Disponible dans {heures_restantes}h."
            )

        montant     = int(float(retrait["montant"]))
        montant_net = montant - FRAIS_RETRAIT

        profil = supabase.from_("utilisateurs")\
            .select("solde_libre")\
            .eq("id", req.user_id)\
            .single()\
            .execute().data

        nouveau_solde = int(float(profil["solde_libre"])) + montant_net

        supabase.from_("utilisateurs").update({
            "solde_libre": nouveau_solde
        }).eq("id", req.user_id).execute()

        supabase.from_("retraits").update({
            "statut": "execute",
        }).eq("id", retrait_id).execute()

        creer_notification(
            req.user_id, "retrait_confirme",
            "✅ Retrait confirmé",
            f"{montant_net} FCFA ont été crédités sur ton solde libre."
        )

        return {
            "message"      : "Retrait confirmé et exécuté ✅",
            "montant_net"  : montant_net,
            "frais"        : FRAIS_RETRAIT,
            "nouveau_solde": nouveau_solde,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ [ERREUR CONFIRMATION RETRAIT] : %s", str(e))
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/retraits/{retrait_id}/annuler")
def annuler_retrait(retrait_id: str, req: ConfirmerRetraitRequest):
    """
    Annule un retrait en attente de carence — l'argent retourne dans l'objectif.
    Permet à l'utilisateur de changer d'avis pendant les 24h.
    """
    try:
        retrait = supabase.from_("retraits")\
            .select("*")\
            .eq("id", retrait_id)\
            .eq("utilisateur_id", req.user_id)\
            .single()\
            .execute().data

        if not retrait:
            raise HTTPException(status_code=404, detail="Retrait introuvable.")

        if retrait["statut"] != "en_attente_carence":
            raise HTTPException(status_code=400, detail="Ce retrait ne peut plus être annulé.")

        objectif = supabase.from_("objectifs")\
            .select("montant_actuel, montant_cible")\
            .eq("id", retrait["objectif_id"])\
            .single()\
            .execute().data

        montant_restaure = int(float(objectif["montant_actuel"])) + int(float(retrait["montant"]))
        nouveau_statut = "atteint" if montant_restaure >= int(float(objectif["montant_cible"])) else "actif"

        supabase.from_("objectifs").update({
            "montant_actuel": montant_restaure,
            "statut"        : nouveau_statut,
        }).eq("id", retrait["objectif_id"]).execute()

        supabase.from_("retraits").update({
            "statut": "annule",
        }).eq("id", retrait_id).execute()

        return {"message": "Retrait annulé, argent restauré dans l'objectif 👍"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ [ERREUR ANNULATION RETRAIT] : %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/retraits/en-attente/{user_id}")
def lister_retraits_en_attente(user_id: str):
    """Liste les retraits en carence pour affichage frontend (bannière + compte à rebours)."""
    try:
        retraits = supabase.from_("retraits")\
            .select("*, objectifs(nom)")\
            .eq("utilisateur_id", user_id)\
            .eq("statut", "en_attente_carence")\
            .execute().data or []

        maintenant = datetime.now(timezone.utc)
        resultats = []
        for r in retraits:
            date_disponible = datetime.fromisoformat(r["date_disponible"])
            resultats.append({
                "id"              : r["id"],
                "objectif_nom"    : r.get("objectifs", {}).get("nom", "Objectif"),
                "montant"         : int(float(r["montant"])),
                "date_disponible" : r["date_disponible"],
                "disponible"      : maintenant >= date_disponible,
            })

        return {"retraits_en_attente": resultats}

    except Exception as e:
        logger.exception("❌ [ERREUR LISTE ATTENTE] : %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Retrait solde libre — toujours immédiat, 200 FCFA de frais (pas de carence,
# ce n'est pas un objectif d'épargne donc pas de logique de discipline à appliquer)
@router.post("/retraits/solde-libre")
def retirer_solde_libre(req: RetraitSoldeLibreRequest):
    try:
        if req.montant <= 0:
            raise HTTPException(status_code=400, detail="Le montant doit être supérieur à 0.")

        if req.montant <= FRAIS_RETRAIT:
            raise HTTPException(
                status_code=400,
                detail=f"Le montant doit être supérieur aux frais de retrait ({FRAIS_RETRAIT} FCFA)."
            )

        profil = supabase.from_("utilisateurs")\
            .select("solde_libre")\
            .eq("id", req.user_id)\
            .single()\
            .execute().data

        if not profil:
            raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

        solde_actuel = int(float(profil["solde_libre"]))

        if req.montant > solde_actuel:
            raise HTTPException(
                status_code=400,
                detail=f"Solde insuffisant. Disponible : {solde_actuel} FCFA."
            )

        montant_net   = req.montant - FRAIS_RETRAIT
        nouveau_solde = solde_actuel - req.montant + FRAIS_RETRAIT - FRAIS_RETRAIT  # = solde_actuel - montant_net - frais... simplifié ci-dessous
        nouveau_solde = solde_actuel - req.montant

        supabase.from_("utilisateurs").update({
            "solde_libre": nouveau_solde
        }).eq("id", req.user_id).execute()

        supabase.from_("retraits").insert({
            "utilisateur_id": req.user_id,
            "objectif_id"   : None,
            "montant"       : req.montant,
            "date"          : date.today().isoformat(),
            "anticipe"      : False,
            "penalite"      : FRAIS_RETRAIT,
            "statut"        : "execute",
        }).execute()

        return {
            "message"      : "Retrait effectué avec succès ✅",
            "frais"        : FRAIS_RETRAIT,
            "montant_net"  : montant_net,
            "nouveau_solde": nouveau_solde,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("❌ [ERREUR RETRAIT SOLDE LIBRE] : %s", str(e))
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/objectifs/transferer-solde")
def transferer_objectif_vers_solde(req: TransfertObjectifRequest):
    """Alias conservé pour compatibilité — redirige vers la même logique que /retraits/effectuer."""
    return effectuer_retrait(RetraitRequest(
        user_id=req.user_id,
        objectif_id=req.objectif_id,
        montant_demande=req.montant,
    ))


@router.put("/objectifs/{objectif_id}/toggle-statut")
def toggle_statut_objectif(objectif_id: str, current_statut: str, user_id: str):
    try:
        if current_statut == "atteint":
            raise HTTPException(status_code=400, detail="Impossible de modifier un objectif atteint.")

        nouveau_statut   = "en_pause" if current_statut == "actif" else "actif"
        nouvelle_couleur = "gris" if nouveau_statut == "en_pause" else "vert"

        supabase.from_("objectifs").update({
            "statut"        : nouveau_statut,
            "couleur_statut": nouvelle_couleur,
        }).eq("id", objectif_id).eq("utilisateur_id", user_id).execute()

        return {
            "message"       : f"Objectif {'mis en pause ⏸️' if nouveau_statut == 'en_pause' else 'réactivé ✅'}",
            "nouveau_statut": nouveau_statut,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))