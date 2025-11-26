"""Pydantic models for Inventory API responses."""

from typing import Optional

from pydantic import BaseModel, Field


class Availability(BaseModel):
    """Inventory item availability information."""

    # TODO: Add fields based on eBay Inventory API availability structure
    pass


class InventoryItem(BaseModel):
    """Represents an inventory item in seller's inventory."""

    sku: str = Field(..., description="Seller-defined SKU for the inventory item")
    condition: Optional[str] = Field(None, description="Item condition")
    product: Optional[dict] = Field(None, description="Product information")
    availability: Optional[Availability] = Field(None, description="Availability information")
    location: Optional[dict] = Field(None, description="Inventory location")

    # TODO: Add more fields based on eBay Inventory API response structure
    # TODO: Add product information model
    # TODO: Add location information model
    # TODO: Add pricing information
    # TODO: Add listing details


class Offer(BaseModel):
    """Represents an offer for an inventory item."""

    offer_id: Optional[str] = Field(None, alias="offerId", description="eBay offer ID")
    sku: str = Field(..., description="Seller-defined SKU")
    marketplace_id: Optional[str] = Field(None, alias="marketplaceId", description="eBay marketplace ID")

    # TODO: Add more fields based on eBay Inventory API offer structure
    # TODO: Add pricing information
    # TODO: Add listing format
    # TODO: Add category ID

    class Config:
        populate_by_name = True

