"""Utility functions for the Clio toolkit."""

import json
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional, Union


def format_datetime(dt: Optional[datetime]) -> Optional[str]:
    """Format datetime for Clio API."""
    return dt.isoformat() if dt else None


def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse datetime from Clio API response."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def format_decimal(value: Optional[Union[Decimal, float, str]]) -> Optional[str]:
    """Format decimal for Clio API."""
    if value is None:
        return None
    return str(Decimal(str(value)))


def parse_decimal(value: Optional[Union[str, float, int]]) -> Optional[Decimal]:
    """Parse decimal from Clio API response."""
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return None


def remove_none_values(data: dict[str, Any]) -> dict[str, Any]:
    """Remove None values from dictionary recursively."""
    cleaned = {}
    for key, value in data.items():
        if value is not None:
            if isinstance(value, dict):
                cleaned_value = remove_none_values(value)
                if cleaned_value:  # Only add if the dict is not empty after cleaning
                    cleaned[key] = cleaned_value
            elif isinstance(value, list):
                cleaned_list = []
                for item in value:
                    if isinstance(item, dict):
                        cleaned_item = remove_none_values(item)
                        if cleaned_item:
                            cleaned_list.append(cleaned_item)
                    elif item is not None:
                        cleaned_list.append(item)
                if cleaned_list:
                    cleaned[key] = cleaned_list
            else:
                cleaned[key] = value
    return cleaned


def prepare_request_data(data: dict[str, Any]) -> dict[str, Any]:
    """Prepare data for API request by cleaning and formatting."""
    # Remove None values
    cleaned = remove_none_values(data)

    # Convert datetime objects to ISO strings
    for key, value in cleaned.items():
        if isinstance(value, datetime):
            cleaned[key] = format_datetime(value)
        elif isinstance(value, Decimal):
            cleaned[key] = format_decimal(value)

    return cleaned


def extract_model_data(response_data: dict[str, Any], model_class: type) -> dict[str, Any]:
    """Extract and clean model data from API response."""
    if not response_data:
        return {}

    # The response might have the actual data nested under the model name
    # e.g., {"contact": {...}} or directly as {...}
    if len(response_data) == 1 and isinstance(next(iter(response_data.values())), dict):
        # Single model response format
        data = next(iter(response_data.values()))
    else:
        # Direct format
        data = response_data

    # Convert string dates to datetime objects
    if isinstance(data, dict):
        for key, value in data.items():
            if key.endswith("_at") and isinstance(value, str):
                data[key] = parse_datetime(value)
            elif key in ["amount", "total", "price", "quantity", "rate"] and value is not None:
                data[key] = parse_decimal(value)

    return data


def extract_list_data(response_data: dict[str, Any], item_key: str) -> list[dict[str, Any]]:
    """Extract list of items from API response."""
    if not response_data:
        return []

    items = response_data.get(item_key, [])
    if not isinstance(items, list):
        return []

    # Process each item
    processed_items = []
    for item in items:
        if isinstance(item, dict):
            # Convert dates and decimals
            for key, value in item.items():
                if key.endswith("_at") and isinstance(value, str):
                    item[key] = parse_datetime(value)
                elif key in ["amount", "total", "price", "quantity", "rate"] and value is not None:
                    item[key] = parse_decimal(value)
            processed_items.append(item)

    return processed_items


