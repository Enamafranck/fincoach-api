# 🔍 RAPPORT D'AUDIT FINCOACH - État des Lieux Backend

**Date** : 26 juin 2026  
**Analysé par** : Kiro AI  
**Périmètre** : Backend API (FastAPI + Supabase)

---

## 1. 🔍 CE QUI EST DÉJÀ OPÉRATIONNEL (Fait ✅)

### ✅ Architecture Backend Solide

**Routes Actives et Fonctionnelles :**

| Domaine | Route | Statut | Détails |
|---------|-------|--------|---------|
| **Objectifs CRUD** | `PATCH /api/objectifs/{id}/desactiver` | ✅ | Change statut → `inactif` + couleur `gris` |
| **Objectifs CRUD** | `PATCH /api/objectifs/{id}/reactiver` | ✅ | Change statut → `actif` + couleur `vert` |
| **Objectifs CRUD** | `DELETE /api/objectifs/{id}` | ✅ | Supprime + reverse l'argent au solde |
| **Cotisations** | `POST /api/cotisations/traiter/{user_id}` | ✅ | Traite échéances dues |
| **Cotisations** | `POST /api/cotisations/verifier-toutes` | ✅ | CRON pour tous les users |
| **Retraits** | `POST /api/retraits/effectuer` | ✅ | Retrait avec pénalité conditionnelle |
| **Transferts** | `POST /api/objectifs/transferer-solde` | ✅ | Transfert objectif → solde |
| **Stats** | `GET /api/transactions/stats/{user_id}` | ✅ | Calcul indicateurs |
| **Historique** | `GET /api/transactions/historique/{user_id}` | ✅ | Agrège cotisations + retraits + transactions |

### ✅ Gestion des Statuts d'Objectifs

**Backend implémente correctement les 3 statuts :**

| Statut | Condition | Couleur | Backend |
|--------|-----------|---------|---------|
| **actif** | Montant actuel < cible | 🟠 orange | ✅ Géré |
| **en_pause** | Désactivé manuellement | 🔵 (inactif/gris) | ✅ Géré |
| **atteint** | Montant actuel ≥ cible | 🟢 vert | ✅ Géré |

**⚠️ Point d'attention Frontend :**
- Le backend utilise le statut `"inactif"` pour les objectifs mis en pause
- Assure-toi que le frontend map bien `inactif` → `en_pause` dans l'UI

### ✅ Logique Métier Cotisations Automatiques

**Fichier :** `routers/cotisations.py`

