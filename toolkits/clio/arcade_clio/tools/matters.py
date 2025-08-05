"""Matter management tools for Clio."""

from datetime import datetime
from typing import Annotated, Optional

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Clio

from ..client import ClioClient
from ..exceptions import ClioError, ClioValidationError
from ..models import Matter
from ..utils import (
    build_search_params,
    extract_list_data,
    extract_model_data,
    format_json_response,
    prepare_request_data,
)
from ..validation import (
    validate_date_string,
    validate_id,
    validate_limit_offset,
    validate_matter_status,
    validate_optional_string,
    validate_required_string,
)


@tool(requires_auth=Clio())
async def list_matters(
    context: ToolContext,
    status: Annotated[
        Optional[str], "Filter by matter status: 'Open', 'Closed', 'Pending' (optional)"
    ] = None,
    client_id: Annotated[Optional[int], "Filter by client contact ID (optional)"] = None,
    responsible_attorney_id: Annotated[
        Optional[int], "Filter by responsible attorney contact ID (optional)"
    ] = None,
    practice_area_id: Annotated[Optional[int], "Filter by practice area ID (optional)"] = None,
    limit: Annotated[
        Optional[int], "Maximum number of matters to return (1-200, default: 50)"
    ] = 50,
    offset: Annotated[Optional[int], "Number of matters to skip for pagination (default: 0)"] = 0,
    include_extra_data: Annotated[
        bool, "Include all available matter data (default: False for summary only)"
    ] = False,
) -> Annotated[str, "JSON string containing the list of matters"]:
    """
    List matters with optional filtering by status, client, attorney, or practice area.

    Examples:
    ```
    list_matters(status="Open")
    list_matters(client_id=12345, limit=10)
    list_matters(responsible_attorney_id=67890, status="Open")
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate inputs
            if status:
                status = validate_matter_status(status)
            if client_id is not None:
                client_id = validate_id(client_id, "Client ID")
            if responsible_attorney_id is not None:
                responsible_attorney_id = validate_id(
                    responsible_attorney_id, "Responsible attorney ID"
                )
            if practice_area_id is not None:
                practice_area_id = validate_id(practice_area_id, "Practice area ID")
            limit, offset = validate_limit_offset(limit, offset)

            # Build search parameters
            params = build_search_params(
                limit=limit,
                offset=offset,
                status=status,
                client_id=client_id,
                responsible_attorney_id=responsible_attorney_id,
                practice_area_id=practice_area_id,
            )

            # Get matters
            response = await client.get_matters(params=params)
            matters_data = extract_list_data(response, "matters")

            return format_json_response(matters_data, include_extra_data=include_extra_data)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to retrieve matters: {e!s}")


@tool(requires_auth=Clio())
async def get_matter(
    context: ToolContext,
    matter_id: Annotated[int, "The ID of the matter to retrieve"],
    include_extra_data: Annotated[
        bool, "Include all available matter data (default: False for summary only)"
    ] = False,
) -> Annotated[str, "JSON string containing the matter details"]:
    """
    Retrieve detailed information about a specific matter.

    Example:
    ```
    get_matter(matter_id=12345)
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate input
            matter_id = validate_id(matter_id, "Matter ID")

            response = await client.get_matter(matter_id)
            matter_data = extract_model_data(response, Matter)

            return format_json_response(matter_data, include_extra_data=include_extra_data)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to retrieve matter {matter_id}: {e!s}")


@tool(requires_auth=Clio())
async def create_matter(
    context: ToolContext,
    description: Annotated[str, "Description or name of the matter"],
    client_id: Annotated[Optional[int], "Client contact ID (optional)"] = None,
    responsible_attorney_id: Annotated[
        Optional[int], "Responsible attorney contact ID (optional)"
    ] = None,
    practice_area_id: Annotated[Optional[int], "Practice area ID (optional)"] = None,
    open_date: Annotated[
        Optional[str], "Matter open date in YYYY-MM-DD format (optional, defaults to today)"
    ] = None,
    billable: Annotated[bool, "Whether the matter is billable (default: True)"] = True,
    billing_method: Annotated[
        Optional[str], "Billing method (e.g., 'hourly', 'flat_fee', optional)"
    ] = None,
) -> Annotated[str, "JSON string containing the created matter details"]:
    """
    Create a new matter in Clio.

    Examples:
    ```
    create_matter(
        description="Personal Injury Case - Smith vs. Acme Corp",
        client_id=12345,
        responsible_attorney_id=67890,
        billable=True
    )

    create_matter(
        description="Contract Review - Tech Startup",
        billing_method="flat_fee"
    )
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate inputs
            description = validate_required_string(description, "Description")
            if client_id is not None:
                client_id = validate_id(client_id, "Client ID")
            if responsible_attorney_id is not None:
                responsible_attorney_id = validate_id(
                    responsible_attorney_id, "Responsible attorney ID"
                )
            if practice_area_id is not None:
                practice_area_id = validate_id(practice_area_id, "Practice area ID")
            billing_method = validate_optional_string(billing_method, "Billing method")

            # Parse open_date if provided
            parsed_open_date = validate_date_string(open_date, "Open date")

            # Build matter data
            matter_data = {
                "description": description,
                "client_id": client_id,
                "responsible_attorney_id": responsible_attorney_id,
                "practice_area_id": practice_area_id,
                "open_date": parsed_open_date,
                "billable": billable,
                "billing_method": billing_method,
                "status": "Open",  # Default status for new matters
            }

            # Clean and prepare data
            request_data = prepare_request_data(matter_data)
            payload = {"matter": request_data}

            # Create matter
            response = await client.post("matters", json_data=payload)
            matter_data = extract_model_data(response, Matter)

            return format_json_response(matter_data, include_extra_data=True)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to create matter: {e!s}")


