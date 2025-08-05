"""Contact management tools for Clio."""

from typing import Annotated, Optional

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Clio

from ..client import ClioClient
from ..exceptions import ClioError, ClioValidationError
from ..models import Contact
from ..utils import (
    build_search_params,
    extract_list_data,
    extract_model_data,
    format_json_response,
    prepare_request_data,
)
from ..validation import (
    validate_contact_type,
    validate_email,
    validate_id,
    validate_limit_offset,
    validate_optional_string,
    validate_phone,
    validate_required_string,
)


@tool(requires_auth=Clio())
async def search_contacts(
    context: ToolContext,
    query: Annotated[str, "Search query for contacts (name, email, phone, company)"],
    contact_type: Annotated[
        Optional[str], "Filter by contact type: 'Person' or 'Company' (optional)"
    ] = None,
    limit: Annotated[
        Optional[int], "Maximum number of contacts to return (1-200, default: 50)"
    ] = 50,
    offset: Annotated[Optional[int], "Number of contacts to skip for pagination (default: 0)"] = 0,
    include_extra_data: Annotated[
        bool, "Include all available contact data (default: False for summary only)"
    ] = False,
) -> Annotated[str, "JSON string containing matching contacts with their details"]:
    """
    Search for contacts in Clio by name, email, phone number, or company.

    Examples:
    ```
    search_contacts(query="john@example.com")
    search_contacts(query="Smith Law Firm", contact_type="Company")
    search_contacts(query="John Smith", limit=10)
    ```
    """
    async with ClioClient(context) as client:
        # Validate inputs
        query = validate_required_string(query, "Search query")
        if contact_type:
            contact_type = validate_contact_type(contact_type)
        limit, offset = validate_limit_offset(limit, offset)

        # Build search parameters
        params = build_search_params(
            query=query,
            limit=limit,
            offset=offset,
            type=contact_type,
        )

        # Search contacts
        response = await client.get("contacts", params=params)
        contacts_data = extract_list_data(response, "contacts")

        return format_json_response(contacts_data, include_extra_data=include_extra_data)


