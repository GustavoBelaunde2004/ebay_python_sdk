"""Pydantic models for Account API responses."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class Privilege(BaseModel):
    """Privilege granted to the account."""

    name: Optional[str] = Field(None, description="Privilege name")
    status: Optional[str] = Field(None, description="Privilege status")
    level: Optional[str] = Field(None, description="Privilege level")

    model_config = ConfigDict(populate_by_name=True)


class Program(BaseModel):
    """Account program enrollment."""

    program_type: Optional[str] = Field(None, alias="programType", description="Program type")
    status: Optional[str] = Field(None, description="Enrollment status")

    model_config = ConfigDict(populate_by_name=True)


class SellingLimit(BaseModel):
    """Selling limit information."""

    amount: Optional[float] = Field(None, description="Amount limit")
    currency: Optional[str] = Field(None, description="Currency code")
    quantity: Optional[int] = Field(None, description="Quantity limit")


class AccountProfile(BaseModel):
    """Represents account profile and privilege information."""

    account_type: Optional[str] = Field(None, alias="accountType", description="Account type")
    seller_display_name: Optional[str] = Field(
        None, alias="sellerDisplayName", description="Seller display name"
    )
    registration_country: Optional[str] = Field(
        None, alias="registrationCountry", description="Registration country"
    )
    privileges: Optional[List[Privilege]] = Field(None, description="Account privileges")
    programs: Optional[List[Program]] = Field(None, description="Program enrollments")
    selling_limit: Optional[SellingLimit] = Field(None, alias="sellingLimit", description="Selling limits")

    model_config = ConfigDict(populate_by_name=True)


class PolicyBase(BaseModel):
    """Common fields for policies."""

    name: Optional[str] = Field(None, description="Policy name")
    marketplace_id: Optional[str] = Field(None, alias="marketplaceId", description="Marketplace ID")

    model_config = ConfigDict(populate_by_name=True)


class ReturnPolicy(PolicyBase):
    """Return policy definition."""

    policy_id: Optional[str] = Field(None, alias="returnPolicyId", description="Return policy ID")
    returns_within: Optional[dict] = Field(None, alias="returnPeriod", description="Return period info")
    refund_methods: Optional[List[str]] = Field(None, alias="returnMethodValues")
    return_shipping_cost_payer: Optional[str] = Field(
        None, alias="returnShippingCostPayer", description="Who pays return shipping"
    )


class ReturnPoliciesResponse(BaseModel):
    return_policies: List[ReturnPolicy] = Field(default_factory=list, alias="returnPolicies")

    model_config = ConfigDict(populate_by_name=True)


class PaymentPolicy(PolicyBase):
    """Payment policy definition."""

    policy_id: Optional[str] = Field(None, alias="paymentPolicyId", description="Payment policy ID")
    payment_instructions: Optional[str] = Field(None, alias="paymentInstructions")
    immediate_pay: Optional[bool] = Field(None, alias="immediatePay")
    payment_methods: Optional[List[dict]] = Field(None, alias="paymentMethods")


class PaymentPoliciesResponse(BaseModel):
    payment_policies: List[PaymentPolicy] = Field(default_factory=list, alias="paymentPolicies")

    model_config = ConfigDict(populate_by_name=True)


class ShippingOption(BaseModel):
    """Single shipping service configuration."""

    cost_type: Optional[str] = Field(None, alias="costType")
    option_type: Optional[str] = Field(None, alias="optionType")
    shipping_services: Optional[List[dict]] = Field(None, alias="shippingServices")

    model_config = ConfigDict(populate_by_name=True)


class ShippingPolicy(PolicyBase):
    """Shipping policy definition."""

    policy_id: Optional[str] = Field(None, alias="shippingPolicyId", description="Shipping policy ID")
    fulfillment_time: Optional[dict] = Field(None, alias="handlingTime")
    shipping_options: Optional[List[ShippingOption]] = Field(None, alias="shippingOptions")
    shipping_from_location: Optional[str] = Field(None, alias="shipFromLocationAvailability")


class ShippingPoliciesResponse(BaseModel):
    shipping_policies: List[ShippingPolicy] = Field(default_factory=list, alias="shippingPolicies")

    model_config = ConfigDict(populate_by_name=True)
