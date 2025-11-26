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
- ✅ **Helper scripts** (`simple_*_test.py`) to validate credentials quickly
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
python simple_browse_test.py           # smoke test browse API
```

### Minimal usage

```python
from ebay_rest import EbayClient

client = EbayClient(
    client_id="YOUR_SANDBOX_APP_ID",
    client_secret="YOUR_SANDBOX_CERT_ID",
    sandbox=True,
)

items = client.browse.search_items(query="laptop", limit=5)
print(items["items"][0]["title"])
```

## Environment & Configuration

| Variable             | Description                                |
|----------------------|--------------------------------------------|
| `EBAY_CLIENT_ID`     | Your sandbox/production App ID (client_id) |
| `EBAY_CLIENT_SECRET` | Your Cert ID (client_secret)               |
| `EBAY_PROD_*`        | Optional production credentials (future)   |

- Store them in `.env` (already gitignored).  
- Helper scripts automatically call `dotenv.load_dotenv()`.
- `simple_auth_test.py`, `simple_browse_test.py`, `simple_orders_test.py` provide quick verification.

### OAuth scopes

- Default scope: `https://api.ebay.com/oauth/api_scope` (Buy APIs)
- Sell Fulfillment requires `https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly`
- eBay must approve Sell API access for your app. Request it in the developer portal → Application Keys → “Add APIs”.
- Without Sell scope approval you’ll see “Access denied” when calling Orders endpoints.

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

## API Coverage

| Module     | Status | Notes |
|------------|--------|-------|
| Auth       | ✅     | Client credentials grant with multi-scope support |
| BaseClient | ✅     | Shared HTTP client w/ error mapping |
| Browse     | ✅     | `search_items`, `get_item` tested against sandbox |
| Orders     | ⚠️     | Implemented, requires Sell Fulfillment scope + sandbox data |
| Inventory  | 🚧     | Client + models stubbed (implementation next) |
| Account    | 🚧     | Client + models stubbed |
| Pagination | 🚧     | Utility planned |

## Roadmap

- [x] Auth + Base client
- [x] Browse API (search + item details)
- [x] Orders API (list + get)
- [ ] Inventory API implementation
- [ ] Account API implementation
- [ ] Pagination helpers
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

