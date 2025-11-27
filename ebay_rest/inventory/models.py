"""Pydantic models for Inventory API responses."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Weight(BaseModel):
    """Package weight."""

    value: Optional[float] = Field(None, description="Weight value")
    unit: Optional[str] = Field(None, description="Weight unit (POUND, KILOGRAM, etc.)")


class Dimensions(BaseModel):
    """Package dimensions."""

    height: Optional[float] = Field(None, description="Height value")
    width: Optional[float] = Field(None, description="Width value")
    length: Optional[float] = Field(None, description="Length value")
    unit: Optional[str] = Field(None, description="Measurement unit (INCH, CENTIMETER, etc.)")


class PackageWeightAndSize(BaseModel):
    """Combined package size information."""

    package_type: Optional[str] = Field(None, alias="packageType", description="Package type code")
    weight: Optional[Weight] = Field(None, description="Package weight")
    dimensions: Optional[Dimensions] = Field(None, description="Package dimensions")

    class Config:
        populate_by_name = True


class Product(BaseModel):
    """Product information for an inventory item."""

    title: Optional[str] = Field(None, description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    brand: Optional[str] = Field(None, description="Brand name")
    mpn: Optional[str] = Field(None, description="Manufacturer part number")
    gtin: Optional[List[str]] = Field(None, description="GTINs (UPC/EAN/ISBN)")
    image_urls: Optional[List[str]] = Field(None, alias="imageUrls", description="Image URLs")
    aspects: Optional[Dict[str, List[str]]] = Field(None, description="Product aspects")

    class Config:
        populate_by_name = True


class AllocationByMarketplace(BaseModel):
    """Quantity allocated to a marketplace."""

    marketplace_id: Optional[str] = Field(None, alias="marketplaceId", description="Marketplace ID")
    quantity: Optional[int] = Field(None, description="Quantity allocated")

    class Config:
        populate_by_name = True


class ShipToLocationAvailability(BaseModel):
    """Availability for ship-to locations."""

    quantity: Optional[int] = Field(None, description="Total available quantity")
    allocation_by_marketplace: Optional[List[AllocationByMarketplace]] = Field(
        None, alias="allocationByMarketplace", description="Quantity allocated by marketplace"
    )

    class Config:
        populate_by_name = True


class Availability(BaseModel):
    """Inventory item availability information."""

    ship_to_location_availability: Optional[ShipToLocationAvailability] = Field(
        None, alias="shipToLocationAvailability", description="Ship-to availability"
    )
    pickup_at_location_availability: Optional[List[dict]] = Field(
        None, alias="pickupAtLocationAvailability", description="Pickup location availability details"
    )

    class Config:
        populate_by_name = True


class InventoryItem(BaseModel):
    """Represents an inventory item in seller's inventory."""

    sku: str = Field(..., description="Seller-defined SKU for the inventory item")
    locale: Optional[str] = Field(None, description="Locale for product data")
    condition: Optional[str] = Field(None, description="Item condition")
    condition_description: Optional[str] = Field(
        None, alias="conditionDescription", description="Condition description"
    )
    product: Optional[Product] = Field(None, description="Product information")
    availability: Optional[Availability] = Field(None, description="Availability information")
    package_weight_and_size: Optional[PackageWeightAndSize] = Field(
        None, alias="packageWeightAndSize", description="Package details"
    )
    inventory_location: Optional[str] = Field(
        None, alias="inventoryLocation", description="Inventory location identifier"
    )
    tax: Optional[dict] = Field(None, description="Tax information")
    regulatory: Optional[dict] = Field(None, description="Regulatory information")
    offers: Optional[List[dict]] = Field(None, description="Associated offers")

    class Config:
        populate_by_name = True


class Offer(BaseModel):
    """Represents an offer for an inventory item."""

    offer_id: Optional[str] = Field(None, alias="offerId", description="eBay offer ID")
    sku: str = Field(..., description="Seller-defined SKU")
    marketplace_id: Optional[str] = Field(None, alias="marketplaceId", description="eBay marketplace ID")
    format: Optional[str] = Field(None, description="Listing format (FIXED_PRICE, AUCTION)")
    available_quantity: Optional[int] = Field(None, alias="availableQuantity", description="Available quantity")
    listing_description: Optional[str] = Field(None, alias="listingDescription", description="Listing description")
    price: Optional[dict] = Field(None, description="Price object {currency,value}")

    class Config:
        populate_by_name = True


class InventoryItemsResponse(BaseModel):
    """Response wrapper for list inventory items."""

    inventory_items: List[InventoryItem] = Field(
        default_factory=list, alias="inventoryItems", description="List of inventory items"
    )
    href: Optional[str] = Field(None, description="Current results URL")
    limit: Optional[int] = Field(None, description="Results per page")
    offset: Optional[int] = Field(None, description="Pagination offset")
    total: Optional[int] = Field(None, description="Total number of items")
    next: Optional[str] = Field(None, description="Next page URL")
    prev: Optional[str] = Field(None, description="Previous page URL")

    class Config:
        populate_by_name = True
