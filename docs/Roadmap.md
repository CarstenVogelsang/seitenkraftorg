# seitenkraft.org Roadmap

This document outlines future development phases beyond the initial POC.

---

## Phase 1: POC ✅ (Current)

**Goal**: Validate core concept with minimal viable wizard

**Features**:
- Domain availability check via INWX OTE (test mode)
- Basic domain suggestions based on business data
- Simple wizard flow (4 steps)
- Fake authentication
- White-label support for 2 partner portals
- Supabase database integration

**Status**: In Development
**Timeline**: Initial POC phase

---

## Phase 2: Production Domain Registration

**Goal**: Enable real domain registration and management

### Domain Registration
- [ ] Switch to INWX Production API
- [ ] Real domain registration flow
- [ ] Domain ownership verification
- [ ] DNS management interface
- [ ] Domain transfer functionality (Providerwechsel)
- [ ] Domain renewal automation
- [ ] WHOIS privacy protection

### Payment Integration
- [ ] Payment provider integration (Stripe/PayPal)
- [ ] Pricing calculation with taxes
- [ ] Invoice generation
- [ ] Payment status tracking
- [ ] Recurring billing for renewals
- [ ] Refund handling

### User Authentication
- [ ] Replace fake auth with OAuth2/JWT
- [ ] User registration and login
- [ ] Password reset flow
- [ ] Email verification
- [ ] Session management
- [ ] Role-based access control (RBAC)

---

## Phase 3: Enhanced Domain Intelligence

**Goal**: Improve domain suggestion quality and user experience

### Advanced Domain Suggestions
- [ ] AI-powered name generation
- [ ] Industry-specific keywords database
- [ ] Trademark conflict checking
- [ ] SEO score for domain names
- [ ] Social media handle availability check
- [ ] Brandability scoring
- [ ] Pronunciation difficulty analysis

### Multi-Language Support
- [ ] German language optimization
- [ ] English language support
- [ ] Country-specific TLD recommendations
- [ ] Localized pricing display

### Domain Analytics
- [ ] Domain value estimation
- [ ] Historical registration trends
- [ ] Competitor domain analysis
- [ ] Keyword search volume data

---

## Phase 4: SiteFactory - Astro-Based Website Generation

**Goal**: Automatically generate and deploy customer websites

### Static Site Generation
- [ ] Astro project template system
- [ ] Component library for business sites
- [ ] Template selection (industry-specific)
- [ ] Theme customization (colors, fonts, layout)
- [ ] Content population from unternehmensdaten.org
- [ ] Product integration from produktdaten.org
- [ ] Image optimization and CDN integration

### Content Management
- [ ] WYSIWYG editor for basic content editing
- [ ] Page management (add/remove pages)
- [ ] Navigation builder
- [ ] Contact form builder
- [ ] Google Maps integration
- [ ] Social media link management

### Deployment
- [ ] Cloudflare Pages integration
- [ ] Automatic deployment on content change
- [ ] Custom domain linking
- [ ] SSL certificate automation
- [ ] CDN configuration
- [ ] Performance optimization
- [ ] SEO meta tags generation

### Templates
Priority templates by industry:
1. **Handwerker** (Craftsmen)
   - Services showcase
   - Project gallery
   - Contact/quote form
   - Service areas map

2. **Händler** (Retailers)
   - Product catalog display
   - Store locations
   - Opening hours
   - Online inquiry form

3. **Dienstleister** (Service Providers)
   - Service descriptions
   - Pricing tables
   - Booking calendar
   - Team/about page

---

## Phase 5: Mobile Apps (React Native / Expo)

**Goal**: Mobile companion apps for website management

### Mobile App Features
- [ ] React Native / Expo setup
- [ ] Shared authentication with web platform
- [ ] Domain management on-the-go
- [ ] Website content editing (simplified)
- [ ] Photo upload for website content
- [ ] Image gallery management
- [ ] Push notifications for:
  - Domain renewal reminders
  - Website update confirmations
  - Registration status changes

### Camera Integration
- [ ] Take photos directly in app
- [ ] Image cropping and filters
- [ ] Automatic image optimization
- [ ] Gallery organization
- [ ] Sync to website media library

### Offline Support
- [ ] Local draft storage
- [ ] Sync when online
- [ ] Offline content viewing

### Platforms
- [ ] iOS (App Store)
- [ ] Android (Google Play)

---

## Phase 6: Admin & Analytics

**Goal**: Administrative tools and business intelligence

