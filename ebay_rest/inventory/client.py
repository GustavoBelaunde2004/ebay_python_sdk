"""Inventory API client for managing inventory items."""

from typing import Optional

from ebay_rest.base_client import BaseClient


class InventoryClient:
    """
    Client for eBay Inventory API.

    Provides methods to manage inventory items, offers, and locations.
    """

    def __init__(self, base_client: BaseClient, sandbox: bool = False):
        """
        Initialize Inventory API client.

        Args:
            base_client: BaseClient instance for making HTTP requests
            sandbox: Whether to use sandbox environment
        """
        self.base_client = base_client
        self.sandbox = sandbox

    def get_inventory_item(self, sku: str) -> dict:
        """
        Get inventory item by SKU.

        Args:
            sku: Seller-defined SKU for the inventory item

        Returns:
            Dictionary containing inventory item details

        Raises:
            NotFoundError: If inventory item is not found
            EbayAPIError: If the request fails

        TODO:
            - Implement API endpoint call
            - Parse and return InventoryItem model
        """
        # TODO: Build endpoint path: /sell/inventory/v1/inventory_item/{sku}
        # TODO: Call base_client.get() with path
        # TODO: Parse response and return InventoryItem model
        raise NotImplementedError("get_inventory_item not yet implemented")

    def list_inventory_items(
        self,
        limit: int = 50,
        offset: int = 0,
        **kwargs: dict,
    ) -> dict:
        """
        List inventory items.

        Args:
            limit: Maximum number of items to return (default: 50)
            offset: Number of results to skip (for pagination)
            **kwargs: Additional query parameters

        Returns:
            Dictionary containing list of inventory items

        Raises:
            EbayAPIError: If the request fails

        TODO:
            - Implement API endpoint call
            - Handle pagination
            - Parse and return list of InventoryItem models
        """
        # TODO: Build endpoint path: /sell/inventory/v1/inventory_item
        # TODO: Build query parameters dict
        # TODO: Call base_client.get() with path and params
        # TODO: Parse response and return list of InventoryItem models
        raise NotImplementedError("list_inventory_items not yet implemented")

    def create_inventory_item(self, sku: str, inventory_item: dict) -> dict:
        """
        Create a new inventory item.

        Args:
            sku: Seller-defined SKU for the inventory item
            inventory_item: Inventory item data

        Returns:
            Dictionary containing created inventory item

        Raises:
            ValidationError: If inventory item data is invalid
            EbayAPIError: If the request fails

        TODO:
            - Implement API endpoint call
            - Validate inventory_item data
            - Parse and return InventoryItem model
        """
        # TODO: Build endpoint path: /sell/inventory/v1/inventory_item/{sku}
        # TODO: Call base_client.put() with path and inventory_item JSON
        # TODO: Parse response and return InventoryItem model
        raise NotImplementedError("create_inventory_item not yet implemented")

