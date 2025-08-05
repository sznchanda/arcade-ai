"""Clio toolkit tools."""

from .billing import (
    create_bill,
    create_expense,
    create_time_entry,
    delete_activity,
    get_activity,
    get_bills,
    get_expenses,
    get_time_entries,
    list_activities,
    update_time_entry,
)
from .contacts import (
    create_contact,
    delete_contact,
    get_contact,
    get_contact_relationships,
    list_contact_activities,
    search_contacts,
    update_contact,
)
from .documents import (
    create_document,
    delete_document,
    get_document,
    list_documents,
    update_document,
)
from .matters import (
    add_matter_participant,
    close_matter,
    create_matter,
    delete_matter,
    get_matter,
    get_matter_activities,
    list_matters,
    remove_matter_participant,
    search_matters,
    update_matter,
)

__all__ = [
    # Matter Management
    "add_matter_participant",
    "close_matter",
    "create_matter",
    "delete_matter",
    "get_matter",
    "get_matter_activities",
    "list_matters",
    "remove_matter_participant",
    "search_matters",
    "update_matter",
    # Contact Management
    "create_contact",
    "delete_contact",
    "get_contact",
    "get_contact_relationships",
    "list_contact_activities",
    "search_contacts",
    "update_contact",
    # Document Management
    "create_document",
    "delete_document",
    "get_document",
    "list_documents",
    "update_document",
    # Billing & Activity Management
    "create_bill",
    "create_expense",
    "create_time_entry",
    "delete_activity",
    "get_activity",
    "get_bills",
    "get_expenses",
    "get_time_entries",
    "list_activities",
    "update_time_entry",
]
