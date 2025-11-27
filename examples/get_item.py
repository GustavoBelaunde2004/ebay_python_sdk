"""Example: Get detailed information about a specific eBay item."""

"""Example: Get detailed information about a specific eBay item."""

import os
from dotenv import load_dotenv

from ebay_rest import EbayClient
from ebay_rest.errors import NotFoundError

load_dotenv()


def main():
    client = EbayClient(
        client_id=os.getenv("EBAY_CLIENT_ID", "YOUR_CLIENT_ID"),
        client_secret=os.getenv("EBAY_CLIENT_SECRET", "YOUR_CLIENT_SECRET"),
        sandbox=True,
        user_access_token=os.getenv("EBAY_USER_ACCESS_TOKEN"),
    )

    item_id = os.getenv("EBAY_ITEM_ID", "1234567890")

    try:
        item = client.browse.get_item(item_id=item_id)
        print(f"Item: {item.get('title')}")
        print(f"Price: {item.get('price', {}).get('value')}")
        print(f"Condition: {item.get('condition')}")
    except NotFoundError:
        print(f"Item {item_id} not found")
    except Exception as exc:
        print(f"Error fetching item: {exc}")


if __name__ == "__main__":
    main()

