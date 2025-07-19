"""Tests for Clio validation utilities."""

import pytest
from datetime import datetime

from arcade_clio.exceptions import ClioValidationError
from arcade_clio.validation import (
    validate_id,
    validate_email,
    validate_phone,
    validate_date_string,
    validate_positive_number,
    validate_required_string,
    validate_optional_string,
    validate_limit_offset,
    validate_contact_type,
    validate_matter_status,
    validate_activity_type,
    validate_hours,
    validate_amount,
    validate_participant_role,
)


class TestBasicValidation:
    """Test basic validation functions."""

    def test_validate_id_valid(self):
        """Test ID validation with valid values."""
        assert validate_id(1) == 1
        assert validate_id(12345) == 12345
        assert validate_id(999999) == 999999

    def test_validate_id_invalid(self):
        """Test ID validation with invalid values."""
        with pytest.raises(ClioValidationError, match="ID must be positive"):
            validate_id(0)
        
        with pytest.raises(ClioValidationError, match="ID must be positive"):
            validate_id(-1)
        
        with pytest.raises(ClioValidationError, match="ID must be an integer"):
            validate_id("123")
        
        with pytest.raises(ClioValidationError, match="ID must be an integer"):
            validate_id(12.5)

    def test_validate_email_valid(self):
        """Test email validation with valid addresses."""
        assert validate_email("test@example.com") == "test@example.com"
        assert validate_email("user.name+tag@domain.co.uk") == "user.name+tag@domain.co.uk"
        assert validate_email("123@test-domain.org") == "123@test-domain.org"
        assert validate_email(None) is None
        assert validate_email("") is None
        assert validate_email("   ") is None

    def test_validate_email_invalid(self):
        """Test email validation with invalid addresses."""
        with pytest.raises(ClioValidationError, match="Invalid email format"):
            validate_email("invalid-email")
        
        with pytest.raises(ClioValidationError, match="Invalid email format"):
            validate_email("@domain.com")
        
        with pytest.raises(ClioValidationError, match="Invalid email format"):
            validate_email("user@")
        
        with pytest.raises(ClioValidationError, match="Invalid email format"):
            validate_email("user.domain.com")
        
        with pytest.raises(ClioValidationError, match="Email must be a string"):
            validate_email(123)

    def test_validate_phone_valid(self):
        """Test phone validation with valid numbers."""
        assert validate_phone("555-123-4567") == "555-123-4567"
        assert validate_phone("(555) 123-4567") == "(555) 123-4567"
        assert validate_phone("+1-555-123-4567") == "+1-555-123-4567"
        assert validate_phone("15551234567") == "15551234567"
        assert validate_phone(None) is None
        assert validate_phone("") is None

    def test_validate_phone_invalid(self):
        """Test phone validation with invalid numbers."""
        with pytest.raises(ClioValidationError, match="Phone number must contain at least 10 digits"):
            validate_phone("123")
        
        with pytest.raises(ClioValidationError, match="Phone number must contain at least 10 digits"):
            validate_phone("555-123")
        
        with pytest.raises(ClioValidationError, match="Phone number must be a string"):
            validate_phone(1234567890)

    def test_validate_date_string_valid(self):
        """Test date string validation with valid dates."""
        result = validate_date_string("2024-01-15")
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        
        assert validate_date_string(None) is None
        assert validate_date_string("") is None

    def test_validate_date_string_invalid(self):
        """Test date string validation with invalid dates."""
        with pytest.raises(ClioValidationError, match="Date must be in YYYY-MM-DD format"):
            validate_date_string("2024/01/15")
        
        with pytest.raises(ClioValidationError, match="Date must be in YYYY-MM-DD format"):
            validate_date_string("01-15-2024")
        
        with pytest.raises(ClioValidationError, match="Date must be in YYYY-MM-DD format"):
            validate_date_string("2024-13-15")  # Invalid month
        
        with pytest.raises(ClioValidationError, match="Date must be a string"):
            validate_date_string(20240115)

    def test_validate_positive_number_valid(self):
        """Test positive number validation with valid values."""
        assert validate_positive_number(0) == 0.0
        assert validate_positive_number(10) == 10.0
        assert validate_positive_number(10.5) == 10.5
        assert validate_positive_number(None) is None

    def test_validate_positive_number_invalid(self):
        """Test positive number validation with invalid values."""
        with pytest.raises(ClioValidationError, match="Value must be non-negative"):
            validate_positive_number(-1)
        
        with pytest.raises(ClioValidationError, match="Value must be non-negative"):
            validate_positive_number(-10.5)
        
        with pytest.raises(ClioValidationError, match="Value must be a number"):
            validate_positive_number("10")

    def test_validate_required_string_valid(self):
        """Test required string validation with valid values."""
        assert validate_required_string("test") == "test"
        assert validate_required_string("  test  ") == "test"  # Trimmed
        assert validate_required_string("a") == "a"

    def test_validate_required_string_invalid(self):
        """Test required string validation with invalid values."""
        with pytest.raises(ClioValidationError, match="Value is required"):
            validate_required_string(None)
        
        with pytest.raises(ClioValidationError, match="Value cannot be empty"):
            validate_required_string("")
        
        with pytest.raises(ClioValidationError, match="Value cannot be empty"):
            validate_required_string("   ")
        
        with pytest.raises(ClioValidationError, match="Value must be a string"):
            validate_required_string(123)

    def test_validate_optional_string_valid(self):
        """Test optional string validation with valid values."""
        assert validate_optional_string("test") == "test"
        assert validate_optional_string("  test  ") == "test"  # Trimmed
        assert validate_optional_string(None) is None
        assert validate_optional_string("") is None
        assert validate_optional_string("   ") is None

    def test_validate_optional_string_invalid(self):
        """Test optional string validation with invalid types."""
        with pytest.raises(ClioValidationError, match="Value must be a string"):
            validate_optional_string(123)


