"""Pagination utilities for eBay API responses."""

from typing import Any, Callable, Generator, Optional
from urllib.parse import parse_qs, urlparse


def paginate(
    client_method: Callable,
    *args: Any,
    limit: Optional[int] = None,
    max_pages: Optional[int] = None,
    items_key: str = "items",
    next_key: str = "next",
    offset_param: str = "offset",
    limit_param: str = "limit",
    **kwargs: Any,
) -> Generator[dict[str, Any], None, None]:
    """
    Generic pagination generator for eBay API endpoints.

    Iterates through pages of results automatically, yielding items one by one.

    Args:
        client_method: The client method to call (e.g., client.browse.search_items)
        *args: Positional arguments to pass to client_method
        limit: Maximum number of items to return (None for all)
        max_pages: Maximum number of pages to fetch (None for all)
        items_key: Response key that contains items (default "items")
        next_key: Response key that contains next page URL (default "next")
        offset_param: Query parameter used for offset-based pagination
        limit_param: Query parameter used for per-page limit
        **kwargs: Keyword arguments to pass to client_method

    Yields:
        Individual items from paginated responses
    """

    emitted = 0
    page_count = 0
    request_kwargs = dict(kwargs)

    while True:
        response = client_method(*args, **request_kwargs)
        items = response.get(items_key)
        if not isinstance(items, list):
            items = []

        for item in items:
            yield item
            emitted += 1
            if limit is not None and emitted >= limit:
                return

        page_count += 1
        if max_pages is not None and page_count >= max_pages:
            return

        next_href = response.get(next_key)
        next_offset = None

        if next_href:
            # Use explicit next link if provided
            next_offset = _extract_offset_from_href(next_href, offset_param)

        if next_offset is None:
            # Only calculate next_offset if:
            # 1. We got items on this page (there might be more)
            # 2. We got a full page (suggesting there could be more data)
            if not items:
                # No items and no explicit next link - stop pagination
                return

            # Check if we got a full page of items
            current_limit = request_kwargs.get(limit_param)
            if current_limit is None:
                current_limit = response.get(limit_param)
            
            # If we got fewer items than the limit, we're done (no more pages)
            if current_limit is not None and len(items) < current_limit:
                return

            # We got a full page, so calculate next offset
            current_offset = request_kwargs.get(offset_param, response.get(offset_param))
            if current_limit is not None and current_offset is not None:
                next_offset = current_offset + current_limit

        if next_offset is None:
            # No further data
            return

        request_kwargs[offset_param] = next_offset


def _extract_offset_from_href(href: str, offset_param: str) -> Optional[int]:
    """Extract offset value from next page href."""
    if not href:
        return None
    parsed = urlparse(href)
    params = parse_qs(parsed.query)
    if offset_param in params and params[offset_param]:
        try:
            return int(params[offset_param][0])
        except (ValueError, TypeError):
            return None
    return None


class Paginator:
    """
    Iterator class for paginated API responses.

    Provides a more object-oriented interface for pagination.
    """

    def __init__(
        self,
        client_method: Callable,
        *args: Any,
        limit: Optional[int] = None,
        max_pages: Optional[int] = None,
        **kwargs: Any,
    ):
        """
        Initialize paginator.

        Args:
            client_method: The client method to call
            *args: Positional arguments for client_method
            limit: Maximum number of items to return
            max_pages: Maximum number of pages to fetch
            **kwargs: Keyword arguments for client_method and paginate()
        """
        self._generator = paginate(
            client_method,
            *args,
            limit=limit,
            max_pages=max_pages,
            **kwargs,
        )

    def __iter__(self) -> "Paginator":
        """Return iterator."""
        return self

    def __next__(self) -> dict[str, Any]:
        """Return next item or raise StopIteration."""
        return next(self._generator)

