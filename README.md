# seitenkraft.org

> Domain-Verwaltung & Website-Generierung als Multi-Tenant SaaS

**seitenkraft.org** ist ein Domain-Management-Service für das Ökosystem aus Branchenportalen wie Handelshelfer und Handwerker24. Der Service ermöglicht Domain-Verfügbarkeitsprüfung, intelligente Domain-Vorschläge und Integration mit INWX für Domain-Registrierungen.

## 🚀 Quick Start

### Voraussetzungen

- Python 3.11+
- Supabase Account (PostgreSQL Datenbank)
- INWX OTE Testaccount (für Domain-Checks)

### Installation

1. **Repository klonen**
   ```bash
   git clone git@github.com:CarstenVogelsang/seitenkraftorg.git
   cd seitenkraftorg
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env
   # .env mit Ihren Credentials bearbeiten
   ```

3. **Datenbank initialisieren**
   ```bash
   python scripts/setup_db.py
   ```

4. **Backend starten**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📚 Dokumentation

**Entwickler-Dokumentation**: Siehe [CLAUDE.md](CLAUDE.md) für:
- Detaillierte Architektur-Übersicht
- Tech Stack & Design-Entscheidungen
- Development Commands
- Multi-Tenant Konzept
- API Endpunkte
- Deployment-Anleitung

**Weitere Dokumentation**:
- [POC Definition of Done](docs/POC_Definition_of_Done.md) - Completion Checklisten
- [Roadmap](docs/Roadmap.md) - Product Roadmap (8 Phasen)
- [Ökosystem Architektur](docs/quellen/Ökosystem_Architektur_Übersicht.md) - System-Diagramm

## 🏗️ Architektur

### Multi-Tenant Design

```
unternehmensdaten.org (Master-System)
         │
         ├── Handelshelfer (Partner Portal)
         └── Handwerker24 (Partner Portal)
                   │
                   ▼
         seitenkraft.org (Domain-Service)
                   │
                   ▼
              INWX API (Registrar)
```

**Key Concepts**:
- Kunden-GUIDs stammen aus `unternehmensdaten.org` (zentrale Identität)
- Gleicher Kunde kann über mehrere Partner-Portale Domains registrieren
- White-Label Support für Partner-Branding
- Partner-spezifische API-Authentifizierung

## 🗄️ Database Schema

```sql
saas_dienste            -- Partner-Dienste (Handelshelfer, Handwerker24)
  ├── dienst_key
  ├── api_token
  └── whitelabel_config

kunden                  -- Kundendaten (von unternehmensdaten.org)
  ├── id               -- GUID von unternehmensdaten.org
  ├── saas_dienst_id
  └── unternehmensdaten_sync_am

domains_tld            -- TLD-Preise & Metadaten
domains_tld_registrar  -- Registrar-spezifische Preise (INWX)
domain_registrierung   -- Registrierungen mit Status
```

## 🛠️ Tech Stack

**Backend** (aktuell):
- FastAPI - REST API Framework
- Uvicorn - ASGI Server
- Supabase - PostgreSQL Datenbank
- HTTPX - HTTP Client für INWX API

**Frontend** (geplant):
- React + TypeScript
- Vite
- TailwindCSS
- shadcn/ui

**Zukunft**:
- Astro - Statische Website-Generierung (SiteFactory)
- React Native/Expo - Mobile Apps

## 🧪 Development Status

**Aktueller Stand**: POC Phase 1 - Planning & Setup
- ✅ Datenbank-Schema definiert
- ✅ Multi-Tenant Architektur dokumentiert
- ✅ Setup-Scripts erstellt
- 🚧 Backend-Implementierung (in Arbeit)
- ⏳ Frontend-Wizard (ausstehend)
- ⏳ INWX Integration (ausstehend)

Siehe [POC Definition of Done](docs/POC_Definition_of_Done.md) für vollständige Checklisten.

## 📝 Lizenz

Proprietary - Alle Rechte vorbehalten

## 🤝 Entwicklung

Dieses Projekt wurde mit Unterstützung von [Claude Code](https://claude.com/claude-code) entwickelt.

---

**Hinweis**: Dies ist ein POC-Projekt. Für produktive Nutzung sind weitere Sicherheits- und Performance-Optimierungen erforderlich.
