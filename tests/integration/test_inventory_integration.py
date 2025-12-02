"""Integration tests for Inventory API (requires user access token)."""

import pytest


@pytest.mark.integration
@pytest.mark.requires_credentials
@pytest.mark.requires_user_token
class TestInventoryIntegration:
    """Integration tests for Inventory API with real sandbox."""

    def test_list_inventory_items(self, sandbox_client_with_user_token):
        """Test listing inventory items with real API."""
        results = sandbox_client_with_user_token.inventory.list_inventory_items(limit=10)

        # Verify response structure
        assert "inventory_items" in results
        assert isinstance(results["inventory_items"], list)
        assert "total" in results
        assert isinstance(results["total"], int)

    def test_list_inventory_items_with_pagination(self, sandbox_client_with_user_token):
        """Test inventory items pagination."""
        # Get first page
        results1 = sandbox_client_with_user_token.inventory.list_inventory_items(limit=5, offset=0)
        items1 = results1.get("inventory_items", [])

        # Get second page
        if results1.get("total", 0) > 5:
            results2 = sandbox_client_with_user_token.inventory.list_inventory_items(limit=5, offset=5)
            items2 = results2.get("inventory_items", [])

            # Should be different items or empty
            assert isinstance(items2, list)

    def test_get_inventory_item_if_exists(self, sandbox_client_with_user_token):
        """Test getting a specific inventory item if one exists."""
        # First, list items
        results = sandbox_client_with_user_token.inventory.list_inventory_items(limit=1)

        items = results.get("inventory_items", [])
        if len(items) > 0:
            # Get the first item's SKU
            sku = items[0].get("sku")
            if sku:
                # Get item details
                item = sandbox_client_with_user_token.inventory.get_inventory_item(sku=sku)

                # Verify structure
                assert "sku" in item
                assert item["sku"] == sku
        else:
            pytest.skip("No inventory items in sandbox to test get_inventory_item")

    def test_list_inventory_items_validation(self, sandbox_client_with_user_token):
        """Test validation of list_inventory_items parameters."""
        with pytest.raises(ValueError, match="limit must be between 1 and 200"):
            sandbox_client_with_user_token.inventory.list_inventory_items(limit=0)

        with pytest.raises(ValueError, match="limit must be between 1 and 200"):
            sandbox_client_with_user_token.inventory.list_inventory_items(limit=201)

        with pytest.raises(ValueError, match="offset must be >= 0"):
            sandbox_client_with_user_token.inventory.list_inventory_items(offset=-1)

