"""Example: Search for items on eBay."""

from ebay_rest import EbayClient


def main():
    """
    Example demonstrating how to search for items using the Browse API.

    TODO:
        - Replace placeholder credentials with actual eBay API credentials
        - Set sandbox=True for testing, False for production
        - Implement result processing
    """
    # Initialize the eBay client
    client = EbayClient(
        client_id="YOUR_CLIENT_ID_HERE",
        client_secret="YOUR_CLIENT_SECRET_HERE",
        sandbox=True,  # Set to False for production
    )

    # Search for items
    # TODO: Replace with actual search query
    query = "laptop"
    limit = 10

    try:
        # TODO: Uncomment when search_items is implemented
        # results = client.browse.search_items(query=query, limit=limit)
        # print(f"Found {len(results.get('items', []))} items")
        #
        # for item in results.get('items', []):
        #     print(f"- {item.get('title')} (${item.get('price', {}).get('value')})")

        print("TODO: Implement search_items functionality")
        print(f"Would search for: '{query}' with limit: {limit}")

    except Exception as e:
        print(f"Error searching items: {e}")


if __name__ == "__main__":
    main()

