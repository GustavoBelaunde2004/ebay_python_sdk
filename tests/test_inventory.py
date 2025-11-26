"""Tests for Inventory API client."""

import pytest

from ebay_rest.errors import NotFoundError, ValidationError
from ebay_rest.inventory.client import InventoryClient


class TestInventoryClient:
    """Test suite for InventoryClient."""

    def test_init(self, mock_base_client, sandbox_flag: bool):
        """
        Test InventoryClient initialization.

        TODO: Implement test
        """
        # TODO: Test that InventoryClient initializes correctly
        client = InventoryClient(base_client=mock_base_client, sandbox=sandbox_flag)
        assert client.base_client == mock_base_client
        assert client.sandbox == sandbox_flag

    def test_get_inventory_item(self, mock_inventory_client: InventoryClient):
        """
        Test get inventory item by SKU.

        TODO: Implement test
        """
        # TODO: Mock successful inventory item response
        # TODO: Test that get_inventory_item() returns item details
        # TODO: Test that SKU is passed correctly in URL
        pass

    def test_get_inventory_item_not_found(self, mock_inventory_client: InventoryClient):
        """
        Test get inventory item with invalid SKU.

        TODO: Implement test
        """
        # TODO: Mock 404 response
        # TODO: Test that NotFoundError is raised
        pass

    def test_list_inventory_items(self, mock_inventory_client: InventoryClient):
        """
        Test list inventory items functionality.

        TODO: Implement test
        """
        # TODO: Mock successful list response
        # TODO: Test that list_inventory_items() returns list of items
        # TODO: Test limit parameter works
        # TODO: Test offset parameter for pagination
        pass

    def test_create_inventory_item(self, mock_inventory_client: InventoryClient):
        """
        Test create inventory item functionality.

        TODO: Implement test
        """
        # TODO: Mock successful create response
        # TODO: Test that create_inventory_item() creates item
        # TODO: Test that inventory_item data is validated
        # TODO: Test that SKU is passed correctly in URL
        pass

    def test_create_inventory_item_validation_error(self, mock_inventory_client: InventoryClient):
        """
        Test create inventory item with invalid data.

        TODO: Implement test
        """
        # TODO: Mock 400/422 response
        # TODO: Test that ValidationError is raised
        pass

