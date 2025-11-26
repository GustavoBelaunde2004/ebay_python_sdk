# ebay-rest

A modern, professional Python SDK for eBay's REST APIs.

## Features

- **OAuth2 Authentication**: Secure token management and automatic refresh
- **Type-Safe Models**: Pydantic models for all API responses
- **Multiple API Support**: Browse, Inventory, Orders, and Account APIs
- **Error Handling**: Comprehensive exception hierarchy for different error scenarios
- **Pagination Support**: Built-in helpers for iterating through paginated results
- **Production Ready**: Clean architecture, comprehensive tests, and CI/CD

## Installation

```bash
# TODO: Update once published to PyPI
pip install ebay-rest
```

For development:

```bash
pip install -e ".[dev]"
```

## Getting Started

### Basic Usage

```python
from ebay_rest import EbayClient

# Initialize the client
client = EbayClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    sandbox=True  # Use sandbox environment
)

# Search for items
items = client.browse.search_items(query="laptop", limit=10)

# Get item details
item = client.browse.get_item(item_id="123456789")

# List orders
orders = client.orders.list_orders(limit=50)
```

### Environment Setup

```python
# TODO: Add environment variable examples
# Set EBAY_CLIENT_ID and EBAY_CLIENT_SECRET
```

## API Modules

### Browse API

Search and retrieve item information from eBay's catalog.

```python
# TODO: Add detailed examples
items = client.browse.search_items(query="vintage camera", limit=20)
item = client.browse.get_item(item_id="item_id_here")
```

### Inventory API

Manage your inventory items.

```python
# TODO: Add detailed examples
inventory_item = client.inventory.get_inventory_item(sku="SKU123")
items = client.inventory.list_inventory_items(limit=100)
```

### Orders API

Retrieve and manage orders.

```python
# TODO: Add detailed examples
orders = client.orders.list_orders(limit=50)
```

### Account API

Access account-related information.

```python
# TODO: Add detailed examples
```

## Error Handling

```python
from ebay_rest.errors import AuthError, NotFoundError, RateLimitExceeded

try:
    item = client.browse.get_item(item_id="123")
except NotFoundError:
    print("Item not found")
except RateLimitExceeded:
    print("Rate limit exceeded, please retry later")
except AuthError:
    print("Authentication failed")
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy ebay_rest/
```

## Documentation

- [Full API Documentation](https://github.com/yourusername/ebay-rest#readme) - TODO: Link to full docs
- [eBay API Documentation](https://developer.ebay.com/api-docs) - Official eBay API docs

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

## License

MIT License - see LICENSE file for details

## Status

⚠️ **This project is currently in development** - The SDK structure is complete, but implementation is in progress. See TODO comments in code for areas needing implementation.

## Roadmap

- [ ] Complete OAuth2 authentication implementation
- [ ] Implement all Browse API endpoints
- [ ] Implement all Inventory API endpoints
- [ ] Implement all Orders API endpoints
- [ ] Implement all Account API endpoints
- [ ] Add async/await support
- [ ] Comprehensive test coverage
- [ ] Full documentation with examples