**Fonctionnalités opérationnelles :**
1. ✅ Récupère uniquement les objectifs avec `statut = "actif"`
2. ✅ Filtre par `prochaine_echeance <= aujourd'hui`
3. ✅ Vérifie le solde avant prélèvement
4. ✅ Trie par montant croissant (épargne les petits objectifs d'abord)
5. ✅ Débite le solde principal
6. ✅ Crédite l'objectif
7. ✅ Calcule la prochaine échéance (jour/semaine/mois)
8. ✅ **Si objectif atteint → reverse automatiquement au solde principal**
9. ✅ Passe l'objectif en `couleur_statut = "rouge"` si solde insuffisant
10. ✅ Enregistre la cotisation dans la table `cotisations`

**✅ CONFIRMATION : Les objectifs en pause (`inactif`) sont bien ignorés**

```python
objectifs = supabase.from_("objectifs")\
    .select("*")\
    .eq("utilisateur_id", user_id)\
    .eq("statut", "actif")\  # ← Seuls les objectifs actifs
    .lte("prochaine_echeance", aujourd_hui)\
    .execute().data or []
```

### ✅ Logique de Pénalité sur Retraits Anticipés

**Fichier :** `routers/retraits.py`

**Règles implémentées côté backend :**

```python
# ✅ Objectif atteint → GRATUIT (0% de frais)
if statut_objectif == "atteint":
    penalite = 0
    type_retrait = "normal"

# ✅ Objectif non atteint → Pénalité de 5%
else:
    penalite = int(req.montant_demande * 5 / 100)
    type_retrait = "anticipe"
```

**Détails techniques :**
- Calcul backend uniquement
- Pénalité va dans `caisse_admin` (si table existe)
- Montant net = montant demandé - pénalité
- L'objectif repasse à `statut = "actif"` après retrait partiel

---

## 2. ⚠️ L'ALIGNEMENT AVEC LA BASE DE DONNÉES (À Vérifier)

### ⚠️ PAS de Table `profils` Dédiée

**Constat :**
- ❌ Aucune référence à une table `profils` dans le code backend
- ✅ Tout repose sur la table `utilisateurs`

**Champs utilisés dans `utilisateurs` :**

| Champ | Utilisation | Fichiers concernés |
|-------|-------------|-------------------|
| `id` | Identifiant user | Tous les routers |
| `solde_libre` | Solde principal | cotisations.py, retraits.py, transactions.py |

**Structure supposée de la table `utilisateurs` (à confirmer dans Supabase) :**

```sql
CREATE TABLE utilisateurs (
    id UUID PRIMARY KEY,
    email TEXT,
    nom TEXT,
    solde_libre NUMERIC DEFAULT 0,  -- ← Clé pour l'épargne
    created_at TIMESTAMP,
    ...
);
```

### ⚠️ Points à Vérifier dans Supabase

**Checklist Base de Données :**

1. [ ] **Table `utilisateurs` existe ?**
   ```sql
   SELECT * FROM utilisateurs LIMIT 1;
   ```

2. [ ] **Colonne `solde_libre` existe et est de type NUMERIC ?**
   ```sql
   SELECT column_name, data_type 
   FROM information_schema.columns 
   WHERE table_name = 'utilisateurs' 
   AND column_name = 'solde_libre';
   ```

3. [ ] **Table `objectifs` a bien les colonnes suivantes ?**
   - `utilisateur_id` (FK vers utilisateurs.id)
   - `montant_actuel` (NUMERIC)
   - `montant_cible` (NUMERIC)
   - `statut` (TEXT : actif, atteint, inactif)
   - `couleur_statut` (TEXT : vert, orange, rouge, gris)
   - `prochaine_echeance` (DATE)
   - `frequence` (TEXT : jour, semaine, mois)
   - `montant_periodique` (NUMERIC)

4. [ ] **Table `cotisations` enregistre bien les transactions ?**
   - `utilisateur_id`
   - `objectif_id`
   - `montant`
   - `type` (TEXT : automatique, mise_de_cote)
   - `statut` (TEXT : effectuee, en_attente)
   - `created_at`

5. [ ] **Table `retraits` enregistre bien les retraits ?**
   - `utilisateur_id`
   - `objectif_id`
   - `montant`
   - `date`
   - `anticipe` (BOOLEAN)
   - `penalite` (NUMERIC)

6. [ ] **Table `caisse_admin` existe ? (optionnelle)**
   - `source` (TEXT : penalite_retrait)
   - `montant` (NUMERIC)
   - `utilisateur_id`
   - `date`

**🔴 ALERTE SI PROBLÈME :**
Si la colonne `solde_libre` n'existe pas, le backend va crasher sur TOUTES les routes de cotisations/retraits.

**Solution rapide :**
```sql
ALTER TABLE utilisateurs ADD COLUMN solde_libre NUMERIC DEFAULT 0;
```

---

## 3. 🛠️ CE QU'IL RESTE À CODER (À Faire)

### 🟠 Frontend : ModalRetrait.jsx

**Fichier introuvable dans ce dépôt (backend only)**

**Ce qui DOIT être fait côté frontend :**

```jsx
// ModalRetrait.jsx - À implémenter

const handleRetrait = async (montantDemande) => {
    // ✅ Le calcul de la pénalité se fait BACKEND
    // ❌ NE PAS calculer la pénalité côté frontend
    
    const response = await fetch('http://localhost:8000/api/retraits/effectuer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: userId,
            objectif_id: objectifId,
            montant_demande: montantDemande
        })
    });
    
    const result = await response.json();
    
    // ✅ Le backend retourne déjà :
    // - type_retrait ("normal" ou "anticipe")
    // - penalite (0 ou 5% du montant)
    // - montant_net (montant après pénalité)
    
    // 📌 Afficher dans l'UI :
    if (result.type_retrait === "anticipe") {
        alert(`⚠️ Retrait anticipé : ${result.penalite} FCFA de frais`);
    }
    alert(`✅ ${result.montant_net} FCFA transférés vers votre solde`);
};
```

**Checklist ModalRetrait.jsx :**

- [ ] Appelle bien `/api/retraits/effectuer`
- [ ] N'essaie PAS de calculer la pénalité en JavaScript
- [ ] Affiche `result.penalite` dans l'UI
- [ ] Affiche `result.montant_net` (montant réellement reçu)
- [ ] Affiche `result.type_retrait` (normal vs anticipé)
- [ ] Gère les erreurs HTTP 400 (montant insuffisant)
- [ ] Met à jour le solde affiché après retrait

### 🟠 Frontend : VueCaisse.jsx

**Fichier introuvable dans ce dépôt (backend only)**

**Checklist à valider :**

- [ ] Appelle `/api/transactions/stats/{user_id}` pour afficher :
  - Entrées totales
  - Sorties totales
  - Solde disponible net
  - Efficacité épargne
- [ ] Appelle `/api/transactions/historique/{user_id}` pour afficher l'historique
- [ ] Affiche les 3 statuts d'objectifs :
  - 🟢 Atteint
  - 🟠 Actif
  - 🔵 En pause (map `"inactif"` du backend)
- [ ] Permet de désactiver un objectif (`PATCH /api/objectifs/{id}/desactiver`)
- [ ] Permet de réactiver un objectif (`PATCH /api/objectifs/{id}/reactiver`)
- [ ] Permet de supprimer un objectif (`DELETE /api/objectifs/{id}`)

### 🟠 Frontend : ObjectifForm.jsx

**Fichier introuvable dans ce dépôt (backend only)**

**Checklist à valider :**

- [ ] Envoie bien les données au bon endpoint (probablement `/api/objectifs` en POST)
- [ ] Inclut tous les champs requis :
  - `utilisateur_id`
  - `nom`
  - `montant_cible`
  - `montant_periodique`
  - `frequence` ("jour", "semaine", "mois")
  - `prochaine_echeance` (date ISO)
  - `statut` (par défaut "actif")
  - `montant_actuel` (par défaut 0)

**⚠️ ATTENTION : Pas de route POST /api/objectifs dans le backend actuel**

**🔴 À CRÉER : Route de création d'objectif**

```python
# À ajouter dans routers/transactions.py

from pydantic import BaseModel
from datetime import date

class ObjectifCreate(BaseModel):
    utilisateur_id: str
    nom: str
    montant_cible: int
    montant_periodique: int
    frequence: str  # "jour" | "semaine" | "mois"
    prochaine_echeance: str  # date ISO

@router.post("/objectifs")
def creer_objectif(obj: ObjectifCreate):
    try:
        result = supabase.from_("objectifs").insert({
            "utilisateur_id": obj.utilisateur_id,
            "nom": obj.nom,
            "montant_cible": obj.montant_cible,
            "montant_periodique": obj.montant_periodique,
            "montant_actuel": 0,
            "frequence": obj.frequence,
            "prochaine_echeance": obj.prochaine_echeance,
            "statut": "actif",
            "couleur_statut": "orange",
        }).execute()
        return {"message": "Objectif créé ✅", "objectif": result.data[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 🟠 Historique des Transactions

**Vérification dans `routers/transactions.py` :**

```python
@router.get("/transactions/historique/{utilisateur_id}")
```

**✅ Types de transactions enregistrées :**

| Type | Table source | Enregistré ? |
|------|-------------|--------------|
| **Cotisation automatique** | `cotisations` | ✅ Oui |
| **Mise de côté manuelle** | `cotisations` (type="mise_de_cote") | ✅ Oui |
| **Retrait** | `retraits` | ✅ Oui |
| **Retrait anticipé** | `retraits` (anticipe=true) | ✅ Oui |
| **Suppression objectif** | `retraits` ? | ⚠️ Pas explicite |
| **Dépôt via CinetPay** | `transactions` | ⚠️ À vérifier |

**🔴 MANQUE PEUT-ÊTRE :**

1. **Enregistrement dans `transactions` lors d'un dépôt CinetPay**
   - À vérifier dans `routers/paiements.py` (webhook)
   - Doit insérer dans `transactions` avec `type = "depot"`

2. **Enregistrement lors de la clôture d'objectif atteint**
   - Actuellement, le reversement automatique ne crée pas de transaction explicite
   - **À ajouter** : insérer dans `transactions` avec `type = "cloture"`

**Exemple de code manquant (à ajouter dans `cotisations.py`) :**

```python
# Après reversement d'un objectif atteint
if nouveau_statut == "atteint":
    solde_profil = supabase.from_("utilisateurs")...
    
    # ✅ Reverser au solde
    supabase.from_("utilisateurs").update({
        "solde_libre": solde_actuel + nouveau_montant_actuel
    }).eq("id", user_id).execute()
    
    # ✅ Remettre l'objectif à 0
    supabase.from_("objectifs").update({
        "montant_actuel": 0
    }).eq("id", obj["id"]).execute()
    
    # 🔴 MANQUE : Enregistrer dans transactions
    supabase.from_("transactions").insert({
        "utilisateur_id": user_id,
        "type": "cloture",
        "montant": nouveau_montant_actuel,
        "categorie": "objectif_atteint",
        "date": date.today().isoformat(),
    }).execute()
```

---

## 📋 RÉSUMÉ EXECUTIF

### ✅ POINTS FORTS

1. ✅ **Architecture backend solide** : routes claires, séparation des responsabilités
2. ✅ **Gestion des statuts objectifs complète** : actif, atteint, inactif
3. ✅ **Logique cotisations automatiques robuste** : filtre bien les objectifs en pause
4. ✅ **Calcul pénalités côté backend** : pas de calcul frontend à faire
5. ✅ **Reversement automatique** : objectifs atteints libèrent l'argent

### ⚠️ POINTS D'ATTENTION

1. ⚠️ **Pas de table `profils`** : tout repose sur `utilisateurs.solde_libre`
2. ⚠️ **Route POST /api/objectifs manquante** : création d'objectif à implémenter
3. ⚠️ **Fichiers frontend absents** : VueCaisse.jsx, ObjectifForm.jsx, ModalRetrait.jsx introuvables
4. ⚠️ **Historique incomplet** : transactions de clôture pas enregistrées

### 🔴 BLOQUANTS À RÉSOUDRE

| Priorité | Problème | Solution |
|----------|----------|----------|
| **🔴 P0** | Route POST /api/objectifs manquante | Créer la route dans `transactions.py` |
| **🔴 P0** | Vérifier que `utilisateurs.solde_libre` existe dans Supabase | Tester en BDD |
| **🟠 P1** | Transactions de clôture pas enregistrées | Ajouter insert dans `cotisations.py` |
| **🟠 P1** | Frontend absent du dépôt | Partager le dépôt frontend pour audit |

---

## 🚀 PROCHAINES ÉTAPES

### Sprint Final - Checklist

1. **Backend :**
   - [ ] Créer `POST /api/objectifs` (création d'objectif)
   - [ ] Enregistrer transactions de clôture dans `transactions`
   - [ ] Vérifier structure table `utilisateurs` dans Supabase
   - [ ] Tester toutes les routes avec Postman/curl

2. **Frontend :**
   - [ ] Partager le code de VueCaisse.jsx, ObjectifForm.jsx, ModalRetrait.jsx
   - [ ] Vérifier que ModalRetrait.jsx n'essaie pas de calculer la pénalité
   - [ ] Vérifier que ObjectifForm.jsx pointe vers la bonne route
   - [ ] Mapper statut `"inactif"` → `"en_pause"` dans l'UI

3. **Base de Données :**
   - [ ] Valider schéma Supabase
   - [ ] Ajouter index sur `prochaine_echeance` (performance)
   - [ ] Ajouter index sur `statut` (performance)

4. **Tests :**
   - [ ] Tester cycle complet : création objectif → cotisations → atteinte → reversement
   - [ ] Tester retrait anticipé avec pénalité
   - [ ] Tester retrait après atteinte (sans pénalité)
   - [ ] Tester désactivation/réactivation objectif

---

**Rapport généré le 26/06/2026**  
**Prêt pour review et ajustements 🚀**
