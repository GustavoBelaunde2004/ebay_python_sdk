"""Pydantic models for Account API responses."""

from typing import Optional

from pydantic import BaseModel, Field


class AccountProfile(BaseModel):
    """Represents account profile and privilege information."""

    account_type: Optional[str] = Field(None, alias="accountType", description="Account type")
    privileges: Optional[list[str]] = Field(None, description="Account privileges")

    # TODO: Add more fields based on eBay Account API response structure
    # TODO: Add seller level information
    # TODO: Add marketplace-specific account details
    # TODO: Add return policy information

    class Config:
        populate_by_name = True

