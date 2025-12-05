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
from ebay_rest import oauth


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
        user_refresh_token: Optional[str] = None,
        user_token_scopes: Optional[list[str]] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        """
        Initialize base client.

        Args:
            auth_client: OAuth2Client instance for authentication
            base_url: Base URL for API requests
            sandbox: Whether to use sandbox environment
            user_access_token: Optional user access token for Sell APIs
            user_refresh_token: Optional refresh token for automatic token refresh
            user_token_scopes: Optional list of OAuth scopes for token refresh
            client_id: Optional client ID for token refresh (from auth_client if not provided)
            client_secret: Optional client secret for token refresh (from auth_client if not provided)
        """
        self.auth_client = auth_client
        self.base_url = base_url.rstrip("/")
        self.sandbox = sandbox
        self.session = requests.Session()
        self.timeout = 30  # Default timeout in seconds
        self.user_access_token = user_access_token
        self.user_refresh_token = user_refresh_token
        self.user_token_scopes = user_token_scopes or []
        # Store client credentials for refresh calls
        self.client_id = client_id or auth_client.client_id
        self.client_secret = client_secret or auth_client.client_secret

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

    def set_user_access_token(
        self,
        token: Optional[str],
        refresh_token: Optional[str] = None,
        scopes: Optional[list[str]] = None,
    ) -> None:
        """
        Override the access token used for requests (e.g., Sell API user token).

        Args:
            token: Bearer token string or None to revert to client credentials.
            refresh_token: Optional refresh token for automatic token refresh.
            scopes: Optional list of OAuth scopes for token refresh.
        """
        self.user_access_token = token
        if refresh_token is not None:
            self.user_refresh_token = refresh_token
        if scopes is not None:
            self.user_token_scopes = scopes

    def _refresh_user_token_if_needed(self) -> str:
        """
        Refresh user access token using refresh token if available.

        Returns:
            New access token string

        Raises:
            AuthError: If refresh token is not available or refresh fails
        """
        if not self.user_refresh_token:
            raise AuthError("Refresh token not available for automatic token refresh")

        if not self.user_token_scopes:
            # Default to common Sell API scopes if not provided
            self.user_token_scopes = [
                "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly",
                "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly",
                "https://api.ebay.com/oauth/api_scope/sell.account.readonly",
            ]

        try:
            # Call refresh_user_token
            environment = "sandbox" if self.sandbox else "production"
            token_response = oauth.refresh_user_token(
                client_id=self.client_id,
                client_secret=self.client_secret,
                refresh_token=self.user_refresh_token,
                scopes=self.user_token_scopes,
                environment=environment,
            )

            # Extract new access token
            new_access_token = token_response.get("access_token")
            if not new_access_token:
                raise AuthError("Access token not found in refresh response")

            # Update stored access token
            self.user_access_token = new_access_token

            # Optionally update refresh token if a new one is provided
            new_refresh_token = token_response.get("refresh_token")
            if new_refresh_token:
                self.user_refresh_token = new_refresh_token

            return new_access_token

        except requests.RequestException as e:
            raise AuthError(f"Network error during token refresh: {str(e)}")
        except Exception as e:
            raise AuthError(f"Failed to refresh user token: {str(e)}")

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

        except AuthError as e:
            # If 401 error and using user token with refresh token available, try to refresh
            if (
                e.status_code == 401
                and self.user_access_token
                and self.user_refresh_token
            ):
                try:
                    # Refresh the token
                    self._refresh_user_token_if_needed()
                    # Retry the request with new token
                    headers = self._get_headers()
                    response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
                    return self._handle_response(response)
                except Exception:
                    # If refresh or retry fails, raise original error
                    raise e
            raise

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

        except AuthError as e:
            # If 401 error and using user token with refresh token available, try to refresh
            if (
                e.status_code == 401
                and self.user_access_token
                and self.user_refresh_token
            ):
                try:
                    # Refresh the token
                    self._refresh_user_token_if_needed()
                    # Retry the request with new token
                    headers = self._get_headers()
                    response = self.session.post(url, json=json, headers=headers, timeout=self.timeout)
                    return self._handle_response(response)
                except Exception:
                    # If refresh or retry fails, raise original error
                    raise e
            raise

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

        except AuthError as e:
            # If 401 error and using user token with refresh token available, try to refresh
            if (
                e.status_code == 401
                and self.user_access_token
                and self.user_refresh_token
            ):
                try:
                    # Refresh the token
                    self._refresh_user_token_if_needed()
                    # Retry the request with new token
                    headers = self._get_headers()
                    response = self.session.put(url, json=json, headers=headers, timeout=self.timeout)
                    return self._handle_response(response)
                except Exception:
                    # If refresh or retry fails, raise original error
                    raise e
            raise

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

        except AuthError as e:
            # If 401 error and using user token with refresh token available, try to refresh
            if (
                e.status_code == 401
                and self.user_access_token
                and self.user_refresh_token
            ):
                try:
                    # Refresh the token
                    self._refresh_user_token_if_needed()
                    # Retry the request with new token
                    headers = self._get_headers()
                    response = self.session.delete(url, params=params, headers=headers, timeout=self.timeout)
                    return self._handle_response(response)
                except Exception:
                    # If refresh or retry fails, raise original error
                    raise e
            raise

        except requests.RequestException as e:
            raise EbayAPIError(f"Network error during DELETE request: {str(e)}")