@tool(requires_auth=Clio())
async def update_matter(
    context: ToolContext,
    matter_id: Annotated[int, "The ID of the matter to update"],
    description: Annotated[Optional[str], "Matter description"] = None,
    status: Annotated[Optional[str], "Matter status: 'Open', 'Closed', 'Pending'"] = None,
    client_id: Annotated[Optional[int], "Client contact ID"] = None,
    responsible_attorney_id: Annotated[Optional[int], "Responsible attorney contact ID"] = None,
    practice_area_id: Annotated[Optional[int], "Practice area ID"] = None,
    close_date: Annotated[
        Optional[str], "Matter close date in YYYY-MM-DD format (required if status is 'Closed')"
    ] = None,
    billable: Annotated[Optional[bool], "Whether the matter is billable"] = None,
    billing_method: Annotated[Optional[str], "Billing method"] = None,
) -> Annotated[str, "JSON string containing the updated matter details"]:
    """
    Update an existing matter's information.

    Examples:
    ```
    update_matter(
        matter_id=12345,
        status="Closed",
        close_date="2024-01-15"
    )

    update_matter(
        matter_id=67890,
        responsible_attorney_id=11111,
        billing_method="hourly"
    )
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Build update data (only include provided fields)
            update_data = {}

            if description is not None:
                update_data["description"] = description
            if status is not None:
                update_data["status"] = validate_matter_status(status)
            if client_id is not None:
                update_data["client_id"] = client_id
            if responsible_attorney_id is not None:
                update_data["responsible_attorney_id"] = responsible_attorney_id
            if practice_area_id is not None:
                update_data["practice_area_id"] = practice_area_id
            if billable is not None:
                update_data["billable"] = billable
            if billing_method is not None:
                update_data["billing_method"] = billing_method

            # Handle close_date
            if close_date is not None:
                try:
                    parsed_close_date = datetime.strptime(close_date, "%Y-%m-%d")
                    update_data["close_date"] = parsed_close_date
                except ValueError:
                    raise ClioValidationError("close_date must be in YYYY-MM-DD format")

            # Validation: if status is Closed, close_date should be provided
            if status == "Closed" and close_date is None:
                update_data["close_date"] = datetime.now()  # Default to today

            if not update_data:
                raise ClioValidationError("At least one field must be provided for update")

            # Clean and prepare data
            request_data = prepare_request_data(update_data)
            payload = {"matter": request_data}

            # Update matter
            response = await client.patch(f"matters/{matter_id}", json_data=payload)
            matter_data = extract_model_data(response, Matter)

            return format_json_response(matter_data, include_extra_data=True)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to update matter {matter_id}: {e!s}")


@tool(requires_auth=Clio())
async def close_matter(
    context: ToolContext,
    matter_id: Annotated[int, "The ID of the matter to close"],
    close_date: Annotated[
        Optional[str], "Close date in YYYY-MM-DD format (optional, defaults to today)"
    ] = None,
) -> Annotated[str, "JSON string containing the closed matter details"]:
    """
    Close a matter by setting its status to 'Closed' and setting the close date.

    Example:
    ```
    close_matter(matter_id=12345, close_date="2024-01-15")
    close_matter(matter_id=67890)  # Uses today's date
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Parse close_date or use today
            if close_date:
                try:
                    parsed_close_date = datetime.strptime(close_date, "%Y-%m-%d")
                except ValueError:
                    raise ClioValidationError("close_date must be in YYYY-MM-DD format")
            else:
                parsed_close_date = datetime.now()

            # Update matter status and close date
            update_data = {
                "status": "Closed",
                "close_date": parsed_close_date,
            }

            request_data = prepare_request_data(update_data)
            payload = {"matter": request_data}

            # Update matter
            response = await client.patch(f"matters/{matter_id}", json_data=payload)
            matter_data = extract_model_data(response, Matter)

            return format_json_response(matter_data, include_extra_data=True)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to close matter {matter_id}: {e!s}")


@tool(requires_auth=Clio())
async def get_matter_activities(
    context: ToolContext,
    matter_id: Annotated[int, "The ID of the matter"],
    activity_type: Annotated[
        Optional[str], "Filter by activity type: 'TimeEntry' or 'ExpenseEntry' (optional)"
    ] = None,
    limit: Annotated[
        Optional[int], "Maximum number of activities to return (1-200, default: 50)"
    ] = 50,
    offset: Annotated[
        Optional[int], "Number of activities to skip for pagination (default: 0)"
    ] = 0,
    include_extra_data: Annotated[
        bool, "Include all available activity data (default: False for summary only)"
    ] = False,
) -> Annotated[str, "JSON string containing the matter's activities"]:
    """
    Get all activities (time entries and expenses) for a specific matter.

    Examples:
    ```
    get_matter_activities(matter_id=12345)
    get_matter_activities(matter_id=12345, activity_type="TimeEntry")
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Build search parameters
            params = build_search_params(
                limit=limit,
                offset=offset,
                matter_id=matter_id,
                type=activity_type,
            )

            # Get activities
            response = await client.get_activities(params=params)
            activities_data = extract_list_data(response, "activities")

            return format_json_response(activities_data, include_extra_data=include_extra_data)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to retrieve activities for matter {matter_id}: {e!s}")


