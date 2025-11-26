"""Example: List orders from eBay."""

from ebay_rest import EbayClient


def main():
    """
    Example demonstrating how to list orders using the Orders API.

    TODO:
        - Replace placeholder credentials with actual eBay API credentials
        - Set sandbox=True for testing, False for production
        - Implement order processing and display
    """
    # Initialize the eBay client
    client = EbayClient(
        client_id="YOUR_CLIENT_ID_HERE",
        client_secret="YOUR_CLIENT_SECRET_HERE",
        sandbox=True,  # Set to False for production
    )

    # List orders
    limit = 50

    try:
        # TODO: Uncomment when list_orders is implemented
        # orders = client.orders.list_orders(limit=limit)
        # print(f"Found {len(orders.get('orders', []))} orders")
        #
        # for order in orders.get('orders', []):
        #     order_id = order.get('orderId')
        #     total = order.get('pricingSummary', {}).get('total', {})
        #     print(f"- Order {order_id}: ${total.get('value')}")

        print("TODO: Implement list_orders functionality")
        print(f"Would fetch up to {limit} orders")

    except Exception as e:
        print(f"Error listing orders: {e}")


if __name__ == "__main__":
    main()

