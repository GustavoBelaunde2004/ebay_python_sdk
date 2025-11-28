# ebay-rest · Modern Python SDK for eBay REST APIs

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

- ✅ **OAuth2 Authentication** - Client credentials grant with automatic token refresh, caching, and multi-scope support
- ✅ **OAuth Authorization Code Flow** - Helper utilities for obtaining user tokens for Sell APIs
- ✅ **Base HTTP Client** - Centralized GET/POST/PUT/DELETE with automatic auth headers, error mapping, and JSON parsing
- ✅ **Browse API** - Search items and retrieve detailed item information (tested against sandbox)
- ✅ **Orders API** - List and retrieve seller orders with typed Pydantic models
- ✅ **Inventory API** - Full CRUD operations for inventory items including bulk operations
- ✅ **Account API** - Access account profiles, privileges, and policy management
- ✅ **Pagination Helper** - Generator and iterator utilities for seamless pagination across large result sets
- ✅ **Type-Safe Models** - Pydantic models for all API responses with automatic validation
- ✅ **Comprehensive Tests** - 46 unit tests covering all major functionality
- ✅ **Example Scripts** - Ready-to-run examples for each API module

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
│ Client   │  │ Client     │  │ Client      │  │ Client       │
└──────────┘  └────────────┘  └─────────────┘  └─────────────┘
```

- `OAuth2Client` handles token management (Client Credentials grant for Buy APIs)
- `oauth` module provides Authorization Code flow helpers for Sell APIs
- `BaseClient` centralizes HTTP operations with consistent error handling
- Each API client receives the shared `BaseClient` for making authenticated requests

## Quick Start

```bash
git clone https://github.com/GustavoBelaunde2004/ebay-rest.git
cd ebay-rest
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate
pip install -e ".[dev]"
cp ENV_TEMPLATE.txt .env && edit .env  # add EBAY_CLIENT_ID / SECRET
python examples/example_browse_test.py # smoke test browse API
```

### Minimal usage

```python
from ebay_rest import EbayClient
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

client = EbayClient(
    client_id=os.getenv("EBAY_CLIENT_ID"),
    client_secret=os.getenv("EBAY_CLIENT_SECRET"),
    sandbox=True,
    # Optional: provide a user access token for Sell APIs
    user_access_token=os.getenv("EBAY_USER_ACCESS_TOKEN"),
)

# Browse API: Search for items
results = client.browse.search_items(query="laptop", limit=10)
print(f"Found {results.get('total', 0)} items:")
for item in results.get('items', [])[:3]:
    print(f"- {item.get('title')} (${item.get('price', {}).get('value')})")
```

## Environment & Configuration

| Variable                 | Description                                                              |
|--------------------------|--------------------------------------------------------------------------|
| `EBAY_CLIENT_ID`         | Your sandbox/production App ID (client_id)                               |
| `EBAY_CLIENT_SECRET`     | Your Cert ID (client_secret)                                             |
| `EBAY_USER_ACCESS_TOKEN` | Optional user token for Sell APIs (from Authorization Code flow)         |
| `EBAY_REDIRECT_URI`      | URL-encoded Redirect URI (RuName) registered in eBay Developer Portal    |
| `EBAY_OAUTH_SCOPES`      | Space-delimited scopes for user consent (e.g. `https://.../sell.inventory`) |
| `EBAY_ENV`               | `sandbox` (default) or `production` for OAuth helpers                    |

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
4. Alternatively, you can grab a sandbox user token from **Application Keys → Sandbox App → “User Tokens”** (uses eBay’s hosted OAuth UI).
5. The script outputs an access token + refresh token. Store them securely (e.g., `.env` using `EBAY_USER_ACCESS_TOKEN`).
6. Pass the access token to `EbayClient` (or call `client.set_user_access_token()`).

When the access token expires, call `oauth.refresh_user_token()` with the refresh token to get a new one.

### Sandbox data checklist

After the seller token is ready, populate the sandbox so Sell APIs have something to return:

