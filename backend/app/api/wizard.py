"""
Wizard API Endpoints

Handles wizard flow initialization and customer data retrieval.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security_fake import verify_fake_token, get_saas_dienst_from_token
from app.models.schemas import WizardStartResponse, Kunde, SaaSDienst
from app.services.supabase_client import SupabaseService

router = APIRouter(prefix="/wizard", tags=["Wizard"])


@router.get("/start/{kundenguid}", response_model=WizardStartResponse)
async def wizard_start(
    kundenguid: UUID,
    token: str = Depends(verify_fake_token)
):
    """
    Start wizard flow for a customer

    Retrieves customer data and SaaS dienst configuration.

    Args:
        kundenguid: Customer GUID from unternehmensdaten.org
        token: Authentication token (from X-Client-Token header)

    Returns:
        Customer and SaaS dienst data

    Raises:
        404: Customer not found
        401: Invalid authentication
    """
    db = SupabaseService()

    # Get SaaS dienst from token
    dienst_key = get_saas_dienst_from_token(token)
    saas_dienst_data = db.get_saas_dienst_by_key(dienst_key)

    if not saas_dienst_data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"SaaS dienst '{dienst_key}' not found in database"
        )

    # Get customer data
    kunde_data = db.get_kunde_by_id_and_dienst(
        kunden_id=kundenguid,
        saas_dienst_id=UUID(saas_dienst_data["id"])
    )

    if not kunde_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {kundenguid} not found for dienst {dienst_key}"
        )

    return WizardStartResponse(
        kunde=Kunde(**kunde_data),
        saas_dienst=SaaSDienst(**saas_dienst_data)
    )
