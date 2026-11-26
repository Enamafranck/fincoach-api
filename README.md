# FinCoach API

Backend d'une application de coaching financier pour le Cameroun et l'Afrique centrale : objectifs d'épargne, cotisations, retraits, paiements mobiles et coach financier basé sur l'IA.

Application associée : [fincoach-app](https://github.com/Enamafranck/fincoach-app)

## Stack
- **Python** et **FastAPI** (serveur Uvicorn), modèles de données avec Pydantic
- **Supabase** : base PostgreSQL et authentification
- **CinetPay** : paiements mobiles
- **IA** : Groq, Gemini ou Anthropic (détection automatique selon la clé fournie)

## Routes principales
| Domaine | Routes |
|---|---|
| Coach IA | `POST /api/coach/chat` |
| Cotisations | `POST /api/cotisations/traiter/{user_id}`, `POST /api/cotisations/verifier-toutes` |
| Retraits | `POST /api/retraits/effectuer`, `POST /api/objectifs/transferer-solde` |
| Paiements | `POST /api/paiements/initier`, `POST /api/paiements/webhook`, `GET /api/paiements/statut/{reference}` |
| Transactions et objectifs | `GET /api/transactions/stats/{utilisateur_id}`, `GET /api/transactions/historique/{utilisateur_id}`, `PATCH /api/objectifs/{objectif_id}/desactiver`, `PATCH /api/objectifs/{objectif_id}/reactiver`, `DELETE /api/objectifs/{objectif_id}` |

## Structure
```text
main.py            Point d'entrée FastAPI (CORS, routers)
config.py          Configuration centralisée (Supabase, IA, variables)
scheduler.py       Tâches planifiées
requirements.txt   Dépendances Python
routers/           Routes par domaine (coach, cotisations, retraits, paiements, transactions)
test_import.py     Vérification de l'architecture
```

## Installation
```bash
git clone https://github.com/Enamafranck/fincoach-api.git
cd fincoach-api
python -m venv venv
# Windows : .\venv\Scripts\activate
# Linux / macOS : source venv/bin/activate
pip install -r requirements.txt
```

Crée un fichier `.env` à la racine avec les clés Supabase, CinetPay et IA. Les noms exacts des variables sont dans `config.py`. Ne publie jamais ce fichier.

## Lancement
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
La documentation interactive de l'API est disponible sur `http://localhost:8000/docs`.

## Sécurité
- [x] Configuration par variables d'environnement
- [ ] Vérification de l'authenticité des appels au webhook de paiement
- [ ] Limitation du débit des requêtes
- [ ] Tests automatisés et analyse de sécurité du code (CodeQL)

## Ajouter un router
1. Créer `routers/mon_router.py` avec un `APIRouter`.
2. L'enregistrer dans `main.py` avec `app.include_router(...)`.

Développé pour FinCoach, Cameroun et Afrique centrale.
