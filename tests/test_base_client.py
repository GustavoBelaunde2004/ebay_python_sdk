"""Tests for Base HTTP client."""

from unittest.mock import MagicMock, patch
import pytest
import requests

from ebay_rest.base_client import BaseClient
from ebay_rest.auth import OAuth2Client
from ebay_rest.errors import (
    AuthError,
    EbayAPIError,
    NotFoundError,
    RateLimitExceeded,
    ServerError,
    ValidationError,
)


class TestBaseClientInit:
    """Test BaseClient initialization."""

    def test_init_with_sandbox_url(self, mock_oauth_client):
        """Test initialization with sandbox URL."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.sandbox.ebay.com",
            sandbox=True,
        )
        assert client.base_url == "https://api.sandbox.ebay.com"
        assert client.sandbox is True
        assert client.timeout == 30
        assert client.session is not None
        assert client.auth_client == mock_oauth_client

    def test_init_with_production_url(self, mock_oauth_client):
        """Test initialization with production URL."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
            sandbox=False,
        )
        assert client.base_url == "https://api.ebay.com"
        assert client.sandbox is False

    def test_init_strips_trailing_slash_from_base_url(self, mock_oauth_client):
        """Test that trailing slashes are stripped from base_url."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com/",
            sandbox=False,
        )
        assert client.base_url == "https://api.ebay.com"

    def test_init_sets_default_timeout(self, mock_oauth_client):
        """Test that default timeout is 30 seconds."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
            sandbox=False,
        )
        assert client.timeout == 30

    def test_init_creates_session(self, mock_oauth_client):
        """Test that a requests.Session is created."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
            sandbox=False,
        )
        assert client.session is not None
        assert isinstance(client.session, requests.Session)

    def test_init_with_user_access_token(self, mock_oauth_client):
        """Test initialization with user access token."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
            sandbox=False,
            user_access_token="user_token_123",
        )
        assert client.user_access_token == "user_token_123"

    def test_init_without_user_access_token(self, mock_oauth_client):
        """Test initialization without user access token."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
            sandbox=False,
        )
        assert client.user_access_token is None


class TestBaseClientHeaders:
    """Test header generation."""

    def test_get_headers_with_user_token(self, mock_oauth_client):
        """Test headers use user token when provided."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
            user_access_token="user_token_123",
        )
        headers = client._get_headers()

        assert headers["Authorization"] == "Bearer user_token_123"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"

    def test_get_headers_without_user_token_uses_auth_client(self, mock_oauth_client):
        """Test headers fall back to auth_client when no user token."""
        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer auth_client_token"}
        )
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        headers = client._get_headers()

        assert headers["Authorization"] == "Bearer auth_client_token"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        mock_oauth_client.build_auth_header.assert_called_once()

    def test_get_headers_includes_content_type(self, mock_oauth_client):
        """Test that Content-Type header is always included."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
            user_access_token="test_token",
        )
        headers = client._get_headers()
        assert headers["Content-Type"] == "application/json"

    def test_get_headers_includes_accept(self, mock_oauth_client):
        """Test that Accept header is always included."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
            user_access_token="test_token",
        )
        headers = client._get_headers()
        assert headers["Accept"] == "application/json"

    def test_get_headers_user_token_overrides_auth_client(self, mock_oauth_client):
        """Test that user token takes precedence over auth_client token."""
        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer auth_client_token"}
        )
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
            user_access_token="user_token_override",
        )
        headers = client._get_headers()

        assert headers["Authorization"] == "Bearer user_token_override"
        # Should not call auth_client when user token is present
        mock_oauth_client.build_auth_header.assert_not_called()


