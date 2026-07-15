"""
Router pour la gestion des cotisations automatiques
"""
from datetime import date, datetime
from fastapi import APIRouter, HTTPException
from dateutil.relativedelta import relativedelta
from config import supabase, logger
from routers.notifications import creer_notification

router = APIRouter(prefix="/api/cotisations", tags=["Cotisations"])


# ── ROUTES ──
@router.post("/traiter/{user_id}")
def traiter_cotisations(user_id: str):
    try:
        aujourd_hui = date.today().isoformat()
        resultats   = []

        objectifs = supabase.from_("objectifs")\
            .select("*")\
            .eq("utilisateur_id", user_id)\
            .eq("statut", "actif")\
            .lte("prochaine_echeance", aujourd_hui)\
            .execute().data or []

        if not objectifs:
            return {"message": "Aucune échéance due.", "resultats": []}

        profil = supabase.from_("utilisateurs")\
            .select("solde_libre")\
            .eq("id", user_id)\
            .single()\
            .execute().data

        solde = int(float(profil["solde_libre"]))
        objectifs.sort(key=lambda o: int(float(o["montant_periodique"] or 0)))

        for obj in objectifs:
            montant = int(float(obj["montant_periodique"] or 0))
            if montant <= 0:
                continue

            if solde >= montant:
                nouveau_montant_actuel = int(float(obj["montant_actuel"])) + montant
                solde -= montant

                prochaine = datetime.fromisoformat(obj["prochaine_echeance"])
                freq = obj["frequence"]
                if freq == "jour":
                    prochaine = prochaine + relativedelta(days=1)
                elif freq == "semaine":
                    prochaine = prochaine + relativedelta(weeks=1)
                elif freq == "mois":
                    prochaine = prochaine + relativedelta(months=1)

                nouveau_statut = "atteint" if nouveau_montant_actuel >= int(float(obj["montant_cible"])) else "actif"

                supabase.from_("objectifs").update({
                    "montant_actuel"    : nouveau_montant_actuel,
                    "prochaine_echeance": prochaine.date().isoformat(),
                    "statut"            : nouveau_statut,
                    "couleur_statut"    : "vert",
                }).eq("id", obj["id"]).execute()

                # ✅ Si objectif atteint → argent retourne au solde principal
                if nouveau_statut == "atteint":
                    solde_profil = supabase.from_("utilisateurs")\
                        .select("solde_libre")\
                        .eq("id", user_id)\
                        .single()\
                        .execute().data
                    solde_actuel = int(float(solde_profil["solde_libre"]))
                    supabase.from_("utilisateurs").update({
                        "solde_libre": solde_actuel + nouveau_montant_actuel
                    }).eq("id", user_id).execute()
                    supabase.from_("objectifs").update({
                        "montant_actuel": 0
                    }).eq("id", obj["id"]).execute()
                    logger.info("🎉 Objectif %s atteint ! %s FCFA reversés au solde.", obj['nom'], nouveau_montant_actuel)

                supabase.from_("cotisations").insert({
                    "utilisateur_id": user_id,
                    "objectif_id"   : obj["id"],
                    "montant"       : montant,
                    "montant_prevu" : montant,
                    "type"          : "automatique",
                    "statut"        : "effectuee",
                }).execute()

                resultats.append({"objectif": obj["nom"], "statut": nouveau_statut, "montant": montant})

                # ✅ Notification si l'objectif vient d'être atteint
                if nouveau_statut == "atteint":
                    try:
                        creer_notification(
                            user_id, "objectif_atteint",
                            f"🎉 Objectif « {obj['nom']} » atteint !",
                            "Ton objectif est atteint, l'argent a été reversé sur ton solde principal."
                        )
                    except Exception as e:
                        logger.warning("Info: Notification non envoyée (%s)", e)

            else:
                supabase.from_("objectifs").update({
                    "couleur_statut": "rouge",
                }).eq("id", obj["id"]).execute()

                logger.warning("⚠️ Solde insuffisant pour %s. Passage en alerte rouge.", obj['nom'])
                resultats.append({
                    "objectif"        : obj["nom"],
                    "statut"          : "en_attente",
                    "montant_manquant": montant - solde
                })

                # ✅ Notification de cotisation échouée
                try:
                    creer_notification(
                        user_id, "cotisation_echouee",
                        f"⚠️ Cotisation manquée — {obj['nom']}",
                        f"Solde insuffisant pour la cotisation de {montant} FCFA. Elle sera retentée automatiquement."
                    )
                except Exception as e:
                    logger.warning("Info: Notification non envoyée (%s)", e)
                break

        supabase.from_("utilisateurs").update({"solde_libre": solde}).eq("id", user_id).execute()
        return {"message": "Traitement terminé", "resultats": resultats}

    except Exception as e:
        logger.exception("❌ [ERREUR COTISATIONS] : %s", str(e))
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")


@router.post("/verifier-toutes")
def verifier_toutes():
    """Vérification CRON pour tous les utilisateurs avec échéances dues"""
    aujourd_hui = date.today().isoformat()
    users = supabase.from_("objectifs")\
        .select("utilisateur_id")\
        .eq("statut", "actif")\
        .lte("prochaine_echeance", aujourd_hui)\
        .execute().data or []

    user_ids = list(set(u["utilisateur_id"] for u in users))
    for uid in user_ids:
        traiter_cotisations(uid)

    return {"message": f"{len(user_ids)} utilisateurs traités."}
