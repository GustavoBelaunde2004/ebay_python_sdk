"""Tests for Orders API client."""

from unittest.mock import MagicMock

import pytest

from ebay_rest.errors import NotFoundError, ValidationError
from ebay_rest.orders.client import OrdersClient


class TestOrdersClient:
    """Test suite for OrdersClient."""

    def test_init(self, mock_base_client, sandbox_flag: bool):
        """Test OrdersClient initialization."""
        client = OrdersClient(base_client=mock_base_client, sandbox=sandbox_flag)
        assert client.base_client == mock_base_client
        assert client.sandbox == sandbox_flag

    def test_list_orders_success(self, mock_base_client, sandbox_flag: bool):
        """Test successful list orders response."""
        mock_base_client.get = MagicMock(
            return_value={
                "orders": [
                    {
                        "orderId": "123456",
                        "orderFulfillmentStatus": "FULFILLED",
                        "pricingSummary": {"total": {"value": "99.99", "currency": "USD"}},
                    }
                ],
                "total": 1,
                "limit": 50,
                "offset": 0,
            }
        )
        client = OrdersClient(base_client=mock_base_client, sandbox=sandbox_flag)

        result = client.list_orders(limit=50, offset=0)

        mock_base_client.get.assert_called_once_with(
            "/sell/fulfillment/v1/order", params={"limit": 50, "offset": 0}
        )
        assert "orders" in result
        assert result["total"] == 1

    def test_list_orders_with_filter(self, mock_base_client, sandbox_flag: bool):
        """Test list orders with filter parameter."""
        mock_base_client.get = MagicMock(return_value={"orders": [], "total": 0})
        client = OrdersClient(base_client=mock_base_client, sandbox=sandbox_flag)

        filter_str = "creationdate:[2024-01-01T00:00:00.000Z..]"
        result = client.list_orders(limit=10, filter=filter_str)

        mock_base_client.get.assert_called_once_with(
            "/sell/fulfillment/v1/order",
            params={"limit": 10, "offset": 0, "filter": filter_str},
        )
        assert "orders" in result

    def test_list_orders_invalid_limit(self, mock_base_client, sandbox_flag: bool):
        """Test list orders with invalid limit raises ValueError."""
        client = OrdersClient(base_client=mock_base_client, sandbox=sandbox_flag)

        with pytest.raises(ValueError, match="limit must be between 1 and 200"):
            client.list_orders(limit=0)

        with pytest.raises(ValueError, match="limit must be between 1 and 200"):
            client.list_orders(limit=201)

    def test_list_orders_invalid_offset(self, mock_base_client, sandbox_flag: bool):
        """Test list orders with invalid offset raises ValueError."""
        client = OrdersClient(base_client=mock_base_client, sandbox=sandbox_flag)

        with pytest.raises(ValueError, match="offset must be >= 0"):
            client.list_orders(offset=-1)

    def test_get_order_success(self, mock_base_client, sandbox_flag: bool):
        """Test successful get order response."""
        order_id = "123456"
        mock_base_client.get = MagicMock(
            return_value={
                "orderId": order_id,
                "orderFulfillmentStatus": "FULFILLED",
                "buyer": {"username": "test_buyer"},
                "pricingSummary": {"total": {"value": "99.99", "currency": "USD"}},
            }
        )
        client = OrdersClient(base_client=mock_base_client, sandbox=sandbox_flag)

        result = client.get_order(order_id=order_id)

        mock_base_client.get.assert_called_once_with(f"/sell/fulfillment/v1/order/{order_id}")
        assert "order_id" in result or "orderId" in result

    def test_get_order_empty_id(self, mock_base_client, sandbox_flag: bool):
        """Test get order with empty order_id raises ValueError."""
        client = OrdersClient(base_client=mock_base_client, sandbox=sandbox_flag)

        with pytest.raises(ValueError, match="order_id cannot be empty"):
            client.get_order(order_id="")

        with pytest.raises(ValueError, match="order_id cannot be empty"):
            client.get_order(order_id="   ")

