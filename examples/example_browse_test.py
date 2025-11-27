"""Quick Browse API test using environment variables."""

import os
from dotenv import load_dotenv

from ebay_rest import EbayClient

load_dotenv()


def main() -> None:
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("❌ Missing EBAY_CLIENT_ID or EBAY_CLIENT_SECRET in environment.")
        return

    print("🛒 Testing Browse API...")
    client = EbayClient(
        client_id=client_id,
        client_secret=client_secret,
        sandbox=True,
    )

    try:
        results = client.browse.search_items(query="laptop", limit=3)
        items = results.get("items", [])
        print(f"✅ Search returned {len(items)} items (total available: {results.get('total')})")
        for i, item in enumerate(items, 1):
            title = item.get("title", "N/A")
            price = item.get("price", {}).get("value")
            print(f"{i}. {title} - ${price}")

        if items:
            item_id = items[0].get("item_id")
            print(f"\n📦 Fetching details for first item: {item_id}")
            item = client.browse.get_item(item_id=item_id)
            print(f"   Title: {item.get('title')}")
    except Exception as exc:
        print(f"❌ Browse test failed: {exc}")


if __name__ == "__main__":
    main()

