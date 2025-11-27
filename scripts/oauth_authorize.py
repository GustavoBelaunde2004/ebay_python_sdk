"""Helper CLI to complete the eBay OAuth Authorization Code flow."""

import os
import urllib.parse

from dotenv import load_dotenv

from ebay_rest import oauth


def main() -> None:
    load_dotenv()

    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")
    redirect_uri = os.getenv("EBAY_REDIRECT_URI")
    scopes = os.getenv("EBAY_OAUTH_SCOPES", "").split()
    environment = os.getenv("EBAY_ENV", "sandbox")

    if not client_id or not client_secret or not redirect_uri:
        print("❌ EBAY_CLIENT_ID, EBAY_CLIENT_SECRET, and EBAY_REDIRECT_URI must be set.")
        return

    if not scopes:
        scopes = ["https://api.ebay.com/oauth/api_scope"]

    print("🔐 eBay OAuth Authorization Helper")
    print(f"Environment: {environment}")
    print(f"Scopes: {scopes}")

    url = oauth.build_authorization_url(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scopes=scopes,
        environment=environment,
    )
    print("\n1. Open this URL in your browser and sign in:")
    print(url)

    print("\n2. After approving, eBay will redirect to your redirect URI with ?code=...")
    code = input("Paste the 'code' value here: ").strip()

    if not code:
        print("❌ Authorization code is required.")
        return

    tokens = oauth.exchange_authorization_code(
        client_id=client_id,
        client_secret=client_secret,
        code=code,
        redirect_uri=redirect_uri,
        environment=environment,
    )

    print("\n✅ Token exchange succeeded!")
    print("Access Token:", tokens.get("access_token"))
    print("Expires In (seconds):", tokens.get("expires_in"))
    print("Refresh Token:", tokens.get("refresh_token"))
    print("\nStore the refresh token securely and use it to refresh access tokens when needed.")


if __name__ == "__main__":
    main()

