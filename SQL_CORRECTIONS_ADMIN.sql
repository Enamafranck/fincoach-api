-- ============================================
-- SQL_CORRECTIONS_ADMIN.sql
-- Corrections pour débloquer l'admin dashboard
-- ============================================

-- ── PROBLÈME 1 : CONTRAINTE STATUTS OBJECTIFS ──
-- Erreur : "violates check constraint 'objectifs_statut_check'"

-- Étape 1 : Supprimer l'ancienne contrainte restrictive
ALTER TABLE objectifs 
DROP CONSTRAINT IF EXISTS objectifs_statut_check;

-- Étape 2 : Ajouter une contrainte flexible (temporaire pour migration)
ALTER TABLE objectifs 
ADD CONSTRAINT objectifs_statut_check 
CHECK (statut IN ('actif', 'atteint', 'inactif', 'En cours', 'Terminé', 'suspendu', 'en_pause'));

-- Étape 3 : Normaliser les statuts existants
UPDATE objectifs SET statut = 'actif' WHERE statut = 'En cours';
UPDATE objectifs SET statut = 'atteint' WHERE statut = 'Terminé';
UPDATE objectifs SET statut = 'inactif' WHERE statut = 'en_pause';

-- Étape 4 : Restreindre à 3 statuts officiels (recommandé après normalisation)
ALTER TABLE objectifs 
DROP CONSTRAINT IF EXISTS objectifs_statut_check;

ALTER TABLE objectifs 
ADD CONSTRAINT objectifs_statut_check 
CHECK (statut IN ('actif', 'atteint', 'inactif'));

-- Note : Si tu veux garder 'en_pause' comme statut distinct :
-- ALTER TABLE objectifs 
-- ADD CONSTRAINT objectifs_statut_check 
-- CHECK (statut IN ('actif', 'atteint', 'inactif', 'en_pause'));


-- ── PROBLÈME 2 : COLONNES MANQUANTES ──

-- S'assurer que tous les champs nécessaires existent dans utilisateurs
DO $$
BEGIN
    -- Colonne nom
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'utilisateurs' AND column_name = 'nom'
    ) THEN
        ALTER TABLE utilisateurs ADD COLUMN nom TEXT;
    END IF;
    
    -- Colonne prenom
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'utilisateurs' AND column_name = 'prenom'
    ) THEN
        ALTER TABLE utilisateurs ADD COLUMN prenom TEXT;
    END IF;
    
    -- Colonne solde_libre
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'utilisateurs' AND column_name = 'solde_libre'
    ) THEN
        ALTER TABLE utilisateurs ADD COLUMN solde_libre NUMERIC DEFAULT 0;
    END IF;
END $$;


-- ── PROBLÈME 3 : INDEX MANQUANTS (Performance) ──

-- Index pour accélérer les requêtes admin
CREATE INDEX IF NOT EXISTS idx_objectifs_utilisateur_statut ON objectifs(utilisateur_id, statut);
CREATE INDEX IF NOT EXISTS idx_cotisations_utilisateur_statut ON cotisations(utilisateur_id, statut);
CREATE INDEX IF NOT EXISTS idx_retraits_utilisateur ON retraits(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_caisse_admin_date ON caisse_admin(date DESC);


-- ── DONNÉES DE TEST (Optionnel - à décommenter si besoin) ──

/*
-- Insérer un utilisateur de test si la table est vide
INSERT INTO utilisateurs (id, email, nom, prenom, solde_libre)
SELECT 
    gen_random_uuid(),
    'test@fincoach.cm',
    'Mbarga',
    'Franck',
    50000
WHERE NOT EXISTS (SELECT 1 FROM utilisateurs WHERE email = 'test@fincoach.cm');

-- Récupérer l'ID de cet utilisateur pour créer un objectif
DO $$
DECLARE
    test_user_id UUID;
BEGIN
    SELECT id INTO test_user_id FROM utilisateurs WHERE email = 'test@fincoach.cm' LIMIT 1;
    
    IF test_user_id IS NOT NULL THEN
        -- Insérer un objectif de test
        INSERT INTO objectifs (utilisateur_id, nom, montant_cible, montant_actuel, statut, frequence, montant_periodique, prochaine_echeance)
        VALUES (
            test_user_id,
            'Épargne moto',
            500000,
            150000,
            'actif',
            'mois',
            25000,
            CURRENT_DATE + INTERVAL '1 month'
        )
        ON CONFLICT DO NOTHING;
        
        -- Insérer une cotisation de test
        INSERT INTO cotisations (utilisateur_id, montant, statut, type)
        VALUES (test_user_id, 25000, 'effectuee', 'mise_de_cote')
        ON CONFLICT DO NOTHING;
        
        -- Insérer un retrait de test
        INSERT INTO retraits (utilisateur_id, montant, date, anticipe, penalite)
        VALUES (test_user_id, 10000, CURRENT_DATE, false, 0)
        ON CONFLICT DO NOTHING;
        
        -- Insérer une entrée caisse_admin de test
        INSERT INTO caisse_admin (source, montant, utilisateur_id, date)
        VALUES ('penalite_retrait', 500, test_user_id, CURRENT_DATE)
        ON CONFLICT DO NOTHING;
    END IF;
END $$;
*/


-- ── VÉRIFICATIONS POST-CORRECTION ──

-- Vérifier que les contraintes sont correctes
SELECT 
    conname AS nom_contrainte,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint 
WHERE conname = 'objectifs_statut_check';

-- Vérifier la distribution des statuts
SELECT statut, COUNT(*) as nombre
FROM objectifs
GROUP BY statut;

-- Vérifier les colonnes de utilisateurs
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'utilisateurs' 
AND column_name IN ('nom', 'prenom', 'solde_libre');


-- ============================================
-- FIN DU SCRIPT
-- ============================================

-- INSTRUCTIONS D'EXÉCUTION :
-- 1. Ouvrir Supabase SQL Editor
-- 2. Coller ce script complet
-- 3. Cliquer sur "Run"
-- 4. Vérifier qu'il n'y a pas d'erreurs
-- 5. Redémarrer le backend : uvicorn main:app --reload
-- 6. Tester l'admin dashboard
