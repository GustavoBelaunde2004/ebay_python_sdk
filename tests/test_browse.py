"""Tests for Browse API client."""

from unittest.mock import MagicMock

import pytest

from ebay_rest.browse.client import BrowseClient
from ebay_rest.errors import NotFoundError, ValidationError


class TestBrowseClient:
    """Test suite for BrowseClient."""

    def test_init(self, mock_base_client, sandbox_flag: bool):
        """Test BrowseClient initialization."""
        client = BrowseClient(base_client=mock_base_client, sandbox=sandbox_flag)
        assert client.base_client == mock_base_client
        assert client.sandbox == sandbox_flag

    def test_search_items_success(self, mock_base_client, sandbox_flag: bool):
        """Test successful item search."""
        mock_base_client.get = MagicMock(
            return_value={
                "itemSummaries": [
                    {
                        "itemId": "123456",
                        "title": "Test Item",
                        "price": {"value": "99.99", "currency": "USD"},
                    }
                ],
                "total": 1,
                "offset": 0,
                "limit": 50,
            }
        )
        client = BrowseClient(base_client=mock_base_client, sandbox=sandbox_flag)

        result = client.search_items(query="test", limit=50, offset=0)

        mock_base_client.get.assert_called_once_with(
            "/buy/browse/v1/item_summary/search",
            params={"q": "test", "limit": 50, "offset": 0},
        )
        assert "items" in result or "itemSummaries" in result

    def test_search_items_with_category_ids(self, mock_base_client, sandbox_flag: bool):
        """Test search items with category filtering."""
        mock_base_client.get = MagicMock(
            return_value={
                "itemSummaries": [],
                "total": 0,
                "offset": 0,
                "limit": 10,
            }
        )
        client = BrowseClient(base_client=mock_base_client, sandbox=sandbox_flag)

        result = client.search_items(query="laptop", category_ids=["12345", "67890"], limit=10)

        mock_base_client.get.assert_called_once()
        call_args = mock_base_client.get.call_args
        assert call_args[1]["params"]["category_ids"] == "12345,67890"

    def test_search_items_invalid_query(self, mock_base_client, sandbox_flag: bool):
        """Test search items with empty query raises ValueError."""
        client = BrowseClient(base_client=mock_base_client, sandbox=sandbox_flag)

        with pytest.raises(ValueError, match="Search query cannot be empty"):
            client.search_items(query="")

        with pytest.raises(ValueError, match="Search query cannot be empty"):
            client.search_items(query="   ")

    def test_search_items_invalid_limit(self, mock_base_client, sandbox_flag: bool):
        """Test search items with invalid limit raises ValueError."""
        client = BrowseClient(base_client=mock_base_client, sandbox=sandbox_flag)

        with pytest.raises(ValueError, match="Limit must be between 1 and 200"):
            client.search_items(query="test", limit=0)

        with pytest.raises(ValueError, match="Limit must be between 1 and 200"):
            client.search_items(query="test", limit=201)

    def test_search_items_invalid_offset(self, mock_base_client, sandbox_flag: bool):
        """Test search items with invalid offset raises ValueError."""
        client = BrowseClient(base_client=mock_base_client, sandbox=sandbox_flag)

        with pytest.raises(ValueError, match="Offset must be >= 0"):
            client.search_items(query="test", offset=-1)

    def test_search_items_empty_results(self, mock_base_client, sandbox_flag: bool):
        """Test search with no results."""
        mock_base_client.get = MagicMock(
            return_value={
                "itemSummaries": [],
                "total": 0,
                "offset": 0,
                "limit": 50,
            }
        )
        client = BrowseClient(base_client=mock_base_client, sandbox=sandbox_flag)

        result = client.search_items(query="nonexistentitemxyz123", limit=50)

        assert result.get("total", 0) == 0
        items = result.get("items", result.get("itemSummaries", []))
        assert len(items) == 0

    def test_get_item_success(self, mock_base_client, sandbox_flag: bool):
        """Test successful get item by ID."""
        item_id = "123456"
        mock_base_client.get = MagicMock(
            return_value={
                "itemId": item_id,
                "title": "Test Item",
                "price": {"value": "99.99", "currency": "USD"},
                "categoryPath": "Electronics > Computers",
            }
        )
        client = BrowseClient(base_client=mock_base_client, sandbox=sandbox_flag)

        result = client.get_item(item_id=item_id)

        mock_base_client.get.assert_called_once_with(f"/buy/browse/v1/item/{item_id}")
        assert "item_id" in result or "itemId" in result

    def test_get_item_empty_id(self, mock_base_client, sandbox_flag: bool):
        """Test get item with empty item_id raises ValueError."""
        client = BrowseClient(base_client=mock_base_client, sandbox=sandbox_flag)

        with pytest.raises(ValueError, match="Item ID cannot be empty"):
            client.get_item(item_id="")

        with pytest.raises(ValueError, match="Item ID cannot be empty"):
            client.get_item(item_id="   ")

