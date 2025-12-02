"""Integration tests for OAuth2 authentication."""

import time

import pytest

from ebay_rest.auth import OAuth2Client


@pytest.mark.integration
@pytest.mark.requires_credentials
class TestAuthIntegration:
    """Integration tests for OAuth2 authentication with real API."""

    def test_refresh_token_real_api(self, sandbox_credentials):
        """Test token refresh with real eBay sandbox API."""
        client = OAuth2Client(
            client_id=sandbox_credentials["client_id"],
            client_secret=sandbox_credentials["client_secret"],
            sandbox=True,
        )

        # Initially no token
        assert client.access_token is None
        assert client.is_expired() is True

        # Refresh token
        token = client.refresh_token()

        # Verify token was obtained
        assert token is not None
        assert len(token) > 0
        assert client.access_token == token
        assert client.token_expires_at is not None
        assert client.token_expires_at > time.time()

    def test_get_access_token_auto_refresh(self, sandbox_credentials):
        """Test that get_access_token automatically refreshes when expired."""
        client = OAuth2Client(
            client_id=sandbox_credentials["client_id"],
            client_secret=sandbox_credentials["client_secret"],
            sandbox=True,
        )

        # Get token (should auto-refresh)
        token1 = client.get_access_token()
        assert token1 is not None

        # Get again (should use cached token)
        token2 = client.get_access_token()
        assert token1 == token2

    def test_token_expiration_logic(self, sandbox_credentials):
        """Test token expiration checking logic."""
        client = OAuth2Client(
            client_id=sandbox_credentials["client_id"],
            client_secret=sandbox_credentials["client_secret"],
            sandbox=True,
        )

        # Get a fresh token
        client.refresh_token()

        # Token should not be expired immediately
        assert client.is_expired() is False

        # Manually set expiration to past
        client.token_expires_at = time.time() - 100
        assert client.is_expired() is True

    def test_build_auth_header(self, sandbox_credentials):
        """Test building authentication header with real token."""
        client = OAuth2Client(
            client_id=sandbox_credentials["client_id"],
            client_secret=sandbox_credentials["client_secret"],
            sandbox=True,
        )

        # Get token and build header
        client.get_access_token()
        headers = client.build_auth_header()

        # Verify header format
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")
        assert len(headers["Authorization"]) > len("Bearer ")

    def test_token_refresh_multiple_times(self, sandbox_credentials):
        """Test refreshing token multiple times."""
        client = OAuth2Client(
            client_id=sandbox_credentials["client_id"],
            client_secret=sandbox_credentials["client_secret"],
            sandbox=True,
        )

        # Refresh multiple times
        token1 = client.refresh_token()
        time.sleep(1)  # Small delay
        token2 = client.refresh_token()

        # Tokens might be the same or different (depending on eBay's token caching)
        # But both should be valid
        assert token1 is not None
        assert token2 is not None
        assert len(token1) > 0
        assert len(token2) > 0

