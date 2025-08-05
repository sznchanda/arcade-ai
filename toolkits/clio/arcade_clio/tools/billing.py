"""Time tracking and billing tools for Clio."""

from datetime import datetime
from decimal import Decimal
from typing import Annotated, Optional

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Clio

from ..client import ClioClient
from ..exceptions import ClioError, ClioValidationError
from ..models import Activity, Bill
from ..utils import (
    build_search_params,
    extract_list_data,
    extract_model_data,
    format_json_response,
    prepare_request_data,
)
from ..validation import (
    validate_amount,
    validate_date_string,
    validate_hours,
    validate_id,
    validate_optional_string,
    validate_positive_number,
    validate_required_string,
)


@tool(requires_auth=Clio())
async def create_time_entry(
    context: ToolContext,
    matter_id: Annotated[int, "The ID of the matter to log time for"],
    date: Annotated[str, "Date of work in YYYY-MM-DD format"],
    hours: Annotated[float, "Number of hours worked (e.g., 2.5 for 2 hours 30 minutes)"],
    description: Annotated[str, "Description of work performed"],
    activity_type_id: Annotated[
        Optional[int], "Activity type ID for billing rates (optional)"
    ] = None,
    rate: Annotated[
        Optional[float], "Hourly rate override (optional, uses default rate if not specified)"
    ] = None,
) -> Annotated[str, "JSON string containing the created time entry details"]:
    """
    Create a new time entry for billable hours on a matter.

    Examples:
    ```
    create_time_entry(
        matter_id=12345,
        date="2024-01-15",
        hours=2.5,
        description="Reviewed contract terms and drafted amendments",
        rate=350.00
    )

    create_time_entry(
        matter_id=67890,
        date="2024-01-16",
        hours=1.0,
        description="Client consultation call"
    )
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate inputs
            matter_id = validate_id(matter_id, "Matter ID")
            work_date = validate_date_string(date, "Date")
            hours = validate_hours(hours)
            description = validate_required_string(description, "Description")
            if activity_type_id is not None:
                activity_type_id = validate_id(activity_type_id, "Activity type ID")
            if rate is not None:
                rate = validate_positive_number(rate, "Rate")

            # Convert hours to decimal for precision
            hours_decimal = Decimal(str(hours))

            # Build time entry data
            time_entry_data = {
                "type": "TimeEntry",
                "matter_id": matter_id,
                "date": work_date,
                "quantity": hours_decimal,  # Hours for time entries
                "description": description,
                "activity_type_id": activity_type_id,
            }

            # Add rate if provided
            if rate is not None:
                if rate < 0:
                    raise ClioValidationError("Rate must be non-negative")
                time_entry_data["price"] = Decimal(str(rate))

            # Clean and prepare data
            request_data = prepare_request_data(time_entry_data)
            payload = {"activity": request_data}

            # Create time entry
            response = await client.post("activities", json_data=payload)
            activity_data = extract_model_data(response, Activity)

            return format_json_response(activity_data, include_extra_data=True)

        except ClioError:
            raise
        except (ValueError, TypeError, ArithmeticError) as e:
            raise ClioValidationError(f"Invalid time entry data: {e!s}")
        except Exception as e:
            raise ClioError(f"Failed to create time entry: {e!s}", retry=True)


@tool(requires_auth=Clio())
async def update_time_entry(
    context: ToolContext,
    time_entry_id: Annotated[int, "The ID of the time entry to update"],
    date: Annotated[Optional[str], "Date in YYYY-MM-DD format"] = None,
    hours: Annotated[Optional[float], "Number of hours worked"] = None,
    description: Annotated[Optional[str], "Description of work performed"] = None,
    activity_type_id: Annotated[Optional[int], "Activity type ID"] = None,
    rate: Annotated[Optional[float], "Hourly rate"] = None,
) -> Annotated[str, "JSON string containing the updated time entry details"]:
    """
    Update an existing time entry.

    Example:
    ```
    update_time_entry(
        time_entry_id=12345,
        hours=3.0,
        description="Updated: Reviewed contract terms, drafted amendments, and client call"
    )
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Build update data (only include provided fields)
            update_data = {}

            if date is not None:
                try:
                    update_data["date"] = datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    raise ClioValidationError("Date must be in YYYY-MM-DD format")

            if hours is not None:
                if hours <= 0:
                    raise ClioValidationError("Hours must be greater than 0")
                update_data["quantity"] = Decimal(str(hours))

            if description is not None:
                update_data["description"] = description

            if activity_type_id is not None:
                update_data["activity_type_id"] = activity_type_id

            if rate is not None:
                if rate < 0:
                    raise ClioValidationError("Rate must be non-negative")
                update_data["price"] = Decimal(str(rate))

            if not update_data:
                raise ClioValidationError("At least one field must be provided for update")

            # Clean and prepare data
            request_data = prepare_request_data(update_data)
            payload = {"activity": request_data}

            # Update time entry
            response = await client.patch(f"activities/{time_entry_id}", json_data=payload)
            activity_data = extract_model_data(response, Activity)

            return format_json_response(activity_data, include_extra_data=True)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to update time entry {time_entry_id}: {e!s}")


@tool(requires_auth=Clio())
async def get_time_entries(
    context: ToolContext,
    matter_id: Annotated[Optional[int], "Filter by matter ID (optional)"] = None,
    user_id: Annotated[Optional[int], "Filter by user/attorney ID (optional)"] = None,
    date_from: Annotated[Optional[str], "Start date filter in YYYY-MM-DD format (optional)"] = None,
    date_to: Annotated[Optional[str], "End date filter in YYYY-MM-DD format (optional)"] = None,
    billed: Annotated[
        Optional[bool],
        "Filter by billing status: True for billed, False for unbilled, None for all",
    ] = None,
    limit: Annotated[
        Optional[int], "Maximum number of entries to return (1-200, default: 50)"
    ] = 50,
    offset: Annotated[Optional[int], "Number of entries to skip for pagination (default: 0)"] = 0,
    include_extra_data: Annotated[
        bool, "Include all available time entry data (default: False for summary only)"
    ] = False,
) -> Annotated[str, "JSON string containing time entries"]:
    """
    Retrieve time entries with optional filtering.

    Examples:
    ```
    get_time_entries(matter_id=12345, billed=False)
    get_time_entries(user_id=67890, date_from="2024-01-01", date_to="2024-01-31")
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Build search parameters
            params = build_search_params(
                limit=limit,
                offset=offset,
                matter_id=matter_id,
                user_id=user_id,
                type="TimeEntry",
                billed=billed,
            )

            # Add date filters
            if date_from:
                try:
                    datetime.strptime(date_from, "%Y-%m-%d")
                    params["date_from"] = date_from
                except ValueError:
                    raise ClioValidationError("date_from must be in YYYY-MM-DD format")

            if date_to:
                try:
                    datetime.strptime(date_to, "%Y-%m-%d")
                    params["date_to"] = date_to
                except ValueError:
                    raise ClioValidationError("date_to must be in YYYY-MM-DD format")

            # Get activities
            response = await client.get_activities(params=params)
            activities_data = extract_list_data(response, "activities")

            return format_json_response(activities_data, include_extra_data=include_extra_data)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to retrieve time entries: {e!s}")


