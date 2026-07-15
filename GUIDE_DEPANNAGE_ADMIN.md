# 🔧 GUIDE DE DÉPANNAGE ADMIN - ERREUR COLONNES

## 🚨 ERREUR ACTUELLE

```
column utilisateurs.email does not exist
```

**Cause** : La table `utilisateurs` dans Supabase n'a pas les colonnes attendues par le backend.

---

## 🔍 ÉTAPE 1 : DIAGNOSTIQUER LA STRUCTURE

### Option A : Via l'API (recommandé)

```bash
# Avec le backend lancé, ouvre ton navigateur :
http://localhost:8000/api/admin/debug/structure-utilisateurs
```

Tu verras les colonnes réelles de ta table `utilisateurs`.

### Option B : Via Supabase

```bash
1. Ouvrir Supabase Dashboard
2. Aller dans "Table Editor"
3. Sélectionner la table "utilisateurs"
4. Noter les noms des colonnes affichées
```

### Option C : Via SQL

```sql
-- Dans Supabase SQL Editor
SELECT column_name, data_type
FROM information_schema.columns 
WHERE table_name = 'utilisateurs'
ORDER BY ordinal_position;
```

---

## 🛠️ ÉTAPE 2 : IDENTIFIER LE PROBLÈME

### Cas 1 : Colonnes avec noms différents

**Exemple** : Tu as `mail` au lieu de `email`, ou `solde` au lieu de `solde_libre`

**Solutions** :

#### Solution A : Renommer les colonnes (recommandé)

```sql
-- Dans Supabase SQL Editor
ALTER TABLE utilisateurs RENAME COLUMN mail TO email;
ALTER TABLE utilisateurs RENAME COLUMN solde TO solde_libre;
```

#### Solution B : Ajouter les colonnes manquantes

Copie tout le contenu de `SQL_FIX_STRUCTURE_UTILISATEURS.sql` et exécute-le dans Supabase SQL Editor.

### Cas 2 : Colonnes manquantes

**Exécuter** : `SQL_FIX_STRUCTURE_UTILISATEURS.sql` dans Supabase

Cela ajoutera :
- `email` (TEXT)
- `nom` (TEXT)
- `prenom` (TEXT)
- `solde_libre` (NUMERIC)

### Cas 3 : Table utilisateurs vide

**Solution** : Insérer un utilisateur de test

```sql
INSERT INTO utilisateurs (
    id, 
    email, 
    nom, 
    prenom, 
    solde_libre
)
VALUES (
    gen_random_uuid(),
    'test@fincoach.cm',
    'Mbarga',
    'Franck',
    50000
);
```

---

## 🔄 ÉTAPE 3 : REDÉMARRER LE BACKEND

```bash
# Arrêter le backend (Ctrl+C)
# Relancer :
uvicorn main:app --reload
```

---

## ✅ ÉTAPE 4 : TESTER

```bash
# Ouvrir navigateur :
http://localhost:5173/admin/login

# Login :
Email: admin@fincoach.cm
Password: admin123

# Vérifier que les données s'affichent
```

---

## 🎯 SOLUTIONS RAPIDES PAR SCÉNARIO

### Scénario 1 : "J'ai 'mail' au lieu de 'email'"

```sql
-- Renommer la colonne
ALTER TABLE utilisateurs RENAME COLUMN mail TO email;
```

Puis redémarrer le backend.

### Scénario 2 : "J'ai des colonnes complètement différentes"

**Option A** : Adapter le backend aux colonnes existantes

Dans `routers/admin.py`, la fonction a déjà été corrigée pour utiliser `select("*")` qui récupère toutes les colonnes disponibles.

**Option B** : Créer les colonnes attendues

Exécuter `SQL_FIX_STRUCTURE_UTILISATEURS.sql`

### Scénario 3 : "Je ne sais pas quelle structure j'ai"

1. Ouvrir : `http://localhost:8000/api/admin/debug/structure-utilisateurs`
2. Noter les colonnes affichées
3. Copier-coller le résultat ici pour analyse

---

