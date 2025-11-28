"""Tests for OAuth2 authentication client."""

import time
from unittest.mock import MagicMock, patch

import pytest

from ebay_rest.auth import OAuth2Client
from ebay_rest.errors import AuthError


class TestOAuth2Client:
    """Test suite for OAuth2Client."""

    def test_init(self, test_client_id: str, test_client_secret: str, sandbox_flag: bool):
        """Test OAuth2Client initialization."""
        client = OAuth2Client(
            client_id=test_client_id,
            client_secret=test_client_secret,
            sandbox=sandbox_flag,
        )
        assert client.client_id == test_client_id
        assert client.client_secret == test_client_secret
        assert client.sandbox == sandbox_flag
        assert client.access_token is None
        assert client.token_expires_at is None
        if sandbox_flag:
            assert "sandbox" in client.oauth_url
        else:
            assert "api.ebay.com" in client.oauth_url

    @patch("ebay_rest.auth.requests.post")
    def test_refresh_token_success(self, mock_post: MagicMock, test_client_id: str, test_client_secret: str):
        """Test successful token refresh."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token_123",
            "expires_in": 7200,
            "token_type": "Bearer",
        }
        mock_post.return_value = mock_response

        client = OAuth2Client(client_id=test_client_id, client_secret=test_client_secret, sandbox=True)
        token = client.refresh_token()

        assert token == "test_token_123"
        assert client.access_token == "test_token_123"
        assert client.token_expires_at is not None
        assert client.token_expires_at > time.time()
        mock_post.assert_called_once()

    @patch("ebay_rest.auth.requests.post")
    def test_refresh_token_with_error_response(self, mock_post: MagicMock, test_client_id: str, test_client_secret: str):
        """Test token refresh with error response."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": "invalid_client",
            "error_description": "Client authentication failed",
        }
        mock_post.return_value = mock_response

        client = OAuth2Client(client_id=test_client_id, client_secret=test_client_secret, sandbox=True)

        with pytest.raises(AuthError) as exc_info:
            client.refresh_token()

        assert "Client authentication failed" in str(exc_info.value)
        assert exc_info.value.status_code == 401

    @patch("ebay_rest.auth.requests.post")
    def test_get_access_token_refreshes_when_expired(self, mock_post: MagicMock, test_client_id: str, test_client_secret: str):
        """Test that get_access_token refreshes token when expired."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "new_token_456",
            "expires_in": 7200,
        }
        mock_post.return_value = mock_response

        client = OAuth2Client(client_id=test_client_id, client_secret=test_client_secret, sandbox=True)
        token = client.get_access_token()

        assert token == "new_token_456"
        mock_post.assert_called_once()

    @patch("ebay_rest.auth.requests.post")
    def test_get_access_token_uses_cached_token(self, mock_post: MagicMock, test_client_id: str, test_client_secret: str):
        """Test that get_access_token uses cached token when valid."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "cached_token_789",
            "expires_in": 7200,
        }
        mock_post.return_value = mock_response

        client = OAuth2Client(client_id=test_client_id, client_secret=test_client_secret, sandbox=True)
        # First call should fetch token
        token1 = client.get_access_token()
        # Second call should use cached token (not call refresh again)
        token2 = client.get_access_token()

        assert token1 == token2 == "cached_token_789"
        assert mock_post.call_count == 1  # Only called once

    def test_is_expired_no_token(self, test_client_id: str, test_client_secret: str):
        """Test is_expired returns True when no token."""
        client = OAuth2Client(client_id=test_client_id, client_secret=test_client_secret, sandbox=True)
        assert client.is_expired() is True

    def test_is_expired_expired_token(self, test_client_id: str, test_client_secret: str):
        """Test is_expired returns True when token expired."""
        client = OAuth2Client(client_id=test_client_id, client_secret=test_client_secret, sandbox=True)
        client.access_token = "some_token"
        client.token_expires_at = time.time() - 100  # Expired 100 seconds ago
        assert client.is_expired() is True

    def test_is_expired_valid_token(self, test_client_id: str, test_client_secret: str):
        """Test is_expired returns False when token is valid."""
        client = OAuth2Client(client_id=test_client_id, client_secret=test_client_secret, sandbox=True)
        client.access_token = "some_token"
        client.token_expires_at = time.time() + 7200  # Expires in 2 hours
        assert client.is_expired() is False

    def test_is_expired_token_near_expiration(self, test_client_id: str, test_client_secret: str):
        """Test is_expired returns True when token is within buffer window."""
        client = OAuth2Client(client_id=test_client_id, client_secret=test_client_secret, sandbox=True)
        client.access_token = "some_token"
        client.token_expires_at = time.time() + 30  # Expires in 30 seconds (within 60s buffer)
        assert client.is_expired() is True

    @patch("ebay_rest.auth.requests.post")
    def test_build_auth_header(self, mock_post: MagicMock, test_client_id: str, test_client_secret: str):
        """Test build_auth_header returns correct format."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "header_token_abc",
            "expires_in": 7200,
        }
        mock_post.return_value = mock_response

        client = OAuth2Client(client_id=test_client_id, client_secret=test_client_secret, sandbox=True)
        headers = client.build_auth_header()

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer header_token_abc"

    @patch("ebay_rest.auth.requests.post")
    def test_refresh_token_network_error(self, mock_post: MagicMock, test_client_id: str, test_client_secret: str):
        """Test that network errors raise AuthError."""
        import requests

        mock_post.side_effect = requests.RequestException("Connection timeout")

        client = OAuth2Client(client_id=test_client_id, client_secret=test_client_secret, sandbox=True)

        with pytest.raises(AuthError) as exc_info:
            client.refresh_token()

        assert "Network error" in str(exc_info.value)

    @patch("ebay_rest.auth.requests.post")
    def test_refresh_token_missing_access_token(self, mock_post: MagicMock, test_client_id: str, test_client_secret: str):
        """Test that missing access_token in response raises AuthError."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "expires_in": 7200,
            # Missing access_token
        }
        mock_post.return_value = mock_response

        client = OAuth2Client(client_id=test_client_id, client_secret=test_client_secret, sandbox=True)

        with pytest.raises(AuthError) as exc_info:
            client.refresh_token()

        assert "Access token not found" in str(exc_info.value)

