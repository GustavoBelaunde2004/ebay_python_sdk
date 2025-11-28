"""Example: Using the paginate helper to stream Browse results."""

import os
from dotenv import load_dotenv

from ebay_rest import EbayClient
from ebay_rest.pagination import paginate

load_dotenv()


def main() -> None:
    client = EbayClient(
        client_id=os.getenv("EBAY_CLIENT_ID", "YOUR_CLIENT_ID"),
        client_secret=os.getenv("EBAY_CLIENT_SECRET", "YOUR_CLIENT_SECRET"),
        sandbox=True,
    )

    print("Iterating first 10 laptops using paginate()...")
    for item in paginate(
        client.browse.search_items,
        query="laptop",
        limit=10,  # total items to yield
        items_key="items",
        offset_param="offset",
        limit_param="limit",
    ):
        title = item.get("title")
        price = item.get("price", {}).get("value")
        print(f"- {title} (${price})")


if __name__ == "__main__":
    main()