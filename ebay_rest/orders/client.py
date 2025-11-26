"""Orders API client for retrieving and managing orders."""

from typing import Any, Optional

from ebay_rest.base_client import BaseClient
from ebay_rest.orders.models import Order, OrdersResponse


class OrdersClient:
    """
    Client for eBay Sell Fulfillment Orders API.

    Provides methods to retrieve and manage orders for sellers.
    """

    def __init__(self, base_client: BaseClient, sandbox: bool = False):
        """
        Initialize Orders API client.

        Args:
            base_client: BaseClient instance for making HTTP requests
            sandbox: Whether to use sandbox environment
        """
        self.base_client = base_client
        self.sandbox = sandbox

    def list_orders(
        self,
        limit: int = 50,
        offset: int = 0,
        filter: Optional[str] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        List orders for the authenticated seller.

        Args:
            limit: Maximum number of orders to return (1-200, default: 50)
            offset: Number of results to skip (for pagination)
            filter: Optional filter string (e.g., \"creationdate:[2024-01-01T00:00:00.000Z..]\")
            **kwargs: Additional query parameters supported by eBay (order_ids, order_statuses, etc.)

        Returns:
            Dictionary containing list of orders and pagination metadata

        Raises:
            ValueError: If parameters are invalid
            EbayAPIError: If the request fails
        """
        if limit < 1 or limit > 200:
            raise ValueError("limit must be between 1 and 200")

        if offset < 0:
            raise ValueError("offset must be >= 0")

        # Build query parameters
        params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }

        if filter:
            params["filter"] = filter

        # Include any additional query parameters
        params.update(kwargs)

        endpoint = "/sell/fulfillment/v1/order"
        response_data = self.base_client.get(endpoint, params=params)

        try:
            orders_response = OrdersResponse(**response_data)
            return {
                "orders": [order.model_dump() for order in orders_response.orders],
                "href": orders_response.href,
                "limit": orders_response.limit,
                "offset": orders_response.offset,
                "total": orders_response.total,
                "next": orders_response.next,
                "prev": orders_response.prev,
            }
        except Exception:
            # If parsing fails, return raw response so callers can inspect structure
            return response_data

    def get_order(self, order_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific order.

        Args:
            order_id: eBay order ID

        Returns:
            Dictionary containing order details

        Raises:
            ValueError: If order_id is empty
            NotFoundError: If order is not found
            EbayAPIError: If the request fails
        """
        if not order_id or not order_id.strip():
            raise ValueError("order_id cannot be empty")

        order_id = order_id.strip()
        endpoint = f"/sell/fulfillment/v1/order/{order_id}"

        response_data = self.base_client.get(endpoint)

        try:
            order = Order(**response_data)
            return order.model_dump()
        except Exception:
            return response_data

