# FinCoach API - Architecture Modulaire

## 📁 Structure du Projet

```
backend/
├── main.py                 # Point d'entrée FastAPI (CORS, routers)
├── config.py               # Configuration centralisée (Supabase, IA, variables)
├── requirements.txt        # Dépendances Python
├── .env                    # Variables d'environnement
│
└── routers/               # Modules de routes organisés par domaine
    ├── __init__.py
    ├── coach.py           # /api/coach/chat
    ├── cotisations.py     # /api/cotisations/*
    ├── retraits.py        # /api/retraits/* + /api/objectifs/transferer-solde
    ├── paiements.py       # /api/paiements/* (CinetPay)
    └── transactions.py    # /api/transactions/* + CRUD objectifs
```

## 🚀 Démarrage Rapide

### Installation

```bash
# Activer l'environnement virtuel
.\venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### Lancement du serveur

```bash
# Démarrage avec Uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Test de l'architecture

```bash
python test_import.py
```

## 📋 Routes Disponibles

### 🤖 Coach IA
- `POST /api/coach/chat` - Dialogue avec le coach financier IA

### 💰 Cotisations
- `POST /api/cotisations/traiter/{user_id}` - Traiter les cotisations dues
- `POST /api/cotisations/verifier-toutes` - CRON pour vérifier tous les utilisateurs

### 🏦 Retraits
- `POST /api/retraits/effectuer` - Retrait depuis un objectif
- `POST /api/objectifs/transferer-solde` - Transfert objectif → solde principal

### 💳 Paiements (CinetPay)
- `POST /api/paiements/initier` - Initier un paiement (dépôt/retrait)
- `POST /api/paiements/webhook` - Webhook CinetPay
- `GET /api/paiements/statut/{reference}` - Vérifier le statut d'un paiement

### 📊 Transactions & Objectifs
- `GET /api/transactions/stats/{utilisateur_id}` - Statistiques compteurs
- `GET /api/transactions/historique/{utilisateur_id}` - Historique global
- `PATCH /api/objectifs/{objectif_id}/desactiver` - Désactiver un objectif
- `PATCH /api/objectifs/{objectif_id}/reactiver` - Réactiver un objectif
- `DELETE /api/objectifs/{objectif_id}` - Supprimer un objectif

## 🔧 Configuration

Les variables d'environnement sont centralisées dans `config.py` :

### Clients initialisés
- **Supabase** : Base de données et authentification
- **IA** : Support de Groq, Gemini ou Anthropic (auto-détection)
- **CinetPay** : Gateway de paiement mobile

### Variables disponibles
```python
from config import (
    supabase,           # Client Supabase
    ai_client,          # Client IA (Groq/Gemini/Anthropic)
    ai_provider,        # Provider IA actif
    SYSTEM_PROMPT,      # Prompt du coach
    CINETPAY_API_KEY,   # Clé API CinetPay
    CINETPAY_SITE_ID,   # Site ID CinetPay
    FRONTEND_URL,       # URL frontend
    BACKEND_URL         # URL backend
)
```

## 📦 Avantages de l'Architecture Modulaire

✅ **Séparation des responsabilités** : Chaque router gère un domaine métier  
✅ **Maintenance facilitée** : Modifications isolées par module  
✅ **Lisibilité améliorée** : Fichiers courts et focalisés  
✅ **Scalabilité** : Ajout facile de nouveaux routers  
✅ **Testabilité** : Tests unitaires par module  

## 🛠️ Ajouter un Nouveau Router

1. Créer `routers/mon_router.py`
2. Définir le router :
   ```python
   from fastapi import APIRouter
   from config import supabase
   
   router = APIRouter(prefix="/api/mon-module", tags=["Mon Module"])
   
   @router.get("/ma-route")
   def ma_fonction():
       return {"message": "OK"}
   ```
3. Enregistrer dans `main.py` :
   ```python
   from routers import mon_router
   app.include_router(mon_router.router)
   ```

## 📝 Notes Techniques

- **FastAPI** : Framework web moderne avec validation automatique
- **Pydantic** : Modèles de données typés
- **Supabase** : PostgreSQL avec API REST automatique
- **CORS** : Configuré pour `localhost:5173` (frontend Vite/React)

---

**Développé pour FinCoach - Cameroun & Afrique Centrale 🇨🇲**
