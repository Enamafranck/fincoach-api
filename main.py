"""
FinCoach API - Point d'entrée principal
Architecture modulaire avec routers FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import ai_provider, logger
from routers import notifications


# Import des routers
from routers import coach, cotisations, retraits, paiements, transactions, admin, abonnements

# Import du scheduler
from scheduler import demarrer_scheduler, arreter_scheduler, lister_taches, executer_tache_manuellement


# ── LIFESPAN : GESTION DU CYCLE DE VIE DE L'APP ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gère le démarrage et l'arrêt de l'application
    """
    # Démarrage
    logger.info("🚀 Démarrage de FinCoach API...")
    demarrer_scheduler()
    yield
    # Arrêt
    logger.info("🛑 Arrêt de FinCoach API...")
    arreter_scheduler()

# ── INITIALISATION FASTAPI ──
app = FastAPI(title="FinCoach API", lifespan=lifespan)

# ── MIDDLEWARE CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ENREGISTREMENT DES ROUTERS ──
app.include_router(coach.router)
app.include_router(cotisations.router)
app.include_router(retraits.router)
app.include_router(paiements.router)
app.include_router(transactions.router)
app.include_router(admin.router)
app.include_router(abonnements.router)
app.include_router(notifications.router)


# ── ROUTE RACINE ──
@app.get("/")
def root():
    return {
        "message": "FinCoach API operationnelle",
        "ia_active": ai_provider or "Aucune",
        "architecture": "Modulaire avec routers",
        "scheduler": "APScheduler actif",
        "taches_planifiees": lister_taches(),
        "routers": [
            "/api/coach/chat",
            "/api/cotisations/traiter/{user_id}",
            "/api/cotisations/verifier-toutes",
            "/api/retraits/effectuer",
            "/api/objectifs/transferer-solde",
            "/api/paiements/initier",
            "/api/paiements/webhook",
            "/api/paiements/statut/{reference}",
            "/api/transactions/stats/{utilisateur_id}",
            "/api/transactions/historique/{utilisateur_id}",
            "/api/objectifs/{objectif_id}/desactiver",
            "/api/objectifs/{objectif_id}/reactiver",
            "/api/objectifs/{objectif_id} [DELETE]",
            "/api/admin/stats",
            "/api/admin/utilisateurs",
            "/api/admin/caisse",
            "/api/abonnements/expirer-echus [POST]",
            "/api/abonnements/statut/{utilisateur_id}",
            "/api/abonnements/actifs",
            "/api/abonnements/expires"
        ]
    }


# ── ROUTE : EXÉCUTER UNE TÂCHE MANUELLEMENT ──
@app.post("/scheduler/executer/{job_id}")
def executer_tache(job_id: str):
    """
    Exécute une tâche planifiée immédiatement (pour debug/test)
    job_id: "expirer_abonnements" ou "verifier_cotisations"
    """
    try:
        resultat = executer_tache_manuellement(job_id)
        return resultat
    except Exception as e:
        return {"error": str(e)}
        
