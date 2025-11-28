"""Inventory API client for managing inventory items."""

from typing import Any, Dict, List, Optional

from ebay_rest.base_client import BaseClient
from ebay_rest.inventory.models import (
    BulkInventoryItem,
    BulkInventoryItemRequest,
    BulkInventoryItemResponse,
    InventoryItem,
    InventoryItemsResponse,
)


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

    def get_inventory_item(self, sku: str) -> dict[str, Any]:
        """
        Get inventory item by SKU.

        Args:
            sku: Seller-defined SKU for the inventory item

        Returns:
            Dictionary containing inventory item details
        """
        if not sku or not sku.strip():
            raise ValueError("SKU cannot be empty")

        endpoint = f"/sell/inventory/v1/inventory_item/{sku.strip()}"
        response_data = self.base_client.get(endpoint)

        try:
            item = InventoryItem(**response_data)
            return item.model_dump(by_alias=False, exclude_none=True)
        except Exception:
            return response_data

    def list_inventory_items(
        self,
        limit: int = 50,
        offset: int = 0,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        List inventory items.

        Args:
            limit: Maximum number of items to return (default: 50, max 200)
            offset: Number of results to skip (for pagination)
            **kwargs: Additional query parameters

        Returns:
            Dictionary containing list of inventory items & pagination metadata
        """
        if limit < 1 or limit > 200:
            raise ValueError("limit must be between 1 and 200")

        if offset < 0:
            raise ValueError("offset must be >= 0")

        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }
        params.update(kwargs)

        endpoint = "/sell/inventory/v1/inventory_item"
        response_data = self.base_client.get(endpoint, params=params)

        try:
            collection = InventoryItemsResponse(**response_data)
            return {
                "inventory_items": [
                    item.model_dump(by_alias=False, exclude_none=True) for item in collection.inventory_items
                ],
                "href": collection.href,
                "limit": collection.limit,
                "offset": collection.offset,
                "total": collection.total,
                "next": collection.next,
                "prev": collection.prev,
            }
        except Exception:
            return response_data

    def create_inventory_item(self, sku: str, inventory_item: Any) -> dict[str, Any]:
        """
        Create or replace an inventory item.

        Args:
            sku: Seller-defined SKU for the inventory item
            inventory_item: Inventory item data (dict or InventoryItem)

        Returns:
            API response data (often empty for successful PUT)
        """
        if not sku or not sku.strip():
            raise ValueError("SKU cannot be empty")

        if hasattr(inventory_item, "model_dump"):
            payload = inventory_item.model_dump(by_alias=True, exclude_none=True)
        else:
            payload = inventory_item

        if not isinstance(payload, dict):
            raise ValueError("inventory_item must be a dict or InventoryItem model")

        endpoint = f"/sell/inventory/v1/inventory_item/{sku.strip()}"
        response_data = self.base_client.put(endpoint, json=payload)

        # Most successful PUT operations return empty body (204 No Content)
        return response_data or {}

    def update_inventory_item(self, sku: str, inventory_item: Any) -> dict[str, Any]:
        """
        Update (replace) an inventory item.

        Args:
            sku: Seller-defined SKU
            inventory_item: Updated inventory item payload
        """
        return self.create_inventory_item(sku, inventory_item)

    def delete_inventory_item(self, sku: str) -> dict[str, Any]:
        """
        Delete an inventory item by SKU.
        """
        if not sku or not sku.strip():
            raise ValueError("SKU cannot be empty")

        endpoint = f"/sell/inventory/v1/inventory_item/{sku.strip()}"
        return self.base_client.delete(endpoint)

    def bulk_create_or_replace_inventory_item(
        self, requests: List[BulkInventoryItem] | BulkInventoryItemRequest | Dict[str, Any]
    ) -> dict[str, Any]:
        """
        Create or replace multiple inventory items in a single call.
        """
        if isinstance(requests, BulkInventoryItemRequest):
            payload = requests.model_dump(by_alias=True, exclude_none=True)
        elif isinstance(requests, list):
            normalized: List[BulkInventoryItem] = []
            for req in requests:
                if isinstance(req, BulkInventoryItem):
                    normalized.append(req)
                elif isinstance(req, dict):
                    normalized.append(BulkInventoryItem(**req))
                else:
                    raise ValueError("Each bulk request must be BulkInventoryItem or dict")
            payload = BulkInventoryItemRequest(requests=normalized).model_dump(by_alias=True, exclude_none=True)
        elif isinstance(requests, dict):
            payload = requests
        else:
            raise ValueError("requests must be list, BulkInventoryItemRequest, or dict")

        endpoint = "/sell/inventory/v1/bulk_create_or_replace_inventory_item"
        response_data = self.base_client.post(endpoint, json=payload)
        try:
            parsed = BulkInventoryItemResponse(**response_data)
            return parsed.model_dump(by_alias=False, exclude_none=True)
        except Exception:
            return response_data