@tool(requires_auth=Clio())
async def create_expense(
    context: ToolContext,
    matter_id: Annotated[int, "The ID of the matter to log expense for"],
    date: Annotated[str, "Date of expense in YYYY-MM-DD format"],
    amount: Annotated[float, "Expense amount"],
    description: Annotated[str, "Description of the expense"],
    vendor: Annotated[Optional[str], "Vendor or payee (optional)"] = None,
    category: Annotated[Optional[str], "Expense category (optional)"] = None,
) -> Annotated[str, "JSON string containing the created expense details"]:
    """
    Create a new expense entry for a matter.

    Examples:
    ```
    create_expense(
        matter_id=12345,
        date="2024-01-15",
        amount=45.50,
        description="Filing fees for motion",
        vendor="County Clerk's Office"
    )

    create_expense(
        matter_id=67890,
        date="2024-01-16",
        amount=125.00,
        description="Expert witness consultation",
        category="Professional Services"
    )
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate inputs
            matter_id = validate_id(matter_id, "Matter ID")
            expense_date = validate_date_string(date, "Date")
            amount = validate_amount(amount, "Amount")
            description = validate_required_string(description, "Description")
            vendor = validate_optional_string(vendor, "Vendor")
            category = validate_optional_string(category, "Category")

            # Convert amount to decimal for precision
            amount_decimal = Decimal(str(amount))

            # Build expense data
            expense_data = {
                "type": "ExpenseEntry",
                "matter_id": matter_id,
                "date": expense_date,
                "quantity": 1,  # Quantity is always 1 for expenses
                "price": amount_decimal,  # Price is the expense amount
                "description": description,
                "vendor": vendor,
                "category": category,
            }

            # Clean and prepare data
            request_data = prepare_request_data(expense_data)
            payload = {"activity": request_data}

            # Create expense
            response = await client.post("activities", json_data=payload)
            activity_data = extract_model_data(response, Activity)

            return format_json_response(activity_data, include_extra_data=True)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to create expense: {e!s}")


@tool(requires_auth=Clio())
async def get_expenses(
    context: ToolContext,
    matter_id: Annotated[Optional[int], "Filter by matter ID (optional)"] = None,
    user_id: Annotated[Optional[int], "Filter by user ID (optional)"] = None,
    date_from: Annotated[Optional[str], "Start date filter in YYYY-MM-DD format (optional)"] = None,
    date_to: Annotated[Optional[str], "End date filter in YYYY-MM-DD format (optional)"] = None,
    billed: Annotated[
        Optional[bool],
        "Filter by billing status: True for billed, False for unbilled, None for all",
    ] = None,
    limit: Annotated[
        Optional[int], "Maximum number of expenses to return (1-200, default: 50)"
    ] = 50,
    offset: Annotated[Optional[int], "Number of expenses to skip for pagination (default: 0)"] = 0,
    include_extra_data: Annotated[
        bool, "Include all available expense data (default: False for summary only)"
    ] = False,
) -> Annotated[str, "JSON string containing expenses"]:
    """
    Retrieve expense entries with optional filtering.

    Examples:
    ```
    get_expenses(matter_id=12345, billed=False)
    get_expenses(date_from="2024-01-01", date_to="2024-01-31")
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Build search parameters
            params = build_search_params(
                limit=limit,
                offset=offset,
                matter_id=matter_id,
                user_id=user_id,
                type="ExpenseEntry",
                billed=billed,
            )

            # Add date filters
            if date_from:
                try:
                    datetime.strptime(date_from, "%Y-%m-%d")
                    params["date_from"] = date_from
                except ValueError:
                    raise ClioValidationError("date_from must be in YYYY-MM-DD format")

            if date_to:
                try:
                    datetime.strptime(date_to, "%Y-%m-%d")
                    params["date_to"] = date_to
                except ValueError:
                    raise ClioValidationError("date_to must be in YYYY-MM-DD format")

            # Get activities
            response = await client.get_activities(params=params)
            activities_data = extract_list_data(response, "activities")

            return format_json_response(activities_data, include_extra_data=include_extra_data)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to retrieve expenses: {e!s}")


@tool(requires_auth=Clio())
async def create_bill(
    context: ToolContext,
    matter_id: Annotated[int, "The ID of the matter to bill"],
    issued_date: Annotated[
        Optional[str], "Bill issue date in YYYY-MM-DD format (optional, defaults to today)"
    ] = None,
    due_date: Annotated[Optional[str], "Bill due date in YYYY-MM-DD format (optional)"] = None,
    include_unbilled_time: Annotated[
        bool, "Include all unbilled time entries (default: True)"
    ] = True,
    include_unbilled_expenses: Annotated[
        bool, "Include all unbilled expenses (default: True)"
    ] = True,
    note: Annotated[Optional[str], "Bill note or memo (optional)"] = None,
) -> Annotated[str, "JSON string containing the created bill details"]:
    """
    Create a new bill for a matter, optionally including unbilled time and expenses.

    Examples:
    ```
    create_bill(
        matter_id=12345,
        due_date="2024-02-15",
        note="January 2024 legal services"
    )

    create_bill(
        matter_id=67890,
        include_unbilled_time=True,
        include_unbilled_expenses=False
    )
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Parse dates
            parsed_issued_date = None
            if issued_date:
                try:
                    parsed_issued_date = datetime.strptime(issued_date, "%Y-%m-%d")
                except ValueError:
                    raise ClioValidationError("issued_date must be in YYYY-MM-DD format")
            else:
                parsed_issued_date = datetime.now()

            parsed_due_date = None
            if due_date:
                try:
                    parsed_due_date = datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    raise ClioValidationError("due_date must be in YYYY-MM-DD format")

            # Build bill data
            bill_data = {
                "matter_id": matter_id,
                "issued_date": parsed_issued_date,
                "due_date": parsed_due_date,
                "state": "draft",  # Default to draft state
                "note": note,
                "include_unbilled_time": include_unbilled_time,
                "include_unbilled_expenses": include_unbilled_expenses,
            }

            # Clean and prepare data
            request_data = prepare_request_data(bill_data)
            payload = {"bill": request_data}

            # Create bill
            response = await client.post("bills", json_data=payload)
            bill_data = extract_model_data(response, Bill)

            return format_json_response(bill_data, include_extra_data=True)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to create bill: {e!s}")