class TestPaginationValidation:
    """Test pagination validation functions."""

    def test_validate_limit_offset_valid(self):
        """Test limit/offset validation with valid values."""
        limit, offset = validate_limit_offset(10, 0)
        assert limit == 10
        assert offset == 0
        
        limit, offset = validate_limit_offset(None, None)
        assert limit is None
        assert offset is None
        
        limit, offset = validate_limit_offset(200, 100)
        assert limit == 200
        assert offset == 100

    def test_validate_limit_offset_invalid_limit(self):
        """Test limit validation with invalid values."""
        with pytest.raises(ClioValidationError, match="Limit must be positive"):
            validate_limit_offset(0, 0)
        
        with pytest.raises(ClioValidationError, match="Limit must be positive"):
            validate_limit_offset(-1, 0)
        
        with pytest.raises(ClioValidationError, match="Limit cannot exceed 200"):
            validate_limit_offset(201, 0)
        
        with pytest.raises(ClioValidationError, match="Limit must be an integer"):
            validate_limit_offset("10", 0)

    def test_validate_limit_offset_invalid_offset(self):
        """Test offset validation with invalid values."""
        with pytest.raises(ClioValidationError, match="Offset must be non-negative"):
            validate_limit_offset(10, -1)
        
        with pytest.raises(ClioValidationError, match="Offset must be an integer"):
            validate_limit_offset(10, "0")


