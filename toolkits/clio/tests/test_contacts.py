"""Tests for Clio contact management tools."""

import json
import pytest
from unittest.mock import AsyncMock, patch

from arcade_clio.exceptions import ClioValidationError
from arcade_clio.tools.contacts import (
    create_contact,
    get_contact,
    search_contacts,
    update_contact,
    list_contact_activities,
    get_contact_relationships,
)


class TestContactTools:
    """Test suite for contact management tools."""

    @pytest.mark.asyncio
    async def test_search_contacts_success(self, mock_tool_context, mock_clio_client):
        """Test successful contact search."""
        with patch('arcade_clio.tools.contacts.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            result = await search_contacts(
                context=mock_tool_context,
                query="john@example.com",
                limit=10
            )
            
            # Verify result is valid JSON
            result_data = json.loads(result)
            assert isinstance(result_data, list)
            assert len(result_data) == 1
            assert result_data[0]["id"] == 12345
            
            # Verify client was called correctly
            mock_clio_client.get.assert_called_once()
            args, kwargs = mock_clio_client.get.call_args
            assert args[0] == "contacts"
            assert kwargs["params"]["query"] == "john@example.com"
            assert kwargs["params"]["limit"] == 10

    @pytest.mark.asyncio
    async def test_search_contacts_validation_error(self, mock_tool_context):
        """Test search contacts with invalid input."""
        with pytest.raises(ClioValidationError, match="Search query cannot be empty"):
            await search_contacts(
                context=mock_tool_context,
                query="",
                limit=10
            )

    @pytest.mark.asyncio
    async def test_search_contacts_invalid_contact_type(self, mock_tool_context):
        """Test search contacts with invalid contact type."""
        with pytest.raises(ClioValidationError, match="Invalid contact type"):
            await search_contacts(
                context=mock_tool_context,
                query="test",
                contact_type="invalid_type"
            )

    @pytest.mark.asyncio
    async def test_search_contacts_invalid_limit(self, mock_tool_context):
        """Test search contacts with invalid limit."""
        with pytest.raises(ClioValidationError, match="Limit must be positive"):
            await search_contacts(
                context=mock_tool_context,
                query="test",
                limit=-1
            )

    @pytest.mark.asyncio
    async def test_get_contact_success(self, mock_tool_context, mock_clio_client):
        """Test successful contact retrieval."""
        with patch('arcade_clio.tools.contacts.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            result = await get_contact(
                context=mock_tool_context,
                contact_id=12345
            )
            
            # Verify result is valid JSON
            result_data = json.loads(result)
            assert result_data["id"] == 12345
            assert result_data["first_name"] == "John"
            assert result_data["last_name"] == "Doe"
            
            # Verify client was called correctly
            mock_clio_client.get_contact.assert_called_once_with(12345)

    @pytest.mark.asyncio
    async def test_get_contact_invalid_id(self, mock_tool_context):
        """Test get contact with invalid ID."""
        with pytest.raises(ClioValidationError, match="Contact ID must be positive"):
            await get_contact(
                context=mock_tool_context,
                contact_id=-1
            )

    @pytest.mark.asyncio
    async def test_create_contact_person_success(self, mock_tool_context, mock_clio_client):
        """Test successful person contact creation."""
        with patch('arcade_clio.tools.contacts.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            result = await create_contact(
                context=mock_tool_context,
                contact_type="Person",
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com",
                phone="555-987-6543"
            )
            
            # Verify result is valid JSON
            result_data = json.loads(result)
            assert result_data["id"] == 12346
            assert result_data["first_name"] == "Jane"
            
            # Verify client was called correctly
            mock_clio_client.post.assert_called_once()
            args, kwargs = mock_clio_client.post.call_args
            assert args[0] == "contacts"
            payload = kwargs["json_data"]
            assert payload["contact"]["type"] == "Person"
            assert payload["contact"]["first_name"] == "Jane"

    @pytest.mark.asyncio
    async def test_create_contact_company_success(self, mock_tool_context, mock_clio_client):
        """Test successful company contact creation."""
        with patch('arcade_clio.tools.contacts.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            result = await create_contact(
                context=mock_tool_context,
                contact_type="Company",
                name="Acme Legal Services",
                email="info@acmelegal.com"
            )
            
            # Verify client was called correctly
            mock_clio_client.post.assert_called_once()
            args, kwargs = mock_clio_client.post.call_args
            payload = kwargs["json_data"]
            assert payload["contact"]["type"] == "Company"
            assert payload["contact"]["name"] == "Acme Legal Services"

    @pytest.mark.asyncio
    async def test_create_contact_invalid_email(self, mock_tool_context):
        """Test create contact with invalid email."""
        with pytest.raises(ClioValidationError, match="Invalid email format"):
            await create_contact(
                context=mock_tool_context,
                contact_type="Person",
                first_name="John",
                email="invalid-email"
            )

    @pytest.mark.asyncio
    async def test_create_contact_invalid_phone(self, mock_tool_context):
        """Test create contact with invalid phone number."""
        with pytest.raises(ClioValidationError, match="Phone number must contain at least 10 digits"):
            await create_contact(
                context=mock_tool_context,
                contact_type="Person",
                first_name="John",
                phone="123"
            )

    @pytest.mark.asyncio
    async def test_create_contact_person_missing_name(self, mock_tool_context):
        """Test create person contact without name fields."""
        with pytest.raises(ClioValidationError, match="Person contacts require"):
            await create_contact(
                context=mock_tool_context,
                contact_type="Person",
                email="test@example.com"
            )

    @pytest.mark.asyncio
    async def test_update_contact_success(self, mock_tool_context, mock_clio_client):
        """Test successful contact update."""
        with patch('arcade_clio.tools.contacts.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            result = await update_contact(
                context=mock_tool_context,
                contact_id=12345,
                email="john.updated@example.com",
                title="Senior Partner"
            )
            
            # Verify result is valid JSON
            result_data = json.loads(result)
            assert result_data["id"] == 12345
            
            # Verify client was called correctly
            mock_clio_client.patch.assert_called_once()
            args, kwargs = mock_clio_client.patch.call_args
            assert args[0] == "contacts/12345"

    @pytest.mark.asyncio
    async def test_update_contact_no_fields(self, mock_tool_context):
        """Test update contact with no fields provided."""
        with pytest.raises(ClioValidationError, match="At least one field must be provided"):
            await update_contact(
                context=mock_tool_context,
                contact_id=12345
            )

    @pytest.mark.asyncio
    async def test_list_contact_activities_success(self, mock_tool_context, mock_clio_client):
        """Test successful contact activities listing."""
        mock_clio_client.get.return_value = {
            "activities": [
                {
                    "id": 99999,
                    "type": "TimeEntry",
                    "date": "2024-01-15",
                    "quantity": 2.5,
                    "description": "Legal research"
                }
            ]
        }
        
        with patch('arcade_clio.tools.contacts.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            result = await list_contact_activities(
                context=mock_tool_context,
                contact_id=12345,
                activity_type="TimeEntry"
            )
            
            # Verify result is valid JSON
            result_data = json.loads(result)
            assert isinstance(result_data, list)
            assert len(result_data) == 1
            assert result_data[0]["type"] == "TimeEntry"

    @pytest.mark.asyncio
    async def test_get_contact_relationships_success(self, mock_tool_context, mock_clio_client):
        """Test successful contact relationships retrieval."""
        mock_clio_client.get.return_value = {
            "matters": [
                {
                    "id": 67890,
                    "description": "Test Matter",
                    "status": "Open"
                }
            ]
        }
        
        with patch('arcade_clio.tools.contacts.ClioClient') as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            
            result = await get_contact_relationships(
                context=mock_tool_context,
                contact_id=12345
            )
            
            # Verify result is valid JSON
            result_data = json.loads(result)
            assert isinstance(result_data, list)