class TestBaseClientUserToken:
    """Test user token management."""

    def test_set_user_access_token(self, mock_oauth_client):
        """Test setting user access token."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        assert client.user_access_token is None

        client.set_user_access_token("new_token_123")
        assert client.user_access_token == "new_token_123"

    def test_set_user_access_token_to_none(self, mock_oauth_client):
        """Test clearing user access token."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
            user_access_token="existing_token",
        )
        assert client.user_access_token == "existing_token"

        client.set_user_access_token(None)
        assert client.user_access_token is None

    def test_set_user_access_token_updates_headers(self, mock_oauth_client):
        """Test that setting token affects subsequent header generation."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )

        # Initially uses auth_client
        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer auth_token"}
        )
        headers1 = client._get_headers()
        assert headers1["Authorization"] == "Bearer auth_token"

        # After setting user token, should use it
        client.set_user_access_token("user_token_456")
        headers2 = client._get_headers()
        assert headers2["Authorization"] == "Bearer user_token_456"


class TestBaseClientHandleResponse:
    """Test response handling and error mapping."""

    def test_handle_response_success_200(self, mock_oauth_client):
        """Test successful 200 response."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}

        result = client._handle_response(mock_response)
        assert result == {"data": "test"}

    def test_handle_response_success_201(self, mock_oauth_client):
        """Test successful 201 response."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.text = '{"id": "123"}'
        mock_response.json.return_value = {"id": "123"}

        result = client._handle_response(mock_response)
        assert result == {"id": "123"}

    def test_handle_response_success_empty_body(self, mock_oauth_client):
        """Test successful response with empty body."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_response.json.side_effect = ValueError("No JSON")

        result = client._handle_response(mock_response)
        assert result == {}

    def test_handle_response_success_non_json_body(self, mock_oauth_client):
        """Test successful response with non-JSON body."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "plain text"
        mock_response.json.side_effect = ValueError("Not JSON")

        result = client._handle_response(mock_response)
        assert result == {"error": "plain text"}

    def test_handle_response_401_auth_error(self, mock_oauth_client):
        """Test 401 error raises AuthError."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = '{"error": "invalid_token"}'
        mock_response.json.return_value = {"error": "invalid_token"}

        with pytest.raises(AuthError) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 401
        assert "Authentication failed" in str(exc_info.value)

    def test_handle_response_401_with_error_description(self, mock_oauth_client):
        """Test 401 error with error_description."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = '{"error_description": "Token expired"}'
        mock_response.json.return_value = {"error_description": "Token expired"}

        with pytest.raises(AuthError) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 401
        assert "Token expired" in str(exc_info.value)

    def test_handle_response_404_not_found(self, mock_oauth_client):
        """Test 404 error raises NotFoundError."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = '{"error": "not found"}'
        mock_response.json.return_value = {"error": "not found"}

        with pytest.raises(NotFoundError) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 404
        assert "Resource not found" in str(exc_info.value)

    def test_handle_response_404_with_errors_array(self, mock_oauth_client):
        """Test 404 error with errors array."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = '{"errors": [{"message": "Item not found"}]}'
        mock_response.json.return_value = {"errors": [{"message": "Item not found"}]}

        with pytest.raises(NotFoundError) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 404
        assert "Item not found" in str(exc_info.value)

    def test_handle_response_429_rate_limit(self, mock_oauth_client):
        """Test 429 error raises RateLimitExceeded."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = '{"error": "rate_limit"}'
        mock_response.json.return_value = {"error": "rate_limit"}
        mock_response.headers = {}

        with pytest.raises(RateLimitExceeded) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in str(exc_info.value)

    def test_handle_response_429_with_retry_after_header(self, mock_oauth_client):
        """Test 429 error with Retry-After header."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = '{"error": "rate_limit"}'
        mock_response.json.return_value = {"error": "rate_limit"}
        mock_response.headers = {"Retry-After": "60"}

        with pytest.raises(RateLimitExceeded) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60

    def test_handle_response_429_with_invalid_retry_after(self, mock_oauth_client):
        """Test 429 error with invalid Retry-After header."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = '{"error": "rate_limit"}'
        mock_response.json.return_value = {"error": "rate_limit"}
        mock_response.headers = {"Retry-After": "invalid"}

        with pytest.raises(RateLimitExceeded) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after is None

    def test_handle_response_400_validation_error(self, mock_oauth_client):
        """Test 400 error raises ValidationError."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = '{"error": "validation"}'
        mock_response.json.return_value = {"error": "validation"}

        with pytest.raises(ValidationError) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 400
        assert "Request validation failed" in str(exc_info.value)

    def test_handle_response_422_validation_error(self, mock_oauth_client):
        """Test 422 error raises ValidationError."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.text = '{"error": "unprocessable"}'
        mock_response.json.return_value = {"error": "unprocessable"}

        with pytest.raises(ValidationError) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 422

    def test_handle_response_validation_with_errors_array(self, mock_oauth_client):
        """Test validation error with errors array."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = '{"errors": [{"message": "Invalid field"}]}'
        mock_response.json.return_value = {"errors": [{"message": "Invalid field"}]}

        with pytest.raises(ValidationError) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 400
        assert "Invalid field" in str(exc_info.value)

    def test_handle_response_500_server_error(self, mock_oauth_client):
        """Test 500 error raises ServerError."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = '{"error": "server_error"}'
        mock_response.json.return_value = {"error": "server_error"}

        with pytest.raises(ServerError) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 500
        assert "server error" in str(exc_info.value).lower()

    def test_handle_response_502_server_error(self, mock_oauth_client):
        """Test 502 error raises ServerError."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 502
        mock_response.text = '{"error": "bad_gateway"}'
        mock_response.json.return_value = {"error": "bad_gateway"}

        with pytest.raises(ServerError) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 502

    def test_handle_response_503_server_error(self, mock_oauth_client):
        """Test 503 error raises ServerError."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.text = '{"error": "service_unavailable"}'
        mock_response.json.return_value = {"error": "service_unavailable"}

        with pytest.raises(ServerError) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 503

    def test_handle_response_403_forbidden(self, mock_oauth_client):
        """Test 403 error raises EbayAPIError."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = '{"error": "forbidden"}'
        mock_response.json.return_value = {"error": "forbidden"}

        with pytest.raises(EbayAPIError) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 403

    def test_handle_response_418_teapot(self, mock_oauth_client):
        """Test other 4xx error raises EbayAPIError."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 418
        mock_response.text = '{"error": "teapot"}'
        mock_response.json.return_value = {"error": "teapot"}

        with pytest.raises(EbayAPIError) as exc_info:
            client._handle_response(mock_response)

        assert exc_info.value.status_code == 418

    def test_handle_response_json_parse_error(self, mock_oauth_client):
        """Test handling of JSON parse errors."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "invalid json {"
        mock_response.json.side_effect = ValueError("Invalid JSON")

        result = client._handle_response(mock_response)
        assert result == {"error": "invalid json {"}

    def test_handle_response_empty_text(self, mock_oauth_client):
        """Test handling of empty response text."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = ""
        mock_response.json.side_effect = ValueError("No JSON")

        result = client._handle_response(mock_response)
        assert result == {}

    def test_handle_response_malformed_errors_array(self, mock_oauth_client):
        """Test handling of malformed errors array."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = '{"errors": "not an array"}'
        mock_response.json.return_value = {"errors": "not an array"}

        with pytest.raises(NotFoundError) as exc_info:
            client._handle_response(mock_response)

        # Should fall back to default message
        assert exc_info.value.status_code == 404
        assert "Resource not found" in str(exc_info.value)

    def test_handle_response_empty_errors_array(self, mock_oauth_client):
        """Test handling of empty errors array."""
        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = '{"errors": []}'
        mock_response.json.return_value = {"errors": []}

        with pytest.raises(NotFoundError) as exc_info:
            client._handle_response(mock_response)

        # Should fall back to default message
        assert exc_info.value.status_code == 404


class TestBaseClientGet:
    """Test GET method."""

    @patch("ebay_rest.base_client.requests.Session")
    def test_get_success(self, mock_session_class, mock_oauth_client):
        """Test successful GET request."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"data": "test"}'
        mock_response.json.return_value = {"data": "test"}
        mock_session.get.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        result = client.get("/test/path")

        assert result == {"data": "test"}
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert call_args[0][0] == "https://api.ebay.com/test/path"
        assert call_args[1]["timeout"] == 30

    @patch("ebay_rest.base_client.requests.Session")
    def test_get_with_params(self, mock_session_class, mock_oauth_client):
        """Test GET request with query parameters."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"items": []}'
        mock_response.json.return_value = {"items": []}
        mock_session.get.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        result = client.get("/test/path", params={"limit": 10, "offset": 0})

        assert result == {"items": []}
        call_args = mock_session.get.call_args
        assert call_args[1]["params"] == {"limit": 10, "offset": 0}

    @patch("ebay_rest.base_client.requests.Session")
    def test_get_path_normalization(self, mock_session_class, mock_oauth_client):
        """Test path normalization removes leading slash."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = {}
        mock_session.get.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        client.get("/test/path")

        call_args = mock_session.get.call_args
        assert call_args[0][0] == "https://api.ebay.com/test/path"

    @patch("ebay_rest.base_client.requests.Session")
    def test_get_path_without_leading_slash(self, mock_session_class, mock_oauth_client):
        """Test path without leading slash."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = {}
        mock_session.get.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        client.get("test/path")

        call_args = mock_session.get.call_args
        assert call_args[0][0] == "https://api.ebay.com/test/path"

    @patch("ebay_rest.base_client.requests.Session")
    def test_get_network_error(self, mock_session_class, mock_oauth_client):
        """Test GET request with network error."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.get.side_effect = requests.RequestException("Connection timeout")

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )

        with pytest.raises(EbayAPIError) as exc_info:
            client.get("/test/path")

        assert "Network error during GET request" in str(exc_info.value)

    @patch("ebay_rest.base_client.requests.Session")
    def test_get_calls_session_with_timeout(self, mock_session_class, mock_oauth_client):
        """Test that GET uses timeout."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = {}
        mock_session.get.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        client.get("/test/path")

        call_args = mock_session.get.call_args
        assert call_args[1]["timeout"] == 30

    @patch("ebay_rest.base_client.requests.Session")
    def test_get_passes_correct_headers(self, mock_session_class, mock_oauth_client):
        """Test that GET passes correct headers."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = {}
        mock_session.get.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer auth_token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        client.get("/test/path")

        call_args = mock_session.get.call_args
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer auth_token"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"


