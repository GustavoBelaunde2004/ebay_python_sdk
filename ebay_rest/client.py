"""Main client class for eBay REST API SDK."""

from ebay_rest.account.client import AccountClient
from ebay_rest.auth import OAuth2Client
from ebay_rest.base_client import BaseClient
from ebay_rest.browse.client import BrowseClient
from ebay_rest.inventory.client import InventoryClient
from ebay_rest.orders.client import OrdersClient


class EbayClient:
    """
    Main client for eBay REST API.

    Provides access to all eBay API modules: Browse, Inventory, Orders, and Account.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        sandbox: bool = False,
        user_access_token: str | None = None,
        user_refresh_token: str | None = None,
        user_token_scopes: list[str] | None = None,
    ):
        """
        Initialize eBay client.

        Args:
            client_id: eBay application client ID
            client_secret: eBay application client secret
            sandbox: Whether to use sandbox environment (default: False)
            user_access_token: Optional user access token for Sell APIs
            user_refresh_token: Optional refresh token for automatic token refresh
            user_token_scopes: Optional list of OAuth scopes for token refresh.
                Defaults to common Sell API scopes if not provided.
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.sandbox = sandbox

        # Initialize OAuth2 client
        self.auth = OAuth2Client(
            client_id=client_id,
            client_secret=client_secret,
            sandbox=sandbox,
        )

        # TODO: Set base URLs based on sandbox flag
        # Production: https://api.ebay.com
        # Sandbox: https://api.sandbox.ebay.com

        # Initialize base HTTP client
        base_url = "https://api.sandbox.ebay.com" if sandbox else "https://api.ebay.com"
        self.base_client = BaseClient(
            auth_client=self.auth,
            base_url=base_url,
            sandbox=sandbox,
            user_access_token=user_access_token,
            user_refresh_token=user_refresh_token,
            user_token_scopes=user_token_scopes,
            client_id=client_id,
            client_secret=client_secret,
        )

        # Initialize API module clients
        self.browse = BrowseClient(base_client=self.base_client, sandbox=sandbox)
        self.inventory = InventoryClient(base_client=self.base_client, sandbox=sandbox)
        self.orders = OrdersClient(base_client=self.base_client, sandbox=sandbox)
        self.account = AccountClient(base_client=self.base_client, sandbox=sandbox)

    def set_user_access_token(
        self,
        token: str | None,
        refresh_token: str | None = None,
        scopes: list[str] | None = None,
    ) -> None:
        """
        Override the access token used for Sell APIs.

        Pass a user token obtained via the Authorization Code flow to call
        seller endpoints (inventory, orders, account). Pass None to revert
        to application (client-credentials) tokens.

        Args:
            token: User access token string or None to revert to client credentials
            refresh_token: Optional refresh token for automatic token refresh
            scopes: Optional list of OAuth scopes for token refresh
        """
        self.base_client.set_user_access_token(token, refresh_token=refresh_token, scopes=scopes)

