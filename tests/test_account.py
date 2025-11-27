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


