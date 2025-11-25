"""Pydantic models for Browse API responses."""

from typing import Optional

from pydantic import BaseModel, Field


class Price(BaseModel):
    """Represents a price with currency."""

    value: str = Field(..., description="Price value as string")
    currency: str = Field(..., description="Currency code (e.g., USD, EUR)")

    # TODO: Add conversion to Decimal if needed
    # TODO: Add validation for currency codes


class ItemSummary(BaseModel):
    """Summary information about an eBay item."""

    item_id: str = Field(..., description="eBay item ID")
    title: str = Field(..., description="Item title")
    price: Optional[Price] = Field(None, description="Item price")
    image_url: Optional[str] = Field(None, alias="imageUrl", description="Primary image URL")
    item_web_url: Optional[str] = Field(None, alias="itemWebUrl", description="Item page URL")
    condition: Optional[str] = Field(None, description="Item condition")

    # TODO: Add more fields based on eBay Browse API response structure
    # TODO: Add field aliases for eBay API naming conventions
    # TODO: Add validators if needed

    class Config:
        populate_by_name = True


class Item(BaseModel):
    """Detailed information about an eBay item."""

    item_id: str = Field(..., description="eBay item ID")
    title: str = Field(..., description="Item title")
    price: Optional[Price] = Field(None, description="Item price")
    description: Optional[str] = Field(None, description="Item description")
    image_urls: Optional[list[str]] = Field(None, alias="imageUrls", description="List of image URLs")
    item_web_url: Optional[str] = Field(None, alias="itemWebUrl", description="Item page URL")
    condition: Optional[str] = Field(None, description="Item condition")
    category_path: Optional[str] = Field(None, alias="categoryPath", description="Category breadcrumb path")

    # TODO: Add more fields based on eBay Browse API detailed response
    # TODO: Add shipping information
    # TODO: Add seller information
    # TODO: Add return policy information

    class Config:
        populate_by_name = True