@tool(requires_auth=Clio())
async def add_matter_participant(
    context: ToolContext,
    matter_id: Annotated[int, "The ID of the matter"],
    contact_id: Annotated[int, "The ID of the contact to add"],
    role: Annotated[
        str, "Role of the participant: 'client', 'responsible_attorney', 'originating_attorney'"
    ],
) -> Annotated[str, "JSON string containing the updated matter details"]:
    """
    Add a participant (client or attorney) to a matter.

    Examples:
    ```
    add_matter_participant(matter_id=12345, contact_id=67890, role="client")
    add_matter_participant(matter_id=12345, contact_id=11111, role="responsible_attorney")
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Map role to field name
            role_mapping = {
                "client": "client_id",
                "responsible_attorney": "responsible_attorney_id",
                "originating_attorney": "originating_attorney_id",
            }

            if role not in role_mapping:
                valid_roles = ", ".join(role_mapping.keys())
                raise ClioValidationError(f"Invalid role '{role}'. Must be one of: {valid_roles}")

            field_name = role_mapping[role]
            update_data = {field_name: contact_id}

            request_data = prepare_request_data(update_data)
            payload = {"matter": request_data}

            # Update matter
            response = await client.patch(f"matters/{matter_id}", json_data=payload)
            matter_data = extract_model_data(response, Matter)

            return format_json_response(matter_data, include_extra_data=True)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to add participant to matter {matter_id}: {e!s}")


@tool(requires_auth=Clio())
async def remove_matter_participant(
    context: ToolContext,
    matter_id: Annotated[int, "The ID of the matter"],
    role: Annotated[
        str, "Role to remove: 'client', 'responsible_attorney', 'originating_attorney'"
    ],
) -> Annotated[str, "JSON string containing the updated matter details"]:
    """
    Remove a participant from a matter by clearing their role.

    Examples:
    ```
    remove_matter_participant(matter_id=12345, role="originating_attorney")
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Map role to field name
            role_mapping = {
                "client": "client_id",
                "responsible_attorney": "responsible_attorney_id",
                "originating_attorney": "originating_attorney_id",
            }

            if role not in role_mapping:
                valid_roles = ", ".join(role_mapping.keys())
                raise ClioValidationError(f"Invalid role '{role}'. Must be one of: {valid_roles}")

            field_name = role_mapping[role]
            update_data = {field_name: None}  # Clear the field

            request_data = prepare_request_data(update_data)
            payload = {"matter": request_data}

            # Update matter
            response = await client.patch(f"matters/{matter_id}", json_data=payload)
            matter_data = extract_model_data(response, Matter)

            return format_json_response(matter_data, include_extra_data=True)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to remove participant from matter {matter_id}: {e!s}")


@tool(requires_auth=Clio())
async def search_matters(
    context: ToolContext,
    query: Annotated[Optional[str], "Search query to filter matters by description"] = None,
    client_id: Annotated[Optional[str], "Filter matters by client contact ID"] = None,
    status: Annotated[Optional[str], "Filter matters by status (Open, Closed, etc.)"] = None,
    practice_area: Annotated[Optional[str], "Filter matters by practice area"] = None,
    responsible_attorney_id: Annotated[Optional[str], "Filter by responsible attorney ID"] = None,
    originating_attorney_id: Annotated[Optional[str], "Filter by originating attorney ID"] = None,
    billing_method: Annotated[Optional[str], "Filter by billing method"] = None,
    open_date_from: Annotated[Optional[str], "Filter by open date from (YYYY-MM-DD)"] = None,
    open_date_to: Annotated[Optional[str], "Filter by open date to (YYYY-MM-DD)"] = None,
    limit: Annotated[int, "Maximum number of matters to return (default: 50)"] = 50,
    offset: Annotated[int, "Number of matters to skip for pagination (default: 0)"] = 0,
    fields: Annotated[Optional[str], "Comma-separated list of fields to include"] = None,
) -> Annotated[str, "JSON response with search results and pagination info"]:
    """Advanced matter search with multiple filters.

    Provides comprehensive search capabilities for matters with support for filtering
    by client, status, practice area, attorneys, billing method, and date ranges.
    Supports text search across matter descriptions and returns paginated results.
    """
    validate_positive_number(limit, "limit")
    validate_positive_number(offset, "offset")

    if client_id:
        validate_id(client_id, "client_id")
    if responsible_attorney_id:
        validate_id(responsible_attorney_id, "responsible_attorney_id")
    if originating_attorney_id:
        validate_id(originating_attorney_id, "originating_attorney_id")
    if query:
        validate_optional_string(query, "query")
    if status:
        validate_optional_string(status, "status")
    if practice_area:
        validate_optional_string(practice_area, "practice_area")
    if billing_method:
        validate_optional_string(billing_method, "billing_method")
    if open_date_from:
        validate_date_string(open_date_from, "open_date_from")
    if open_date_to:
        validate_date_string(open_date_to, "open_date_to")
    if fields:
        validate_optional_string(fields, "fields")

    try:
        async with ClioClient(context) as client:
            # Build comprehensive search parameters
            params = build_search_params({
                "limit": limit,
                "offset": offset,
                "query": query,
                "client_id": client_id,
                "status": status,
                "practice_area": practice_area,
                "responsible_attorney_id": responsible_attorney_id,
                "originating_attorney_id": originating_attorney_id,
                "billing_method": billing_method,
                "open_date_from": open_date_from,
                "open_date_to": open_date_to,
                "fields": fields,
            })

            response = await client.get("/matters", params=params)
            matters = extract_list_data(response, "matters", Matter)

            return format_json_response({
                "success": True,
                "matters": matters,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": response.get("meta", {}).get("total_count"),
                },
                "search_query": query,
                "filters_applied": {
                    key: value
                    for key, value in {
                        "client_id": client_id,
                        "status": status,
                        "practice_area": practice_area,
                        "responsible_attorney_id": responsible_attorney_id,
                        "originating_attorney_id": originating_attorney_id,
                        "billing_method": billing_method,
                        "open_date_from": open_date_from,
                        "open_date_to": open_date_to,
                    }.items()
                    if value is not None
                },
            })

    except ClioError as e:
        raise ClioValidationError(f"Failed to search matters: {e}")


@tool(requires_auth=Clio())
async def delete_matter(
    context: ToolContext,
    matter_id: Annotated[str, "The ID of the matter to delete"],
) -> Annotated[str, "JSON response confirming matter deletion"]:
    """Delete a matter.

    Permanently removes a matter from Clio. This action cannot be undone.
    If the matter has associated time entries, expenses, documents, or bills,
    deletion may be restricted to maintain data integrity. Ensure proper
    authorization and validation before deletion.

    Note: Matters with existing billing records, documents, or activities
    may require special handling or cannot be deleted. Consider closing
    the matter instead of deletion for matters with historical data.
    """
    validate_id(matter_id, "matter_id")

    try:
        async with ClioClient(context) as client:
            # First get matter info for confirmation message
            matter_response = await client.get(f"/matters/{matter_id}")
            matter = extract_model_data(matter_response, "matter", Matter)
            matter_desc = matter.get("description", f"Matter {matter_id}")

            # Check if matter has associated activities (time/expenses)
            activities_response = await client.get(
                "/activities", params={"matter_id": matter_id, "limit": 1}
            )
            if activities_response.get("activities") and len(activities_response["activities"]) > 0:
                raise ClioValidationError(
                    f"Cannot delete matter '{matter_desc}' - matter has associated time entries or expenses. "
                    f"Remove all activities first or use close_matter instead."
                )

            # Check if matter has associated documents
            documents_response = await client.get(
                "/documents", params={"matter_id": matter_id, "limit": 1}
            )
            if documents_response.get("documents") and len(documents_response["documents"]) > 0:
                raise ClioValidationError(
                    f"Cannot delete matter '{matter_desc}' - matter has associated documents. "
                    f"Remove all documents first or use close_matter instead."
                )

            # Check if matter has associated bills
            bills_response = await client.get("/bills", params={"matter_id": matter_id, "limit": 1})
            if bills_response.get("bills") and len(bills_response["bills"]) > 0:
                raise ClioValidationError(
                    f"Cannot delete matter '{matter_desc}' - matter has associated bills. "
                    f"Billing records must be preserved for audit purposes. Use close_matter instead."
                )

            # Delete the matter
            await client.delete(f"/matters/{matter_id}")

            return format_json_response({
                "success": True,
                "message": f"Matter '{matter_desc}' (ID: {matter_id}) deleted successfully",
            })

    except ClioError as e:
        raise ClioValidationError(f"Failed to delete matter {matter_id}: {e}")
