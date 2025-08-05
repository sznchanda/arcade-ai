"""Input validation utilities for Clio toolkit."""

import re
from datetime import datetime
from typing import Optional

from .exceptions import ClioValidationError


def validate_id(value: int, name: str = "ID") -> int:
    """Validate that an ID is a positive integer."""
    if not isinstance(value, int):
        raise ClioValidationError(f"{name} must be an integer, got {type(value).__name__}")
    if value <= 0:
        raise ClioValidationError(f"{name} must be positive, got {value}")
    return value


def validate_email(email: Optional[str]) -> Optional[str]:
    """Validate email address format."""
    if email is None:
        return None

    if not isinstance(email, str):
        raise ClioValidationError(f"Email must be a string, got {type(email).__name__}")

    email = email.strip()
    if not email:
        return None

    # Basic email validation regex
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email):
        raise ClioValidationError(f"Invalid email format: {email}")

    return email


def validate_phone(phone: Optional[str]) -> Optional[str]:
    """Validate phone number format."""
    if phone is None:
        return None

    if not isinstance(phone, str):
        raise ClioValidationError(f"Phone number must be a string, got {type(phone).__name__}")

    phone = phone.strip()
    if not phone:
        return None

    # Remove common phone formatting characters
    cleaned_phone = re.sub(r"[^\d+\-\(\)\s]", "", phone)

    # Basic validation - at least 10 digits
    digits_only = re.sub(r"\D", "", cleaned_phone)
    if len(digits_only) < 10:
        raise ClioValidationError(f"Phone number must contain at least 10 digits: {phone}")

    return phone


def validate_date_string(date_str: Optional[str], name: str = "Date") -> Optional[datetime]:
    """Validate date string in YYYY-MM-DD format."""
    if date_str is None:
        return None

    if not isinstance(date_str, str):
        raise ClioValidationError(f"{name} must be a string, got {type(date_str).__name__}")

    date_str = date_str.strip()
    if not date_str:
        return None

    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ClioValidationError(f"{name} must be in YYYY-MM-DD format, got: {date_str}")


def validate_positive_number(value: Optional[float], name: str = "Value") -> Optional[float]:
    """Validate that a number is positive."""
    if value is None:
        return None

    if not isinstance(value, (int, float)):
        raise ClioValidationError(f"{name} must be a number, got {type(value).__name__}")

    if value < 0:
        raise ClioValidationError(f"{name} must be non-negative, got {value}")

    return float(value)


def validate_required_string(value: Optional[str], name: str = "Value") -> str:
    """Validate that a required string is provided and non-empty."""
    if value is None:
        raise ClioValidationError(f"{name} is required")

    if not isinstance(value, str):
        raise ClioValidationError(f"{name} must be a string, got {type(value).__name__}")

    value = value.strip()
    if not value:
        raise ClioValidationError(f"{name} cannot be empty")

    return value


def validate_optional_string(value: Optional[str], name: str = "Value") -> Optional[str]:
    """Validate and clean an optional string."""
    if value is None:
        return None

    if not isinstance(value, str):
        raise ClioValidationError(f"{name} must be a string, got {type(value).__name__}")

    value = value.strip()
    return value if value else None


def validate_limit_offset(
    limit: Optional[int], offset: Optional[int]
) -> tuple[Optional[int], Optional[int]]:
    """Validate pagination parameters."""
    if limit is not None:
        if not isinstance(limit, int):
            raise ClioValidationError(f"Limit must be an integer, got {type(limit).__name__}")
        if limit <= 0:
            raise ClioValidationError(f"Limit must be positive, got {limit}")
        if limit > 200:
            raise ClioValidationError(f"Limit cannot exceed 200, got {limit}")

    if offset is not None:
        if not isinstance(offset, int):
            raise ClioValidationError(f"Offset must be an integer, got {type(offset).__name__}")
        if offset < 0:
            raise ClioValidationError(f"Offset must be non-negative, got {offset}")

    return limit, offset


def validate_contact_type(contact_type: str) -> str:
    """Validate and normalize contact type."""
    if not isinstance(contact_type, str):
        raise ClioValidationError(
            f"Contact type must be a string, got {type(contact_type).__name__}"
        )

    contact_type = contact_type.strip().lower()
    if contact_type in ["person", "individual"]:
        return "Person"
    elif contact_type in ["company", "organization", "business"]:
        return "Company"
    else:
        raise ClioValidationError(
            f"Invalid contact type: {contact_type}. Must be 'Person' or 'Company'"
        )


def validate_matter_status(status: str) -> str:
    """Validate and normalize matter status."""
    if not isinstance(status, str):
        raise ClioValidationError(f"Matter status must be a string, got {type(status).__name__}")

    status = status.strip().lower()
    valid_statuses = ["open", "closed", "pending"]

    if status in valid_statuses:
        return status.title()
    else:
        raise ClioValidationError(
            f"Invalid matter status: {status}. Must be one of: {', '.join(valid_statuses)}"
        )


def validate_activity_type(activity_type: str) -> str:
    """Validate and normalize activity type."""
    if not isinstance(activity_type, str):
        raise ClioValidationError(
            f"Activity type must be a string, got {type(activity_type).__name__}"
        )

    activity_type = activity_type.strip().lower()
    if activity_type in ["time", "timeentry", "time_entry"]:
        return "TimeEntry"
    elif activity_type in ["expense", "expenseentry", "expense_entry"]:
        return "ExpenseEntry"
    else:
        raise ClioValidationError(
            f"Invalid activity type: {activity_type}. Must be 'TimeEntry' or 'ExpenseEntry'"
        )


def validate_hours(hours: float) -> float:
    """Validate hours for time entries."""
    if not isinstance(hours, (int, float)):
        raise ClioValidationError(f"Hours must be a number, got {type(hours).__name__}")

    if hours <= 0:
        raise ClioValidationError(f"Hours must be greater than 0, got {hours}")

    if hours > 24:
        raise ClioValidationError(f"Hours cannot exceed 24 in a single entry, got {hours}")

    return float(hours)


def validate_amount(amount: float, name: str = "Amount") -> float:
    """Validate monetary amounts."""
    if not isinstance(amount, (int, float)):
        raise ClioValidationError(f"{name} must be a number, got {type(amount).__name__}")

    if amount < 0:
        raise ClioValidationError(f"{name} must be non-negative, got {amount}")

    # Check for reasonable monetary limits (adjust as needed)
    if amount > 1_000_000:
        raise ClioValidationError(f"{name} exceeds reasonable limit of $1,000,000, got {amount}")

    return float(amount)


def validate_participant_role(role: str) -> str:
    """Validate matter participant role."""
    if not isinstance(role, str):
        raise ClioValidationError(f"Role must be a string, got {type(role).__name__}")

    role = role.strip().lower()
    valid_roles = ["client", "responsible_attorney", "originating_attorney"]

    if role not in valid_roles:
        raise ClioValidationError(f"Invalid role: {role}. Must be one of: {', '.join(valid_roles)}")

    return role