@tool(requires_auth=Clio())
async def get_contact(
    context: ToolContext,
    contact_id: Annotated[int, "The ID of the contact to retrieve"],
    include_extra_data: Annotated[
        bool, "Include all available contact data (default: False for summary only)"
    ] = False,
) -> Annotated[str, "JSON string containing the contact details"]:
    """
    Retrieve detailed information about a specific contact.

    Example:
    ```
    get_contact(contact_id=12345)
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate input
            contact_id = validate_id(contact_id, "Contact ID")

            response = await client.get_contact(contact_id)
            contact_data = extract_model_data(response, Contact)

            return format_json_response(contact_data, include_extra_data=include_extra_data)

        except ClioError:
            raise
        except (ValueError, TypeError) as e:
            raise ClioValidationError(f"Invalid parameter for contact {contact_id}: {e!s}")
        except Exception as e:
            raise ClioError(f"Failed to retrieve contact {contact_id}: {e!s}", retry=True)


@tool(requires_auth=Clio())
async def create_contact(
    context: ToolContext,
    contact_type: Annotated[str, "Contact type: 'Person' or 'Company'"],
    name: Annotated[Optional[str], "Full name for companies or display name"] = None,
    first_name: Annotated[Optional[str], "First name (for Person type)"] = None,
    last_name: Annotated[Optional[str], "Last name (for Person type)"] = None,
    company: Annotated[
        Optional[str], "Company name (for Company type or person's employer)"
    ] = None,
    email: Annotated[Optional[str], "Primary email address"] = None,
    phone: Annotated[Optional[str], "Primary phone number"] = None,
    title: Annotated[Optional[str], "Job title or position"] = None,
) -> Annotated[str, "JSON string containing the created contact details"]:
    """
    Create a new contact (person or company) in Clio.

    Examples:
    ```
    create_contact(
        contact_type="Person",
        first_name="John",
        last_name="Smith",
        email="john.smith@example.com",
        phone="555-123-4567"
    )

    create_contact(
        contact_type="Company",
        name="Acme Legal Services",
        email="info@acmelegal.com",
        phone="555-987-6543"
    )
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate and normalize inputs
            contact_type = validate_contact_type(contact_type)
            name = validate_optional_string(name, "Name")
            first_name = validate_optional_string(first_name, "First name")
            last_name = validate_optional_string(last_name, "Last name")
            company = validate_optional_string(company, "Company")
            email = validate_email(email)
            phone = validate_phone(phone)
            title = validate_optional_string(title, "Title")

            # Build contact data
            contact_data = {
                "type": contact_type,
                "name": name,
                "first_name": first_name,
                "last_name": last_name,
                "company": company,
                "primary_email_address": email,
                "primary_phone_number": phone,
                "title": title,
            }

            # Validate required fields
            if contact_type == "Person":
                if not first_name and not last_name:
                    raise ClioValidationError(
                        "Person contacts require at least first_name or last_name"
                    )
            elif contact_type == "Company" and not name and not company:
                raise ClioValidationError("Company contacts require either name or company field")

            # Clean and prepare data
            request_data = prepare_request_data(contact_data)
            payload = {"contact": request_data}

            # Create contact
            response = await client.post("contacts", json_data=payload)
            contact_data = extract_model_data(response, Contact)

            return format_json_response(contact_data, include_extra_data=True)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to create contact: {e!s}")


@tool(requires_auth=Clio())
async def update_contact(
    context: ToolContext,
    contact_id: Annotated[int, "The ID of the contact to update"],
    contact_type: Annotated[Optional[str], "Contact type: 'Person' or 'Company'"] = None,
    name: Annotated[Optional[str], "Full name for companies or display name"] = None,
    first_name: Annotated[Optional[str], "First name (for Person type)"] = None,
    last_name: Annotated[Optional[str], "Last name (for Person type)"] = None,
    company: Annotated[Optional[str], "Company name"] = None,
    email: Annotated[Optional[str], "Primary email address"] = None,
    phone: Annotated[Optional[str], "Primary phone number"] = None,
    title: Annotated[Optional[str], "Job title or position"] = None,
) -> Annotated[str, "JSON string containing the updated contact details"]:
    """
    Update an existing contact's information.

    Example:
    ```
    update_contact(
        contact_id=12345,
        email="new.email@example.com",
        phone="555-999-8888",
        title="Senior Partner"
    )
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate contact ID
            contact_id = validate_id(contact_id, "Contact ID")

            # Build update data (only include provided fields)
            update_data = {}

            if contact_type is not None:
                update_data["type"] = validate_contact_type(contact_type)
            if name is not None:
                update_data["name"] = validate_optional_string(name, "Name")
            if first_name is not None:
                update_data["first_name"] = validate_optional_string(first_name, "First name")
            if last_name is not None:
                update_data["last_name"] = validate_optional_string(last_name, "Last name")
            if company is not None:
                update_data["company"] = validate_optional_string(company, "Company")
            if email is not None:
                update_data["primary_email_address"] = validate_email(email)
            if phone is not None:
                update_data["primary_phone_number"] = validate_phone(phone)
            if title is not None:
                update_data["title"] = validate_optional_string(title, "Title")

            if not update_data:
                raise ClioValidationError("At least one field must be provided for update")

            # Clean and prepare data
            request_data = prepare_request_data(update_data)
            payload = {"contact": request_data}

            # Update contact
            response = await client.patch(f"contacts/{contact_id}", json_data=payload)
            contact_data = extract_model_data(response, Contact)

            return format_json_response(contact_data, include_extra_data=True)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to update contact {contact_id}: {e!s}")


