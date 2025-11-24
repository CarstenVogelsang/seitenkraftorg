"""
Domain API Endpoints

Handles domain suggestions, availability checks, and registrations.
"""

from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security_fake import verify_fake_token
from app.models.schemas import (
    DomainSuggestionRequest,
    DomainSuggestionResponse,
    DomainCheckRequest,
    DomainCheckResponse,
    DomainCheckResult,
    DomainRegisterRequest,
    DomainRegisterResponse,
    DomainRegistrierung,
)
from app.services.domain_suggestion import DomainSuggestionService
from app.services.inwx_service import INWXService
from app.services.supabase_client import SupabaseService

router = APIRouter(prefix="/domains", tags=["Domains"])


@router.post("/suggest", response_model=DomainSuggestionResponse)
async def suggest_domains(
    request: DomainSuggestionRequest,
    token: str = Depends(verify_fake_token)
):
    """
    Generate domain suggestions

    Creates intelligent domain suggestions based on business name,
    country, and industry sector.

    Args:
        request: Domain suggestion parameters
        token: Authentication token

    Returns:
        List of domain suggestions with pricing and priority
    """
    suggestion_service = DomainSuggestionService()

    suggestions = suggestion_service.generate_suggestions(
        wunschdomain_basis=request.wunschdomain_basis,
        land=request.land,
        branche=request.branche,
        max_suggestions=request.max_suggestions
    )

    return DomainSuggestionResponse(
        suggestions=suggestions,
        wunschdomain_basis=request.wunschdomain_basis
    )


@router.post("/check", response_model=DomainCheckResponse)
async def check_domains(
    request: DomainCheckRequest,
    token: str = Depends(verify_fake_token)
):
    """
    Check domain availability via INWX API

    Args:
        request: List of domains to check
        token: Authentication token

    Returns:
        Availability results for each domain

    Raises:
        500: INWX API error
    """
    db = SupabaseService()
    results = []

    async with INWXService() as inwx:
        for domain in request.domains:
            try:
                # Check via INWX
                inwx_result = await inwx.check_domain(domain)

                # Get pricing from database
                tld = domain.split(".")[-1]
                tld_data = db.get_tld_by_name(tld)

                result = DomainCheckResult(
                    domain=domain,
                    verfuegbar=inwx_result.get("avail", False),
                    preis_eur=tld_data["vk_eur"] if tld_data else None,
                    fehler=inwx_result.get("error")
                )

                results.append(result)

            except Exception as e:
                results.append(
                    DomainCheckResult(
                        domain=domain,
                        verfuegbar=False,
                        fehler=str(e)
                    )
                )

    return DomainCheckResponse(results=results)


@router.post("/register", response_model=DomainRegisterResponse)
async def register_domain(
    request: DomainRegisterRequest,
    token: str = Depends(verify_fake_token)
):
    """
    Register a domain (POC: Fake registration)

    Args:
        request: Domain registration request
        token: Authentication token

    Returns:
        Registration result

    Raises:
        404: Customer not found
        400: Invalid domain or TLD
    """
    db = SupabaseService()

    # Validate customer exists
    kunde = db.get_kunde_by_id(request.kunden_id)
    if not kunde:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {request.kunden_id} not found"
        )

    # Parse domain
    if "." not in request.domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid domain format"
        )

    parts = request.domain.rsplit(".", 1)
    wunschdomain = parts[0]
    tld = parts[1]

    # Validate TLD exists
    tld_data = db.get_tld_by_name(tld)
    if not tld_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"TLD '{tld}' not supported"
        )

    # POC: Fake INWX registration
    async with INWXService() as inwx:
        inwx_result = await inwx.register_domain(
            request.domain,
            customer_data={}
        )

    # Store registration in database
    registrierung_data = {
        "id": str(uuid4()),
        "kunden_id": str(request.kunden_id),
        "wunschdomain": wunschdomain,
        "tld": tld,
        "vollstaendige_domain": request.domain,
        "vk_preis_eur": tld_data["vk_eur"],
        "status": "registered" if inwx_result.get("success") else "failed",
        "inwx_request_payload": {"domain": request.domain},
        "inwx_response_payload": inwx_result
    }

    registrierung = db.create_domain_registrierung(registrierung_data)

    return DomainRegisterResponse(
        success=inwx_result.get("success", False),
        registrierung=DomainRegistrierung(**registrierung),
        fehler=inwx_result.get("error")
    )