def format_json_response(data: Any, *, include_extra_data: bool = False) -> str:
    """Format response data as JSON string."""
    if not include_extra_data and isinstance(data, dict):
        # Filter to important fields only (always preserve ETag and status info)
        important_fields = {
            "id",
            "name",
            "first_name",
            "last_name",
            "email",
            "phone",
            "description",
            "status",
            "number",
            "amount",
            "total",
            "created_at",
            "updated_at",
            "type",
            "_etag",  # Always preserve ETag information
            "pagination",  # Preserve pagination info
        }

        if isinstance(data, list):
            filtered_data = []
            for item in data:
                if isinstance(item, dict):
                    filtered_item = {k: v for k, v in item.items() if k in important_fields}
                    filtered_data.append(filtered_item)
                else:
                    filtered_data.append(item)
            data = filtered_data
        elif isinstance(data, dict):
            # Always preserve special status responses like 'not_modified'
            if data.get("status") in ["not_modified", "deleted"]:
                # Don't filter special status responses
                pass
            else:
                data = {k: v for k, v in data.items() if k in important_fields}

    # Custom JSON encoder for datetime and Decimal
    def json_encoder(obj: Any) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return str(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    return json.dumps(data, default=json_encoder, indent=2)


def validate_contact_type(contact_type: str) -> str:
    """Validate and normalize contact type."""
    contact_type = contact_type.strip().lower()
    if contact_type in ["person", "individual"]:
        return "Person"
    elif contact_type in ["company", "organization", "business"]:
        return "Company"
    else:
        raise ValueError(f"Invalid contact type: {contact_type}. Must be 'Person' or 'Company'")


def validate_matter_status(status: str) -> str:
    """Validate and normalize matter status."""
    status = status.strip().lower()
    valid_statuses = ["open", "closed", "pending"]

    if status in valid_statuses:
        return status.title()
    else:
        raise ValueError(
            f"Invalid matter status: {status}. Must be one of: {', '.join(valid_statuses)}"
        )


def validate_activity_type(activity_type: str) -> str:
    """Validate and normalize activity type."""
    activity_type = activity_type.strip().lower()
    if activity_type in ["time", "timeentry", "time_entry"]:
        return "TimeEntry"
    elif activity_type in ["expense", "expenseentry", "expense_entry"]:
        return "ExpenseEntry"
    else:
        raise ValueError(
            f"Invalid activity type: {activity_type}. Must be 'TimeEntry' or 'ExpenseEntry'"
        )


def build_search_params(
    *,
    query: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    order_by: Optional[str] = None,
    order_direction: Optional[str] = None,
    cursor_pagination: bool = False,
    **filters: Any,
) -> dict[str, Any]:
    """Build search parameters for API requests."""
    params = {}

    if query:
        params["q"] = query
    if limit is not None:
        params["limit"] = min(limit, 200)  # Clio typically limits to 200

    # Handle pagination: cursor vs offset
    if cursor_pagination:
        # For unlimited cursor pagination, offset is not allowed
        # Must use order=id(asc) for cursor pagination
        params["order"] = "id(asc)"
        if offset is not None and offset > 0:
            raise ValueError("Offset pagination cannot be used with cursor pagination")
    else:
        # Standard offset pagination (limited to 10,000 records)
        if offset is not None:
            params["offset"] = offset

    if order_by and not cursor_pagination:
        params["order_by"] = order_by
    if order_direction and order_direction.lower() in ["asc", "desc"] and not cursor_pagination:
        params["order_direction"] = order_direction.lower()

    # Add additional filters
    for key, value in filters.items():
        if value is not None:
            params[key] = value

    return params


def paginate_results(
    data: dict[str, Any], *, limit: Optional[int] = None, offset: int = 0
) -> dict[str, Any]:
    """Handle pagination in results."""
    meta = data.get("meta", {})

    pagination_info = {
        "total_count": meta.get("count", 0),
        "current_offset": offset,
        "limit": limit or 50,
        "has_more": False,
    }

    # Check if there are more results
    if "paging" in meta:
        paging = meta["paging"]
        pagination_info["has_more"] = "next" in paging
        if "next" in paging:
            pagination_info["next_url"] = paging["next"]

    data["pagination"] = pagination_info
    return data


def create_error_summary(error: Exception) -> dict[str, Any]:
    """Create a standardized error summary."""
    return {
        "error": True,
        "error_type": type(error).__name__,
        "message": str(error),
        "retry_recommended": getattr(error, "retry", False),
    }
