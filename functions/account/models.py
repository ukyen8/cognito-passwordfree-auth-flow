# Standard library
import datetime
import uuid

# Third-party
import phonenumbers
from pydantic import BaseModel, EmailStr, Field, field_validator


class BaseAccount(BaseModel):
    first_name: str
    last_name: str
    email_address: EmailStr
    phone_number: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, phone_number: str) -> str:
        try:
            parsed_phone = phonenumbers.parse(phone_number)
        except phonenumbers.NumberParseException:
            raise ValueError(
                f"Invalid phone number: {phone_number}. Validate by custom field."
            )
        if phonenumbers.is_valid_number(parsed_phone):
            return phone_number
        raise ValueError(
            f"Invalid phone number: {phone_number}. Validate by custom field."
        )


class Account(BaseAccount):
    """Model for inserting account record to database."""

    id: uuid.UUID = Field(alias="account_id")

    created_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow
    )
    modified_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow
    )


class PostAccount(BaseAccount):
    """Request model for creating an account record."""


class PatchAccount(BaseAccount):
    """Request model for updating account details."""

    id: uuid.UUID = Field(alias="account_id")
    first_name: str | None = None
    last_name: str | None = None
    email_address: EmailStr | None = None
    phone_number: str | None = None
    modified_at: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow
    )

    @classmethod
    def validate_phone_number(cls, phone_number: str) -> str:
        try:
            parsed_phone = phonenumbers.parse(phone_number)
        except phonenumbers.NumberParseException:
            raise ValueError(
                f"Invalid phone number: {phone_number}. Validate by custom field."
            )
        if phonenumbers.is_valid_number(parsed_phone):
            return phone_number
        raise ValueError(
            f"Invalid phone number: {phone_number}. Validate by custom field."
        )
