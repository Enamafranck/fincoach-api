# 🏗️ Architecture FinCoach API

## 📊 Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│                  http://localhost:5173                   │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/JSON
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   main.py (FastAPI)                      │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │           CORS Middleware                       │    │
│  │  allow_origins: ["http://localhost:5173"]      │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │             Router Inclusions                   │    │
│  │  • coach.router                                 │    │
│  │  • cotisations.router                           │    │
│  │  • retraits.router                              │    │
│  │  • paiements.router                             │    │
│  │  • transactions.router                          │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  config.py  │ │  routers/   │ │   models    │
│             │ │             │ │  (Pydantic) │
│ • Supabase  │ │ • coach     │ │             │
│ • IA Client │ │ • cotis...  │ │ Intégrés    │
│ • Variables │ │ • retraits  │ │ dans les    │
│ • Constantes│ │ • paiements │ │ routers     │
│             │ │ • transac...│ │             │
└─────────────┘ └─────────────┘ └─────────────┘
       │
       └──────────────┬──────────────┐
                      ▼              ▼
           ┌──────────────┐  ┌──────────────┐
           │   Supabase   │  │  IA Providers │
           │  PostgreSQL  │  │               │
           │              │  │ • Groq (Llama)│
           │ Tables:      │  │ • Gemini      │
           │ • utilisat.. │  │ • Anthropic   │
           │ • objectifs  │  └──────────────┘
           │ • cotisations│
           │ • retraits   │  ┌──────────────┐
           │ • transac... │  │  CinetPay    │
           └──────────────┘  │  Payment API │
                             │              │
                             │ • Initiate   │
                             │ • Webhook    │
                             │ • Status     │
                             └──────────────┘
```

## 🔄 Flux de Requêtes

### Exemple : Chat avec le Coach IA

```
1. Frontend → POST /api/coach/chat
                ↓
2. main.py → CORS check → coach.router
                ↓
3. coach.py → Récupère user data depuis config.supabase
                ↓
4. coach.py → Construit contexte utilisateur
                ↓
5. coach.py → Appelle config.ai_client (Groq/Gemini/Anthropic)
                ↓
6. coach.py → Retourne réponse formatée
                ↓
7. Frontend ← JSON response
```

### Exemple : Traitement Cotisation

```
1. CRON/Frontend → POST /api/cotisations/traiter/{user_id}
                     ↓
2. main.py → cotisations.router
                     ↓
3. cotisations.py → Query objectifs dus (Supabase)
                     ↓
4. cotisations.py → Vérifie solde utilisateur
                     ↓
5. cotisations.py → Débite solde, crédite objectifs
                     ↓
6. cotisations.py → Si atteint → reverse au solde
                     ↓
7. Frontend ← Résultats cotisations
```

### Exemple : Paiement CinetPay

```
1. Frontend → POST /api/paiements/initier
                ↓
2. paiements.py → Crée transaction dans Supabase
                ↓
3. paiements.py → Appelle CinetPay API
                ↓
4. Frontend ← URL de paiement CinetPay
                ↓
5. User paie sur CinetPay
                ↓
6. CinetPay → POST /api/paiements/webhook
                ↓