1. **Create inventory items**
   - Log into [Sandbox Seller Hub](https://sandbox.ebay.com/) with your seller account.
   - Use the Inventory API (`examples/example_inventory_test.py`) or Seller Hub to add SKUs.
2. **Create sample offers/listings**
   - From Seller Hub → Listings → Create listing.
   - Keep note of SKU/item IDs for testing.
3. **Place sample orders**
   - Create a sandbox buyer account (Develop → Tools → eBay Sandbox → Create Test Users).
   - Sign in as the buyer, purchase the seller’s items (sandbox checkout uses fake funds).
4. **Record useful IDs**
   - SKU(s), offer IDs, order IDs for quick regression tests.

## Development & Testing

```bash
# install dependencies in editable mode
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# run automated tests (46 unit tests)
pytest

# lint / format
ruff check .
black .

# type checking
mypy ebay_rest
```

- **Unit tests**: 46 tests covering all API clients, auth, OAuth, and pagination
- **Manual testing**: Use scripts in `examples/` for integration testing with sandbox
- **Test structure**: All tests use mocks for fast, reliable testing

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
# List inventory items
inventory = client.inventory.list_inventory_items(limit=10)
if inventory["inventory_items"]:
    first_sku = inventory["inventory_items"][0]["sku"]
    item = client.inventory.get_inventory_item(sku=first_sku)
    print(item["availability"]["ship_to_location_availability"]["quantity"])

# Create a new inventory item
client.inventory.create_inventory_item(
    sku="DEMO-SKU-001",
    inventory_item={
        "condition": "NEW",
        "product": {"title": "Demo Widget"},
        "availability": {"shipToLocationAvailability": {"quantity": 5}},
    },
)

# Bulk create/update multiple items
client.inventory.bulk_create_or_replace_inventory_item([
    {"sku": "SKU-001", "condition": "NEW", "product": {"title": "Item 1"}},
    {"sku": "SKU-002", "condition": "USED", "product": {"title": "Item 2"}},
])
```

### Account (requires Sell Account scope)

```python
# Get account profile and privileges
profile = client.account.get_account_profile()
print(f"Account type: {profile['account_type']}")

# List return policies
return_policies = client.account.list_return_policies(marketplace_id="EBAY_US")

# List payment policies
payment_policies = client.account.list_payment_policies(marketplace_id="EBAY_US")

# List shipping policies
shipping_policies = client.account.list_shipping_policies(marketplace_id="EBAY_US")
```

> Tip: call `client.set_user_access_token("...")` at runtime if you fetch the user token elsewhere.

### Pagination helper

```python
from ebay_rest.pagination import paginate

# Iterate through all items automatically
for item in paginate(
    client.browse.search_items,
    query="laptop",
    limit=100,              # total items to yield
    items_key="items",
    limit_param="limit",
    offset_param="offset",
):
    print(item["title"])
```

See `examples/example_pagination.py` for a runnable demo.

## API Coverage

| Module     | Status | Methods                                                                       |
|------------|--------|-------------------------------------------------------------------------------|
| Auth       | ✅     | `OAuth2Client` - Client credentials grant with automatic token refresh        |
| OAuth      | ✅     | Authorization Code flow helpers (`build_authorization_url`, `exchange_code_for_token`, `refresh_user_token`) |
| BaseClient | ✅     | Shared HTTP client with error mapping (GET, POST, PUT, DELETE)                |
| Browse     | ✅     | `search_items`, `get_item` - Tested against sandbox                          |
| Orders     | ✅     | `list_orders`, `get_order` - Requires Sell Fulfillment scope + user token     |
| Inventory  | ✅     | `get_inventory_item`, `list_inventory_items`, `create_inventory_item`, `update_inventory_item`, `delete_inventory_item`, `bulk_create_or_replace_inventory_item` |
| Account    | ✅     | `get_account_profile`, `get_account_privileges`, `list_return_policies`, `list_payment_policies`, `list_shipping_policies` |
| Pagination | ✅     | `paginate()` generator function and `Paginator` class                         |

## Roadmap

- [x] Auth + Base client
- [x] Browse API (search + item details)
- [x] Orders API (list + get)
- [x] Inventory API (full CRUD + bulk operations)
- [x] Account API (profile + policies)
- [x] Pagination helpers
- [x] OAuth Authorization Code flow helpers
- [x] Comprehensive unit test coverage
- [ ] Additional Inventory & Account endpoints (offers, listings, etc.)
- [ ] Integration tests with real API calls
- [ ] BaseClient unit tests
- [ ] Code coverage reporting
- [ ] Async client support
- [ ] Publish to PyPI

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines. In short:

1. Fork the repo and create a feature branch.
2. Install dev dependencies (`pip install -e ".[dev]"`).
3. Run the checks before opening a PR:
   ```bash
   pytest
   ruff check .
   black .
   mypy ebay_rest
   ```
4. Describe how to exercise the change (especially if it touches Sell APIs / sandbox data).

Bug reports and feature requests are welcome via GitHub Issues.

## License

MIT © Gustavo Belaunde. See [LICENSE](LICENSE) for details.

## Credits

- Built with ❤️ using [eBay REST APIs](https://developer.ebay.com/api-docs)
- Inspired by SDK patterns from Stripe, Supabase, AWS

