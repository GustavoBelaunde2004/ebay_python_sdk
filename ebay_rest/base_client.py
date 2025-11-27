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

    def __init__(
        self,
        auth_client: OAuth2Client,
        base_url: str,
        sandbox: bool = False,
        user_access_token: Optional[str] = None,
    ):
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
        self.timeout = 30  # Default timeout in seconds
        self.user_access_token = user_access_token

    def _get_headers(self) -> dict[str, str]:
        """
        Get headers for API requests, including authorization.

        Returns:
            Dictionary of HTTP headers
        """
        # Use override token for Sell APIs if provided
        if self.user_access_token:
            headers = {"Authorization": f"Bearer {self.user_access_token}"}
        else:
            headers = self.auth_client.build_auth_header()

        # Add standard headers
        headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

        return headers

    def set_user_access_token(self, token: Optional[str]) -> None:
        """
        Override the access token used for requests (e.g., Sell API user token).

        Args:
            token: Bearer token string or None to revert to client credentials.
        """
        self.user_access_token = token

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
        status_code = response.status_code

        # Try to parse JSON response
        response_data = None
        try:
            if response.text:
                response_data = response.json()
        except Exception:
            # If JSON parsing fails, use text response
            response_data = {"error": response.text} if response.text else {}

        # Map status codes to appropriate exceptions
        if status_code == 401:
            error_msg = "Authentication failed. Check your credentials."
            if response_data and "error_description" in response_data:
                error_msg = response_data["error_description"]
            raise AuthError(error_msg, status_code=status_code, response_data=response_data)

        elif status_code == 404:
            error_msg = "Resource not found"
            if response_data and "errors" in response_data:
                # eBay API often returns errors array
                errors = response_data["errors"]
                if errors and isinstance(errors, list) and len(errors) > 0:
                    error_msg = errors[0].get("message", error_msg)
            raise NotFoundError(error_msg, status_code=status_code, response_data=response_data)

        elif status_code == 429:
            retry_after = None
            if "Retry-After" in response.headers:
                try:
                    retry_after = int(response.headers["Retry-After"])
                except ValueError:
                    pass
            error_msg = "Rate limit exceeded"
            if response_data and "errors" in response_data:
                errors = response_data["errors"]
                if errors and isinstance(errors, list) and len(errors) > 0:
                    error_msg = errors[0].get("message", error_msg)
            raise RateLimitExceeded(error_msg, retry_after=retry_after, status_code=status_code, response_data=response_data)

        elif status_code in (400, 422):
            error_msg = "Request validation failed"
            if response_data and "errors" in response_data:
                errors = response_data["errors"]
                if errors and isinstance(errors, list) and len(errors) > 0:
                    error_msg = errors[0].get("message", error_msg)
            raise ValidationError(error_msg, status_code=status_code, response_data=response_data)

        elif 500 <= status_code < 600:
            error_msg = "eBay API server error"
            if response_data and "errors" in response_data:
                errors = response_data["errors"]
                if errors and isinstance(errors, list) and len(errors) > 0:
                    error_msg = errors[0].get("message", error_msg)
            raise ServerError(error_msg, status_code=status_code, response_data=response_data)

        elif not (200 <= status_code < 300):
            # Other 4xx or unexpected status codes
            error_msg = f"API request failed with status {status_code}"
            if response_data and "errors" in response_data:
                errors = response_data["errors"]
                if errors and isinstance(errors, list) and len(errors) > 0:
                    error_msg = errors[0].get("message", error_msg)
            raise EbayAPIError(error_msg, status_code=status_code, response_data=response_data)

        # Success - return parsed JSON or empty dict
        return response_data if response_data is not None else {}

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
        # Build full URL
        url = f"{self.base_url}/{path.lstrip('/')}"

        # Get headers
        headers = self._get_headers()

        try:
            # Make GET request
            response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)

            # Handle response and return data
            return self._handle_response(response)

        except requests.RequestException as e:
            raise EbayAPIError(f"Network error during GET request: {str(e)}")

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
        # Build full URL
        url = f"{self.base_url}/{path.lstrip('/')}"

        # Get headers
        headers = self._get_headers()

        try:
            # Make POST request
            response = self.session.post(url, json=json, headers=headers, timeout=self.timeout)

            # Handle response and return data
            return self._handle_response(response)

        except requests.RequestException as e:
            raise EbayAPIError(f"Network error during POST request: {str(e)}")

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
        # Build full URL
        url = f"{self.base_url}/{path.lstrip('/')}"

        # Get headers
        headers = self._get_headers()

        try:
            # Make PUT request
            response = self.session.put(url, json=json, headers=headers, timeout=self.timeout)

            # Handle response and return data
            return self._handle_response(response)

        except requests.RequestException as e:
            raise EbayAPIError(f"Network error during PUT request: {str(e)}")

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
        # Build full URL
        url = f"{self.base_url}/{path.lstrip('/')}"

        # Get headers
        headers = self._get_headers()

        try:
            # Make DELETE request
            response = self.session.delete(url, params=params, headers=headers, timeout=self.timeout)

            # Handle response and return data
            return self._handle_response(response)

        except requests.RequestException as e:
            raise EbayAPIError(f"Network error during DELETE request: {str(e)}")

