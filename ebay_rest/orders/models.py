"""Pydantic models for Orders API responses."""

from typing import Optional

from pydantic import BaseModel, Field


class Money(BaseModel):
    """Represents a monetary amount with currency."""

    value: str = Field(..., description="Monetary value as string")
    currency: str = Field(..., description="Currency code (e.g., USD, EUR)")

    # TODO: Add conversion to Decimal if needed


class LineItem(BaseModel):
    """Represents a line item in an order."""

    line_item_id: Optional[str] = Field(None, alias="lineItemId", description="Line item ID")
    sku: Optional[str] = Field(None, description="Seller SKU")
    title: Optional[str] = Field(None, description="Item title")
    quantity: Optional[int] = Field(None, description="Quantity ordered")
    line_item_cost: Optional[Money] = Field(None, alias="lineItemCost", description="Line item cost")

    # TODO: Add more fields based on eBay Orders API line item structure
    # TODO: Add item details
    # TODO: Add shipping details

    class Config:
        populate_by_name = True


class Order(BaseModel):
    """Represents an eBay order."""

    order_id: Optional[str] = Field(None, alias="orderId", description="eBay order ID")
    order_fulfillment_status: Optional[str] = Field(
        None, alias="orderFulfillmentStatus", description="Order fulfillment status"
    )
    line_items: Optional[list[LineItem]] = Field(None, alias="lineItems", description="Order line items")
    pricing_summary: Optional[dict] = Field(None, alias="pricingSummary", description="Order pricing summary")
    buyer: Optional[dict] = Field(None, description="Buyer information")

    # TODO: Add more fields based on eBay Orders API response structure
    # TODO: Add creation date
    # TODO: Add payment status
    # TODO: Add shipping address
    # TODO: Add fulfillment details

    class Config:
        populate_by_name = True