@tool(requires_auth=Clio())
async def get_bills(
    context: ToolContext,
    matter_id: Annotated[Optional[int], "Filter by matter ID (optional)"] = None,
    state: Annotated[
        Optional[str], "Filter by bill state: 'draft', 'sent', 'paid', etc. (optional)"
    ] = None,
    date_from: Annotated[Optional[str], "Start date filter in YYYY-MM-DD format (optional)"] = None,
    date_to: Annotated[Optional[str], "End date filter in YYYY-MM-DD format (optional)"] = None,
    limit: Annotated[Optional[int], "Maximum number of bills to return (1-200, default: 50)"] = 50,
    offset: Annotated[Optional[int], "Number of bills to skip for pagination (default: 0)"] = 0,
    include_extra_data: Annotated[
        bool, "Include all available bill data (default: False for summary only)"
    ] = False,
) -> Annotated[str, "JSON string containing bills"]:
    """
    Retrieve bills with optional filtering.

    Examples:
    ```
    get_bills(matter_id=12345, state="sent")
    get_bills(state="draft", limit=10)
    get_bills(date_from="2024-01-01", date_to="2024-01-31")
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Build search parameters
            params = build_search_params(
                limit=limit,
                offset=offset,
                matter_id=matter_id,
                state=state,
            )

            # Add date filters
            if date_from:
                try:
                    datetime.strptime(date_from, "%Y-%m-%d")
                    params["issued_date_from"] = date_from
                except ValueError:
                    raise ClioValidationError("date_from must be in YYYY-MM-DD format")

            if date_to:
                try:
                    datetime.strptime(date_to, "%Y-%m-%d")
                    params["issued_date_to"] = date_to
                except ValueError:
                    raise ClioValidationError("date_to must be in YYYY-MM-DD format")

            # Get bills
            response = await client.get_bills(params=params)
            bills_data = extract_list_data(response, "bills")

            return format_json_response(bills_data, include_extra_data=include_extra_data)

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to retrieve bills: {e!s}")


# Unified Activity Management Tools (based on Klavis MCP documentation)


@tool(requires_auth=Clio())
async def list_activities(
    context: ToolContext,
    limit: Annotated[int, "Maximum number of activities to return (default: 50)"] = 50,
    offset: Annotated[int, "Number of activities to skip for pagination (default: 0)"] = 0,
    matter_id: Annotated[Optional[str], "Filter activities by matter ID"] = None,
    user_id: Annotated[Optional[str], "Filter activities by user ID"] = None,
    type: Annotated[Optional[str], "Filter by activity type: 'TimeEntry' or 'ExpenseEntry'"] = None,
    date_from: Annotated[Optional[str], "Filter activities from date (YYYY-MM-DD)"] = None,
    date_to: Annotated[Optional[str], "Filter activities to date (YYYY-MM-DD)"] = None,
    billable: Annotated[Optional[bool], "Filter by billable status"] = None,
    billed: Annotated[Optional[bool], "Filter by billed status"] = None,
    fields: Annotated[Optional[str], "Comma-separated list of fields to include"] = None,
) -> Annotated[str, "JSON response with list of activities and pagination info"]:
    """List activities (time entries and expenses) in Clio with filtering.

    Provides unified access to both time entries and expense entries with comprehensive
    filtering options. Returns paginated results with activity details including
    matter association, billing status, and financial information.
    """
    validate_positive_number(limit, "limit")
    validate_positive_number(offset, "offset")

    if matter_id:
        validate_id(matter_id, "matter_id")
    if user_id:
        validate_id(user_id, "user_id")
    if type and type not in ["TimeEntry", "ExpenseEntry"]:
        raise ClioValidationError("type must be 'TimeEntry' or 'ExpenseEntry'")
    if date_from:
        validate_date_string(date_from, "date_from")
    if date_to:
        validate_date_string(date_to, "date_to")
    if fields:
        validate_optional_string(fields, "fields")

    try:
        async with ClioClient(context) as client:
            # Build query parameters
            params = build_search_params({
                "limit": limit,
                "offset": offset,
                "matter_id": matter_id,
                "user_id": user_id,
                "type": type,
                "date_from": date_from,
                "date_to": date_to,
                "billable": billable,
                "billed": billed,
                "fields": fields,
            })

            response = await client.get("/activities", params=params)
            activities = extract_list_data(response, "activities", Activity)

            return format_json_response({
                "success": True,
                "activities": activities,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": response.get("meta", {}).get("total_count"),
                },
            })

    except ClioError as e:
        raise ClioValidationError(f"Failed to list activities: {e}")


@tool(requires_auth=Clio())
async def get_activity(
    context: ToolContext,
    activity_id: Annotated[str, "The ID of the activity to retrieve"],
    fields: Annotated[Optional[str], "Comma-separated list of fields to include"] = None,
) -> Annotated[str, "JSON response with activity details"]:
    """Get a specific activity by ID.

    Returns detailed information about a time entry or expense entry including
    matter association, billing status, financial details, and user information.
    Works for both time entries and expense entries.
    """
    validate_id(activity_id, "activity_id")
    if fields:
        validate_optional_string(fields, "fields")

    try:
        async with ClioClient(context) as client:
            params = build_search_params({"fields": fields})
            response = await client.get(f"/activities/{activity_id}", params=params)
            activity = extract_model_data(response, "activity", Activity)

            return format_json_response({"success": True, "activity": activity})

    except ClioError as e:
        raise ClioValidationError(f"Failed to get activity {activity_id}: {e}")


@tool(requires_auth=Clio())
async def delete_activity(
    context: ToolContext,
    activity_id: Annotated[str, "The ID of the activity to delete"],
) -> Annotated[str, "JSON response confirming activity deletion"]:
    """Delete an activity.

    Permanently removes a time entry or expense entry from Clio. This action cannot
    be undone. If the activity has been billed, deletion may affect billing records.
    Ensure proper authorization and validation before deletion.

    Note: Deleting billed activities may require additional permissions and
    could impact financial reporting.
    """
    validate_id(activity_id, "activity_id")

    try:
        async with ClioClient(context) as client:
            # First get activity info for confirmation message
            activity_response = await client.get(f"/activities/{activity_id}")
            activity = extract_model_data(activity_response, "activity", Activity)
            activity_type = activity.get("type", "Activity")
            activity_desc = activity.get("description", f"{activity_type} {activity_id}")

            # Check if activity is billed
            if activity.get("billed"):
                raise ClioValidationError(
                    f"Cannot delete billed {activity_type.lower()}. "
                    f"Remove from bill first or contact administrator."
                )

            # Delete the activity
            await client.delete(f"/activities/{activity_id}")

            return format_json_response({
                "success": True,
                "message": f"{activity_type} '{activity_desc}' (ID: {activity_id}) deleted successfully",
            })

    except ClioError as e:
        raise ClioValidationError(f"Failed to delete activity {activity_id}: {e}")
