"""Pydantic models for Clio API entities."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ClioBaseModel(BaseModel):
    """Base model for all Clio entities."""

    model_config = ConfigDict(
        extra="ignore",
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: str,
        }
    )

    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ContactInfo(BaseModel):
    """Contact information fields."""

    type: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class PhoneNumber(BaseModel):
    """Phone number model."""

    id: Optional[int] = None
    name: Optional[str] = None
    number: Optional[str] = None
    default_number: Optional[bool] = None


class EmailAddress(BaseModel):
    """Email address model."""

    id: Optional[int] = None
    name: Optional[str] = None
    address: Optional[str] = None
    default_email: Optional[bool] = None


class Contact(ClioBaseModel):
    """Contact entity model."""

    type: Optional[str] = None  # "Person" or "Company"
    name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None

    # Contact information
    primary_email_address: Optional[str] = None
    primary_phone_number: Optional[str] = None
    email_addresses: list[EmailAddress] = Field(default_factory=list)
    phone_numbers: list[PhoneNumber] = Field(default_factory=list)

    # Address information
    addresses: list[ContactInfo] = Field(default_factory=list)

    # Additional fields
    title: Optional[str] = None
    initials: Optional[str] = None
    preferred_language: Optional[str] = None
    time_zone: Optional[str] = None

    # Metadata
    custom_field_values: list[dict[str, Any]] = Field(default_factory=list)


class PracticeArea(ClioBaseModel):
    """Practice area model."""

    name: Optional[str] = None


class Matter(ClioBaseModel):
    """Matter/case entity model."""

    number: Optional[str] = None
    display_number: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # "Open", "Closed", etc.

    # Dates
    open_date: Optional[datetime] = None
    close_date: Optional[datetime] = None

    # Relationships
    client: Optional[Contact] = None
    responsible_attorney: Optional[Contact] = None
    originating_attorney: Optional[Contact] = None
    practice_area: Optional[PracticeArea] = None

    # Billing
    billable: Optional[bool] = None
    billing_method: Optional[str] = None

    # Custom fields
    custom_field_values: list[dict[str, Any]] = Field(default_factory=list)


class ActivityType(BaseModel):
    """Activity type model."""

    name: Optional[str] = None
    billable: Optional[bool] = None
    rate: Optional[Decimal] = None


class Activity(ClioBaseModel):
    """Activity (time entry/expense) model."""

    type: Optional[str] = None  # "TimeEntry" or "ExpenseEntry"
    date: Optional[datetime] = None
    quantity: Optional[Decimal] = None
    price: Optional[Decimal] = None
    total: Optional[Decimal] = None

    # Description and details
    description: Optional[str] = None
    note: Optional[str] = None

    # Relationships
    matter: Optional[Matter] = None
    user: Optional[Contact] = None
    activity_type: Optional[ActivityType] = None

    # Billing status
    billed: Optional[bool] = None
    bill: Optional["Bill"] = None

    # Time entry specific fields
    hours: Optional[Decimal] = None
    minutes: Optional[Decimal] = None

    # Expense entry specific fields
    vendor: Optional[str] = None
    category: Optional[str] = None


class LineItem(BaseModel):
    """Bill line item model."""

    id: Optional[int] = None
    type: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[Decimal] = None
    rate: Optional[Decimal] = None
    amount: Optional[Decimal] = None
    activity: Optional[Activity] = None


class Bill(ClioBaseModel):
    """Bill entity model."""

    number: Optional[str] = None
    state: Optional[str] = None  # "draft", "sent", "paid", etc.

    # Dates
    issued_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    # Amounts
    subtotal: Optional[Decimal] = None
    tax_total: Optional[Decimal] = None
    total: Optional[Decimal] = None
    paid_total: Optional[Decimal] = None
    balance: Optional[Decimal] = None

    # Relationships
    matter: Optional[Matter] = None
    bill_to: Optional[Contact] = None

    # Line items
    line_items: list[LineItem] = Field(default_factory=list)

    # Additional fields
    note: Optional[str] = None
    footer: Optional[str] = None


class DocumentVersion(BaseModel):
    """Document version model."""

    id: Optional[int] = None
    uuid: Optional[str] = None
    filename: Optional[str] = None
    size: Optional[int] = None
    content_type: Optional[str] = None
    created_at: Optional[datetime] = None


class Document(ClioBaseModel):
    """Document entity model."""

    name: Optional[str] = None
    description: Optional[str] = None

    # Relationships
    matter: Optional[Matter] = None
    parent_document: Optional["Document"] = None

    # Version information
    current_version: Optional[DocumentVersion] = None
    versions: list[DocumentVersion] = Field(default_factory=list)

    # Status
    is_folder: Optional[bool] = None

    # Permissions
    public: Optional[bool] = None


class PaymentMethod(BaseModel):
    """Payment method model."""

    type: Optional[str] = None
    name: Optional[str] = None


class Payment(ClioBaseModel):
    """Payment entity model."""

    amount: Optional[Decimal] = None
    payment_date: Optional[datetime] = None
    reference: Optional[str] = None
    note: Optional[str] = None

    # Relationships
    matter: Optional[Matter] = None
    bill: Optional[Bill] = None
    payment_method: Optional[PaymentMethod] = None

    # Status
    status: Optional[str] = None


class PaymentLink(ClioBaseModel):
    """Payment link model."""

    url: Optional[str] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None

    # Dates
    expires_at: Optional[datetime] = None

    # Status
    status: Optional[str] = None

    # Relationships
    matter: Optional[Matter] = None


# Request/Response models

class ContactCreateRequest(BaseModel):
    """Request model for creating a contact."""

    type: str = Field(..., description="Contact type: 'Person' or 'Company'")
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    primary_email_address: Optional[str] = None
    primary_phone_number: Optional[str] = None
    title: Optional[str] = None


class MatterCreateRequest(BaseModel):
    """Request model for creating a matter."""

    description: str = Field(..., description="Matter description")
    client_id: Optional[int] = None
    responsible_attorney_id: Optional[int] = None
    practice_area_id: Optional[int] = None
    open_date: Optional[datetime] = None
    billable: bool = True
    billing_method: Optional[str] = None


class ActivityCreateRequest(BaseModel):
    """Request model for creating an activity."""

    type: str = Field(..., description="Activity type: 'TimeEntry' or 'ExpenseEntry'")
    matter_id: int = Field(..., description="Associated matter ID")
    date: datetime = Field(..., description="Activity date")
    quantity: Decimal = Field(..., description="Quantity (hours for time, amount for expense)")
    description: str = Field(..., description="Activity description")
    activity_type_id: Optional[int] = None
    price: Optional[Decimal] = None


class PaymentLinkCreateRequest(BaseModel):
    """Request model for creating a payment link."""

    amount: Decimal = Field(..., description="Payment amount")
    description: str = Field(..., description="Payment description")
    matter_id: Optional[int] = None
    expires_at: Optional[datetime] = None


# Update models inherit from create models but make fields optional
class ContactUpdateRequest(BaseModel):
    """Request model for updating a contact."""

    type: Optional[str] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None
    primary_email_address: Optional[str] = None
    primary_phone_number: Optional[str] = None
    title: Optional[str] = None


class MatterUpdateRequest(BaseModel):
    """Request model for updating a matter."""

    description: Optional[str] = None
    client_id: Optional[int] = None
    responsible_attorney_id: Optional[int] = None
    practice_area_id: Optional[int] = None
    status: Optional[str] = None
    close_date: Optional[datetime] = None
    billable: Optional[bool] = None
    billing_method: Optional[str] = None


class ActivityUpdateRequest(BaseModel):
    """Request model for updating an activity."""

    date: Optional[datetime] = None
    quantity: Optional[Decimal] = None
    description: Optional[str] = None
    activity_type_id: Optional[int] = None
    price: Optional[Decimal] = None