## 📋 STRUCTURE ATTENDUE PAR LE BACKEND

```sql
CREATE TABLE utilisateurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT,                      -- ← ESSENTIEL
    nom TEXT,                        -- ← ESSENTIEL
    prenom TEXT,                     -- ← ESSENTIEL
    solde_libre NUMERIC DEFAULT 0,  -- ← ESSENTIEL
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔍 VÉRIFICATIONS POST-CORRECTION

### 1. Structure table
```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'utilisateurs';
```

Doit retourner au moins :
- `id`
- `email`
- `nom`
- `prenom`
- `solde_libre`

### 2. Données test
```sql
SELECT * FROM utilisateurs LIMIT 1;
```

Doit retourner au moins 1 ligne.

### 3. API backend
```bash
curl http://localhost:8000/api/admin/utilisateurs
```

Doit retourner JSON sans erreur.

### 4. Frontend admin
```
http://localhost:5173/admin
```

Doit afficher les utilisateurs dans la vue "Utilisateurs".

---

## 🐛 PROBLÈMES FRÉQUENTS

### Erreur : "column does not exist"

**Cause** : Colonne manquante ou mal nommée  
**Solution** : Exécuter `SQL_FIX_STRUCTURE_UTILISATEURS.sql`

### Erreur : "table utilisateurs does not exist"

**Cause** : Table pas encore créée  
**Solution** : Créer la table :

```sql
CREATE TABLE utilisateurs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    nom TEXT,
    prenom TEXT,
    solde_libre NUMERIC DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Erreur : "relation utilisateurs is a view"

**Cause** : Tu as créé une vue au lieu d'une table  
**Solution** : Supprimer la vue et créer la table :

```sql
DROP VIEW IF EXISTS utilisateurs;
CREATE TABLE utilisateurs (...);
```

### Tous les chiffres à 0

**Cause** : Tables vides  
**Solution** : Insérer des données de test (voir ci-dessus)

---

## 📞 CHECKLIST DE DÉPANNAGE

- [ ] Backend lancé (`uvicorn main:app --reload`)
- [ ] Supabase accessible
- [ ] Route debug testée : `/api/admin/debug/structure-utilisateurs`
- [ ] Structure table vérifiée
- [ ] Colonnes manquantes ajoutées
- [ ] SQL de correction exécuté
- [ ] Backend redémarré
- [ ] Frontend rafraîchi (F5)
- [ ] Login admin testé
- [ ] Vue utilisateurs affichée

---

## 🚀 SCRIPT DE DÉMARRAGE RAPIDE

```bash
# 1. Vérifier structure
curl http://localhost:8000/api/admin/debug/structure-utilisateurs

# 2. Si erreur, exécuter SQL dans Supabase
# Copier SQL_FIX_STRUCTURE_UTILISATEURS.sql

# 3. Redémarrer backend
# Ctrl+C puis :
uvicorn main:app --reload

# 4. Tester
curl http://localhost:8000/api/admin/utilisateurs

# 5. Frontend
# Ouvrir : http://localhost:5173/admin
```

---

## 📊 EXEMPLE DE RÉPONSE CORRECTE

### `/api/admin/debug/structure-utilisateurs`

```json
{
  "message": "Structure de la table utilisateurs",
  "colonnes": [
    "id",
    "email",
    "nom",
    "prenom",
    "solde_libre",
    "created_at"
  ],
  "exemple": {
    "id": "12345678-...",
    "email": "test@fincoach.cm",
    "nom": "Mbarga",
    "prenom": "Franck",
    "solde_libre": 50000,
    "created_at": "2026-07-03T..."
  }
}
```

### `/api/admin/utilisateurs`

```json
{
  "total": 1,
  "utilisateurs": [
    {
      "id": "12345678-...",
      "email": "test@fincoach.cm",
      "nom": "Mbarga",
      "prenom": "Franck",
      "solde_libre": 50000,
      "nb_objectifs": 2,
      "montant_epargne": 150000
    }
  ]
}
```

---

**Guide de dépannage FinCoach Admin 2026** 🔧
