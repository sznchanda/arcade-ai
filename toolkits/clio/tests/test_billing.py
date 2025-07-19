"""Tests for Clio billing and time tracking tools."""

import json
import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from arcade_clio.exceptions import ClioValidationError
from arcade_clio.tools.billing import (
    create_bill,
    create_expense,
    create_time_entry,
    get_bills,
    get_expenses,
    get_time_entries,
    update_time_entry,
)


class TestTimeEntryTools:
    """Test suite for time entry tools."""

    @pytest.mark.asyncio
    async def test_create_time_entry_success(self, mock_tool_context, mock_clio_client):
        """Test successful time entry creation."""
        with patch('arcade_clio.tools.billing.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            # Mock response
            mock_clio_client.post.return_value = {
                "activity": {
                    "id": 99999,
                    "type": "TimeEntry",
                    "matter_id": 67890,
                    "date": "2024-01-15",
                    "quantity": "2.5",
                    "price": "350.00",
                    "total": "875.00",
                    "description": "Contract review and revision",
                    "billed": False
                }
            }
            
            result = await create_time_entry(
                context=mock_tool_context,
                matter_id=67890,
                hours=2.5,
                date="2024-01-15",
                description="Contract review and revision",
                rate=350.00
            )
            
            # Verify result is valid JSON
            result_data = json.loads(result)
            assert result_data["id"] == 99999
            assert result_data["quantity"] == "2.5"
            assert result_data["total"] == "875.00"
            
            # Verify client was called correctly
            mock_clio_client.post.assert_called_once()
            args, kwargs = mock_clio_client.post.call_args
            assert args[0] == "activities"
            payload = kwargs["json_data"]["activity"]
            assert payload["type"] == "TimeEntry"
            assert payload["matter"]["id"] == 67890
            assert payload["quantity"] == 2.5

    @pytest.mark.asyncio
    async def test_create_time_entry_invalid_hours(self, mock_tool_context):
        """Test time entry creation with invalid hours."""
        with pytest.raises(ClioValidationError, match="Hours must be greater than 0"):
            await create_time_entry(
                context=mock_tool_context,
                matter_id=67890,
                hours=0,
                date="2024-01-15",
                description="Test"
            )
        
        with pytest.raises(ClioValidationError, match="Hours cannot exceed 24"):
            await create_time_entry(
                context=mock_tool_context,
                matter_id=67890,
                hours=25,
                date="2024-01-15",
                description="Test"
            )

    @pytest.mark.asyncio
    async def test_create_time_entry_decimal_precision(self, mock_tool_context, mock_clio_client):
        """Test time entry maintains decimal precision for legal billing."""
        with patch('arcade_clio.tools.billing.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            # Mock response with precise decimals
            mock_clio_client.post.return_value = {
                "activity": {
                    "id": 99999,
                    "quantity": "2.75",  # 2 hours 45 minutes
                    "price": "425.50",
                    "total": "1170.13"  # Precise calculation
                }
            }
            
            result = await create_time_entry(
                context=mock_tool_context,
                matter_id=67890,
                hours=2.75,
                date="2024-01-15",
                description="Deposition preparation",
                rate=425.50
            )
            
            result_data = json.loads(result)
            
            # Verify decimal precision is maintained
            assert result_data["quantity"] == "2.75"
            assert result_data["price"] == "425.50"
            assert result_data["total"] == "1170.13"

    @pytest.mark.asyncio
    async def test_update_time_entry_success(self, mock_tool_context, mock_clio_client):
        """Test successful time entry update."""
        with patch('arcade_clio.tools.billing.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            result = await update_time_entry(
                context=mock_tool_context,
                time_entry_id=99999,
                hours=3.0,
                description="Updated description"
            )
            
            # Verify client was called correctly
            mock_clio_client.patch.assert_called_once()
            args, kwargs = mock_clio_client.patch.call_args
            assert args[0] == "activities/99999"
            payload = kwargs["json_data"]["activity"]
            assert payload["quantity"] == 3.0
            assert payload["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_get_time_entries_with_filters(self, mock_tool_context, mock_clio_client):
        """Test getting time entries with various filters."""
        with patch('arcade_clio.tools.billing.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            # Mock response
            mock_clio_client.get.return_value = {
                "activities": [
                    {
                        "id": 99999,
                        "type": "TimeEntry",
                        "quantity": "2.5",
                        "billed": False
                    }
                ],
                "meta": {"count": 1}
            }
            
            result = await get_time_entries(
                context=mock_tool_context,
                matter_id=67890,
                billed=False,
                start_date="2024-01-01",
                end_date="2024-01-31",
                limit=20
            )
            
            # Verify filters were applied
            args, kwargs = mock_clio_client.get.call_args
            params = kwargs["params"]
            assert params["type"] == "TimeEntry"
            assert params["matter_id"] == 67890
            assert params["billed"] is False
            assert params["date_from"] == "2024-01-01"
            assert params["date_to"] == "2024-01-31"


class TestExpenseTools:
    """Test suite for expense tools."""

    @pytest.mark.asyncio
    async def test_create_expense_success(self, mock_tool_context, mock_clio_client):
        """Test successful expense creation."""
        with patch('arcade_clio.tools.billing.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            # Mock response
            mock_clio_client.post.return_value = {
                "activity": {
                    "id": 88888,
                    "type": "ExpenseEntry",
                    "matter_id": 67890,
                    "date": "2024-01-15",
                    "quantity": "1",
                    "price": "125.00",
                    "total": "125.00",
                    "description": "Court filing fees",
                    "vendor": "County Clerk",
                    "category": "Filing Fees",
                    "billed": False
                }
            }
            
            result = await create_expense(
                context=mock_tool_context,
                matter_id=67890,
                amount=125.00,
                date="2024-01-15",
                description="Court filing fees",
                vendor="County Clerk",
                category="Filing Fees"
            )
            
            # Verify result
            result_data = json.loads(result)
            assert result_data["id"] == 88888
            assert result_data["type"] == "ExpenseEntry"
            assert result_data["total"] == "125.00"
            assert result_data["vendor"] == "County Clerk"

    @pytest.mark.asyncio
    async def test_create_expense_negative_amount(self, mock_tool_context):
        """Test expense creation with negative amount."""
        with pytest.raises(ClioValidationError, match="Amount must be non-negative"):
            await create_expense(
                context=mock_tool_context,
                matter_id=67890,
                amount=-50.00,
                date="2024-01-15",
                description="Invalid expense"
            )

    @pytest.mark.asyncio
    async def test_create_expense_excessive_amount(self, mock_tool_context):
        """Test expense creation with excessive amount."""
        with pytest.raises(ClioValidationError, match="exceeds reasonable limit"):
            await create_expense(
                context=mock_tool_context,
                matter_id=67890,
                amount=1500000.00,  # Over $1M limit
                date="2024-01-15",
                description="Excessive expense"
            )

    @pytest.mark.asyncio
    async def test_get_expenses_with_filters(self, mock_tool_context, mock_clio_client):
        """Test getting expenses with filters."""
        with patch('arcade_clio.tools.billing.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            mock_clio_client.get.return_value = {
                "activities": [
                    {
                        "id": 88888,
                        "type": "ExpenseEntry",
                        "total": "125.00",
                        "vendor": "County Clerk"
                    }
                ],
                "meta": {"count": 1}
            }
            
            result = await get_expenses(
                context=mock_tool_context,
                matter_id=67890,
                billed=False,
                vendor="County Clerk"
            )
            
            # Verify filters
            args, kwargs = mock_clio_client.get.call_args
            params = kwargs["params"]
            assert params["type"] == "ExpenseEntry"
            assert params["matter_id"] == 67890
            assert params["vendor"] == "County Clerk"


class TestBillingTools:
    """Test suite for billing tools."""

    @pytest.mark.asyncio
    async def test_create_bill_success(self, mock_tool_context, mock_clio_client):
        """Test successful bill creation."""
        with patch('arcade_clio.tools.billing.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            # Mock response
            mock_clio_client.post.return_value = {
                "bill": {
                    "id": 77777,
                    "number": "INV-2024-001",
                    "state": "draft",
                    "matter_id": 67890,
                    "issued_date": "2024-01-20",
                    "due_date": "2024-02-20",
                    "subtotal": "920.50",
                    "tax_total": "0.00",
                    "total": "920.50",
                    "balance": "920.50"
                }
            }
            
            result = await create_bill(
                context=mock_tool_context,
                matter_id=67890,
                include_unbilled_time=True,
                include_unbilled_expenses=True,
                issued_date="2024-01-20",
                due_date="2024-02-20"
            )
            
            # Verify result
            result_data = json.loads(result)
            assert result_data["id"] == 77777
            assert result_data["number"] == "INV-2024-001"
            assert result_data["total"] == "920.50"
            
            # Verify client call
            mock_clio_client.post.assert_called_once()
            args, kwargs = mock_clio_client.post.call_args
            assert args[0] == "bills"
            payload = kwargs["json_data"]["bill"]
            assert payload["matter"]["id"] == 67890

    @pytest.mark.asyncio
    async def test_create_bill_invalid_dates(self, mock_tool_context):
        """Test bill creation with due date before issued date."""
        with pytest.raises(ClioValidationError, match="Due date must be after issued date"):
            await create_bill(
                context=mock_tool_context,
                matter_id=67890,
                issued_date="2024-01-20",
                due_date="2024-01-10"  # Before issued date
            )

    @pytest.mark.asyncio
    async def test_get_bills_with_filters(self, mock_tool_context, mock_clio_client):
        """Test getting bills with various filters."""
        with patch('arcade_clio.tools.billing.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            mock_clio_client.get_bills.return_value = {
                "bills": [
                    {
                        "id": 77777,
                        "state": "sent",
                        "total": "920.50",
                        "balance": "920.50"
                    }
                ],
                "meta": {"count": 1}
            }
            
            result = await get_bills(
                context=mock_tool_context,
                matter_id=67890,
                state="sent",
                limit=10
            )
            
            # Verify filters
            mock_clio_client.get_bills.assert_called_once_with(
                matter_id=67890,
                state="sent",
                limit=10,
                offset=0
            )


class TestBillingValidation:
    """Test suite for billing-specific validation."""

    def test_validate_hours_valid(self, legal_validation_test_cases):
        """Test hours validation with valid values."""
        from arcade_clio.validation import validate_hours
        
        for hours in legal_validation_test_cases["valid_hours"]:
            if hours > 0 and hours <= 24:
                assert validate_hours(hours) == float(hours)

    def test_validate_hours_invalid(self, legal_validation_test_cases):
        """Test hours validation with invalid values."""
        from arcade_clio.validation import validate_hours
        
        for hours in [-1, 0, 24.1, 100]:
            with pytest.raises(ClioValidationError):
                validate_hours(hours)

    def test_validate_amount_valid(self, legal_validation_test_cases):
        """Test amount validation with valid values."""
        from arcade_clio.validation import validate_amount
        
        for amount in legal_validation_test_cases["valid_amounts"]:
            assert validate_amount(amount) == float(amount)

    def test_validate_amount_invalid(self, legal_validation_test_cases):
        """Test amount validation with invalid values."""
        from arcade_clio.validation import validate_amount
        
        with pytest.raises(ClioValidationError):
            validate_amount(-10)
        
        with pytest.raises(ClioValidationError):
            validate_amount(1000001)


class TestBillingEdgeCases:
    """Test edge cases and legal industry-specific scenarios."""

    @pytest.mark.asyncio
    async def test_legal_billing_increments(self, mock_tool_context, mock_clio_client):
        """Test legal industry standard 6-minute (0.1 hour) billing increments."""
        with patch('arcade_clio.tools.billing.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            # Test various 6-minute increments
            test_cases = [
                (0.1, "6 minutes"),
                (0.25, "15 minutes"),
                (0.5, "30 minutes"),
                (1.0, "1 hour"),
                (2.75, "2 hours 45 minutes")
            ]
            
            for hours, description in test_cases:
                mock_clio_client.post.return_value = {
                    "activity": {
                        "id": 99999,
                        "quantity": str(hours),
                        "description": description
                    }
                }
                
                result = await create_time_entry(
                    context=mock_tool_context,
                    matter_id=67890,
                    hours=hours,
                    date="2024-01-15",
                    description=description
                )
                
                result_data = json.loads(result)
                assert result_data["quantity"] == str(hours)

    @pytest.mark.asyncio
    async def test_billing_workflow_integration(
        self, 
        mock_tool_context, 
        mock_clio_client,
        sample_time_entry_data,
        sample_expense_data
    ):
        """Test complete billing workflow: time entries → expenses → bill."""
        with patch('arcade_clio.tools.billing.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            # Step 1: Create time entries
            mock_clio_client.post.return_value = {"activity": sample_time_entry_data}
            time_entry = await create_time_entry(
                context=mock_tool_context,
                matter_id=67890,
                hours=2.5,
                date="2024-01-15",
                description="Contract review"
            )
            
            # Step 2: Create expenses
            mock_clio_client.post.return_value = {"activity": sample_expense_data}
            expense = await create_expense(
                context=mock_tool_context,
                matter_id=67890,
                amount=45.50,
                date="2024-01-15",
                description="Filing fees"
            )
            
            # Step 3: Create bill including all unbilled items
            mock_clio_client.post.return_value = {
                "bill": {
                    "id": 77777,
                    "subtotal": "920.50",  # 875.00 + 45.50
                    "total": "920.50",
                    "line_items": [
                        {"type": "TimeEntry", "amount": "875.00"},
                        {"type": "ExpenseEntry", "amount": "45.50"}
                    ]
                }
            }
            
            bill = await create_bill(
                context=mock_tool_context,
                matter_id=67890,
                include_unbilled_time=True,
                include_unbilled_expenses=True
            )
            
            bill_data = json.loads(bill)
            assert bill_data["total"] == "920.50"
            assert len(bill_data["line_items"]) == 2