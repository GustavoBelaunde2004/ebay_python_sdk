"""Account API client for accessing account information."""

from ebay_rest.account.models import AccountProfile
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
        Get account privilege/profile information.

        Returns:
            Dictionary containing account profile information.
        """
        endpoint = "/sell/account/v1/privilege"
        response_data = self.base_client.get(endpoint)

        try:
            profile = AccountProfile(**response_data)
            return profile.model_dump()
        except Exception:
            return response_data
