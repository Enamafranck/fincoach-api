"""
Scheduler pour les tâches automatiques FinCoach
Utilise APScheduler pour exécuter des tâches planifiées
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

# Import des fonctions métier
from routers.abonnements import expirer_abonnements_echus
from routers.cotisations import verifier_toutes

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── INITIALISATION DU SCHEDULER ──
scheduler = BackgroundScheduler()


# ── TÂCHE : EXPIRER LES ABONNEMENTS (Quotidien à 00h05) ──
def job_expirer_abonnements():
    """
    Tâche quotidienne : expirer les abonnements échus
    S'exécute tous les jours à 00h05
    """
    try:
        logger.info("🕐 [JOB] Début expiration abonnements...")
        resultat = expirer_abonnements_echus()
        logger.info(f"✅ [JOB] Abonnements expirés : {resultat['nb_expires']}")
    except Exception as e:
        logger.error(f"❌ [JOB] Erreur expiration abonnements : {str(e)}")


# ── TÂCHE : VÉRIFIER COTISATIONS (Quotidien à 06h00) ──
def job_verifier_cotisations():
    """
    Tâche quotidienne : vérifier et traiter les cotisations dues
    S'exécute tous les jours à 06h00
    """
    try:
        logger.info("🕐 [JOB] Début vérification cotisations...")
        resultat = verifier_toutes()
        logger.info(f"✅ [JOB] Cotisations vérifiées : {resultat}")
    except Exception as e:
        logger.error(f"❌ [JOB] Erreur vérification cotisations : {str(e)}")


# ── ENREGISTREMENT DES TÂCHES ──
def demarrer_scheduler():
    """
    Démarre le scheduler et enregistre toutes les tâches planifiées
    """
    try:
        # Tâche 1 : Expirer abonnements (tous les jours à 00h05)
        scheduler.add_job(
            job_expirer_abonnements,
            trigger=CronTrigger(hour=0, minute=5),
            id="expirer_abonnements",
            name="Expirer les abonnements échus",
            replace_existing=True
        )
        logger.info("✅ Tâche planifiée : Expiration abonnements (00h05)")
        
        # Tâche 2 : Vérifier cotisations (tous les jours à 06h00)
        scheduler.add_job(
            job_verifier_cotisations,
            trigger=CronTrigger(hour=6, minute=0),
            id="verifier_cotisations",
            name="Vérifier cotisations automatiques",
            replace_existing=True
        )
        logger.info("✅ Tâche planifiée : Vérification cotisations (06h00)")
        
        # Démarrer le scheduler
        scheduler.start()
        logger.info("🚀 Scheduler démarré avec succès")
        
        # Afficher les tâches enregistrées
        jobs = scheduler.get_jobs()
        logger.info(f"📋 {len(jobs)} tâche(s) planifiée(s) :")
        for job in jobs:
            logger.info(f"   - {job.name} (ID: {job.id})")
    
    except Exception as e:
        logger.error(f"❌ Erreur démarrage scheduler : {str(e)}")


def arreter_scheduler():
    """
    Arrête le scheduler proprement
    """
    try:
        scheduler.shutdown(wait=False)
        logger.info("🛑 Scheduler arrêté")
    except Exception as e:
        logger.error(f"❌ Erreur arrêt scheduler : {str(e)}")


# ── FONCTIONS D'INSPECTION ──
def lister_taches():
    """
    Liste toutes les tâches planifiées
    """
    jobs = scheduler.get_jobs()
    return [{
        "id": job.id,
        "name": job.name,
        "next_run": str(job.next_run_time) if job.next_run_time else "N/A",
        "trigger": str(job.trigger)
    } for job in jobs]


def executer_tache_manuellement(job_id: str):
    """
    Exécute une tâche immédiatement sans attendre le planning
    """
    try:
        job = scheduler.get_job(job_id)
        if not job:
            raise Exception(f"Tâche {job_id} introuvable")
        
        job.func()
        return {"message": f"Tâche {job_id} exécutée manuellement"}
    except Exception as e:
        raise Exception(f"Erreur exécution manuelle : {str(e)}")


# ── EXPORT ──
__all__ = [
    "demarrer_scheduler",
    "arreter_scheduler",
    "lister_taches",
    "executer_tache_manuellement",
    "scheduler"
]
