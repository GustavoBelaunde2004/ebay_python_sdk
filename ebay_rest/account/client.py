"""Account API client for accessing account information."""

from ebay_rest.account.models import (
    AccountProfile,
    PaymentPoliciesResponse,
    ReturnPoliciesResponse,
    ShippingPoliciesResponse,
)
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
            return profile.model_dump(by_alias=False, exclude_none=True)
        except Exception:
            return response_data

    def get_account_privileges(self) -> dict:
        """Alias for get_account_profile for clarity."""
        return self.get_account_profile()

    def list_return_policies(self, marketplace_id: str) -> dict:
        """List return policies for a marketplace."""
        endpoint = "/sell/account/v1/return_policy"
        response_data = self.base_client.get(endpoint, params={"marketplace_id": marketplace_id})
        try:
            parsed = ReturnPoliciesResponse(**response_data)
            return parsed.model_dump(by_alias=False, exclude_none=True)
        except Exception:
            return response_data

    def list_payment_policies(self, marketplace_id: str) -> dict:
        """List payment policies for a marketplace."""
        endpoint = "/sell/account/v1/payment_policy"
        response_data = self.base_client.get(endpoint, params={"marketplace_id": marketplace_id})
        try:
            parsed = PaymentPoliciesResponse(**response_data)
            return parsed.model_dump(by_alias=False, exclude_none=True)
        except Exception:
            return response_data

    def list_shipping_policies(self, marketplace_id: str) -> dict:
        """List shipping policies for a marketplace."""
        endpoint = "/sell/account/v1/shipping_policy"
        response_data = self.base_client.get(endpoint, params={"marketplace_id": marketplace_id})
        try:
            parsed = ShippingPoliciesResponse(**response_data)
            return parsed.model_dump(by_alias=False, exclude_none=True)
        except Exception:
            return response_data
