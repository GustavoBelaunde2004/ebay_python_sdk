"""Tests for Account API client."""

from unittest.mock import MagicMock

import pytest

from ebay_rest.account.client import AccountClient


class TestAccountClient:
    """AccountClient test suite."""

    def test_init(self, mock_base_client, sandbox_flag: bool):
        client = AccountClient(base_client=mock_base_client, sandbox=sandbox_flag)
        assert client.base_client == mock_base_client
        assert client.sandbox is sandbox_flag

    def test_get_account_profile(self, mock_base_client, sandbox_flag: bool):
        mock_base_client.get = MagicMock(
            return_value={
                "accountType": "BUSINESS",
                "privileges": [{"name": "CREATE_LISTING", "status": "ENABLED"}],
            }
        )
        client = AccountClient(base_client=mock_base_client, sandbox=sandbox_flag)

        profile = client.get_account_profile()

        mock_base_client.get.assert_called_once_with("/sell/account/v1/privilege")
        assert profile["account_type"] == "BUSINESS"

    def test_list_return_policies(self, mock_base_client, sandbox_flag: bool):
        mock_base_client.get = MagicMock(
            return_value={"returnPolicies": [{"returnPolicyId": "123", "name": "Default"}]}
        )
        client = AccountClient(base_client=mock_base_client, sandbox=sandbox_flag)
        result = client.list_return_policies("EBAY_US")
        mock_base_client.get.assert_called_once_with(
            "/sell/account/v1/return_policy", params={"marketplace_id": "EBAY_US"}
        )
        assert result["return_policies"][0]["policy_id"] == "123"

    def test_list_payment_policies(self, mock_base_client, sandbox_flag: bool):
        mock_base_client.get = MagicMock(
            return_value={"paymentPolicies": [{"paymentPolicyId": "p1", "name": "PayPal"}]}
        )
        client = AccountClient(base_client=mock_base_client, sandbox=sandbox_flag)
        result = client.list_payment_policies("EBAY_US")
        mock_base_client.get.assert_called_once_with(
            "/sell/account/v1/payment_policy", params={"marketplace_id": "EBAY_US"}
        )
        assert result["payment_policies"][0]["policy_id"] == "p1"

    def test_list_shipping_policies(self, mock_base_client, sandbox_flag: bool):
        mock_base_client.get = MagicMock(
            return_value={"shippingPolicies": [{"shippingPolicyId": "s1", "name": "Standard"}]}
        )
        client = AccountClient(base_client=mock_base_client, sandbox=sandbox_flag)
        result = client.list_shipping_policies("EBAY_US")
        mock_base_client.get.assert_called_once_with(
            "/sell/account/v1/shipping_policy", params={"marketplace_id": "EBAY_US"}
        )
        assert result["shipping_policies"][0]["policy_id"] == "s1"


