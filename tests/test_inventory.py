"""Tests for Inventory API client."""

from unittest.mock import MagicMock

import pytest

from ebay_rest.inventory.client import InventoryClient
from ebay_rest.inventory.models import InventoryItem


class TestInventoryClient:
    """Test suite for InventoryClient."""

    def test_init(self, mock_base_client, sandbox_flag: bool):
        """InventoryClient stores base client and sandbox flag."""
        client = InventoryClient(base_client=mock_base_client, sandbox=sandbox_flag)
        assert client.base_client == mock_base_client
        assert client.sandbox is sandbox_flag

    def test_get_inventory_item_success(self, mock_inventory_client: InventoryClient):
        """get_inventory_item should invoke base client with SKU."""
        mock_inventory_client.base_client.get = MagicMock(
            return_value={"sku": "SKU123", "condition": "NEW"}
        )

        result = mock_inventory_client.get_inventory_item("SKU123")

        mock_inventory_client.base_client.get.assert_called_once_with(
            "/sell/inventory/v1/inventory_item/SKU123"
        )
        assert result["sku"] == "SKU123"

    def test_get_inventory_item_empty_sku(self, mock_inventory_client: InventoryClient):
        """Empty SKU should raise ValueError."""
        with pytest.raises(ValueError):
            mock_inventory_client.get_inventory_item("")

    def test_list_inventory_items_validates_params(self, mock_inventory_client: InventoryClient):
        """Invalid pagination params raise ValueError."""
        with pytest.raises(ValueError):
            mock_inventory_client.list_inventory_items(limit=0)
        with pytest.raises(ValueError):
            mock_inventory_client.list_inventory_items(offset=-1)

    def test_list_inventory_items_parses_response(self, mock_inventory_client: InventoryClient):
        """list_inventory_items should parse inventory items list."""
        mock_inventory_client.base_client.get = MagicMock(
            return_value={
                "inventoryItems": [{"sku": "A"}, {"sku": "B"}],
                "total": 2,
                "offset": 0,
                "limit": 2,
            }
        )

        response = mock_inventory_client.list_inventory_items(limit=2, offset=0)

        assert len(response["inventory_items"]) == 2
        assert response["total"] == 2
        mock_inventory_client.base_client.get.assert_called_once()

    def test_create_inventory_item_with_model(self, mock_inventory_client: InventoryClient):
        """create_inventory_item accepts InventoryItem models."""
        mock_inventory_client.base_client.put = MagicMock(return_value={})
        model = InventoryItem(sku="SKU999", condition="NEW")

        response = mock_inventory_client.create_inventory_item("SKU999", model)

        assert response == {}
        mock_inventory_client.base_client.put.assert_called_once()


