-- seitenkraft.org Database Schema
-- Supabase PostgreSQL Schema für Domain-Verwaltung & Website-Generierung

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Table: saas_dienste (SaaS Services / Partner Portals)
-- ============================================================================
CREATE TABLE IF NOT EXISTS saas_dienste (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dienst_key VARCHAR(100) NOT NULL UNIQUE, -- z.B. "handelshelfer", "handwerker24"
    name VARCHAR(255) NOT NULL, -- Anzeigename
    aktiv BOOLEAN NOT NULL DEFAULT true,
    api_token VARCHAR(255), -- Token für API-Authentifizierung
    whitelabel_config JSONB, -- White-Label Konfiguration (Farben, Logo-URLs, etc.)
    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    aktualisiert_am TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index
CREATE INDEX IF NOT EXISTS idx_saas_dienste_key ON saas_dienste(dienst_key);
CREATE INDEX IF NOT EXISTS idx_saas_dienste_aktiv ON saas_dienste(aktiv);

-- ============================================================================
-- Table: kunden (Customers)
-- ============================================================================
CREATE TABLE IF NOT EXISTS kunden (
    id UUID PRIMARY KEY, -- WICHTIG: Übernommen von unternehmensdaten.org (KEINE auto-generation!)
    saas_dienst_id UUID NOT NULL REFERENCES saas_dienste(id) ON DELETE CASCADE, -- Welcher Dienst hat den Kunden registriert

    -- Cached data from unternehmensdaten.org
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    land VARCHAR(2) NOT NULL, -- ISO 3166-1 alpha-2 (DE, AT, CH, etc.)
    branche VARCHAR(100), -- Industry/sector (haendler, handwerker, dienstleister, etc.)

    -- Sync tracking
    unternehmensdaten_sync_am TIMESTAMPTZ, -- Letzter Sync mit unternehmensdaten.org

    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    aktualisiert_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Ein Kunde kann über mehrere SaaS-Dienste Domains registrieren
    UNIQUE(id, saas_dienst_id)
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_kunden_email ON kunden(email);
CREATE INDEX IF NOT EXISTS idx_kunden_land ON kunden(land);
CREATE INDEX IF NOT EXISTS idx_kunden_saas_dienst ON kunden(saas_dienst_id);

-- ============================================================================
-- Table: domains_tld (TLD Pricing & Metadata)
-- ============================================================================
CREATE TABLE IF NOT EXISTS domains_tld (
    tld VARCHAR(50) PRIMARY KEY, -- e.g., "de", "com", "berlin"
    vk_eur NUMERIC(10,2) NOT NULL, -- Verkaufspreis in EUR
    aktiv BOOLEAN NOT NULL DEFAULT true, -- Ist diese TLD aktiv?
    sortierung INTEGER DEFAULT 0, -- Sortierreihenfolge in UI
    tld_gruppe VARCHAR(50), -- Gruppierung (z.B. "cctld", "gtld", "new-gtld")
    gruppe VARCHAR(50), -- Weitere Gruppierung (z.B. "standard", "premium")
    prio INTEGER DEFAULT 0, -- Priorität für Vorschläge (höher = wichtiger)
    prio_regel TEXT, -- Beschreibung der Priorisierungsregel
    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    aktualisiert_am TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for queries
CREATE INDEX IF NOT EXISTS idx_domains_tld_aktiv ON domains_tld(aktiv);
CREATE INDEX IF NOT EXISTS idx_domains_tld_prio ON domains_tld(prio DESC);

-- ============================================================================
-- Table: domains_tld_registrar (Registrar-specific TLD Pricing)
-- ============================================================================
CREATE TABLE IF NOT EXISTS domains_tld_registrar (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tld VARCHAR(50) NOT NULL REFERENCES domains_tld(tld) ON DELETE CASCADE,
    registrar_id VARCHAR(50) NOT NULL, -- e.g., "inwx", "schlundtech"

    -- Registrierung (New Registration)
    registrierung_ek_eur NUMERIC(10,2), -- Einkaufspreis
    registrierung_periodejahre INTEGER DEFAULT 1, -- Periode in Jahren

    -- Providerwechsel (Transfer)
    providerwechsel_ek_eur NUMERIC(10,2),
    providerwechsel_periodejahre INTEGER DEFAULT 1,

    -- Erneuerung (Renewal)
    erneuerung_ek_eur NUMERIC(10,2),
    erneuerung_periodejahre INTEGER DEFAULT 1,

    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    aktualisiert_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(tld, registrar_id)
);

-- Index for registrar lookups
CREATE INDEX IF NOT EXISTS idx_domains_tld_registrar_tld ON domains_tld_registrar(tld);
CREATE INDEX IF NOT EXISTS idx_domains_tld_registrar_registrar ON domains_tld_registrar(registrar_id);

-- ============================================================================
-- Table: domain_registrierung (Domain Registration Records)
-- ============================================================================
CREATE TABLE IF NOT EXISTS domain_registrierung (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    kunden_id UUID NOT NULL REFERENCES kunden(id) ON DELETE CASCADE,

    -- Domain Information
    wunschdomain VARCHAR(255) NOT NULL, -- Base domain ohne TLD (z.B. "schreinerei-mueller")
    tld VARCHAR(50) NOT NULL REFERENCES domains_tld(tld),
    vollstaendige_domain VARCHAR(255) NOT NULL, -- Komplett (z.B. "schreinerei-mueller.de")

    -- Pricing
    vk_preis_eur NUMERIC(10,2) NOT NULL, -- Verkaufspreis

    -- Status
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, registered, failed, cancelled

    -- INWX API Payloads (for debugging & audit)
    inwx_request_payload JSONB,
    inwx_response_payload JSONB,

    -- Timestamps
    erstellt_am TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    aktualisiert_am TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_domain_registrierung_kunden ON domain_registrierung(kunden_id);
CREATE INDEX IF NOT EXISTS idx_domain_registrierung_domain ON domain_registrierung(vollstaendige_domain);
CREATE INDEX IF NOT EXISTS idx_domain_registrierung_status ON domain_registrierung(status);
CREATE INDEX IF NOT EXISTS idx_domain_registrierung_created ON domain_registrierung(erstellt_am DESC);

-- ============================================================================
-- Triggers: Auto-update aktualisiert_am timestamp
-- ============================================================================

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_aktualisiert_am()
RETURNS TRIGGER AS $$
BEGIN
    NEW.aktualisiert_am = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables
CREATE TRIGGER update_saas_dienste_aktualisiert_am
    BEFORE UPDATE ON saas_dienste
    FOR EACH ROW
    EXECUTE FUNCTION update_aktualisiert_am();

CREATE TRIGGER update_kunden_aktualisiert_am
    BEFORE UPDATE ON kunden
    FOR EACH ROW
    EXECUTE FUNCTION update_aktualisiert_am();

CREATE TRIGGER update_domains_tld_aktualisiert_am
    BEFORE UPDATE ON domains_tld
    FOR EACH ROW
    EXECUTE FUNCTION update_aktualisiert_am();

CREATE TRIGGER update_domains_tld_registrar_aktualisiert_am
    BEFORE UPDATE ON domains_tld_registrar
    FOR EACH ROW
    EXECUTE FUNCTION update_aktualisiert_am();

CREATE TRIGGER update_domain_registrierung_aktualisiert_am
    BEFORE UPDATE ON domain_registrierung
    FOR EACH ROW
    EXECUTE FUNCTION update_aktualisiert_am();

-- ============================================================================
-- Sample Data (for testing)
-- ============================================================================

-- Insert SaaS Services / Partner Portals
INSERT INTO saas_dienste (id, dienst_key, name, aktiv, api_token, whitelabel_config) VALUES
(
    '10000000-0000-0000-0000-000000000001',
    'handelshelfer',
    'Handelshelfer',
    true,
    'token_handelshelfer_dev_123',
    '{"primaryColor": "#1e40af", "secondaryColor": "#3b82f6", "logoUrl": "https://handelshelfer.de/logo.png"}'::jsonb
),
(
    '10000000-0000-0000-0000-000000000002',
    'handwerker24',
    'Handwerker24',
    true,
    'token_handwerker24_dev_456',
    '{"primaryColor": "#dc2626", "secondaryColor": "#ef4444", "logoUrl": "https://handwerker24.de/logo.png"}'::jsonb
)
ON CONFLICT (dienst_key) DO NOTHING;

-- Insert some popular TLDs
INSERT INTO domains_tld (tld, vk_eur, aktiv, sortierung, tld_gruppe, gruppe, prio, prio_regel) VALUES
('de', 8.99, true, 1, 'cctld', 'standard', 100, 'Deutsche TLD - höchste Prio für DE'),
('com', 12.99, true, 2, 'gtld', 'standard', 90, 'International - sehr beliebt'),
('net', 12.99, true, 3, 'gtld', 'standard', 70, 'Alternative zu .com'),
('org', 12.99, true, 4, 'gtld', 'standard', 60, 'Für Organisationen'),
('info', 9.99, true, 5, 'gtld', 'standard', 50, 'Informationsseiten'),
('berlin', 39.99, true, 10, 'new-gtld', 'geo', 40, 'Berlin-spezifisch'),
('shop', 34.99, true, 11, 'new-gtld', 'thematisch', 70, 'E-Commerce'),
('online', 29.99, true, 12, 'new-gtld', 'standard', 50, 'Allgemein online')
ON CONFLICT (tld) DO NOTHING;

-- Insert INWX registrar pricing
INSERT INTO domains_tld_registrar (tld, registrar_id, registrierung_ek_eur, registrierung_periodejahre, erneuerung_ek_eur, erneuerung_periodejahre) VALUES
('de', 'inwx', 5.50, 1, 5.50, 1),
('com', 'inwx', 9.50, 1, 9.50, 1),
('net', 'inwx', 9.50, 1, 9.50, 1),
('org', 'inwx', 9.50, 1, 9.50, 1),
('info', 'inwx', 6.50, 1, 6.50, 1),
('berlin', 'inwx', 32.00, 1, 32.00, 1),
('shop', 'inwx', 28.00, 1, 28.00, 1),
('online', 'inwx', 24.00, 1, 24.00, 1)
ON CONFLICT (tld, registrar_id) DO NOTHING;

-- Insert test customers (same company GUID from unternehmensdaten.org, but registered via different services)
INSERT INTO kunden (id, saas_dienst_id, name, email, land, branche, unternehmensdaten_sync_am) VALUES
(
    '00000000-0000-0000-0000-000000000001', -- Unternehmensdaten.org GUID
    '10000000-0000-0000-0000-000000000001', -- Handelshelfer
    'Mustermann GmbH',
    'info@mustermann-gmbh.de',
    'DE',
    'haendler',
    NOW()
),
(
    '00000000-0000-0000-0000-000000000002', -- Unternehmensdaten.org GUID
    '10000000-0000-0000-0000-000000000002', -- Handwerker24
    'Schreinerei Schmidt',
    'kontakt@schreinerei-schmidt.de',
    'DE',
    'handwerker',
    NOW()
)
ON CONFLICT (id, saas_dienst_id) DO NOTHING;

-- ============================================================================
-- Comments for documentation
-- ============================================================================

COMMENT ON TABLE saas_dienste IS 'SaaS Partner-Dienste (Handelshelfer, Handwerker24, etc.), die den Domain-Service nutzen';
COMMENT ON TABLE kunden IS 'Kundenstammdaten - Unternehmen aus unternehmensdaten.org, die über Partner-Dienste Domains registrieren';
COMMENT ON TABLE domains_tld IS 'TLD-Stammdaten mit Verkaufspreisen und Metadaten';
COMMENT ON TABLE domains_tld_registrar IS 'Registrar-spezifische Einkaufspreise (INWX, Schlundtech, etc.)';
COMMENT ON TABLE domain_registrierung IS 'Domain-Registrierungen mit Status und INWX-Payloads';

COMMENT ON COLUMN saas_dienste.dienst_key IS 'Eindeutiger Schlüssel für den Dienst (z.B. handelshelfer, handwerker24)';
COMMENT ON COLUMN saas_dienste.whitelabel_config IS 'White-Label Konfiguration als JSON (Farben, Logo-URLs, Fonts, etc.)';
COMMENT ON COLUMN kunden.id IS 'UUID aus unternehmensdaten.org - NICHT auto-generated!';
COMMENT ON COLUMN kunden.saas_dienst_id IS 'Referenz zum SaaS-Dienst, der diesen Kunden registriert hat';
COMMENT ON COLUMN kunden.land IS 'ISO 3166-1 alpha-2 Ländercode';
COMMENT ON COLUMN kunden.branche IS 'Branche: haendler, handwerker, dienstleister, etc.';
COMMENT ON COLUMN kunden.unternehmensdaten_sync_am IS 'Zeitpunkt des letzten Sync mit unternehmensdaten.org';
COMMENT ON COLUMN domains_tld.prio IS 'Priorität für Domain-Vorschläge (höher = wichtiger)';
COMMENT ON COLUMN domain_registrierung.status IS 'Status: pending, registered, failed, cancelled';
COMMENT ON COLUMN domain_registrierung.inwx_request_payload IS 'Original INWX API Request (JSON)';
COMMENT ON COLUMN domain_registrierung.inwx_response_payload IS 'Original INWX API Response (JSON)';