class TestBaseClientPost:
    """Test POST method."""

    @patch("ebay_rest.base_client.requests.Session")
    def test_post_success(self, mock_session_class, mock_oauth_client):
        """Test successful POST request."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.text = '{"id": "123"}'
        mock_response.json.return_value = {"id": "123"}
        mock_session.post.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        result = client.post("/test/path", json={"name": "test"})

        assert result == {"id": "123"}
        call_args = mock_session.post.call_args
        assert call_args[0][0] == "https://api.ebay.com/test/path"
        assert call_args[1]["json"] == {"name": "test"}

    @patch("ebay_rest.base_client.requests.Session")
    def test_post_with_empty_json(self, mock_session_class, mock_oauth_client):
        """Test POST request with empty JSON."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = {}
        mock_session.post.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        result = client.post("/test/path", json=None)

        assert result == {}
        call_args = mock_session.post.call_args
        assert call_args[1]["json"] is None

    @patch("ebay_rest.base_client.requests.Session")
    def test_post_path_normalization(self, mock_session_class, mock_oauth_client):
        """Test POST path normalization."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = {}
        mock_session.post.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        client.post("/test/path", json={})

        call_args = mock_session.post.call_args
        assert call_args[0][0] == "https://api.ebay.com/test/path"

    @patch("ebay_rest.base_client.requests.Session")
    def test_post_network_error(self, mock_session_class, mock_oauth_client):
        """Test POST request with network error."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.post.side_effect = requests.RequestException("Connection timeout")

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )

        with pytest.raises(EbayAPIError) as exc_info:
            client.post("/test/path", json={})

        assert "Network error during POST request" in str(exc_info.value)

    @patch("ebay_rest.base_client.requests.Session")
    def test_post_calls_session_with_timeout(self, mock_session_class, mock_oauth_client):
        """Test that POST uses timeout."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = {}
        mock_session.post.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        client.post("/test/path", json={})

        call_args = mock_session.post.call_args
        assert call_args[1]["timeout"] == 30

    @patch("ebay_rest.base_client.requests.Session")
    def test_post_passes_correct_headers(self, mock_session_class, mock_oauth_client):
        """Test that POST passes correct headers."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = {}
        mock_session.post.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer auth_token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        client.post("/test/path", json={})

        call_args = mock_session.post.call_args
        headers = call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer auth_token"
        assert headers["Content-Type"] == "application/json"


