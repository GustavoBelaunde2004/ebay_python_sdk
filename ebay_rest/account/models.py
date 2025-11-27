"""Pydantic models for Account API responses."""

from typing import List, Optional

from pydantic import BaseModel, Field


class Privilege(BaseModel):
    """Privilege granted to the account."""

    name: Optional[str] = Field(None, description="Privilege name")
    status: Optional[str] = Field(None, description="Privilege status")
    level: Optional[str] = Field(None, description="Privilege level")


class Program(BaseModel):
    """Account program enrollment."""

    program_type: Optional[str] = Field(None, alias="programType", description="Program type")
    status: Optional[str] = Field(None, description="Enrollment status")

    class Config:
        populate_by_name = True


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

    class Config:
        populate_by_name = True
