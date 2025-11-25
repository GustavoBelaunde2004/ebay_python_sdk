"""Pytest configuration and shared fixtures."""

import pytest

from ebay_rest.auth import OAuth2Client
from ebay_rest.base_client import BaseClient
from ebay_rest.browse.client import BrowseClient
from ebay_rest.client import EbayClient
from ebay_rest.inventory.client import InventoryClient
from ebay_rest.orders.client import OrdersClient


@pytest.fixture
def test_client_id() -> str:
    """Return test client ID."""
    return "test_client_id"


@pytest.fixture
def test_client_secret() -> str:
    """Return test client secret."""
    return "test_client_secret"


@pytest.fixture
def sandbox_flag() -> bool:
    """Return sandbox flag for testing."""
    return True


@pytest.fixture
def mock_oauth_client(test_client_id: str, test_client_secret: str, sandbox_flag: bool) -> OAuth2Client:
    """
    Create a mock OAuth2Client for testing.

    TODO:
        - Consider using unittest.mock.patch for OAuth2Client methods
        - Mock token responses
        - Mock expiration logic
    """
    return OAuth2Client(
        client_id=test_client_id,
        client_secret=test_client_secret,
        sandbox=sandbox_flag,
    )


@pytest.fixture
def mock_base_client(mock_oauth_client: OAuth2Client, sandbox_flag: bool) -> BaseClient:
    """
    Create a mock BaseClient for testing.

    TODO:
        - Consider using unittest.mock.patch for HTTP methods
        - Mock HTTP responses
        - Mock error scenarios
    """
    base_url = "https://api.sandbox.ebay.com" if sandbox_flag else "https://api.ebay.com"
    return BaseClient(
        auth_client=mock_oauth_client,
        base_url=base_url,
        sandbox=sandbox_flag,
    )


@pytest.fixture
def mock_ebay_client(test_client_id: str, test_client_secret: str, sandbox_flag: bool) -> EbayClient:
    """
    Create a mock EbayClient for testing.

    TODO:
        - Consider using unittest.mock.patch for sub-clients
        - Mock API responses
        - Set up test fixtures for common scenarios
    """
    return EbayClient(
        client_id=test_client_id,
        client_secret=test_client_secret,
        sandbox=sandbox_flag,
    )


@pytest.fixture
def mock_browse_client(mock_base_client: BaseClient, sandbox_flag: bool) -> BrowseClient:
    """Create a mock BrowseClient for testing."""
    return BrowseClient(base_client=mock_base_client, sandbox=sandbox_flag)


@pytest.fixture
def mock_inventory_client(mock_base_client: BaseClient, sandbox_flag: bool) -> InventoryClient:
    """Create a mock InventoryClient for testing."""
    return InventoryClient(base_client=mock_base_client, sandbox=sandbox_flag)


@pytest.fixture
def mock_orders_client(mock_base_client: BaseClient, sandbox_flag: bool) -> OrdersClient:
    """Create a mock OrdersClient for testing."""
    return OrdersClient(base_client=mock_base_client, sandbox=sandbox_flag)