class TestBaseClientPut:
    """Test PUT method."""

    @patch("ebay_rest.base_client.requests.Session")
    def test_put_success(self, mock_session_class, mock_oauth_client):
        """Test successful PUT request."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"updated": true}'
        mock_response.json.return_value = {"updated": True}
        mock_session.put.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        result = client.put("/test/path", json={"name": "updated"})

        assert result == {"updated": True}
        call_args = mock_session.put.call_args
        assert call_args[1]["json"] == {"name": "updated"}

    @patch("ebay_rest.base_client.requests.Session")
    def test_put_network_error(self, mock_session_class, mock_oauth_client):
        """Test PUT request with network error."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.put.side_effect = requests.RequestException("Connection timeout")

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )

        with pytest.raises(EbayAPIError) as exc_info:
            client.put("/test/path", json={})

        assert "Network error during PUT request" in str(exc_info.value)

    @patch("ebay_rest.base_client.requests.Session")
    def test_put_calls_session_with_timeout(self, mock_session_class, mock_oauth_client):
        """Test that PUT uses timeout."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{}'
        mock_response.json.return_value = {}
        mock_session.put.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        client.put("/test/path", json={})

        call_args = mock_session.put.call_args
        assert call_args[1]["timeout"] == 30


class TestBaseClientDelete:
    """Test DELETE method."""

    @patch("ebay_rest.base_client.requests.Session")
    def test_delete_success(self, mock_session_class, mock_oauth_client):
        """Test successful DELETE request."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_response.json.side_effect = ValueError("No JSON")
        mock_session.delete.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        result = client.delete("/test/path")

        assert result == {}
        call_args = mock_session.delete.call_args
        assert call_args[0][0] == "https://api.ebay.com/test/path"

    @patch("ebay_rest.base_client.requests.Session")
    def test_delete_with_params(self, mock_session_class, mock_oauth_client):
        """Test DELETE request with query parameters."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.text = ""
        mock_response.json.side_effect = ValueError("No JSON")
        mock_session.delete.return_value = mock_response

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )
        result = client.delete("/test/path", params={"force": True})

        assert result == {}
        call_args = mock_session.delete.call_args
        assert call_args[1]["params"] == {"force": True}

    @patch("ebay_rest.base_client.requests.Session")
    def test_delete_network_error(self, mock_session_class, mock_oauth_client):
        """Test DELETE request with network error."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.delete.side_effect = requests.RequestException("Connection timeout")

        mock_oauth_client.build_auth_header = MagicMock(
            return_value={"Authorization": "Bearer token"}
        )

        client = BaseClient(
            auth_client=mock_oauth_client,
            base_url="https://api.ebay.com",
        )

        with pytest.raises(EbayAPIError) as exc_info:
            client.delete("/test/path")

        assert "Network error during DELETE request" in str(exc_info.value)

