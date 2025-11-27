# ebay-rest · Modern Python SDK for eBay REST APIs

[![Tests](https://img.shields.io/github/actions/workflow/status/yourusername/ebay-rest/tests.yml?label=tests)](#)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](#)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> Batteries-included toolkit for building Python apps on top of eBay’s REST APIs (Buy + Sell).  
> Handles OAuth2, HTTP plumbing, typed models, and provides friendly client classes.

---

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Quick Start](#quick-start)
- [Environment & Configuration](#environment--configuration)
- [Usage Examples](#usage-examples)
- [API Coverage](#api-coverage)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- ✅ **OAuth2 client credentials** with automatic refresh, token caching, and scope management
- ✅ **Base HTTP client** that injects auth headers, handles errors, and parses JSON
- ✅ **Browse API** (search items + get item details) verified against sandbox
- ✅ **Orders API** client (list + get order) with typed models  
  ⚠ requires Sell Fulfillment scope + sandbox orders
- ✅ **Helper scripts** (`examples/example_*_test.py`) to validate credentials quickly
- 🚧 **Inventory / Account clients** stubbed and ready for implementation
- 🚧 **Pagination helper** placeholder for iterating large result sets

## Architecture Overview

```
┌─────────────┐
│ EbayClient  │  ← entry point
└────┬────────┘
     │ creates once
┌────▼────────┐
│ BaseClient  │  ← auth, requests, error mapping
└────┬────────┘
     ├───────────────────────────────┐
┌────▼─────┐  ┌──────▼─────┐  ┌──────▼──────┐  ┌──────▼──────┐
│ Browse   │  │ Orders     │  │ Inventory   │  │ Account      │
│ Client   │  │ Client     │  │ Client*     │  │ Client*      │
└──────────┘  └────────────┘  └─────────────┘  └─────────────┘
                                          *implementation in progress
```

- `OAuth2Client` fetches tokens (Buy scope + Sell Fulfillment scope if granted)
- `BaseClient` centralizes GET/POST/PUT/DELETE with consistent headers + exceptions
- Each API module receives the shared `BaseClient`

## Quick Start

```bash
git clone https://github.com/yourusername/ebay-rest.git
cd ebay-rest
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate
pip install -e ".[dev]"
cp ENV_TEMPLATE.txt .env && edit .env  # add EBAY_CLIENT_ID / SECRET
python examples/example_browse_test.py # smoke test browse API
```

### Minimal usage

```python
from ebay_rest import EbayClient

client = EbayClient(
    client_id="YOUR_SANDBOX_APP_ID",
    client_secret="YOUR_SANDBOX_CERT_ID",
    sandbox=True,
    # Optional: provide a user access token (Sell APIs)
    user_access_token=os.getenv("EBAY_USER_ACCESS_TOKEN"),
)

items = client.browse.search_items(query="laptop", limit=5)
print(items["items"][0]["title"])
```

## Environment & Configuration

| Variable                | Description                                                             |
|-------------------------|-------------------------------------------------------------------------|
| `EBAY_CLIENT_ID`        | Your sandbox/production App ID (client_id)                              |
| `EBAY_CLIENT_SECRET`    | Your Cert ID (client_secret)                                            |
| `EBAY_USER_ACCESS_TOKEN`| Optional user token for Sell APIs (from Authorization Code flow)        |
| `EBAY_REDIRECT_URI`     | URL-encoded Redirect URI (RuName) registered in eBay Developer Portal   |
| `EBAY_OAUTH_SCOPES`     | Space-delimited scopes for user consent (e.g. `https://.../sell.inventory`) |
| `EBAY_ENV`              | `sandbox` (default) or `production` for OAuth helpers                   |
| `EBAY_PROD_*`           | Optional production credentials (future)                                |

- Store them in `.env` (already gitignored).  
- Helper scripts automatically call `dotenv.load_dotenv()`.
- `examples/example_auth_test.py`, `examples/example_browse_test.py`, `examples/example_inventory_test.py`, `examples/example_orders_test.py` provide quick verification.

### OAuth scopes

- **Buy scope** (default, included): `https://api.ebay.com/oauth/api_scope`
- **Sell Fulfillment** (orders): `https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly`
- **Sell Inventory** (inventory): `https://api.ebay.com/oauth/api_scope/sell.inventory.readonly`
- **Sell Account** (privileges/programs): `https://api.ebay.com/oauth/api_scope/sell.account.readonly`

> Client credentials tokens only cover Buy APIs. For Sell APIs you must obtain a **user access token**
> via the Authorization Code flow. Each seller runs through consent once; store their refresh token.

### Obtaining a Sell API user token

1. In the eBay Developer Portal, register a redirect URI (RuName) for your app. Note the encoded value.
2. Create a sandbox seller user if you haven't already:
   - Portal path: **Develop → Tools → eBay Sandbox → Create Test Users**
   - Choose “Seller” type, set a password via “Sandbox User Password” tool.
3. Set these env vars:
   ```
   EBAY_CLIENT_ID=YourSandboxAppID
   EBAY_CLIENT_SECRET=YourSandboxCertID
   EBAY_REDIRECT_URI=YourEncodedRuName
   EBAY_OAUTH_SCOPES="https://api.ebay.com/oauth/api_scope/sell.inventory https://api.ebay.com/oauth/api_scope/sell.fulfillment"
   ```
4. Run the helper script:
   ```bash
   python scripts/oauth_authorize.py
   ```
   It prints a consent URL. Open it, log in as your sandbox seller, and paste the returned `code`.
5. Alternatively, you can grab a sandbox user token from **Application Keys → Sandbox App → “User Tokens”** (uses eBay’s hosted OAuth UI).
6. The script outputs an access token + refresh token. Store them securely (e.g., `.env` using `EBAY_USER_ACCESS_TOKEN`).
6. Pass the access token to `EbayClient` (or call `client.set_user_access_token()`).

When the access token expires, call `oauth.refresh_user_token()` with the refresh token to get a new one.

## Usage Examples

### Browse search + get item

```python
results = client.browse.search_items(query="mirrorless camera", limit=3)
for item in results["items"]:
    print(item["title"], item.get("price", {}).get("value"))

item_id = results["items"][0]["item_id"]
details = client.browse.get_item(item_id=item_id)
print(details["category_path"])
```

### Orders (requires Sell Fulfillment scope)

```python
orders = client.orders.list_orders(limit=10)
if orders["orders"]:
    first_order_id = orders["orders"][0]["order_id"]
    order = client.orders.get_order(order_id=first_order_id)
    print(order["buyer"]["username"])
else:
    print("No orders yet. Create sandbox orders to exercise this API.")
```

### Inventory (requires Sell Inventory scope)

```python
inventory = client.inventory.list_inventory_items(limit=10)
if inventory["inventory_items"]:
    first_sku = inventory["inventory_items"][0]["sku"]
    item = client.inventory.get_inventory_item(sku=first_sku)
    print(item["availability"]["ship_to_location_availability"]["quantity"])

client.inventory.create_inventory_item(
    sku="DEMO-SKU-001",
    inventory_item={
        "condition": "NEW",
        "product": {"title": "Demo Widget"},
        "availability": {"shipToLocationAvailability": {"quantity": 5}},
    },
)
```

> Tip: call `client.set_user_access_token("...")` at runtime if you fetch the user token elsewhere.

### Pagination helper

```python
from ebay_rest.pagination import paginate

for item in paginate(
    client.inventory.list_inventory_items,
    limit=100,              # total items to yield
    items_key="inventory_items",
    limit_param="limit",
):
    print(item["sku"])
```

## API Coverage

| Module     | Status | Notes |
|------------|--------|-------|
| Auth       | ✅     | Client credentials grant with multi-scope support |
| BaseClient | ✅     | Shared HTTP client w/ error mapping |
| Browse     | ✅     | `search_items`, `get_item` tested against sandbox |
| Orders     | ⚠️     | Implemented, requires Sell Fulfillment scope + sandbox data |
| Inventory  | ⚠️     | get/list/create inventory item implemented (requires Sell Inventory scope) |
| Account    | ⚠️     | privilege profile endpoint implemented (requires Sell Account scope) |
| Pagination | ✅     | Generator + iterator helpers |

## Roadmap

- [x] Auth + Base client
- [x] Browse API (search + item details)
- [x] Orders API (list + get)
- [x] Inventory API implementation
- [x] Account API implementation
- [x] Pagination helpers
- [ ] Unit tests + CI validation
- [ ] Async client
- [ ] Publish to PyPI

## Contributing

1. Fork repo, create feature branch.
2. Install dev deps: `pip install -e ".[dev]"`
3. Run tests / linters:
   ```bash
   pytest
   ruff check .
   black .
   mypy ebay_rest
   ```
4. Submit PR with description + screenshots/logs when relevant.

Bug reports and feature requests welcome via GitHub Issues.

## License

MIT © Gustavo Belaunde. See [LICENSE](LICENSE) for details.

## Credits

- Built with ❤️ using [eBay REST APIs](https://developer.ebay.com/api-docs)
- Inspired by SDK patterns from Stripe, Supabase, AWS

