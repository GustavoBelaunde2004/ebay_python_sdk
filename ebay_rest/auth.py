"""OAuth2 authentication client for eBay API."""

import base64
import time
from typing import Optional

import requests

from ebay_rest.errors import AuthError


class OAuth2Client:
    """
    OAuth2 client for managing eBay API authentication.

    Handles access token retrieval, refresh, and expiration checking.
    """

    def __init__(self, client_id: str, client_secret: str, sandbox: bool = False):
        """
        Initialize OAuth2 client.

        Args:
            client_id: eBay application client ID
            client_secret: eBay application client secret
            sandbox: Whether to use sandbox environment
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.sandbox = sandbox
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[float] = None

        # Set OAuth URL based on sandbox flag
        if sandbox:
            self.oauth_url = "https://api.sandbox.ebay.com/identity/v1/oauth2/token"
        else:
            self.oauth_url = "https://api.ebay.com/identity/v1/oauth2/token"

        # Default scope for eBay API
        self.scope = "https://api.ebay.com/oauth/api_scope"

    def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.

        Returns:
            Valid access token string

        Raises:
            AuthError: If token retrieval fails
        """
        # Check if token is expired or missing
        if self.is_expired():
            # Fetch new token
            self.refresh_token()

        # Return the stored access token (should be valid at this point)
        if not self.access_token:
            raise AuthError("Failed to obtain access token")

        return self.access_token

    def refresh_token(self) -> str:
        """
        Force refresh the access token.

        Returns:
            New access token string

        Raises:
            AuthError: If token refresh fails
        """
        try:
            # Create Basic Auth header
            credentials = f"{self.client_id}:{self.client_secret}"
            encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

            # Build request headers
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {encoded_credentials}",
            }

            # Build request body
            data = {
                "grant_type": "client_credentials",
                "scope": self.scope,
            }

            # Make POST request to OAuth token endpoint
            response = requests.post(self.oauth_url, headers=headers, data=data, timeout=30)

            # Check for HTTP errors
            if response.status_code != 200:
                error_message = f"Token refresh failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if "error_description" in error_data:
                        error_message = error_data["error_description"]
                    elif "error" in error_data:
                        error_message = error_data["error"]
                except Exception:
                    error_message = f"{error_message}: {response.text}"

                raise AuthError(
                    message=error_message,
                    status_code=response.status_code,
                    response_data=response.json() if response.text else None,
                )

            # Parse response
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 7200)  # Default to 2 hours

            # Calculate expiration time
            self.token_expires_at = time.time() + expires_in

            if not self.access_token:
                raise AuthError("Access token not found in response", response_data=token_data)

            return self.access_token

        except requests.RequestException as e:
            raise AuthError(f"Network error during token refresh: {str(e)}")
        except KeyError as e:
            raise AuthError(f"Invalid token response format: missing key {str(e)}")
        except AuthError:
            # Re-raise AuthError as-is
            raise
        except Exception as e:
            raise AuthError(f"Unexpected error during token refresh: {str(e)}")

    def is_expired(self) -> bool:
        """
        Check if the current access token is expired or will expire soon.

        Returns:
            True if token is expired or missing, False otherwise
        """
        # Token is expired if it's missing
        if self.access_token is None:
            return True

        # Token is expired if expiration time is missing
        if self.token_expires_at is None:
            return True

        # Token is expired if current time is past expiration (with 60 second buffer)
        current_time = time.time()
        buffer_seconds = 60
        return current_time >= (self.token_expires_at - buffer_seconds)

    def build_auth_header(self) -> dict[str, str]:
        """
        Build Authorization header for API requests.

        Returns:
            Dictionary with 'Authorization' header value

        Raises:
            AuthError: If token cannot be obtained
        """
        # Get valid access token (will refresh if needed)
        token = self.get_access_token()
        return {"Authorization": f"Bearer {token}"}

