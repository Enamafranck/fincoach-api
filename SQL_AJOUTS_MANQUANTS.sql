-- ============================================
-- SQL_AJOUTS_MANQUANTS.sql
-- Script pour compléter la base de données FinCoach
-- ============================================

-- ── TABLE CAISSE ADMIN ──
-- Stocke les pénalités et autres revenus de la plateforme

CREATE TABLE IF NOT EXISTS caisse_admin (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,                    -- ex: "penalite_retrait", "frais_service"
    montant NUMERIC NOT NULL DEFAULT 0,
    utilisateur_id UUID REFERENCES utilisateurs(id) ON DELETE SET NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_caisse_admin_date ON caisse_admin(date DESC);
CREATE INDEX IF NOT EXISTS idx_caisse_admin_source ON caisse_admin(source);


-- ── TABLE TRANSACTIONS ──
-- Historique des transactions manuelles (dépenses de poche, dépôts manuels, etc.)

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    montant NUMERIC NOT NULL,
    type TEXT NOT NULL,                      -- "depot", "depense"
    categorie TEXT,                          -- ex: "Transport", "Nourriture", "Clôture Objectif"
    texte_brut TEXT,                         -- Description libre
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date DESC);
CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);


-- ── VÉRIFICATIONS & CONTRAINTES ──

-- S'assurer que les montants sont toujours positifs
ALTER TABLE caisse_admin 
ADD CONSTRAINT check_caisse_montant_positif 
CHECK (montant >= 0);

ALTER TABLE transactions 
ADD CONSTRAINT check_transaction_montant_positif 
CHECK (montant >= 0);

-- S'assurer que les types de transactions sont valides
ALTER TABLE transactions 
ADD CONSTRAINT check_transaction_type_valide 
CHECK (type IN ('depot', 'depense', 'transfert'));


-- ── COLONNES MANQUANTES DANS UTILISATEURS ──

-- Ajouter la colonne solde_libre si elle n'existe pas
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'utilisateurs' 
        AND column_name = 'solde_libre'
    ) THEN
        ALTER TABLE utilisateurs ADD COLUMN solde_libre NUMERIC DEFAULT 0;
    END IF;
END $$;

-- Ajouter les colonnes nom et prenom si elles n'existent pas
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'utilisateurs' 
        AND column_name = 'nom'
    ) THEN
        ALTER TABLE utilisateurs ADD COLUMN nom TEXT;
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'utilisateurs' 
        AND column_name = 'prenom'
    ) THEN
        ALTER TABLE utilisateurs ADD COLUMN prenom TEXT;
    END IF;
END $$;


-- ── COLONNES MANQUANTES DANS OBJECTIFS ──

-- S'assurer que toutes les colonnes nécessaires existent
DO $$
BEGIN
    -- montant_periodique
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'objectifs' 
        AND column_name = 'montant_periodique'
    ) THEN
        ALTER TABLE objectifs ADD COLUMN montant_periodique NUMERIC DEFAULT 0;
    END IF;
    
    -- prochaine_echeance
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'objectifs' 
        AND column_name = 'prochaine_echeance'
    ) THEN
        ALTER TABLE objectifs ADD COLUMN prochaine_echeance DATE;
    END IF;
    
    -- couleur_statut
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'objectifs' 
        AND column_name = 'couleur_statut'
    ) THEN
        ALTER TABLE objectifs ADD COLUMN couleur_statut TEXT DEFAULT 'vert';
    END IF;
END $$;


-- ── COLONNES MANQUANTES DANS RETRAITS ──

DO $$
BEGIN
    -- anticipe
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'retraits' 
        AND column_name = 'anticipe'
    ) THEN
        ALTER TABLE retraits ADD COLUMN anticipe BOOLEAN DEFAULT FALSE;
    END IF;
    
    -- penalite
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'retraits' 
        AND column_name = 'penalite'
    ) THEN
        ALTER TABLE retraits ADD COLUMN penalite NUMERIC DEFAULT 0;
    END IF;
END $$;


-- ── COLONNES MANQUANTES DANS COTISATIONS ──

DO $$
BEGIN
    -- type (automatique, mise_de_cote)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'cotisations' 
        AND column_name = 'type'
    ) THEN
        ALTER TABLE cotisations ADD COLUMN type TEXT DEFAULT 'automatique';
    END IF;
    
    -- montant_prevu
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'cotisations' 
        AND column_name = 'montant_prevu'
    ) THEN
        ALTER TABLE cotisations ADD COLUMN montant_prevu NUMERIC;
    END IF;
END $$;


-- ── INDEX POUR PERFORMANCE ──

-- Objectifs : recherches fréquentes par statut et échéance
CREATE INDEX IF NOT EXISTS idx_objectifs_statut ON objectifs(statut);
CREATE INDEX IF NOT EXISTS idx_objectifs_echeance ON objectifs(prochaine_echeance);
CREATE INDEX IF NOT EXISTS idx_objectifs_user ON objectifs(utilisateur_id);

-- Cotisations : recherches par utilisateur et statut
CREATE INDEX IF NOT EXISTS idx_cotisations_user ON cotisations(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_cotisations_statut ON cotisations(statut);
CREATE INDEX IF NOT EXISTS idx_cotisations_objectif ON cotisations(objectif_id);

-- Retraits : recherches par utilisateur
CREATE INDEX IF NOT EXISTS idx_retraits_user ON retraits(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_retraits_objectif ON retraits(objectif_id);


-- ── DONNÉES DE TEST (Optionnel) ──

-- Insérer un utilisateur de test si la table est vide
-- INSERT INTO utilisateurs (id, email, nom, prenom, solde_libre)
-- SELECT 
--     gen_random_uuid(),
--     'test@fincoach.cm',
--     'Utilisateur',
--     'Test',
--     50000
-- WHERE NOT EXISTS (SELECT 1 FROM utilisateurs LIMIT 1);


-- ============================================
-- FIN DU SCRIPT
-- ============================================

-- Pour exécuter ce script dans Supabase :
-- 1. Aller dans le SQL Editor
-- 2. Coller ce script
-- 3. Cliquer sur "Run"
-- 4. Vérifier qu'il n'y a pas d'erreurs

-- NOTES :
-- - Les blocs DO $$ sont utilisés pour éviter les erreurs si les colonnes existent déjà
-- - Les contraintes CHECK garantissent l'intégrité des données
-- - Les index améliorent les performances des requêtes fréquentes
