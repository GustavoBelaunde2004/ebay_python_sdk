"""Quick standalone auth test using environment variables."""

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

    print("🔐 Testing Authentication Only...")
    client = EbayClient(
        client_id=client_id,
        client_secret=client_secret,
        sandbox=True,
    )

    try:
        token = client.auth.get_access_token()
        print("✅ Authentication successful!")
        print(f"   Token (first 60 chars): {token[:60]}...")
    except Exception as exc:
        print(f"❌ Authentication failed: {exc}")


if __name__ == "__main__":
    main()

