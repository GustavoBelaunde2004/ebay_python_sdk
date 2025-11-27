"""Quick Orders API test using environment variables."""

import os
from dotenv import load_dotenv

from ebay_rest import EbayClient

load_dotenv()


def main() -> None:
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")
    user_access_token = os.getenv("EBAY_USER_ACCESS_TOKEN")

    if not client_id or not client_secret:
        print("❌ Missing EBAY_CLIENT_ID or EBAY_CLIENT_SECRET in environment.")
        return

    print("📦 Testing Orders API...")
    client = EbayClient(
        client_id=client_id,
        client_secret=client_secret,
        sandbox=True,
        user_access_token=user_access_token,
    )

    try:
        orders_response = client.orders.list_orders(limit=5)
        orders = orders_response.get("orders", [])
        print(f"✅ list_orders returned {len(orders)} orders (total available: {orders_response.get('total')})")

        if not orders:
            print("⚠️ No orders found in sandbox. Create test orders to exercise this API.")
            return

        first_order = orders[0]
        order_id = first_order.get("order_id") or first_order.get("orderId")
        print(f"\n🔍 Fetching first order details: {order_id}")

        order = client.orders.get_order(order_id=order_id)
        print(f"   Order status: {order.get('order_fulfillment_status')}")
        print(f"   Buyer: {order.get('buyer', {}).get('username')}")
        line_items = order.get("line_items", [])
        print(f"   Line items: {len(line_items)}")
    except Exception as exc:
        print(f"❌ Orders test failed: {exc}")


if __name__ == "__main__":
    main()

