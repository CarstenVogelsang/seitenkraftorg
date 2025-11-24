"""
Fake Authentication for POC

IMPORTANT: This is a POC implementation only!
For production, replace with proper OAuth2/JWT authentication.
"""

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


def verify_fake_token(x_client_token: str = Header(...)) -> str:
    """
    Verify fake authentication token.

    Args:
        x_client_token: Token from X-Client-Token header

    Returns:
        Token if valid

    Raises:
        HTTPException: 401 if token is invalid
    """
    settings = get_settings()

    if x_client_token != settings.fake_auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return x_client_token


def get_saas_dienst_from_token(token: str) -> str:
    """
    Extract SaaS dienst_key from token.

    POC: Returns hardcoded dienst_key.
    Production: Decode JWT and extract dienst_key from claims.

    Args:
        token: Authentication token

    Returns:
        dienst_key (e.g., "handelshelfer", "handwerker24")
    """
    # POC: Map token to dienst_key
    # In production, this would be extracted from JWT claims
    token_mapping = {
        "token_handelshelfer_dev_123": "handelshelfer",
        "token_handwerker24_dev_456": "handwerker24",
        "dev-token-123": "handelshelfer",  # Default for testing
    }

    return token_mapping.get(token, "handelshelfer")
