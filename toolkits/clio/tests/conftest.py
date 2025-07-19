"""Test configuration and fixtures for Clio toolkit tests."""

from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import pytest_asyncio

from arcade_core.schema import ToolAuthorizationContext
from arcade_tdk import ToolContext

from arcade_clio.exceptions import (
    ClioAuthenticationError,
    ClioError,
    ClioPermissionError,
    ClioRateLimitError,
    ClioResourceNotFoundError,
    ClioServerError,
    ClioTimeoutError,
    ClioValidationError,
)


@pytest.fixture
def mock_auth_context():
    """Mock authorization context with test token."""
    auth_context = MagicMock(spec=ToolAuthorizationContext)
    auth_context.token = "test_token_12345"
    auth_context.user_id = "test_user_123"
    return auth_context


@pytest.fixture
def mock_tool_context(mock_auth_context):
    """Mock tool context for testing."""
    context = MagicMock(spec=ToolContext)
    context.authorization = mock_auth_context
    return context


@pytest.fixture
def mock_clio_client():
    """Mock Clio client for testing API interactions."""
    client = AsyncMock()
    
    # Mock successful responses
    client.get_contact.return_value = {
        "contact": {
            "id": 12345,
            "type": "Person",
            "first_name": "John",
            "last_name": "Doe",
            "primary_email_address": "john.doe@example.com",
            "primary_phone_number": "555-123-4567",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    }
    
    client.get_matter.return_value = {
        "matter": {
            "id": 67890,
            "description": "Test Legal Matter",
            "status": "Open",
            "billable": True,
            "open_date": "2024-01-01",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    }
    
    client.get.return_value = {
        "contacts": [
            {
                "id": 12345,
                "type": "Person",
                "first_name": "John",
                "last_name": "Doe",
                "primary_email_address": "john.doe@example.com"
            }
        ],
        "meta": {
            "count": 1,
            "paging": {}
        }
    }
    
    client.post.return_value = {
        "contact": {
            "id": 12346,
            "type": "Person",
            "first_name": "Jane",
            "last_name": "Smith",
            "primary_email_address": "jane.smith@example.com",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    }
    
    client.patch.return_value = {
        "contact": {
            "id": 12345,
            "type": "Person",
            "first_name": "John",
            "last_name": "Updated",
            "primary_email_address": "john.updated@example.com",
            "updated_at": "2024-01-02T00:00:00Z"
        }
    }
    
    return client


@pytest.fixture
def sample_contact_data():
    """Sample contact data for testing."""
    return {
        "id": 12345,
        "type": "Person",
        "first_name": "John",
        "last_name": "Doe",
        "primary_email_address": "john.doe@example.com",
        "primary_phone_number": "555-123-4567",
        "title": "Attorney",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_matter_data():
    """Sample matter data for testing."""
    return {
        "id": 67890,
        "description": "Personal Injury Case - Smith vs. Acme Corp",
        "status": "Open",
        "billable": True,
        "billing_method": "hourly",
        "open_date": "2024-01-01",
        "client_id": 12345,
        "responsible_attorney_id": 11111,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_time_entry_data():
    """Sample time entry data for testing."""
    return {
        "id": 99999,
        "type": "TimeEntry",
        "matter_id": 67890,
        "date": "2024-01-15",
        "quantity": 2.5,
        "price": 350.00,
        "total": 875.00,
        "description": "Reviewed contract terms and drafted amendments",
        "billed": False,
        "created_at": "2024-01-15T00:00:00Z",
        "updated_at": "2024-01-15T00:00:00Z"
    }


@pytest.fixture
def sample_expense_data():
    """Sample expense data for testing."""
    return {
        "id": 88888,
        "type": "ExpenseEntry",
        "matter_id": 67890,
        "date": "2024-01-15",
        "quantity": 1,
        "price": 45.50,
        "total": 45.50,
        "description": "Filing fees for motion",
        "vendor": "County Clerk's Office",
        "billed": False,
        "created_at": "2024-01-15T00:00:00Z",
        "updated_at": "2024-01-15T00:00:00Z"
    }


@pytest.fixture
def sample_bill_data():
    """Sample bill data for testing."""
    return {
        "id": 77777,
        "number": "INV-2024-001",
        "state": "draft",
        "matter_id": 67890,
        "issued_date": "2024-01-20",
        "due_date": "2024-02-20",
        "subtotal": 920.50,
        "tax_total": 0.00,
        "total": 920.50,
        "paid_total": 0.00,
        "balance": 920.50,
        "created_at": "2024-01-20T00:00:00Z",
        "updated_at": "2024-01-20T00:00:00Z"
    }


@pytest.fixture
def mock_httpx_response():
    """Factory for creating mock httpx responses."""
    def _make_response(status_code=200, json_data=None, text="", headers=None):
        response = MagicMock(spec=httpx.Response)
        response.status_code = status_code
        response.is_success = 200 <= status_code < 300
        response.json.return_value = json_data or {}
        response.text = text
        response.headers = headers or {}
        return response
    return _make_response


@pytest.fixture
def sample_company_contact_data():
    """Sample company contact data for testing."""
    return {
        "id": 22222,
        "type": "Company",
        "name": "Acme Corporation",
        "primary_email_address": "info@acmecorp.com",
        "primary_phone_number": "555-987-6543",
        "addresses": [
            {
                "type": "work",
                "address": "123 Business St",
                "city": "New York",
                "province": "NY",
                "postal_code": "10001",
                "country": "US"
            }
        ],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_error_responses(mock_httpx_response):
    """Sample error responses for testing error handling."""
    return {
        "401": mock_httpx_response(
            401, 
            {"error": "Unauthorized", "message": "Invalid or expired token"}
        ),
        "403": mock_httpx_response(
            403,
            {"error": "Forbidden", "message": "Insufficient permissions"}
        ),
        "404": mock_httpx_response(
            404,
            {"error": "Not Found", "message": "Resource not found"}
        ),
        "422": mock_httpx_response(
            422,
            {
                "error": "Unprocessable Entity",
                "message": "Validation failed",
                "errors": {
                    "first_name": ["can't be blank"],
                    "email": ["is invalid"]
                }
            }
        ),
        "429": mock_httpx_response(
            429,
            {"error": "Too Many Requests", "message": "Rate limit exceeded"}
        ),
        "500": mock_httpx_response(
            500,
            {"error": "Internal Server Error", "message": "Something went wrong"}
        ),
    }


@pytest_asyncio.fixture
async def mock_clio_client_with_errors():
    """Mock Clio client that can simulate various error conditions."""
    client = AsyncMock()
    
    # Track call count for rate limiting simulation
    client.call_count = 0
    
    async def get_with_errors(endpoint, **kwargs):
        client.call_count += 1
        
        # Simulate rate limiting on 3rd call
        if client.call_count == 3:
            raise ClioRateLimitError("Rate limit exceeded")
        
        # Default success response
        return {"contacts": [], "meta": {"count": 0}}
    
    client.get.side_effect = get_with_errors
    return client


@pytest.fixture
def sample_search_results():
    """Sample search results with multiple contacts."""
    return {
        "contacts": [
            {
                "id": 12345,
                "type": "Person",
                "first_name": "John",
                "last_name": "Doe",
                "primary_email_address": "john.doe@example.com"
            },
            {
                "id": 12346,
                "type": "Person", 
                "first_name": "Jane",
                "last_name": "Smith",
                "primary_email_address": "jane.smith@example.com"
            },
            {
                "id": 22222,
                "type": "Company",
                "name": "Acme Corporation",
                "primary_email_address": "info@acmecorp.com"
            }
        ],
        "meta": {
            "count": 3,
            "paging": {
                "next": "/api/v4/contacts?offset=50&limit=50"
            }
        }
    }


@pytest.fixture
def sample_activities_response():
    """Sample activities response with time entries and expenses."""
    return {
        "activities": [
            {
                "id": 99999,
                "type": "TimeEntry",
                "matter_id": 67890,
                "date": "2024-01-15",
                "quantity": Decimal("2.5"),
                "price": Decimal("350.00"),
                "total": Decimal("875.00"),
                "description": "Reviewed contract terms",
                "billed": False
            },
            {
                "id": 88888,
                "type": "ExpenseEntry",
                "matter_id": 67890,
                "date": "2024-01-15",
                "quantity": Decimal("1"),
                "price": Decimal("45.50"),
                "total": Decimal("45.50"),
                "description": "Filing fees",
                "vendor": "County Clerk",
                "billed": False
            }
        ],
        "meta": {
            "count": 2,
            "paging": {}
        }
    }


@pytest.fixture
def sample_matter_with_participants():
    """Sample matter with participant relationships."""
    return {
        "matter": {
            "id": 67890,
            "description": "Smith vs. Acme Corp",
            "status": "Open",
            "billable": True,
            "open_date": "2024-01-01",
            "client": {
                "id": 12345,
                "name": "John Doe"
            },
            "responsible_attorney": {
                "id": 11111,
                "name": "Sarah Attorney"
            },
            "originating_attorney": {
                "id": 11112,
                "name": "Mike Partner"
            },
            "participants": [
                {
                    "id": 55555,
                    "contact_id": 12345,
                    "role": "client"
                },
                {
                    "id": 55556,
                    "contact_id": 11111,
                    "role": "responsible_attorney"
                }
            ]
        }
    }


@pytest.fixture
def legal_validation_test_cases():
    """Test cases for legal-specific validations."""
    return {
        "valid_hours": [0.1, 0.25, 0.5, 1.0, 2.5, 8.0, 24.0],
        "invalid_hours": [-1, 0, 24.1, 100, "two", None],
        "valid_amounts": [0, 0.01, 100.50, 9999.99, 999999.99],
        "invalid_amounts": [-10, 1000001, "hundred", None],
        "valid_dates": ["2024-01-01", "2024-12-31", "2025-02-28"],
        "invalid_dates": ["01/01/2024", "2024-13-01", "2024-01-32", "January 1, 2024"],
        "valid_emails": ["test@example.com", "user.name@law-firm.co.uk"],
        "invalid_emails": ["notanemail", "@example.com", "test@", "test..@example.com"],
        "valid_phones": ["555-123-4567", "(555) 123-4567", "5551234567", "+1-555-123-4567"],
        "invalid_phones": ["123", "abc-def-ghij", "555-CALL-NOW"]
    }