class TestDomainValidation:
    """Test domain-specific validation functions."""

    def test_validate_contact_type_valid(self):
        """Test contact type validation with valid values."""
        assert validate_contact_type("person") == "Person"
        assert validate_contact_type("Person") == "Person"
        assert validate_contact_type("PERSON") == "Person"
        assert validate_contact_type("individual") == "Person"
        
        assert validate_contact_type("company") == "Company"
        assert validate_contact_type("Company") == "Company"
        assert validate_contact_type("organization") == "Company"
        assert validate_contact_type("business") == "Company"

    def test_validate_contact_type_invalid(self):
        """Test contact type validation with invalid values."""
        with pytest.raises(ClioValidationError, match="Invalid contact type"):
            validate_contact_type("invalid")
        
        with pytest.raises(ClioValidationError, match="Contact type must be a string"):
            validate_contact_type(123)

    def test_validate_matter_status_valid(self):
        """Test matter status validation with valid values."""
        assert validate_matter_status("open") == "Open"
        assert validate_matter_status("Open") == "Open"
        assert validate_matter_status("OPEN") == "Open"
        
        assert validate_matter_status("closed") == "Closed"
        assert validate_matter_status("pending") == "Pending"

    def test_validate_matter_status_invalid(self):
        """Test matter status validation with invalid values."""
        with pytest.raises(ClioValidationError, match="Invalid matter status"):
            validate_matter_status("invalid")
        
        with pytest.raises(ClioValidationError, match="Matter status must be a string"):
            validate_matter_status(123)

    def test_validate_activity_type_valid(self):
        """Test activity type validation with valid values."""
        assert validate_activity_type("time") == "TimeEntry"
        assert validate_activity_type("timeentry") == "TimeEntry"
        assert validate_activity_type("time_entry") == "TimeEntry"
        assert validate_activity_type("TimeEntry") == "TimeEntry"
        
        assert validate_activity_type("expense") == "ExpenseEntry"
        assert validate_activity_type("expenseentry") == "ExpenseEntry"
        assert validate_activity_type("expense_entry") == "ExpenseEntry"

    def test_validate_activity_type_invalid(self):
        """Test activity type validation with invalid values."""
        with pytest.raises(ClioValidationError, match="Invalid activity type"):
            validate_activity_type("invalid")
        
        with pytest.raises(ClioValidationError, match="Activity type must be a string"):
            validate_activity_type(123)

    def test_validate_hours_valid(self):
        """Test hours validation with valid values."""
        assert validate_hours(1.0) == 1.0
        assert validate_hours(8.5) == 8.5
        assert validate_hours(24) == 24.0
        assert validate_hours(0.1) == 0.1

    def test_validate_hours_invalid(self):
        """Test hours validation with invalid values."""
        with pytest.raises(ClioValidationError, match="Hours must be greater than 0"):
            validate_hours(0)
        
        with pytest.raises(ClioValidationError, match="Hours must be greater than 0"):
            validate_hours(-1)
        
        with pytest.raises(ClioValidationError, match="Hours cannot exceed 24"):
            validate_hours(25)
        
        with pytest.raises(ClioValidationError, match="Hours must be a number"):
            validate_hours("8")

    def test_validate_amount_valid(self):
        """Test amount validation with valid values."""
        assert validate_amount(0) == 0.0
        assert validate_amount(100.50) == 100.50
        assert validate_amount(1000) == 1000.0
        assert validate_amount(999999.99) == 999999.99

    def test_validate_amount_invalid(self):
        """Test amount validation with invalid values."""
        with pytest.raises(ClioValidationError, match="Amount must be non-negative"):
            validate_amount(-1)
        
        with pytest.raises(ClioValidationError, match="Amount exceeds reasonable limit"):
            validate_amount(2000000)
        
        with pytest.raises(ClioValidationError, match="Amount must be a number"):
            validate_amount("100")

    def test_validate_participant_role_valid(self):
        """Test participant role validation with valid values."""
        assert validate_participant_role("client") == "client"
        assert validate_participant_role("responsible_attorney") == "responsible_attorney"
        assert validate_participant_role("originating_attorney") == "originating_attorney"
        assert validate_participant_role("CLIENT") == "client"

    def test_validate_participant_role_invalid(self):
        """Test participant role validation with invalid values."""
        with pytest.raises(ClioValidationError, match="Invalid role"):
            validate_participant_role("invalid")
        
        with pytest.raises(ClioValidationError, match="Role must be a string"):
            validate_participant_role(123)