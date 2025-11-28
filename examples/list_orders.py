"""Example: List orders from eBay."""

import os
from dotenv import load_dotenv

from ebay_rest import EbayClient

load_dotenv()


def main():
    """Example demonstrating how to list orders using the Orders API."""
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")
    user_access_token = os.getenv("EBAY_USER_ACCESS_TOKEN")

    if not client_id or not client_secret:
        print("❌ Missing EBAY_CLIENT_ID or EBAY_CLIENT_SECRET in environment.")
        return

    if not user_access_token:
        print("❌ Missing EBAY_USER_ACCESS_TOKEN in environment.")
        print("💡 Orders API requires a user access token (not just client credentials).")
        return

    # Initialize the eBay client
    client = EbayClient(
        client_id=client_id,
        client_secret=client_secret,
        sandbox=True,  # Set to False for production
        user_access_token=user_access_token,
    )

    # List orders
    limit = 50

    try:
        print(f"📦 Listing up to {limit} orders...")
        orders_response = client.orders.list_orders(limit=limit)
        
        orders = orders_response.get("orders", [])
        total = orders_response.get("total", 0)
        
        print(f"✅ Found {len(orders)} orders (total available: {total})")
        
        if not orders:
            print("⚠️  No orders found in sandbox. Create test orders to exercise this API.")
            return
        
        print()
        for i, order in enumerate(orders, 1):
            order_id = order.get("order_id") or order.get("orderId", "N/A")
            status = order.get("order_fulfillment_status") or order.get("orderFulfillmentStatus", "N/A")
            
            # Get total price
            pricing = order.get("pricing_summary") or order.get("pricingSummary", {})
            total_price = pricing.get("total", {})
            price_value = total_price.get("value", "N/A")
            currency = total_price.get("currency", "")
            
            print(f"{i}. Order {order_id}")
            print(f"   Status: {status}")
            print(f"   Total: {currency}${price_value}")

    except Exception as e:
        print(f"❌ Error listing orders: {e}")


if __name__ == "__main__":
    main()

