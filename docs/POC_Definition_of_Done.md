# POC Definition of Done

This document defines the completion criteria for the seitenkraft.org Proof of Concept (POC).

---

## Backend Requirements

### ✅ Projektstruktur
- [ ] FastAPI application setup with proper directory structure
- [ ] Configuration management (`core/config.py`)
- [ ] Fake authentication system (`core/security_fake.py`)
- [ ] API route organization (health, wizard, domains)

### ✅ Supabase Schema
- [ ] Database schema file created (`backend/app/db/supabase_schema.sql`)
- [ ] Schema applied to Supabase instance
- [ ] All tables created:
  - [ ] `kunden` (customer data)
  - [ ] `domains_tld` (TLD pricing & metadata)
  - [ ] `domains_tld_registrar` (registrar-specific pricing)
  - [ ] `domain_registrierung` (registration records)
- [ ] TLD data imported from `docs/quellen/tld_info.xlsx`

### ✅ Domain Suggestion Logic
- [ ] Service implemented (`services/domain_suggestion.py`)
- [ ] Business name processing (clean, normalize)
- [ ] TLD combination generation
- [ ] Scoring/prioritization based on:
  - [ ] TLD popularity
  - [ ] Country relevance
  - [ ] Industry fit
  - [ ] Pricing

### ✅ INWX OTE Check
- [ ] INWX API client service (`services/inwx_service.py`)
- [ ] JSON-RPC communication implemented
- [ ] Authentication with OTE credentials
- [ ] Domain availability check working
- [ ] Error handling for API failures
- [ ] Response parsing and formatting

### ✅ Fake Registration
- [ ] Registration endpoint (`POST /domains/register`)
- [ ] Write registration record to database
- [ ] Store INWX request/response payloads
- [ ] Return confirmation to frontend
- [ ] Status tracking (pending, completed, failed)

---

## Frontend Requirements

### ✅ Vite + React Setup
- [ ] Vite project initialized
- [ ] TypeScript configuration
- [ ] Development server running
- [ ] Build process working
- [ ] Environment variable handling (`.env`)

### ✅ TailwindCSS
- [ ] Tailwind installed and configured
- [ ] Custom theme/colors defined
- [ ] Utility classes working
- [ ] Build optimization configured

### ✅ shadcn/ui
- [ ] Component library initialized
- [ ] Required components installed locally:
  - [ ] Button
  - [ ] Input
  - [ ] Card
  - [ ] Select
  - [ ] Dialog/Modal
  - [ ] Loading spinner
- [ ] Component styling consistent with design

### ✅ Wizard Flow
- [ ] `CustomerSelectorPOC` - Select test customer
- [ ] `WizardStep1_DomainInput` - Enter desired domain
- [ ] `WizardStep2_CheckAndPrice` - Display suggestions and prices
- [ ] `WizardStep3_ConfirmFake` - Confirm fake registration
- [ ] State management between steps
- [ ] Navigation (forward/back)
- [ ] Form validation
- [ ] Error handling and display

### ✅ White-Labeling
- [ ] `UI_WhiteLabelThemeProvider` component
- [ ] URL parameter reading (`?brand=...`)
- [ ] Theme switching for:
  - [ ] Handelshelfer (colors, logo, fonts)
  - [ ] Handwerker24 (colors, logo, fonts)
- [ ] Default theme for direct access
- [ ] Theme persistence during session

---

## Documentation Requirements

### ✅ CLAUDE.md
- [x] Restructured as developer guide
- [x] Development commands documented
- [x] Architecture highlights included
- [x] Environment setup instructions
- [x] Links to additional documentation

### ✅ PRDs (Product Requirement Documents)
Recommended structure in `docs/PRD/`:
- [ ] PRD_01_Wizard_Flow.md
- [ ] PRD_02_Domain_Check_and_Scoring.md
- [ ] PRD_03_INWX_Integration.md
- [ ] PRD_04_TLD_Konzept.md
- [ ] PRD_05_WhiteLabel_Embedding_and_CI.md

*Note: PRDs are optional for POC but recommended for clarity*

---

## Testing Criteria

### Manual Testing
- [ ] Health check endpoint responds
- [ ] Customer selection works
- [ ] Domain input accepts business name
- [ ] Suggestions are generated
- [ ] INWX availability check returns results
- [ ] Pricing is displayed correctly
- [ ] Fake registration completes
- [ ] Registration is stored in database
- [ ] White-label themes switch properly

### Integration Testing
- [ ] Backend ↔ Supabase communication
- [ ] Backend ↔ INWX OTE API communication
- [ ] Frontend ↔ Backend API communication
- [ ] Environment variable loading
- [ ] Error handling for API failures

---

## Deployment Readiness

### Development Environment
- [x] Backend runs locally with hot reload
- [x] Frontend runs locally with hot reload
- [x] Database accessible (Supabase)
- [x] INWX OTE API accessible

### Configuration
- [ ] `.env.example` files created for both backend and frontend
- [ ] Sensitive data not committed to git
- [ ] `.gitignore` properly configured

### Documentation
- [ ] README.md with quick start guide
- [ ] CLAUDE.md with architecture and commands
- [ ] API documentation (FastAPI auto-docs)

---

## Out of Scope for POC

The following features are **not** required for POC completion:

- Real domain registration (use INWX OTE only)
- Payment processing
- User authentication (fake auth is sufficient)
- Email notifications
- Admin panel
- Production deployment
- Automated testing (unit/integration tests)
- CI/CD pipeline
- Performance optimization
- SEO optimization
- Accessibility audit
- Security audit
- Mobile app development
- Astro website generation

These items are documented in [Roadmap.md](Roadmap.md) for future development.
