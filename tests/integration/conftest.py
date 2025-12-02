"""Pytest configuration and fixtures for integration tests."""

import os

import pytest
from dotenv import load_dotenv

from ebay_rest import EbayClient

# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def sandbox_credentials():
    """
    Load sandbox credentials from environment variables.

    Skips test if credentials are not available.
    """
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")

    if not client_id or not client_secret:
        pytest.skip("EBAY_CLIENT_ID and EBAY_CLIENT_SECRET required for integration tests")

    return {
        "client_id": client_id,
        "client_secret": client_secret,
    }


@pytest.fixture
def sandbox_client(sandbox_credentials):
    """
    Create a real EbayClient instance configured for sandbox.

    Uses credentials from environment variables.
    """
    return EbayClient(
        client_id=sandbox_credentials["client_id"],
        client_secret=sandbox_credentials["client_secret"],
        sandbox=True,
    )


@pytest.fixture
def user_access_token():
    """
    Get user access token from environment variables.

    Returns None if not available (tests can skip if needed).
    """
    return os.getenv("EBAY_USER_ACCESS_TOKEN")


@pytest.fixture
def sandbox_client_with_user_token(sandbox_credentials, user_access_token):
    """
    Create a real EbayClient instance with user access token.

    Skips test if user token is not available.
    """
    if not user_access_token:
        pytest.skip("EBAY_USER_ACCESS_TOKEN required for this test")

    client = EbayClient(
        client_id=sandbox_credentials["client_id"],
        client_secret=sandbox_credentials["client_secret"],
        sandbox=True,
        user_access_token=user_access_token,
    )
    return client