7. paiements.py → Valide paiement → Met à jour solde
```

## 📦 Modules et Responsabilités

### config.py
**Responsabilité** : Configuration centralisée  
**Exports** :
- `supabase` : Client Supabase initialisé
- `ai_client` : Client IA (Groq/Gemini/Anthropic)
- `ai_provider` : Nom du provider actif
- `SYSTEM_PROMPT` : Prompt du coach IA
- Constantes CinetPay, URLs

**Dépendances** :
```python
from supabase import create_client
from groq import Groq
import google.generativeai as genai
import anthropic
```

### routers/coach.py
**Responsabilité** : Dialogue avec le coach IA  
**Routes** :
- `POST /api/coach/chat`

**Logique métier** :
- Récupération profil utilisateur
- Construction contexte dynamique
- Gestion multi-providers IA
- Formatage réponses

**Dépendances** :
```python
from config import SYSTEM_PROMPT, ai_client, ai_provider, supabase
```

### routers/cotisations.py
**Responsabilité** : Gestion cotisations automatiques  
**Routes** :
- `POST /api/cotisations/traiter/{user_id}`
- `POST /api/cotisations/verifier-toutes`

**Logique métier** :
- Calcul échéances périodiques
- Prélèvement automatique
- Gestion solde insuffisant
- Reversement si objectif atteint

**Dépendances** :
```python
from config import supabase
from dateutil.relativedelta import relativedelta
```

### routers/retraits.py
**Responsabilité** : Retraits et transferts objectifs  
**Routes** :
- `POST /api/retraits/effectuer`
- `POST /api/objectifs/transferer-solde`

**Logique métier** :
- Calcul pénalités (5% si non atteint)
- Mise à jour soldes
- Versement caisse admin
- Validation montants

**Dépendances** :
```python
from config import supabase
```

### routers/paiements.py
**Responsabilité** : Intégration CinetPay  
**Routes** :
- `POST /api/paiements/initier`
- `POST /api/paiements/webhook`
- `GET /api/paiements/statut/{reference}`

**Logique métier** :
- Génération références uniques
- Appels API CinetPay
- Traitement webhooks
- Mode test/production

**Dépendances** :
```python
from config import supabase, CINETPAY_API_KEY, CINETPAY_SITE_ID
import httpx
import uuid
```

### routers/transactions.py
**Responsabilité** : Stats, historique, CRUD objectifs  
**Routes** :
- `GET /api/transactions/stats/{utilisateur_id}`
- `GET /api/transactions/historique/{utilisateur_id}`
- `PATCH /api/objectifs/{objectif_id}/desactiver`
- `PATCH /api/objectifs/{objectif_id}/reactiver`
- `DELETE /api/objectifs/{objectif_id}`

**Logique métier** :
- Calcul indicateurs financiers
- Agrégation historique
- Gestion états objectifs
- Suppression avec reversement

**Dépendances** :
```python
from config import supabase
```

## 🔐 Sécurité

### Variables sensibles (.env)
```
❌ Jamais en dur dans le code
✅ Toujours via os.getenv() dans config.py
✅ .env dans .gitignore
```

### Validation données
```
✅ Pydantic models pour validation auto
✅ HTTPException pour erreurs explicites
✅ Vérifications montants > 0
✅ Checks user_id ownership
```

### CORS
```
✅ Origine autorisée : http://localhost:5173
✅ Méthodes : toutes (*, development)
✅ Headers : tous (*, development)
```

## 📈 Scalabilité

### Ajout d'une nouvelle route
```python
# 1. Créer routers/nouveau.py
from fastapi import APIRouter
from config import supabase

router = APIRouter(prefix="/api/nouveau", tags=["Nouveau"])

@router.get("/route")
def ma_route():
    return {"ok": True}
```

```python
# 2. Enregistrer dans main.py
from routers import nouveau
app.include_router(nouveau.router)
```

### Ajout d'une nouvelle dépendance
```bash
# 1. Installer
pip install nouvelle-lib

# 2. Ajouter à requirements.txt
echo "nouvelle-lib==1.0.0" >> requirements.txt

# 3. Importer dans config.py si partagée
# Ou directement dans le router si spécifique
```

## 🧪 Testing

### Tests unitaires (structure recommandée)
```
tests/
├── test_coach.py
├── test_cotisations.py
├── test_retraits.py
├── test_paiements.py
└── test_transactions.py
```

### Exemple test
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "ia_active" in response.json()
```

## 📊 Monitoring

### Logs structurés
```python
# Dans chaque router
import logging
logger = logging.getLogger(__name__)

logger.info(f"✅ Action réussie : {data}")
logger.warning(f"⚠️ Attention : {warning}")
logger.error(f"❌ Erreur : {error}")
```

### Métriques recommandées
- Temps réponse par endpoint
- Taux d'erreur par router
- Appels IA (coût)
- Webhooks CinetPay (succès/échec)

---

**Architecture modulaire, scalable et maintenable ✨**
