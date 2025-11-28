"""Example: Search for items on eBay."""

import os
from dotenv import load_dotenv

from ebay_rest import EbayClient

load_dotenv()


def main():
    """Example demonstrating how to search for items using the Browse API."""
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("❌ Missing EBAY_CLIENT_ID or EBAY_CLIENT_SECRET in environment.")
        return

    # Initialize the eBay client
    client = EbayClient(
        client_id=client_id,
        client_secret=client_secret,
        sandbox=True,  # Set to False for production
    )

    # Search for items
    query = "laptop"
    limit = 10

    try:
        print(f"🔍 Searching for '{query}' (limit: {limit})...")
        results = client.browse.search_items(query=query, limit=limit)
        
        items = results.get("items", [])
        total = results.get("total", 0)
        
        print(f"✅ Found {len(items)} items (total available: {total})")
        print()
        
        for i, item in enumerate(items, 1):
            title = item.get("title", "N/A")
            price = item.get("price", {}).get("value", "N/A")
            currency = item.get("price", {}).get("currency", "")
            print(f"{i}. {title} - {currency}${price}")

    except Exception as e:
        print(f"❌ Error searching items: {e}")


if __name__ == "__main__":
    main()

