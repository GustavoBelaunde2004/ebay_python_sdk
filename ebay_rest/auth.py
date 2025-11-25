"""OAuth2 authentication client for eBay API."""

from typing import Optional


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

        # TODO: Set base OAuth URL based on sandbox flag
        # Production: https://api.ebay.com/identity/v1/oauth2/token
        # Sandbox: https://api.sandbox.ebay.com/identity/v1/oauth2/token

    def get_access_token(self) -> str:
        """
        Get a valid access token, refreshing if necessary.

        Returns:
            Valid access token string

        Raises:
            AuthError: If token retrieval fails
        """
        # TODO: Check if token is expired using is_expired()
        # TODO: If expired or missing, fetch new token
        # TODO: Make POST request to OAuth token endpoint
        # TODO: Store token and expiration time
        # TODO: Return access token
        raise NotImplementedError("Token retrieval not yet implemented")

    def refresh_token(self) -> str:
        """
        Force refresh the access token.

        Returns:
            New access token string

        Raises:
            AuthError: If token refresh fails
        """
        # TODO: Make POST request to OAuth token endpoint
        # TODO: Update stored token and expiration
        # TODO: Return new access token
        raise NotImplementedError("Token refresh not yet implemented")

    def is_expired(self) -> bool:
        """
        Check if the current access token is expired or will expire soon.

        Returns:
            True if token is expired or missing, False otherwise
        """
        # TODO: Check if access_token is None
        # TODO: Check if token_expires_at is None
        # TODO: Check if current time is past expiration (with buffer, e.g., 60 seconds)
        # TODO: Return True if expired/missing, False otherwise
        return True

    def build_auth_header(self) -> dict[str, str]:
        """
        Build Authorization header for API requests.

        Returns:
            Dictionary with 'Authorization' header value

        Raises:
            AuthError: If token cannot be obtained
        """
        # TODO: Call get_access_token() to ensure valid token
        # TODO: Return dict with format: {"Authorization": f"Bearer {token}"}
        raise NotImplementedError("Auth header building not yet implemented")

