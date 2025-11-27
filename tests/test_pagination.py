"""Tests for pagination helpers."""

from typing import Any, Dict, List

import pytest

from ebay_rest.pagination import Paginator, paginate


class FakePagedAPI:
    """Simulate an API returning paginated data."""

    def __init__(self, pages: List[Dict[str, Any]]):
        self.pages = pages
        self.calls = 0

    def list_items(self, offset: int = 0, limit: int = 2):
        page_index = offset // limit
        self.calls += 1
        if page_index < len(self.pages):
            return self.pages[page_index]
        return {"items": [], "limit": limit, "offset": offset}


def test_paginate_generator():
    api = FakePagedAPI(
        [
            {"items": [{"id": 1}, {"id": 2}], "limit": 2, "offset": 0, "next": "mock?offset=2"},
            {"items": [{"id": 3}], "limit": 2, "offset": 2},
        ]
    )

    results = list(
        paginate(
            api.list_items,
            limit=10,
            items_key="items",
            offset_param="offset",
            limit_param="limit",
        )
    )

    assert [item["id"] for item in results] == [1, 2, 3]
    assert api.calls == 2


def test_paginator_stops_at_limit():
    api = FakePagedAPI(
        [
            {"items": [{"id": 1}, {"id": 2}], "limit": 2, "offset": 0, "next": "mock?offset=2"},
            {"items": [{"id": 3}], "limit": 2, "offset": 2},
        ]
    )

    paginator = Paginator(
        api.list_items,
        limit=2,  # total items to yield
        items_key="items",
        offset_param="offset",
        limit_param="limit",
    )
    results = list(paginator)
    assert [item["id"] for item in results] == [1, 2]

