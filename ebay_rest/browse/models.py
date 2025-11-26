"""Pydantic models for Browse API responses."""

from typing import Optional

from pydantic import BaseModel, Field


class Price(BaseModel):
    """Represents a price with currency."""

    value: str = Field(..., description="Price value as string")
    currency: str = Field(..., description="Currency code (e.g., USD, EUR)")

    class Config:
        populate_by_name = True


class ItemSummary(BaseModel):
    """Summary information about an eBay item."""

    item_id: str = Field(..., alias="itemId", description="eBay item ID")
    title: str = Field(..., description="Item title")
    price: Optional[Price] = Field(None, description="Item price")
    image_url: Optional[str] = Field(None, alias="imageUrl", description="Primary image URL")
    item_web_url: Optional[str] = Field(None, alias="itemWebUrl", description="Item page URL")
    condition: Optional[str] = Field(None, description="Item condition")
    condition_id: Optional[str] = Field(None, alias="conditionId", description="Item condition ID")
    epid: Optional[str] = Field(None, description="ePID (eBay Product Identifier)")
    item_location: Optional[dict] = Field(None, alias="itemLocation", description="Item location information")
    seller: Optional[dict] = Field(None, description="Seller information")
    shipping_options: Optional[list[dict]] = Field(None, alias="shippingOptions", description="Shipping options")
    buying_options: Optional[list[str]] = Field(None, alias="buyingOptions", description="Buying options (e.g., 'BUY_IT_NOW', 'AUCTION')")
    categories: Optional[list[dict]] = Field(None, description="Item categories")
    thumbnail_images: Optional[list[dict]] = Field(None, alias="thumbnailImages", description="Thumbnail images")

    class Config:
        populate_by_name = True


class Item(BaseModel):
    """Detailed information about an eBay item."""

    item_id: str = Field(..., alias="itemId", description="eBay item ID")
    title: str = Field(..., description="Item title")
    price: Optional[Price] = Field(None, description="Item price")
    description: Optional[str] = Field(None, description="Item description")
    image_urls: Optional[list[dict]] = Field(None, alias="imageUrls", description="List of image objects/URLs")
    item_web_url: Optional[str] = Field(None, alias="itemWebUrl", description="Item page URL")
    item_affiliate_web_url: Optional[str] = Field(None, alias="itemAffiliateWebUrl", description="Affiliate item URL")
    condition: Optional[str] = Field(None, description="Item condition")
    condition_id: Optional[str] = Field(None, alias="conditionId", description="Item condition ID")
    condition_description: Optional[str] = Field(None, alias="conditionDescription", description="Condition description")
    category_path: Optional[str] = Field(None, alias="categoryPath", description="Category breadcrumb path")
    categories: Optional[list[dict]] = Field(None, description="Item categories")
    epid: Optional[str] = Field(None, description="ePID (eBay Product Identifier)")
    gtin: Optional[str] = Field(None, description="Global Trade Item Number")
    mpn: Optional[str] = Field(None, description="Manufacturer Part Number")
    brand: Optional[str] = Field(None, description="Item brand")
    item_location: Optional[dict] = Field(None, alias="itemLocation", description="Item location information")
    seller: Optional[dict] = Field(None, description="Seller information")
    shipping_options: Optional[list[dict]] = Field(None, alias="shippingOptions", description="Shipping options")
    return_terms: Optional[dict] = Field(None, alias="returnTerms", description="Return policy information")
    buying_options: Optional[list[str]] = Field(None, alias="buyingOptions", description="Buying options")
    leaf_category_ids: Optional[list[str]] = Field(None, alias="leafCategoryIds", description="Leaf category IDs")
    adult_only: Optional[bool] = Field(None, alias="adultOnly", description="Adult-only item flag")
    item_aspects: Optional[list[dict]] = Field(None, alias="itemAspects", description="Item aspects/attributes")
    item_end_date: Optional[str] = Field(None, alias="itemEndDate", description="Item listing end date")
    legacy_item_id: Optional[str] = Field(None, alias="legacyItemId", description="Legacy item ID")
    available_coupons: Optional[list[dict]] = Field(None, alias="availableCoupons", description="Available coupons")

    class Config:
        populate_by_name = True


class SearchResponse(BaseModel):
    """Response model for item search results."""

    items: list[ItemSummary] = Field(default_factory=list, alias="itemSummaries", description="List of item summaries")
    total: int = Field(0, description="Total number of results")
    offset: int = Field(0, description="Pagination offset")
    limit: int = Field(0, description="Results per page")
    href: Optional[str] = Field(None, description="API response URL")
    next: Optional[str] = Field(None, description="Next page URL")
    prev: Optional[str] = Field(None, description="Previous page URL")

    class Config:
        populate_by_name = True

