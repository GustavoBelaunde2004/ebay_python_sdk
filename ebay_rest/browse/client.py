"""Browse API client for searching and retrieving items."""

from typing import Any, Optional

from ebay_rest.base_client import BaseClient
from ebay_rest.browse.models import Item, ItemSummary, SearchResponse


class BrowseClient:
    """
    Client for eBay Browse API.

    Provides methods to search for items and retrieve item details.
    """

    def __init__(self, base_client: BaseClient, sandbox: bool = False):
        """
        Initialize Browse API client.

        Args:
            base_client: BaseClient instance for making HTTP requests
            sandbox: Whether to use sandbox environment
        """
        self.base_client = base_client
        self.sandbox = sandbox

    def search_items(
        self,
        query: str,
        limit: int = 50,
        offset: int = 0,
        category_ids: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Search for items on eBay.

        Args:
            query: Search query string
            limit: Maximum number of results to return (default: 50, max: 200)
            offset: Number of results to skip (for pagination)
            category_ids: Optional list of category IDs to filter by
            **kwargs: Additional query parameters (filter, sort, aspect_filter, etc.)

        Returns:
            Dictionary containing search results with items list and pagination info

        Raises:
            ValidationError: If parameters are invalid
            EbayAPIError: If the search request fails
        """
        # Validate parameters
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")

        if limit < 1 or limit > 200:
            raise ValueError("Limit must be between 1 and 200")

        if offset < 0:
            raise ValueError("Offset must be >= 0")

        # Build query parameters
        params: dict[str, Any] = {
            "q": query.strip(),
            "limit": limit,
            "offset": offset,
        }

        # Handle category_ids
        if category_ids:
            # eBay API accepts category_ids as comma-separated string or array
            # Using comma-separated string for compatibility
            params["category_ids"] = ",".join(str(cat_id) for cat_id in category_ids)

        # Add any additional parameters from kwargs
        params.update(kwargs)

        # Build endpoint path
        endpoint = "/buy/browse/v1/item_summary/search"

        # Make API call
        response_data = self.base_client.get(endpoint, params=params)

        # Parse response into SearchResponse model
        # Handle both camelCase (eBay API) and snake_case (our models)
        try:
            search_response = SearchResponse(**response_data)
            # Convert back to dict for flexibility, but with parsed items
            return {
                "items": [item.model_dump() for item in search_response.items],
                "total": search_response.total,
                "offset": search_response.offset,
                "limit": search_response.limit,
                "href": search_response.href,
                "next": search_response.next,
                "prev": search_response.prev,
            }
        except Exception:
            # If parsing fails, return raw response for debugging
            # This allows us to see actual API response structure
            return response_data

    def get_item(self, item_id: str) -> dict[str, Any]:
        """
        Get detailed information about a specific item.

        Args:
            item_id: eBay item ID (can be legacy ID or new format like "v1|123456789")

        Returns:
            Dictionary containing detailed item information

        Raises:
            ValueError: If item_id is empty
            NotFoundError: If item is not found
            EbayAPIError: If the request fails
        """
        # Validate item_id
        if not item_id or not item_id.strip():
            raise ValueError("Item ID cannot be empty")

        # Clean item_id
        item_id = item_id.strip()

        # Build endpoint path with item_id
        endpoint = f"/buy/browse/v1/item/{item_id}"

        # Make API call
        response_data = self.base_client.get(endpoint)

        # Parse response into Item model
        try:
            item = Item(**response_data)
            # Convert back to dict for flexibility
            return item.model_dump()
        except Exception:
            # If parsing fails, return raw response for debugging
            # This allows us to see actual API response structure
            return response_data

