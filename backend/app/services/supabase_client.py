"""
Supabase Client Service

Provides database access using the Supabase Python client.
"""

from functools import lru_cache
from typing import Optional
from uuid import UUID

from supabase import create_client, Client

from app.core.config import get_settings


@lru_cache
def get_supabase_client() -> Client:
    """
    Get cached Supabase client instance.

    Returns:
        Supabase Client
    """
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_key)


class SupabaseService:
    """Service for database operations"""

    def __init__(self):
        self.client = get_supabase_client()

    # ========================================================================
    # SaaS Dienste
    # ========================================================================

    def get_saas_dienst_by_key(self, dienst_key: str) -> Optional[dict]:
        """Get SaaS dienst by key"""
        response = self.client.table("saas_dienste").select("*").eq("dienst_key", dienst_key).execute()
        return response.data[0] if response.data else None

    def get_saas_dienst_by_id(self, dienst_id: UUID) -> Optional[dict]:
        """Get SaaS dienst by ID"""
        response = self.client.table("saas_dienste").select("*").eq("id", str(dienst_id)).execute()
        return response.data[0] if response.data else None

    # ========================================================================
    # Kunden
    # ========================================================================

    def get_kunde_by_id_and_dienst(self, kunden_id: UUID, saas_dienst_id: UUID) -> Optional[dict]:
        """Get customer by ID and service"""
        response = (
            self.client.table("kunden")
            .select("*")
            .eq("id", str(kunden_id))
            .eq("saas_dienst_id", str(saas_dienst_id))
            .execute()
        )
        return response.data[0] if response.data else None

    def get_kunde_by_id(self, kunden_id: UUID) -> Optional[dict]:
        """Get customer by ID (any service)"""
        response = self.client.table("kunden").select("*").eq("id", str(kunden_id)).execute()
        return response.data[0] if response.data else None

    def create_kunde(self, kunde_data: dict) -> dict:
        """Create new customer"""
        response = self.client.table("kunden").insert(kunde_data).execute()
        return response.data[0]

    # ========================================================================
    # Domain TLDs
    # ========================================================================

    def get_all_active_tlds(self) -> list[dict]:
        """Get all active TLDs sorted by priority"""
        response = (
            self.client.table("domains_tld")
            .select("*")
            .eq("aktiv", True)
            .order("prio", desc=True)
            .order("sortierung", desc=False)
            .execute()
        )
        return response.data

    def get_tld_by_name(self, tld: str) -> Optional[dict]:
        """Get TLD by name"""
        response = self.client.table("domains_tld").select("*").eq("tld", tld).execute()
        return response.data[0] if response.data else None

    def get_tlds_for_country(self, land: str, limit: int = 10) -> list[dict]:
        """Get recommended TLDs for a specific country"""
        # For POC: Simple logic - return top TLDs
        # Future: More sophisticated country-specific logic
        response = (
            self.client.table("domains_tld")
            .select("*")
            .eq("aktiv", True)
            .order("prio", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data

    # ========================================================================
    # Domain Registrierungen
    # ========================================================================

    def create_domain_registrierung(self, registrierung_data: dict) -> dict:
        """Create domain registration record"""
        response = self.client.table("domain_registrierung").insert(registrierung_data).execute()
        return response.data[0]

    def get_domain_registrierung_by_id(self, registrierung_id: UUID) -> Optional[dict]:
        """Get domain registration by ID"""
        response = (
            self.client.table("domain_registrierung")
            .select("*")
            .eq("id", str(registrierung_id))
            .execute()
        )
        return response.data[0] if response.data else None

    def get_registrierungen_by_kunde(self, kunden_id: UUID) -> list[dict]:
        """Get all registrations for a customer"""
        response = (
            self.client.table("domain_registrierung")
            .select("*")
            .eq("kunden_id", str(kunden_id))
            .order("erstellt_am", desc=True)
            .execute()
        )
        return response.data

    def update_registrierung_status(
        self,
        registrierung_id: UUID,
        status: str,
        inwx_response: Optional[dict] = None
    ) -> dict:
        """Update domain registration status"""
        update_data = {"status": status}
        if inwx_response:
            update_data["inwx_response_payload"] = inwx_response

        response = (
            self.client.table("domain_registrierung")
            .update(update_data)
            .eq("id", str(registrierung_id))
            .execute()
        )
        return response.data[0]
