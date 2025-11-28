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

    if not user_access_token:
        print("❌ Missing EBAY_USER_ACCESS_TOKEN in environment.")
        print("💡 Inventory API requires a user access token (not just client credentials).")
        print("   Get one from: https://developer.ebay.com/my/keys → Your Sandbox App → User Tokens")
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
        error_msg = str(exc)
        print(f"❌ Inventory test failed: {error_msg}")
        
        if "Authentication failed" in error_msg or "401" in error_msg:
            print("\n💡 Token may be expired or invalid.")
            print("   Get a new token from: https://developer.ebay.com/my/keys")
            print("   Check that your token has 'sell.inventory' scope")


if __name__ == "__main__":
    main()

