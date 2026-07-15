-- ============================================
-- SQL_ABONNEMENTS.sql
-- Création de la table abonnements pour FinCoach
-- ============================================

-- ── TABLE ABONNEMENTS ──
CREATE TABLE IF NOT EXISTS abonnements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID NOT NULL REFERENCES utilisateurs(id) ON DELETE CASCADE,
    type_abonnement TEXT NOT NULL,           -- ex: "basic", "premium", "entreprise"
    date_debut DATE NOT NULL DEFAULT CURRENT_DATE,
    date_fin DATE NOT NULL,
    statut TEXT NOT NULL DEFAULT 'actif',    -- "actif", "expire", "suspendu", "remplace"
    montant NUMERIC,                         -- Montant payé (optionnel)
    reference_paiement TEXT,                 -- Référence du paiement associé (optionnel)
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ── INDEX POUR PERFORMANCE ──
CREATE INDEX IF NOT EXISTS idx_abonnements_utilisateur ON abonnements(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_abonnements_statut ON abonnements(statut);
CREATE INDEX IF NOT EXISTS idx_abonnements_date_fin ON abonnements(date_fin);
CREATE INDEX IF NOT EXISTS idx_abonnements_type ON abonnements(type_abonnement);

-- Index composite pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_abonnements_user_statut ON abonnements(utilisateur_id, statut);
CREATE INDEX IF NOT EXISTS idx_abonnements_statut_date ON abonnements(statut, date_fin);

-- ── CONTRAINTES ──
ALTER TABLE abonnements 
ADD CONSTRAINT check_abonnement_statut_valide 
CHECK (statut IN ('actif', 'expire', 'suspendu', 'remplace', 'annule'));

ALTER TABLE abonnements 
ADD CONSTRAINT check_abonnement_dates_coherentes 
CHECK (date_fin >= date_debut);

-- ── TRIGGER : MISE À JOUR AUTOMATIQUE updated_at ──
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_abonnements_updated_at
    BEFORE UPDATE ON abonnements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ── FONCTION : EXPIRER AUTOMATIQUEMENT LES ABONNEMENTS ──
CREATE OR REPLACE FUNCTION expirer_abonnements_automatiquement()
RETURNS INTEGER AS $$
DECLARE
    nb_expires INTEGER;
BEGIN
    UPDATE abonnements
    SET statut = 'expire'
    WHERE statut = 'actif'
    AND date_fin < CURRENT_DATE;
    
    GET DIAGNOSTICS nb_expires = ROW_COUNT;
    RETURN nb_expires;
END;
$$ LANGUAGE plpgsql;

-- ── DONNÉES DE TEST (Optionnel - à décommenter si besoin) ──

/*
-- Insérer un abonnement de test (expire dans 30 jours)
INSERT INTO abonnements (utilisateur_id, type_abonnement, date_debut, date_fin, statut)
SELECT 
    id,
    'premium',
    CURRENT_DATE,
    CURRENT_DATE + INTERVAL '30 days',
    'actif'
FROM utilisateurs
LIMIT 1
ON CONFLICT DO NOTHING;

-- Insérer un abonnement expiré (pour tester l'expiration)
INSERT INTO abonnements (utilisateur_id, type_abonnement, date_debut, date_fin, statut)
SELECT 
    id,
    'basic',
    CURRENT_DATE - INTERVAL '60 days',
    CURRENT_DATE - INTERVAL '1 day',
    'actif'
FROM utilisateurs
LIMIT 1
ON CONFLICT DO NOTHING;
*/

-- ── REQUÊTES UTILES POUR ADMINISTRATION ──

-- Voir tous les abonnements actifs
-- SELECT * FROM abonnements WHERE statut = 'actif' ORDER BY date_fin;

-- Voir les abonnements qui expirent dans les 7 prochains jours
-- SELECT * FROM abonnements 
-- WHERE statut = 'actif' 
-- AND date_fin BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days';

-- Expirer manuellement les abonnements échus
-- SELECT expirer_abonnements_automatiquement();

-- Statistiques des abonnements par type
-- SELECT type_abonnement, statut, COUNT(*) as nombre
-- FROM abonnements
-- GROUP BY type_abonnement, statut;

-- ============================================
-- FIN DU SCRIPT
-- ============================================

-- NOTES :
-- 1. Cette table stocke les abonnements des utilisateurs
-- 2. Le scheduler Python exécute automatiquement l'expiration quotidienne
-- 3. La fonction SQL expirer_abonnements_automatiquement() peut aussi être appelée manuellement
-- 4. Les index optimisent les recherches fréquentes (par user, statut, date)
-- 5. Le trigger updated_at met à jour automatiquement la date de modification
