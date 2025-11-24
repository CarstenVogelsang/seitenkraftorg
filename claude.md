# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**seitenkraft.org** is a domain management and website generation SaaS within a larger ecosystem. It serves as a central service for:
- Domain availability checking and registration via INWX API
- Domain suggestion and pricing
- Future: Static website generation (Astro-based SiteFactory)
- Future: Mobile app integration (React Native/Expo)

### Ecosystem Integration
seitenkraft.org integrates with partner services:
- **unternehmensdaten.org** → Company master data (central GUID source for all customers)
- **produktdaten.org** → Product catalogs
- **Partner portals** → Handelshelfer, Handwerker24 (white-label embedding)

**Multi-Tenant Design:**
- Customer GUIDs come from unternehmensdaten.org (never generated locally)
- Same customer can use domain service via multiple partner portals
- Each partner portal has its own white-label configuration stored in `saas_dienste` table
- API authentication via partner-specific tokens

Architecture diagram: [docs/quellen/Ökosystem_Architektur_Übersicht.md](docs/quellen/Ökosystem_Architektur_Übersicht.md)

---

## Tech Stack

### Backend
- **FastAPI** (Python) - REST API
- **Uvicorn** - ASGI server
- **Supabase PostgreSQL** - Database (existing instance)
- **HTTPX** - HTTP client for INWX API calls

### Frontend
- **React + TypeScript** - UI framework
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **shadcn/ui** - Component library (local components)
- **No routing required** - Wizard uses local state management

### External APIs
- **INWX OTE API** (Test): `https://api.ote.inwx.com/jsonrpc/`
- **INWX Production API**: `https://api.inwx.com/jsonrpc/`

---

## Development Commands

### Backend
```bash
cd backend
pip install -r requirements.txt  # or: poetry install
uvicorn app.main:app --reload
# Server runs on http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Vite dev server runs on http://localhost:5173
```

### Database Setup
Choose one option:

**Option A: SQL Editor (Supabase Dashboard)**
```bash
# Copy SQL from backend/app/db/supabase_schema.sql
# Paste and execute in Supabase SQL Editor
```

**Option B: Python Setup Script**
```bash
cd backend
python scripts/setup_db.py
```

---

## Architecture Highlights

### Database Schema (Supabase)

**Multi-Tenant Architecture:**
seitenkraft.org serves multiple SaaS partner services (Handelshelfer, Handwerker24, etc.). Customer GUIDs originate from **unternehmensdaten.org** and are shared across all services in the ecosystem.

**Core Tables:**
- `saas_dienste` - Partner services that use domain service (dienst_key, name, api_token, whitelabel_config)
- `kunden` - Customer data from unternehmensdaten.org (id=unternehmensdaten_guid, saas_dienst_id, name, email, land, branche)
  - **Important**: `id` is NOT auto-generated but provided by unternehmensdaten.org
  - Customers can register domains via multiple partner services
  - Each customer-service combination tracked separately
- `domains_tld` - TLD pricing & metadata (tld, vk_eur, aktiv, sortierung, prio)
- `domains_tld_registrar` - Registrar-specific pricing (tld, registrar_id, ek_eur, periode)
- `domain_registrierung` - Domain registration records (id, kunden_id, domain, status, inwx payloads)

TLD reference data for import: [docs/quellen/tld_info.xlsx](docs/quellen/tld_info.xlsx)

### INWX Integration

**POC Phase**: Use OTE (test) server
- No real domain registrations
- Test credentials required in `.env`

**Production**: Switch to production API endpoint
- Real registrations and billing
- Production credentials required

**API Method**: JSON-RPC over HTTPS
- `domain.check` - Availability check
- `domain.register` - Domain registration (future)

### White-Label Embedding

The wizard supports white-label branding via URL parameters:
- `?brand=handelshelfer` → Handelshelfer CI/CD
- `?brand=handwerker24` → Handwerker24 CI/CD

Implementation: `UI_WhiteLabelThemeProvider` component reads params and applies theme.

### Authentication (POC)

**Fake auth for POC**: Custom header `X-Client-Token`
- Backend validates token in `core/security_fake.py`
- Sufficient for initial testing
- Production: Replace with proper OAuth2/JWT

### API Endpoints

**Health Check:**
- `GET /health` → `{"status": "ok"}`

**Wizard Flow:**
- `GET /wizard/start/{kundenguid}` → Fetch customer data (fake auth)
- `POST /domains/suggest` → Generate domain suggestions based on business data
- `POST /domains/check` → Check availability via INWX
- `POST /domains/register` → Register domain (POC: fake registration, logs to DB)

---

## Environment Variables

Create `.env` files in backend and frontend directories:

### Backend `.env`
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
INWX_API_URL=https://api.ote.inwx.com/jsonrpc/  # OTE for testing
INWX_USERNAME=your-test-username
INWX_PASSWORD=your-test-password
```

### Frontend `.env`
```bash
VITE_API_URL=http://localhost:8000
```

---

## Project Structure

```
backend/
├── app/
│   ├── main.py                    # FastAPI app entry
│   ├── api/                       # Route handlers
│   │   ├── wizard.py
│   │   ├── domains.py
│   │   └── health.py
│   ├── core/                      # Config & security
│   │   ├── config.py
│   │   └── security_fake.py
│   ├── services/                  # Business logic
│   │   ├── inwx_service.py
│   │   ├── domain_suggestion.py
│   │   └── unternehmensdaten_fake.py
│   ├── models/                    # Pydantic models
│   │   ├── kunden.py
│   │   └── domains.py
│   └── db/
│       └── supabase_schema.sql

frontend/
├── src/
│   ├── App.tsx                    # Main app component
│   ├── main.tsx                   # Entry point
│   └── components/
│       ├── WizardStart.tsx
│       ├── WizardStep1_DomainInput.tsx
│       ├── WizardStep2_CheckAndPrice.tsx
│       ├── WizardStep3_ConfirmFake.tsx
│       ├── CustomerSelectorPOC.tsx
│       └── UI_WhiteLabelThemeProvider.tsx

docs/
├── quellen/                       # Reference data
│   ├── Ökosystem_Architektur_Übersicht.md
│   └── tld_info.xlsx
├── POC_Definition_of_Done.md      # Completion criteria
└── Roadmap.md                     # Future features
```

---

## Additional Documentation

- **POC Completion Criteria**: [docs/POC_Definition_of_Done.md](docs/POC_Definition_of_Done.md)
- **Future Roadmap**: [docs/Roadmap.md](docs/Roadmap.md) (Astro SiteFactory, React Native apps)
- **Ecosystem Architecture**: [docs/quellen/Ökosystem_Architektur_Übersicht.md](docs/quellen/Ökosystem_Architektur_Übersicht.md)
