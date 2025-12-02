"""Integration tests for Orders API (requires user access token)."""

import pytest


@pytest.mark.integration
@pytest.mark.requires_credentials
@pytest.mark.requires_user_token
class TestOrdersIntegration:
    """Integration tests for Orders API with real sandbox."""

    def test_list_orders(self, sandbox_client_with_user_token):
        """Test listing orders with real API."""
        results = sandbox_client_with_user_token.orders.list_orders(limit=10)

        # Verify response structure
        assert "orders" in results
        assert isinstance(results["orders"], list)
        assert "total" in results
        assert isinstance(results["total"], int)

    def test_list_orders_with_pagination(self, sandbox_client_with_user_token):
        """Test orders pagination."""
        # Get first page
        results1 = sandbox_client_with_user_token.orders.list_orders(limit=5, offset=0)
        orders1 = results1.get("orders", [])

        # Get second page
        if results1.get("total", 0) > 5:
            results2 = sandbox_client_with_user_token.orders.list_orders(limit=5, offset=5)
            orders2 = results2.get("orders", [])

            # Should be different orders or empty
            assert isinstance(orders2, list)

    def test_get_order_if_exists(self, sandbox_client_with_user_token):
        """Test getting a specific order if one exists."""
        # First, list orders
        results = sandbox_client_with_user_token.orders.list_orders(limit=1)

        orders = results.get("orders", [])
        if len(orders) > 0:
            # Get the first order's ID
            order_id = orders[0].get("order_id")
            if order_id:
                # Get order details
                order = sandbox_client_with_user_token.orders.get_order(order_id=order_id)

                # Verify structure
                assert "order_id" in order
                assert order["order_id"] == order_id
        else:
            pytest.skip("No orders in sandbox to test get_order")

    def test_list_orders_validation(self, sandbox_client_with_user_token):
        """Test validation of list_orders parameters."""
        with pytest.raises(ValueError, match="limit must be between 1 and 200"):
            sandbox_client_with_user_token.orders.list_orders(limit=0)

        with pytest.raises(ValueError, match="limit must be between 1 and 200"):
            sandbox_client_with_user_token.orders.list_orders(limit=201)

        with pytest.raises(ValueError, match="offset must be >= 0"):
            sandbox_client_with_user_token.orders.list_orders(offset=-1)

