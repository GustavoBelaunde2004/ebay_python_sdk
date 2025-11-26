"""Account API client for accessing account information."""

from ebay_rest.base_client import BaseClient


class AccountClient:
    """
    Client for eBay Account API.

    Provides methods to access account-related information and settings.
    """

    def __init__(self, base_client: BaseClient, sandbox: bool = False):
        """
        Initialize Account API client.

        Args:
            base_client: BaseClient instance for making HTTP requests
            sandbox: Whether to use sandbox environment
        """
        self.base_client = base_client
        self.sandbox = sandbox

    def get_account_profile(self) -> dict:
        """
        Get account profile information.

        Returns:
            Dictionary containing account profile

        Raises:
            EbayAPIError: If the request fails

        TODO:
            - Implement API endpoint call
            - Parse and return AccountProfile model
        """
        # TODO: Build endpoint path: /sell/account/v1/privilege
        # TODO: Call base_client.get() with path
        # TODO: Parse response and return AccountProfile model
        raise NotImplementedError("get_account_profile not yet implemented")