class TestContactValidation:
    """Test suite for contact validation functions."""

    def test_validate_contact_type_person(self):
        """Test contact type validation for person."""
        from arcade_clio.validation import validate_contact_type
        
        assert validate_contact_type("person") == "Person"
        assert validate_contact_type("Person") == "Person"
        assert validate_contact_type("individual") == "Person"

    def test_validate_contact_type_company(self):
        """Test contact type validation for company."""
        from arcade_clio.validation import validate_contact_type
        
        assert validate_contact_type("company") == "Company"
        assert validate_contact_type("Company") == "Company"
        assert validate_contact_type("organization") == "Company"

    def test_validate_contact_type_invalid(self):
        """Test contact type validation with invalid type."""
        from arcade_clio.validation import validate_contact_type
        
        with pytest.raises(ClioValidationError):
            validate_contact_type("invalid")

    def test_validate_email_valid(self):
        """Test email validation with valid emails."""
        from arcade_clio.validation import validate_email
        
        assert validate_email("test@example.com") == "test@example.com"
        assert validate_email("user.name+tag@domain.co.uk") == "user.name+tag@domain.co.uk"
        assert validate_email(None) is None
        assert validate_email("") is None

    def test_validate_email_invalid(self):
        """Test email validation with invalid emails."""
        from arcade_clio.validation import validate_email
        
        with pytest.raises(ClioValidationError):
            validate_email("invalid-email")
        
        with pytest.raises(ClioValidationError):
            validate_email("@domain.com")
        
        with pytest.raises(ClioValidationError):
            validate_email("user@")

    def test_validate_phone_valid(self):
        """Test phone validation with valid numbers."""
        from arcade_clio.validation import validate_phone
        
        assert validate_phone("555-123-4567") == "555-123-4567"
        assert validate_phone("(555) 123-4567") == "(555) 123-4567"
        assert validate_phone("+1-555-123-4567") == "+1-555-123-4567"
        assert validate_phone(None) is None

    def test_validate_phone_invalid(self):
        """Test phone validation with invalid numbers."""
        from arcade_clio.validation import validate_phone
        
        with pytest.raises(ClioValidationError):
            validate_phone("123")  # Too short