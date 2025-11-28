"""Quick Account API test using environment variables."""

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
        print("💡 Account API requires a user access token (not just client credentials).")
        return

    print("👤 Testing Account API...")
    client = EbayClient(
        client_id=client_id,
        client_secret=client_secret,
        sandbox=True,
        user_access_token=user_access_token,
    )

    try:
        # Get account profile
        print("\n📋 Fetching account profile...")
        profile = client.account.get_account_profile()
        account_type = profile.get("account_type") or profile.get("accountType", "N/A")
        print(f"✅ Account type: {account_type}")

        # Get privileges
        privileges = profile.get("privileges", [])
        if privileges:
            print(f"   Privileges: {len(privileges)} found")
            for priv in privileges[:3]:  # Show first 3
                name = priv.get("name", "N/A")
                status = priv.get("status", "N/A")
                print(f"   - {name}: {status}")

        # List return policies
        print("\n📜 Fetching return policies...")
        return_policies = client.account.list_return_policies(marketplace_id="EBAY_US")
        policies = return_policies.get("return_policies", [])
        print(f"✅ Found {len(policies)} return policy(ies)")

        # List payment policies
        print("\n💳 Fetching payment policies...")
        payment_policies = client.account.list_payment_policies(marketplace_id="EBAY_US")
        pay_policies = payment_policies.get("payment_policies", [])
        print(f"✅ Found {len(pay_policies)} payment policy(ies)")

        # List shipping policies
        print("\n📦 Fetching shipping policies...")
        shipping_policies = client.account.list_shipping_policies(marketplace_id="EBAY_US")
        ship_policies = shipping_policies.get("shipping_policies", [])
        print(f"✅ Found {len(ship_policies)} shipping policy(ies)")

    except Exception as exc:
        error_msg = str(exc)
        print(f"❌ Account test failed: {error_msg}")
        
        if "Authentication failed" in error_msg or "401" in error_msg:
            print("\n💡 Token may be expired or invalid.")
            print("   Get a new token from: https://developer.ebay.com/my/keys")


if __name__ == "__main__":
    main()

