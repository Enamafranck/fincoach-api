# 🚀 Guide de Démarrage Rapide - FinCoach API

## ✅ Vérification Installation

```bash
# 1. Activer l'environnement virtuel
.\venv\Scripts\activate

# 2. Tester l'architecture
python test_import.py
```

**Résultat attendu :**
```
🤖 Coach IA initialisé avec GROQ (Llama-3)
✅ Application FastAPI chargée avec succès
📋 Routers disponibles:
  [POST] /api/coach/chat
  [POST] /api/cotisations/traiter/{user_id}
  ...
✨ Tous les tests d'import réussis !
```

## 🎯 Démarrer le Serveur

```bash
# Démarrage avec rechargement automatique
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Ou (plus simple) :**
```bash
python -m uvicorn main:app --reload
```

**Serveur actif sur :**
- API : http://localhost:8000
- Docs interactives : http://localhost:8000/docs
- Documentation ReDoc : http://localhost:8000/redoc

## 📖 Tester une Route

### Avec cURL
```bash
# Test route racine
curl http://localhost:8000/

# Test coach IA
curl -X POST http://localhost:8000/api/coach/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "messages": [
      {"role": "user", "content": "Salut coach, comment ça va ?"}
    ]
  }'
```

### Avec Swagger UI
1. Ouvrir http://localhost:8000/docs
2. Cliquer sur une route (ex: `/api/coach/chat`)
3. Cliquer "Try it out"
4. Remplir les paramètres
5. Cliquer "Execute"

## 🔧 Variables d'Environnement

Vérifier votre fichier `.env` :

```env
# IA Provider (au moins un requis)
GROQ_API_KEY=gsk_xxx...
ANTHROPIC_API_KEY=sk-ant-xxx...
GEMINI_API_KEY=xxx...

# Supabase (requis)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...

# CinetPay (optionnel, mode test si absent)
CINETPAY_API_KEY=pvk_xxx...
CINETPAY_SITE_ID=xxx...

# URLs
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

## 📂 Navigation Rapide

| Je veux modifier... | Fichier à éditer |
|---------------------|------------------|
| Le chat IA | `routers/coach.py` |
| Les cotisations auto | `routers/cotisations.py` |
| Les retraits | `routers/retraits.py` |
| Les paiements CinetPay | `routers/paiements.py` |
| Les stats/historique | `routers/transactions.py` |
| La config globale | `config.py` |
| Les routes CORS | `main.py` |

## 🐛 Dépannage

### Erreur : Module not found
```bash
pip install -r requirements.txt
```

### Erreur : Port déjà utilisé
```bash
# Changer le port
uvicorn main:app --reload --port 8001
```

### Erreur : Supabase connection
- Vérifier `SUPABASE_URL` et `SUPABASE_SERVICE_KEY` dans `.env`
- Tester la connexion : https://xxx.supabase.co/rest/v1/

### Erreur : IA Provider non configuré
- Au moins une clé API IA doit être présente dans `.env`
- Priorité : GROQ > GEMINI > ANTHROPIC

## 📝 Logs Utiles

```python
# Dans n'importe quel router
print(f"✅ Action réussie : {variable}")
print(f"⚠️ Attention : {warning}")
print(f"❌ Erreur : {error}")
```

## 🎯 Routes Principales

### Coach IA
```bash
POST /api/coach/chat
Body: {
  "user_id": "uuid",
  "messages": [{"role": "user", "content": "..."}]
}
```

### Traiter Cotisations
```bash
POST /api/cotisations/traiter/{user_id}
```

### Effectuer Retrait
```bash
POST /api/retraits/effectuer
Body: {
  "user_id": "uuid",
  "objectif_id": "uuid",
  "montant_demande": 5000
}
```

### Initier Paiement
```bash
POST /api/paiements/initier
Body: {
  "user_id": "uuid",
  "montant": 10000,
  "sens": "depot",
  "methode": "mobile_money"
}
```

### Statistiques
```bash
GET /api/transactions/stats/{utilisateur_id}
```

## 🔥 Commandes Utiles

```bash
# Voir les routes disponibles
python test_import.py

# Lancer tests (si configurés)
pytest

# Formater le code
black .

# Vérifier les imports
pylint routers/

# Production (avec Gunicorn + Uvicorn workers)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📚 Documentation Complète

- **Architecture** : Voir `README.md`
- **Migration** : Voir `MIGRATION.md`
- **API Docs** : http://localhost:8000/docs (après démarrage)

---

**Prêt à coder ! 🚀**
