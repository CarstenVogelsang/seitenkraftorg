"""
INWX API Service

Handles communication with INWX domain registrar API.
Uses JSON-RPC over HTTPS.
"""

import httpx
from typing import Optional

from app.core.config import get_settings


class INWXService:
    """Service for INWX API communication"""

    def __init__(self):
        self.settings = get_settings()
        self.api_url = self.settings.inwx_api_url
        self.username = self.settings.inwx_username
        self.password = self.settings.inwx_password
        self._session_id: Optional[str] = None

    async def _call_api(self, method: str, params: Optional[dict] = None) -> dict:
        """
        Call INWX JSON-RPC API

        Args:
            method: API method name (e.g., "account.login", "domain.check")
            params: Method parameters

        Returns:
            API response dict

        Raises:
            httpx.HTTPError: On network errors
            ValueError: On API errors
        """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.api_url, json=payload)
            response.raise_for_status()

            data = response.json()

            if "error" in data:
                raise ValueError(f"INWX API Error: {data['error']}")

            return data.get("result", {})

    async def login(self) -> str:
        """
        Login to INWX API and get session ID

        Returns:
            Session ID

        Raises:
            ValueError: On login failure
        """
        result = await self._call_api(
            "account.login",
            {
                "user": self.username,
                "pass": self.password
            }
        )

        if result.get("code") != 1000:
            raise ValueError(f"INWX login failed: {result.get('msg')}")

        self._session_id = result.get("resData", {}).get("sessid")
        return self._session_id

    async def logout(self):
        """Logout from INWX API"""
        if self._session_id:
            try:
                await self._call_api("account.logout")
            finally:
                self._session_id = None

    async def check_domain(self, domain: str) -> dict:
        """
        Check domain availability

        Args:
            domain: Full domain name (e.g., "example.de")

        Returns:
            Dict with availability info:
            {
                "domain": "example.de",
                "avail": True/False,
                "status": "available" | "registered" | "unknown",
                "price": float (if available)
            }

        Raises:
            ValueError: On API errors
        """
        # Ensure we're logged in
        if not self._session_id:
            await self.login()

        try:
            result = await self._call_api(
                "domain.check",
                {
                    "domain": domain
                }
            )

            if result.get("code") != 1000:
                return {
                    "domain": domain,
                    "avail": False,
                    "status": "error",
                    "error": result.get("msg")
                }

            res_data = result.get("resData", {})
            avail = res_data.get("avail", 0) == 1

            return {
                "domain": domain,
                "avail": avail,
                "status": "available" if avail else "registered",
                "price": res_data.get("price")
            }

        except Exception as e:
            return {
                "domain": domain,
                "avail": False,
                "status": "error",
                "error": str(e)
            }

    async def check_domains_batch(self, domains: list[str]) -> list[dict]:
        """
        Check multiple domains for availability

        Args:
            domains: List of domain names

        Returns:
            List of availability results
        """
        results = []
        for domain in domains:
            result = await self.check_domain(domain)
            results.append(result)

        return results

    async def register_domain(self, domain: str, customer_data: dict) -> dict:
        """
        Register a domain (POC: Fake registration)

        Args:
            domain: Full domain name
            customer_data: Customer contact information

        Returns:
            Registration result

        Note:
            For POC, this returns a fake success response.
            In production, this would call INWX domain.create API.
        """
        # POC: Return fake success
        # Production: Implement actual INWX domain.create call
        return {
            "success": True,
            "domain": domain,
            "status": "pending",
            "message": "POC: Fake domain registration successful",
            "registration_id": f"fake-reg-{domain}"
        }

    async def __aenter__(self):
        """Context manager entry"""
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.logout()
