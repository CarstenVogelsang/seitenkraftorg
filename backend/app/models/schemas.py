"""
Pydantic Models for API Request/Response Schemas
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# SaaS Dienste
# ============================================================================

class SaaSDienstBase(BaseModel):
    dienst_key: str
    name: str
    aktiv: bool = True


class SaaSDienst(SaaSDienstBase):
    id: UUID
    whitelabel_config: Optional[dict] = None
    erstellt_am: datetime
    aktualisiert_am: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Kunden
# ============================================================================

class KundeBase(BaseModel):
    name: str
    email: EmailStr
    land: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2")
    branche: Optional[str] = None


class KundeCreate(KundeBase):
    id: UUID  # From unternehmensdaten.org
    saas_dienst_id: UUID


class Kunde(KundeBase):
    id: UUID
    saas_dienst_id: UUID
    unternehmensdaten_sync_am: Optional[datetime] = None
    erstellt_am: datetime
    aktualisiert_am: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Domain TLD
# ============================================================================

class DomainTLDBase(BaseModel):
    tld: str
    vk_eur: float
    aktiv: bool = True
    sortierung: int = 0
    tld_gruppe: Optional[str] = None
    gruppe: Optional[str] = None
    prio: int = 0
    prio_regel: Optional[str] = None


class DomainTLD(DomainTLDBase):
    erstellt_am: datetime
    aktualisiert_am: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Domain Registrierung
# ============================================================================

class DomainRegistrierungBase(BaseModel):
    wunschdomain: str
    tld: str
    vollstaendige_domain: str
    vk_preis_eur: float


class DomainRegistrierungCreate(DomainRegistrierungBase):
    kunden_id: UUID


class DomainRegistrierung(DomainRegistrierungBase):
    id: UUID
    kunden_id: UUID
    status: str
    inwx_request_payload: Optional[dict] = None
    inwx_response_payload: Optional[dict] = None
    erstellt_am: datetime
    aktualisiert_am: datetime

    class Config:
        from_attributes = True


# ============================================================================
# API Requests/Responses
# ============================================================================

class WizardStartResponse(BaseModel):
    """Response for /wizard/start/{kundenguid}"""
    kunde: Kunde
    saas_dienst: SaaSDienst


class DomainSuggestionRequest(BaseModel):
    """Request for domain suggestions"""
    wunschdomain_basis: str = Field(..., description="Base domain without TLD, e.g. 'schreinerei-mueller'")
    land: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2")
    branche: Optional[str] = Field(None, description="Industry sector")
    max_suggestions: int = Field(10, ge=1, le=50, description="Max number of suggestions")


class DomainSuggestion(BaseModel):
    """Single domain suggestion"""
    domain: str
    tld: str
    verfuegbar: Optional[bool] = None
    preis_eur: float
    prio: int
    empfohlen: bool = False


class DomainSuggestionResponse(BaseModel):
    """Response with domain suggestions"""
    suggestions: list[DomainSuggestion]
    wunschdomain_basis: str


class DomainCheckRequest(BaseModel):
    """Request to check domain availability"""
    domains: list[str] = Field(..., description="List of full domains to check, e.g. ['example.de', 'example.com']")


class DomainCheckResult(BaseModel):
    """Single domain check result"""
    domain: str
    verfuegbar: bool
    preis_eur: Optional[float] = None
    fehler: Optional[str] = None


class DomainCheckResponse(BaseModel):
    """Response with domain check results"""
    results: list[DomainCheckResult]


class DomainRegisterRequest(BaseModel):
    """Request to register a domain"""
    kunden_id: UUID
    domain: str = Field(..., description="Full domain, e.g. 'example.de'")


class DomainRegisterResponse(BaseModel):
    """Response after domain registration"""
    success: bool
    registrierung: Optional[DomainRegistrierung] = None
    fehler: Optional[str] = None


# ============================================================================
# Health Check
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str = "0.1.0-poc"
    environment: str
