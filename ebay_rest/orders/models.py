"""Pydantic models for Orders API responses."""

from typing import Optional

from pydantic import BaseModel, Field


class Money(BaseModel):
    """Represents a monetary amount with currency."""

    value: str = Field(..., description="Monetary value as string")
    currency: str = Field(..., description="Currency code (e.g., USD, EUR)")

    class Config:
        populate_by_name = True


class Buyer(BaseModel):
    """Represents buyer information."""

    username: Optional[str] = Field(None, description="Buyer username")
    email: Optional[str] = Field(None, description="Buyer email address")
    contact_address: Optional[dict] = Field(None, alias="contactAddress", description="Buyer contact address")

    class Config:
        populate_by_name = True


class ShippingStep(BaseModel):
    """Represents shipping step details."""

    ship_to: Optional[dict] = Field(None, alias="shipTo", description="Shipping destination details")
    shipping_service_code: Optional[str] = Field(None, alias="shippingServiceCode", description="Shipping service code")
    shipping_carrier_code: Optional[str] = Field(None, alias="shippingCarrierCode", description="Shipping carrier code")
    weight: Optional[dict] = Field(None, description="Package weight information")

    class Config:
        populate_by_name = True


class FulfillmentStartInstruction(BaseModel):
    """Represents instructions for starting fulfillment."""

    fulfillment_instructions_type: Optional[str] = Field(
        None, alias="fulfillmentInstructionsType", description="Type of fulfillment instructions"
    )
    store_id: Optional[str] = Field(None, alias="storeId", description="Store identifier if applicable")
    ship_to: Optional[dict] = Field(None, alias="shipTo", description="Ship-to information")
    shipping_step: Optional[ShippingStep] = Field(None, alias="shippingStep", description="Shipping step details")

    class Config:
        populate_by_name = True


class PricingSummary(BaseModel):
    """Represents pricing summary for an order."""

    total: Optional[Money] = Field(None, description="Total order amount")
    subtotal: Optional[Money] = Field(None, description="Subtotal amount")
    delivery_cost: Optional[Money] = Field(None, alias="deliveryCost", description="Delivery cost")
    discount_amount: Optional[Money] = Field(None, alias="discountAmount", description="Discount amount applied")
    pricing_discount_summary: Optional[dict] = Field(
        None, alias="pricingDiscountSummary", description="Pricing discount details"
    )

    class Config:
        populate_by_name = True


class LineItem(BaseModel):
    """Represents a line item in an order."""

    line_item_id: Optional[str] = Field(None, alias="lineItemId", description="Line item ID")
    sku: Optional[str] = Field(None, description="Seller SKU")
    title: Optional[str] = Field(None, description="Item title")
    quantity: Optional[int] = Field(None, description="Quantity ordered")
    line_item_cost: Optional[Money] = Field(None, alias="lineItemCost", description="Line item cost")
    total: Optional[Money] = Field(None, description="Total line item amount")
    delivery_cost: Optional[Money] = Field(None, alias="deliveryCost", description="Delivery cost for the line item")
    taxes: Optional[list[dict]] = Field(None, description="Taxes applied to the line item")
    properties: Optional[dict] = Field(None, description="Additional line item properties")
    legacy_item_id: Optional[str] = Field(None, alias="legacyItemId", description="Legacy item ID")

    class Config:
        populate_by_name = True


class Order(BaseModel):
    """Represents an eBay order."""

    order_id: Optional[str] = Field(None, alias="orderId", description="eBay order ID")
    order_website: Optional[str] = Field(None, alias="orderWebUrl", description="Order page URL")
    order_fulfillment_status: Optional[str] = Field(
        None, alias="orderFulfillmentStatus", description="Order fulfillment status"
    )
    order_payment_status: Optional[str] = Field(
        None, alias="orderPaymentStatus", description="Order payment status"
    )
    creation_date: Optional[str] = Field(None, alias="creationDate", description="Order creation date ISO8601")
    last_modified_date: Optional[str] = Field(None, alias="lastModifiedDate", description="Last modified date ISO8601")
    cancel_status: Optional[str] = Field(None, alias="cancelStatus", description="Cancel status of the order")
    buyer: Optional[Buyer] = Field(None, description="Buyer information")
    pricing_summary: Optional[PricingSummary] = Field(None, alias="pricingSummary", description="Pricing summary")
    line_items: Optional[list[LineItem]] = Field(None, alias="lineItems", description="Order line items")
    fulfillment_start_instructions: Optional[list[FulfillmentStartInstruction]] = Field(
        None, alias="fulfillmentStartInstructions", description="Fulfillment start instructions"
    )

    class Config:
        populate_by_name = True


class OrdersResponse(BaseModel):
    """Response model for listing orders."""

    orders: list[Order] = Field(default_factory=list, description="List of orders")
    href: Optional[str] = Field(None, description="API response URL")
    limit: Optional[int] = Field(None, description="Results per page")
    offset: Optional[int] = Field(None, description="Pagination offset")
    total: Optional[int] = Field(None, description="Total number of orders available")
    next: Optional[str] = Field(None, description="Next page URL")
    prev: Optional[str] = Field(None, description="Previous page URL")

    class Config:
        populate_by_name = True

