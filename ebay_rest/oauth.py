"""OAuth Authorization Code flow helpers for eBay Sell APIs."""

from __future__ import annotations

import base64
import urllib.parse
from typing import Iterable

import requests


AUTH_URLS = {
    "sandbox": "https://auth.sandbox.ebay.com/oauth2/authorize",
    "production": "https://auth.ebay.com/oauth2/authorize",
}

TOKEN_URLS = {
    "sandbox": "https://api.sandbox.ebay.com/identity/v1/oauth2/token",
    "production": "https://api.ebay.com/identity/v1/oauth2/token",
}


def build_authorization_url(
    client_id: str,
    redirect_uri: str,
    scopes: Iterable[str],
    state: str | None = None,
    environment: str = "sandbox",
) -> str:
    """
    Construct the seller consent URL for the Authorization Code flow.

    Args:
        client_id: eBay App ID
        redirect_uri: eBay-registered Redirect URL (RUName). Must already be URL encoded per eBay rules.
        scopes: Iterable of OAuth scopes requested
        state: Optional state parameter echoed back after consent
        environment: "sandbox" or "production"

    Returns:
        Full URL string that the seller should open to grant access.
    """
    if environment not in AUTH_URLS:
        raise ValueError("environment must be 'sandbox' or 'production'")

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
    }
    if state:
        params["state"] = state

    return f"{AUTH_URLS[environment]}?{urllib.parse.urlencode(params)}"


def exchange_authorization_code(
    client_id: str,
    client_secret: str,
    code: str,
    redirect_uri: str,
    environment: str = "sandbox",
) -> dict:
    """
    Exchange an authorization code for access + refresh tokens.

    Args:
        client_id: App ID
        client_secret: Cert ID
        code: Authorization code returned from consent
        redirect_uri: Same redirect URI used during consent (URL encoded)
        environment: "sandbox" or "production"
    """
    return _token_request(
        client_id,
        client_secret,
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        },
        environment,
    )


def refresh_user_token(
    client_id: str,
    client_secret: str,
    refresh_token: str,
    scopes: Iterable[str],
    environment: str = "sandbox",
) -> dict:
    """
    Refresh a user access token using the stored refresh token.

    Args:
        client_id: App ID
        client_secret: Cert ID
        refresh_token: Refresh token obtained from previous exchange
        scopes: Scopes to request for the refreshed token
        environment: "sandbox" or "production"
    """
    return _token_request(
        client_id,
        client_secret,
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "scope": " ".join(scopes),
        },
        environment,
    )


def _token_request(
    client_id: str,
    client_secret: str,
    data: dict,
    environment: str,
) -> dict:
    if environment not in TOKEN_URLS:
        raise ValueError("environment must be 'sandbox' or 'production'")

    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode("utf-8")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_header}",
    }

    response = requests.post(TOKEN_URLS[environment], headers=headers, data=data, timeout=30)
    response.raise_for_status()
    return response.json()

