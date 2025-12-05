"""Get user access token and refresh token via Authorization Code flow."""

import os
import urllib.parse
from dotenv import load_dotenv

from ebay_rest import oauth

load_dotenv()


def main() -> None:
    """Get user access token and refresh token via OAuth Authorization Code flow."""
    client_id = os.getenv("EBAY_CLIENT_ID")
    client_secret = os.getenv("EBAY_CLIENT_SECRET")
    redirect_uri = os.getenv("EBAY_REDIRECT_URI")
    scopes_str = os.getenv("EBAY_OAUTH_SCOPES", "")
    environment = os.getenv("EBAY_ENV", "sandbox")

    if not client_id or not client_secret:
        print("❌ Missing EBAY_CLIENT_ID or EBAY_CLIENT_SECRET in environment.")
        print("   Add them to your .env file.")
        return

    if not redirect_uri:
        print("❌ Missing EBAY_REDIRECT_URI in environment.")
        print("   Get your encoded RuName from: https://developer.ebay.com/my/keys")
        print("   Add it to your .env file as EBAY_REDIRECT_URI")
        return

    # Parse scopes
    if scopes_str:
        scopes = scopes_str.split()
    else:
        # Default to common Sell API scopes
        scopes = [
            "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly",
            "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly",
            "https://api.ebay.com/oauth/api_scope/sell.account.readonly",
        ]
        print("💡 Using default Sell API scopes. Set EBAY_OAUTH_SCOPES to customize.")

    # Step 1: Build authorization URL
    print("\n" + "=" * 70)
    print("STEP 1: Get Authorization Code")
    print("=" * 70)
    auth_url = oauth.build_authorization_url(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scopes=scopes,
        environment=environment,
    )

    print("\n📋 Open this URL in your browser:")
    print("-" * 70)
    print(auth_url)
    print("-" * 70)
    print("\nAfter authorizing, eBay will redirect you to a URL like:")
    print(f"  https://auth2.ebay.com/oauth2/ThirdPartyAuthSucessFailure?code=CODE_HERE")
    print("\nCopy the ENTIRE redirect URL from your browser's address bar.")
    print("(You can paste the full URL or just the code - both work!)")
    print("=" * 70)

    # Step 2: Get authorization code from user
    user_input = input("\n📝 Paste the redirect URL (or just the code): ").strip()

    if not user_input:
        print("❌ No input provided. Exiting.")
        return

    # Extract code from URL if full URL was pasted
    code = user_input
    
    # Check if it's a full URL
    if "code=" in user_input:
        # Parse the URL to extract code parameter
        if user_input.startswith("http"):
            # Full URL
            parsed = urllib.parse.urlparse(user_input)
            params = urllib.parse.parse_qs(parsed.query)
        else:
            # Just query string
            params = urllib.parse.parse_qs(user_input)
        
        if "code" in params and params["code"]:
            code = params["code"][0]  # Get first code value
            print(f"✅ Extracted code: {code[:50]}...")
        else:
            print("❌ Could not find 'code' parameter in URL.")
            return
    
    # URL-decode the code if it contains encoded characters
    if "%" in code:
        code = urllib.parse.unquote(code)
        print(f"✅ URL-decoded code: {code[:50]}...")

    # Step 3: Exchange code for tokens
    print("\n🔄 Exchanging authorization code for tokens...")
    print(f"   Using redirect_uri: {redirect_uri}")
    try:
        token_response = oauth.exchange_authorization_code(
            client_id=client_id,
            client_secret=client_secret,
            code=code,
            redirect_uri=redirect_uri,  # Must match what was used in auth URL
            environment=environment,
        )

        access_token = token_response.get("access_token")
        refresh_token = token_response.get("refresh_token")
        expires_in = token_response.get("expires_in", 7200)

        if not access_token:
            print("❌ Access token not found in response.")
            return

        if not refresh_token:
            print("⚠️  Warning: Refresh token not found in response.")
            print("   You may need to request offline_access scope or check your app settings.")

        print("\n" + "=" * 70)
        print("✅ Success! Add these to your .env file:")
        print("=" * 70)
        print(f"\nEBAY_USER_ACCESS_TOKEN={access_token}")
        print("\n")
        if refresh_token:
            print(f"EBAY_USER_REFRESH_TOKEN={refresh_token}")
        print("=" * 70)

        print(f"\n📝 Token Details:")
        print(f"   • Access token expires in: {expires_in / 3600:.1f} hours")
        if refresh_token:
            print(f"   • Refresh token lasts: ~18 months")
            print(f"   • SDK will automatically refresh when access token expires!")
        else:
            print(f"   • ⚠️  No refresh token - you'll need to re-run this script when token expires")

        print("\n✨ You're all set! Your SDK will now handle token refresh automatically.")

    except Exception as exc:
        error_msg = str(exc)
        print(f"\n❌ Failed to exchange authorization code: {error_msg}")
        
        # Try to get more details from the response
        if hasattr(exc, 'response') and exc.response is not None:
            try:
                error_detail = exc.response.json()
                print(f"\n📋 Error details: {error_detail}")
            except:
                try:
                    error_text = exc.response.text
                    if error_text:
                        print(f"\n📋 Error response: {error_text[:200]}")
                except:
                    pass
        
        print("\n💡 Troubleshooting:")
        print("   • Check that EBAY_REDIRECT_URI matches exactly what's registered in eBay Developer Portal")
        print("   • Verify the authorization code hasn't expired (codes expire in ~5 minutes)")
        print("   • Ensure EBAY_CLIENT_ID and EBAY_CLIENT_SECRET are correct")
        print("   • Make sure you're using the same redirect_uri that was used in the authorization URL")
        print("   • Try generating a new authorization code (they expire quickly)")


if __name__ == "__main__":
    main()