@tool(requires_auth=Clio())
async def list_contact_activities(
    context: ToolContext,
    contact_id: Annotated[int, "The ID of the contact"],
    limit: Annotated[
        Optional[int], "Maximum number of activities to return (1-200, default: 50)"
    ] = 50,
    offset: Annotated[
        Optional[int], "Number of activities to skip for pagination (default: 0)"
    ] = 0,
    activity_type: Annotated[
        Optional[str], "Filter by activity type: 'TimeEntry' or 'ExpenseEntry'"
    ] = None,
    include_extra_data: Annotated[
        bool, "Include all available activity data (default: False for summary only)"
    ] = False,
) -> Annotated[str, "JSON string containing the contact's activities"]:
    """
    List all activities (time entries and expenses) associated with a contact.

    Example:
    ```
    list_contact_activities(contact_id=12345, activity_type="TimeEntry")
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate inputs
            contact_id = validate_id(contact_id, "Contact ID")
            limit, offset = validate_limit_offset(limit, offset)
            if activity_type:
                from ..validation import validate_activity_type

                activity_type = validate_activity_type(activity_type)

            # Build search parameters
            params = build_search_params(
                limit=limit,
                offset=offset,
                user_id=contact_id,
                type=activity_type,
            )

            # Get activities
            response = await client.get("activities", params=params)
            activities_data = extract_list_data(response, "activities")

            return format_json_response(activities_data, include_extra_data=include_extra_data)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to retrieve activities for contact {contact_id}: {e!s}")


@tool(requires_auth=Clio())
async def get_contact_relationships(
    context: ToolContext,
    contact_id: Annotated[int, "The ID of the contact"],
    limit: Annotated[
        Optional[int], "Maximum number of relationships to return (1-200, default: 50)"
    ] = 50,
    include_extra_data: Annotated[
        bool, "Include all available relationship data (default: False for summary only)"
    ] = False,
) -> Annotated[str, "JSON string containing the contact's matter relationships"]:
    """
    Get all matter relationships for a contact (as client, attorney, etc.).

    Example:
    ```
    get_contact_relationships(contact_id=12345)
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate inputs
            contact_id = validate_id(contact_id, "Contact ID")
            if limit is not None:
                limit = validate_limit_offset(limit, None)[0]

            # Get matters where this contact is involved
            params = build_search_params(
                limit=limit,
                client_id=contact_id,
            )

            # First, get matters where contact is the client
            client_matters = await client.get("matters", params=params)
            client_data = extract_list_data(client_matters, "matters")

            # Get matters where contact is responsible attorney
            params["responsible_attorney_id"] = contact_id
            del params["client_id"]
            attorney_matters = await client.get("matters", params=params)
            attorney_data = extract_list_data(attorney_matters, "matters")

            # Combine and deduplicate by matter ID
            all_matters = {}
            for matter in client_data:
                matter["relationship_type"] = "client"
                all_matters[matter.get("id")] = matter

            for matter in attorney_data:
                matter_id = matter.get("id")
                if matter_id in all_matters:
                    # Contact has multiple roles in this matter
                    all_matters[matter_id]["relationship_type"] = "client_and_attorney"
                else:
                    matter["relationship_type"] = "responsible_attorney"
                    all_matters[matter_id] = matter

            relationships_data = list(all_matters.values())

            return format_json_response(relationships_data, include_extra_data=include_extra_data)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to retrieve relationships for contact {contact_id}: {e!s}")


@tool(requires_auth=Clio())
async def delete_contact(
    context: ToolContext,
    contact_id: Annotated[str, "The ID of the contact to delete"],
) -> Annotated[str, "JSON response confirming contact deletion"]:
    """Delete a contact.

    Permanently removes a contact from Clio. This action cannot be undone.
    If the contact is associated with matters, documents, or activities,
    deletion may be restricted. Ensure proper authorization and validation
    before deletion.

    Note: Contacts with existing matter relationships or billing records
    may require special handling or cannot be deleted to maintain data integrity.
    """
    validate_id(contact_id, "contact_id")

    try:
        async with ClioClient(context) as client:
            # First get contact info for confirmation message
            contact_response = await client.get(f"/contacts/{contact_id}")
            contact = extract_model_data(contact_response, "contact", Contact)
            contact_name = contact.get("name", f"Contact {contact_id}")

            # Check if contact has active matter relationships
            matters_response = await client.get(
                "/matters", params={"client_id": contact_id, "limit": 1}
            )
            if matters_response.get("matters") and len(matters_response["matters"]) > 0:
                raise ClioValidationError(
                    f"Cannot delete contact '{contact_name}' - contact has active matter relationships. "
                    f"Remove from all matters first or contact administrator."
                )

            # Delete the contact
            await client.delete(f"/contacts/{contact_id}")

            return format_json_response({
                "success": True,
                "message": f"Contact '{contact_name}' (ID: {contact_id}) deleted successfully",
            })

    except ClioError as e:
        raise ClioValidationError(f"Failed to delete contact {contact_id}: {e}")
