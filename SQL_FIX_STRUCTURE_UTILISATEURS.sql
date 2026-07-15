-- ============================================
-- SQL_FIX_STRUCTURE_UTILISATEURS.sql
-- Correction structure table utilisateurs
-- ============================================

-- ── ÉTAPE 1 : VÉRIFIER LA STRUCTURE ACTUELLE ──
-- Exécute cette requête pour voir les colonnes existantes
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'utilisateurs'
ORDER BY ordinal_position;

-- ── ÉTAPE 2 : AJOUTER LES COLONNES MANQUANTES ──

-- Colonne email (si elle n'existe pas)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'utilisateurs' AND column_name = 'email'
    ) THEN
        ALTER TABLE utilisateurs ADD COLUMN email TEXT;
        RAISE NOTICE 'Colonne email ajoutée';
    ELSE
        RAISE NOTICE 'Colonne email existe déjà';
    END IF;
END $$;

-- Colonne nom (si elle n'existe pas)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'utilisateurs' AND column_name = 'nom'
    ) THEN
        ALTER TABLE utilisateurs ADD COLUMN nom TEXT;
        RAISE NOTICE 'Colonne nom ajoutée';
    ELSE
        RAISE NOTICE 'Colonne nom existe déjà';
    END IF;
END $$;

-- Colonne prenom (si elle n'existe pas)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'utilisateurs' AND column_name = 'prenom'
    ) THEN
        ALTER TABLE utilisateurs ADD COLUMN prenom TEXT;
        RAISE NOTICE 'Colonne prenom ajoutée';
    ELSE
        RAISE NOTICE 'Colonne prenom existe déjà';
    END IF;
END $$;

-- Colonne solde_libre (si elle n'existe pas)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'utilisateurs' AND column_name = 'solde_libre'
    ) THEN
        ALTER TABLE utilisateurs ADD COLUMN solde_libre NUMERIC DEFAULT 0;
        RAISE NOTICE 'Colonne solde_libre ajoutée';
    ELSE
        RAISE NOTICE 'Colonne solde_libre existe déjà';
    END IF;
END $$;

-- ── ÉTAPE 3 : MIGRER LES DONNÉES SI BESOIN ──

-- Si tu as une colonne 'mail' au lieu de 'email'
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'utilisateurs' AND column_name = 'mail'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'utilisateurs' AND column_name = 'email'
    ) THEN
        UPDATE utilisateurs SET email = mail WHERE email IS NULL;
        RAISE NOTICE 'Données migrées de mail vers email';
    END IF;
END $$;

-- Si tu as une colonne 'solde' au lieu de 'solde_libre'
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'utilisateurs' AND column_name = 'solde'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'utilisateurs' AND column_name = 'solde_libre'
    ) THEN
        UPDATE utilisateurs SET solde_libre = solde WHERE solde_libre IS NULL OR solde_libre = 0;
        RAISE NOTICE 'Données migrées de solde vers solde_libre';
    END IF;
END $$;

-- ── ÉTAPE 4 : VÉRIFICATION FINALE ──
-- Vérifier que tout est OK
SELECT 
    column_name,
    data_type,
    CASE 
        WHEN column_name IN ('email', 'nom', 'prenom', 'solde_libre') THEN '✅ OK'
        ELSE '⚠️ Colonne supplémentaire'
    END as statut
FROM information_schema.columns 
WHERE table_name = 'utilisateurs'
ORDER BY ordinal_position;

-- ── ÉTAPE 5 : DONNÉES DE TEST (Optionnel) ──

-- Insérer un utilisateur de test complet
/*
INSERT INTO utilisateurs (
    id, 
    email, 
    nom, 
    prenom, 
    solde_libre,
    created_at
)
VALUES (
    gen_random_uuid(),
    'test@fincoach.cm',
    'Mbarga',
    'Franck',
    50000,
    NOW()
)
ON CONFLICT DO NOTHING;
*/

-- ── ALTERNATIVE : SI LA TABLE EXISTE DÉJÀ AVEC D'AUTRES NOMS ──

-- Option A : Renommer les colonnes existantes
-- ALTER TABLE utilisateurs RENAME COLUMN mail TO email;
-- ALTER TABLE utilisateurs RENAME COLUMN solde TO solde_libre;

-- Option B : Créer des vues avec alias
/*
CREATE OR REPLACE VIEW v_utilisateurs AS
SELECT 
    id,
    mail as email,  -- Si tu as 'mail' au lieu de 'email'
    nom,
    prenom,
    solde as solde_libre,  -- Si tu as 'solde' au lieu de 'solde_libre'
    created_at
FROM utilisateurs;
*/

-- ============================================
-- FIN DU SCRIPT
-- ============================================

-- INSTRUCTIONS :
-- 1. Exécuter d'abord l'ÉTAPE 1 pour voir la structure actuelle
-- 2. Noter les colonnes qui existent (ex: mail, solde, etc.)
-- 3. Exécuter les ÉTAPES 2-3 pour ajouter/migrer
-- 4. Vérifier avec ÉTAPE 4
-- 5. Redémarrer le backend
