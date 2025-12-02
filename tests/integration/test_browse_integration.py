"""Integration tests for Browse API."""

import pytest

from ebay_rest.errors import NotFoundError


@pytest.mark.integration
@pytest.mark.requires_credentials
class TestBrowseIntegration:
    """Integration tests for Browse API with real sandbox."""

    def test_search_items_real_api(self, sandbox_client):
        """Test search_items with real eBay sandbox API."""
        results = sandbox_client.browse.search_items(query="laptop", limit=5)

        # Verify response structure
        assert "items" in results or "itemSummaries" in results
        assert "total" in results

        # Get items list (handle both response formats)
        items = results.get("items", results.get("itemSummaries", []))

        # Should have some results (sandbox may have limited data)
        assert isinstance(items, list)
        assert results.get("total", 0) >= 0

        # If items exist, verify structure
        if len(items) > 0:
            item = items[0]
            assert "item_id" in item or "itemId" in item
            assert "title" in item

    def test_search_items_with_limit(self, sandbox_client):
        """Test search_items with specific limit."""
        results = sandbox_client.browse.search_items(query="phone", limit=3)

        items = results.get("items", results.get("itemSummaries", []))
        assert len(items) <= 3

    def test_search_items_with_offset(self, sandbox_client):
        """Test search_items with pagination offset."""
        # Get first page
        results1 = sandbox_client.browse.search_items(query="book", limit=5, offset=0)
        items1 = results1.get("items", results1.get("itemSummaries", []))

        # Get second page
        if len(items1) > 0:
            results2 = sandbox_client.browse.search_items(query="book", limit=5, offset=5)
            items2 = results2.get("items", results2.get("itemSummaries", []))

            # Items should be different (or empty if no more results)
            assert isinstance(items2, list)

    def test_get_item_real_api(self, sandbox_client):
        """Test get_item with real item ID from search."""
        # First, search for an item
        results = sandbox_client.browse.search_items(query="laptop", limit=1)
        items = results.get("items", results.get("itemSummaries", []))

        if len(items) > 0:
            # Get item ID (handle both formats)
            item_id = items[0].get("item_id") or items[0].get("itemId")

            # Get full item details
            item_details = sandbox_client.browse.get_item(item_id=item_id)

            # Verify response structure
            assert "item_id" in item_details or "itemId" in item_details
            assert "title" in item_details

            # Verify it's the same item
            retrieved_id = item_details.get("item_id") or item_details.get("itemId")
            assert retrieved_id == item_id
        else:
            pytest.skip("No items found in sandbox to test get_item")

    def test_get_item_invalid_id(self, sandbox_client):
        """Test get_item with invalid item ID raises NotFoundError."""
        with pytest.raises(NotFoundError):
            sandbox_client.browse.get_item(item_id="invalid_item_id_12345")

    def test_search_items_empty_query_validation(self, sandbox_client):
        """Test that empty query raises ValueError."""
        with pytest.raises(ValueError, match="Search query cannot be empty"):
            sandbox_client.browse.search_items(query="")

    def test_search_items_invalid_limit_validation(self, sandbox_client):
        """Test that invalid limit raises ValueError."""
        with pytest.raises(ValueError, match="Limit must be between 1 and 200"):
            sandbox_client.browse.search_items(query="test", limit=0)

        with pytest.raises(ValueError, match="Limit must be between 1 and 200"):
            sandbox_client.browse.search_items(query="test", limit=201)

    def test_search_items_response_structure(self, sandbox_client):
        """Test that search response has expected structure."""
        results = sandbox_client.browse.search_items(query="camera", limit=10)

        # Check required fields
        assert "total" in results
        assert isinstance(results["total"], int)
        assert results["total"] >= 0

        # Check items/itemSummaries
        items = results.get("items", results.get("itemSummaries", []))
        assert isinstance(items, list)

        # If items exist, check structure
        if len(items) > 0:
            item = items[0]
            # Should have at least item_id/itemId and title
            assert "item_id" in item or "itemId" in item
            assert "title" in item