### Admin Dashboard
- [ ] Customer management
- [ ] Domain registration overview
- [ ] Revenue tracking
- [ ] Support ticket system
- [ ] Registrar account management (INWX, Schlundtech)
- [ ] TLD pricing management
- [ ] White-label partner configuration

### Analytics & Reporting
- [ ] Domain registration trends
- [ ] Revenue reports
- [ ] Popular TLDs analysis
- [ ] Conversion funnel tracking
- [ ] Customer lifetime value (CLV)
- [ ] Partner portal performance
- [ ] A/B testing framework

### Customer Success
- [ ] Onboarding automation
- [ ] Email notification system
- [ ] Customer health scoring
- [ ] Churn prediction
- [ ] Renewal reminders

---

## Phase 7: Ecosystem Expansion

**Goal**: Deeper integration with partner services

### Integration Enhancements
- [ ] Real-time sync with unternehmensdaten.org
- [ ] Automatic website updates on data changes
- [ ] Product catalog live integration
- [ ] Inventory sync for e-commerce sites
- [ ] Order management integration
- [ ] CRM integration (HubSpot, Salesforce)

### Additional Partner Portals
- [ ] White-label for additional vertical SaaS platforms
- [ ] Partner API for third-party integrations
- [ ] Webhook support for event notifications
- [ ] SSO integration options

### Multi-Registrar Support
- [ ] Schlundtech (InternetX) integration
- [ ] Additional registrar options
- [ ] Automatic registrar selection (pricing optimization)
- [ ] Load balancing across registrars

---

## Phase 8: Enterprise Features

**Goal**: Support for larger customers and agencies

### Multi-Site Management
- [ ] Manage multiple domains per customer
- [ ] Bulk operations (registration, renewal, transfer)
- [ ] Domain portfolio overview
- [ ] Consolidated billing
- [ ] Team collaboration features

### White-Label Reseller Program
- [ ] Reseller dashboard
- [ ] Custom pricing tiers
- [ ] Branded customer experience
- [ ] Commission tracking
- [ ] Sub-account management

### Advanced Security
- [ ] Two-factor authentication (2FA)
- [ ] IP whitelisting
- [ ] Audit logging
- [ ] GDPR compliance tools
- [ ] Data export functionality

---

## Technical Debt & Infrastructure

Ongoing improvements across all phases:

### Performance
- [ ] Database query optimization
- [ ] Caching layer (Redis)
- [ ] CDN for static assets
- [ ] API response time monitoring
- [ ] Load testing and optimization

### Testing & Quality
- [ ] Unit test coverage (80%+)
- [ ] Integration test suite
- [ ] End-to-end testing (Playwright/Cypress)
- [ ] Performance testing
- [ ] Security testing (OWASP)

### DevOps
- [ ] CI/CD pipeline
- [ ] Automated deployment
- [ ] Environment management (dev/staging/prod)
- [ ] Database migration system
- [ ] Backup and disaster recovery
- [ ] Monitoring and alerting (Sentry, DataDog)

### Documentation
- [ ] API documentation (OpenAPI/Swagger)
- [ ] User guides
- [ ] Admin documentation
- [ ] Developer onboarding guide
- [ ] Architecture decision records (ADRs)

---

## Technology Considerations

### Future Tech Explorations
- **Edge Computing**: Cloudflare Workers for dynamic content
- **Real-time Updates**: WebSockets for live status updates
- **AI Integration**: GPT-based content generation for websites
- **Voice Interface**: Alexa/Google Assistant integration
- **Blockchain**: Domain ownership verification via blockchain

---

## Release Strategy

**Release Cadence**: Bi-weekly sprints with monthly releases

**Versioning**: Semantic versioning (MAJOR.MINOR.PATCH)
- MAJOR: Breaking API changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

**Beta Program**: Early access for select partners before general release

---

## Success Metrics

Key performance indicators (KPIs) to track:

1. **Domain Registrations**: Monthly registration volume
2. **Conversion Rate**: Wizard completion rate
3. **Customer Satisfaction**: NPS score
4. **Revenue Growth**: MRR and ARR
5. **Partner Engagement**: Active partner portals
6. **Website Deployments**: Sites generated via SiteFactory
7. **Mobile App Adoption**: Active mobile users
8. **Platform Stability**: Uptime (target: 99.9%)

---

*This roadmap is subject to change based on customer feedback, market conditions, and technical feasibility.*

*Last updated: 2025-11-24*
