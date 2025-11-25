"""Base HTTP client for eBay API requests."""

from typing import Any, Optional

import requests

from ebay_rest.auth import OAuth2Client
from ebay_rest.errors import (
    AuthError,
    EbayAPIError,
    NotFoundError,
    RateLimitExceeded,
    ServerError,
    ValidationError,
)


class BaseClient:
    """
    Base HTTP client for making requests to eBay API.

    Handles authentication, error mapping, and common HTTP operations.
    """

    def __init__(self, auth_client: OAuth2Client, base_url: str, sandbox: bool = False):
        """
        Initialize base client.

        Args:
            auth_client: OAuth2Client instance for authentication
            base_url: Base URL for API requests
            sandbox: Whether to use sandbox environment
        """
        self.auth_client = auth_client
        self.base_url = base_url.rstrip("/")
        self.sandbox = sandbox
        self.session = requests.Session()

        # TODO: Configure session headers, timeouts, retries if needed

    def _get_headers(self) -> dict[str, str]:
        """
        Get headers for API requests, including authorization.

        Returns:
            Dictionary of HTTP headers
        """
        # TODO: Get auth header from auth_client.build_auth_header()
        # TODO: Add Content-Type: application/json if needed
        # TODO: Add Accept header
        # TODO: Return combined headers
        return {}

    def _handle_response(self, response: requests.Response) -> dict[str, Any]:
        """
        Handle API response and map errors appropriately.

        Args:
            response: requests.Response object

        Returns:
            JSON response data as dictionary

        Raises:
            AuthError: For 401 errors
            NotFoundError: For 404 errors
            RateLimitExceeded: For 429 errors
            ServerError: For 5xx errors
            ValidationError: For 400/422 errors
            EbayAPIError: For other API errors
        """
        # TODO: Check status code
        # TODO: Parse JSON response if available
        # TODO: Map status codes to appropriate exceptions:
        #   - 401 -> AuthError
        #   - 404 -> NotFoundError
        #   - 429 -> RateLimitExceeded (extract retry_after if available)
        #   - 400, 422 -> ValidationError
        #   - 5xx -> ServerError
        #   - Other -> EbayAPIError
        # TODO: Return parsed JSON on success
        raise NotImplementedError("Response handling not yet implemented")

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Make a GET request to the API.

        Args:
            path: API endpoint path (relative to base_url)
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            EbayAPIError: If request fails
        """
        # TODO: Build full URL from base_url and path
        # TODO: Get headers using _get_headers()
        # TODO: Make GET request using session
        # TODO: Handle response using _handle_response()
        # TODO: Return response data
        raise NotImplementedError("GET method not yet implemented")

    def post(self, path: str, json: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Make a POST request to the API.

        Args:
            path: API endpoint path (relative to base_url)
            json: JSON payload

        Returns:
            JSON response as dictionary

        Raises:
            EbayAPIError: If request fails
        """
        # TODO: Build full URL from base_url and path
        # TODO: Get headers using _get_headers()
        # TODO: Make POST request using session
        # TODO: Handle response using _handle_response()
        # TODO: Return response data
        raise NotImplementedError("POST method not yet implemented")

    def put(self, path: str, json: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Make a PUT request to the API.

        Args:
            path: API endpoint path (relative to base_url)
            json: JSON payload

        Returns:
            JSON response as dictionary

        Raises:
            EbayAPIError: If request fails
        """
        # TODO: Build full URL from base_url and path
        # TODO: Get headers using _get_headers()
        # TODO: Make PUT request using session
        # TODO: Handle response using _handle_response()
        # TODO: Return response data
        raise NotImplementedError("PUT method not yet implemented")

    def delete(self, path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """
        Make a DELETE request to the API.

        Args:
            path: API endpoint path (relative to base_url)
            params: Query parameters

        Returns:
            JSON response as dictionary (may be empty for successful deletes)

        Raises:
            EbayAPIError: If request fails
        """
        # TODO: Build full URL from base_url and path
        # TODO: Get headers using _get_headers()
        # TODO: Make DELETE request using session
        # TODO: Handle response using _handle_response()
        # TODO: Return response data
        raise NotImplementedError("DELETE method not yet implemented")

