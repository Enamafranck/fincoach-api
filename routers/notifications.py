"""
Router pour la gestion des notifications utilisateur
"""
from datetime import date, timedelta
from fastapi import APIRouter, HTTPException
from config import supabase, logger

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


def creer_notification(utilisateur_id: str, type_notif: str, titre: str, message: str):
    """
    Fonction utilitaire appelée depuis d'autres routers (cotisations, retraits, abonnements)
    pour créer une notification. Ne lève jamais d'exception bloquante.
    """
    try:
        supabase.table("notifications").insert({
            "utilisateur_id": utilisateur_id,
            "type"          : type_notif,
            "titre"         : titre,
            "message"       : message,
        }).execute()
    except Exception as e:
        logger.warning("⚠️ Notification non créée : %s", str(e))


@router.get("/{utilisateur_id}")
def lister_notifications(utilisateur_id: str):
    try:
        notifs = supabase.table("notifications")\
            .select("*")\
            .eq("utilisateur_id", utilisateur_id)\
            .order("created_at", desc=True)\
            .limit(30)\
            .execute().data or []

        nb_non_lues = sum(1 for n in notifs if not n.get("lu"))

        return {"notifications": notifs, "nb_non_lues": nb_non_lues}

    except Exception as e:
        logger.exception("❌ [ERREUR LISTE NOTIFICATIONS] : %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{notification_id}/lire")
def marquer_lue(notification_id: str):
    try:
        supabase.table("notifications").update({"lu": True}).eq("id", notification_id).execute()
        return {"message": "Notification marquée comme lue"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{utilisateur_id}/lire-tout")
def marquer_toutes_lues(utilisateur_id: str):
    try:
        supabase.table("notifications").update({"lu": True})\
            .eq("utilisateur_id", utilisateur_id).eq("lu", False).execute()
        return {"message": "Toutes les notifications ont été marquées comme lues"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ Analyse comportementale — dépenses déclarées sur les 3 derniers jours
@router.post("/{utilisateur_id}/analyser-depenses")
def analyser_depenses_recentes(utilisateur_id: str):
    """
    Appelée périodiquement (ou au login) pour détecter un comportement de
    dépense excessif sur les 3 derniers jours et générer une notification
    du Coach IA si nécessaire.
    """
    try:
        il_y_a_3_jours = (date.today() - timedelta(days=3)).isoformat()

        depenses = supabase.table("transactions")\
            .select("montant, categorie")\
            .eq("utilisateur_id", utilisateur_id)\
            .eq("type", "depense")\
            .gte("date", il_y_a_3_jours)\
            .execute().data or []

        total = sum(int(float(d.get("montant", 0))) for d in depenses)

        # Seuil simple : plus de 5 000 FCFA de dépenses déclarées sur 3 jours
        if total >= 5000:
            creer_notification(
                utilisateur_id,
                "comportement",
                "Ton Coach a remarqué quelque chose 👀",
                f"Tu as déclaré {total:,} FCFA de dépenses ces 3 derniers jours. Discute avec ton Coach IA pour voir comment ajuster.".replace(",", " ")
            )
            return {"alerte_creee": True, "total": total}

        return {"alerte_creee": False, "total": total}

    except Exception as e:
        logger.exception("❌ [ERREUR ANALYSE DEPENSES] : %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))