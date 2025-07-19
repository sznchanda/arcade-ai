"""Clio legal practice management toolkit for Arcade AI."""

from .client import ClioClient
from .exceptions import (
    ClioAuthenticationError,
    ClioError,
    ClioPermissionError,
    ClioRateLimitError,
    ClioResourceNotFoundError,
    ClioServerError,
    ClioTimeoutError,
    ClioValidationError,
)
from .tools import (
    # Matter tools
    add_matter_participant,
    close_matter,
    # Billing tools
    create_bill,
    # Contact tools
    create_contact,
    create_expense,
    create_matter,
    create_time_entry,
    get_bills,
    get_contact,
    get_contact_relationships,
    get_expenses,
    get_matter,
    get_matter_activities,
    get_time_entries,
    list_contact_activities,
    list_matters,
    remove_matter_participant,
    search_contacts,
    update_contact,
    update_matter,
    update_time_entry,
)

__version__ = "0.1.0"

__all__ = [
    "ClioAuthenticationError",
    "ClioClient",
    "ClioError",
    "ClioPermissionError",
    "ClioRateLimitError",
    "ClioResourceNotFoundError",
    "ClioServerError",
    "ClioTimeoutError",
    "ClioValidationError",
    "add_matter_participant",
    "close_matter",
    "create_bill",
    "create_contact",
    "create_expense",
    "create_matter",
    "create_time_entry",
    "get_bills",
    "get_contact",
    "get_contact_relationships",
    "get_expenses",
    "get_matter",
    "get_matter_activities",
    "get_time_entries",
    "list_contact_activities",
    "list_matters",
    "remove_matter_participant",
    "search_contacts",
    "update_contact",
    "update_matter",
    "update_time_entry",
]
