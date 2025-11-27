"""Quick Inventory API test using environment variables."""

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

    print("📦 Testing Inventory API...")
    client = EbayClient(
        client_id=client_id,
        client_secret=client_secret,
        sandbox=True,
        user_access_token=user_access_token,
    )

    try:
        response = client.inventory.list_inventory_items(limit=5)
        items = response.get("inventory_items", [])
        print(f"✅ list_inventory_items returned {len(items)} items (total: {response.get('total')})")
        if items:
            first_sku = items[0].get("sku")
            print(f"🔎 Fetching first SKU: {first_sku}")
            item = client.inventory.get_inventory_item(sku=first_sku)
            print(f"   Condition: {item.get('condition')}")
        else:
            print("⚠️  No inventory items found. Create some via Seller Hub or create_inventory_item().")
    except Exception as exc:
        print(f"❌ Inventory test failed: {exc}")


if __name__ == "__main__":
    main()

