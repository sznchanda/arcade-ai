"""Tests for Clio matter management tools."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from arcade_clio.exceptions import ClioValidationError
from arcade_clio.tools.matters import (
    add_matter_participant,
    close_matter,
    create_matter,
    get_matter,
    get_matter_activities,
    list_matters,
    remove_matter_participant,
    update_matter,
)


class TestMatterTools:
    """Test suite for matter management tools."""

    @pytest.mark.asyncio
    async def test_list_matters_success(self, mock_tool_context, mock_clio_client):
        """Test successful matter listing."""
        with patch("arcade_clio.tools.matters.ClioClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client

            # Setup mock response
            mock_clio_client.get.return_value = {
                "matters": [
                    {
                        "id": 67890,
                        "description": "Test Legal Matter",
                        "status": "Open",
                        "billable": True,
                    }
                ],
                "meta": {"count": 1},
            }

            result = await list_matters(context=mock_tool_context, status="open", limit=10)

            # Verify result is valid JSON
            result_data = json.loads(result)
            assert isinstance(result_data, list)
            assert len(result_data) == 1
            assert result_data[0]["id"] == 67890

            # Verify client was called correctly
            mock_clio_client.get.assert_called_once()
            args, kwargs = mock_clio_client.get.call_args
            assert args[0] == "matters"
            assert kwargs["params"]["status"] == "Open"
            assert kwargs["params"]["limit"] == 10

    @pytest.mark.asyncio
    async def test_list_matters_with_filters(self, mock_tool_context, mock_clio_client):
        """Test listing matters with multiple filters."""
        with patch("arcade_clio.tools.matters.ClioClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client
            mock_clio_client.get.return_value = {"matters": [], "meta": {"count": 0}}

            await list_matters(
                context=mock_tool_context,
                status="closed",
                client_id=12345,
                billable=True,
                limit=50,
                offset=100,
            )

            # Verify all filters were passed
            args, kwargs = mock_clio_client.get.call_args
            params = kwargs["params"]
            assert params["status"] == "Closed"
            assert params["client_id"] == 12345
            assert params["billable"] is True
            assert params["limit"] == 50
            assert params["offset"] == 100

    @pytest.mark.asyncio
    async def test_get_matter_success(self, mock_tool_context, mock_clio_client):
        """Test successful matter retrieval."""
        with patch("arcade_clio.tools.matters.ClioClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client

            result = await get_matter(context=mock_tool_context, matter_id=67890)

            # Verify result is valid JSON
            result_data = json.loads(result)
            assert result_data["id"] == 67890
            assert result_data["description"] == "Test Legal Matter"

            # Verify client was called correctly
            mock_clio_client.get_matter.assert_called_once_with(67890)

    @pytest.mark.asyncio
    async def test_create_matter_success(self, mock_tool_context, mock_clio_client):
        """Test successful matter creation."""
        with patch("arcade_clio.tools.matters.ClioClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client

            # Mock response for new matter
            mock_clio_client.post.return_value = {
                "matter": {
                    "id": 67891,
                    "description": "New Legal Matter",
                    "status": "Open",
                    "open_date": "2024-01-01",
                }
            }

            result = await create_matter(
                context=mock_tool_context,
                description="New Legal Matter",
                client_id=12345,
                billable=True,
                billing_method="hourly",
                open_date="2024-01-01",
            )

            # Verify result is valid JSON
            result_data = json.loads(result)
            assert result_data["id"] == 67891
            assert result_data["description"] == "New Legal Matter"

            # Verify client was called correctly
            mock_clio_client.post.assert_called_once()
            args, kwargs = mock_clio_client.post.call_args
            assert args[0] == "matters"
            payload = kwargs["json_data"]["matter"]
            assert payload["description"] == "New Legal Matter"
            assert payload["client"]["id"] == 12345
            assert payload["billable"] is True

    @pytest.mark.asyncio
    async def test_create_matter_missing_description(self, mock_tool_context):
        """Test create matter without description."""
        with pytest.raises(ClioValidationError, match="Description is required"):
            await create_matter(context=mock_tool_context, description="", client_id=12345)

    @pytest.mark.asyncio
    async def test_create_matter_invalid_date(self, mock_tool_context):
        """Test create matter with invalid date format."""
        with pytest.raises(ClioValidationError, match="must be in YYYY-MM-DD format"):
            await create_matter(
                context=mock_tool_context,
                description="Test Matter",
                client_id=12345,
                open_date="01/01/2024",  # Wrong format
            )

    @pytest.mark.asyncio
    async def test_update_matter_success(self, mock_tool_context, mock_clio_client):
        """Test successful matter update."""
        with patch("arcade_clio.tools.matters.ClioClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client

            result = await update_matter(
                context=mock_tool_context,
                matter_id=67890,
                description="Updated Matter Description",
                billable=False,
            )

            # Verify client was called correctly
            mock_clio_client.patch.assert_called_once()
            args, kwargs = mock_clio_client.patch.call_args
            assert args[0] == "matters/67890"
            payload = kwargs["json_data"]["matter"]
            assert payload["description"] == "Updated Matter Description"
            assert payload["billable"] is False

    @pytest.mark.asyncio
    async def test_close_matter_success(self, mock_tool_context, mock_clio_client):
        """Test successful matter closure."""
        with patch("arcade_clio.tools.matters.ClioClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client

            result = await close_matter(
                context=mock_tool_context, matter_id=67890, close_date="2024-01-31"
            )

            # Verify client was called correctly
            mock_clio_client.patch.assert_called_once()
            args, kwargs = mock_clio_client.patch.call_args
            assert args[0] == "matters/67890"
            payload = kwargs["json_data"]["matter"]
            assert payload["status"] == "Closed"
            assert payload["close_date"] == "2024-01-31"

    @pytest.mark.asyncio
    async def test_close_matter_without_date(self, mock_tool_context):
        """Test close matter without close date."""
        with pytest.raises(ClioValidationError, match="Close date is required"):
            await close_matter(context=mock_tool_context, matter_id=67890, close_date="")

    @pytest.mark.asyncio
    async def test_get_matter_activities_success(
        self, mock_tool_context, sample_activities_response
    ):
        """Test successful matter activities retrieval."""
        with patch("arcade_clio.tools.matters.ClioClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get.return_value = sample_activities_response
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await get_matter_activities(
                context=mock_tool_context, matter_id=67890, activity_type="TimeEntry", limit=20
            )

            # Verify result is valid JSON
            result_data = json.loads(result)
            assert isinstance(result_data, list)
            assert len(result_data) == 2

            # Verify client was called correctly
            mock_client.get.assert_called_once()
            args, kwargs = mock_client.get.call_args
            assert args[0] == "activities"
            assert kwargs["params"]["matter_id"] == 67890
            assert kwargs["params"]["type"] == "TimeEntry"

    @pytest.mark.asyncio
    async def test_add_matter_participant_success(self, mock_tool_context, mock_clio_client):
        """Test successful matter participant addition."""
        with patch("arcade_clio.tools.matters.ClioClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client

            mock_clio_client.post.return_value = {
                "matter_participant": {
                    "id": 55555,
                    "contact_id": 12345,
                    "matter_id": 67890,
                    "role": "client",
                }
            }

            result = await add_matter_participant(
                context=mock_tool_context, matter_id=67890, contact_id=12345, role="client"
            )

            # Verify result is valid JSON
            result_data = json.loads(result)
            assert result_data["id"] == 55555
            assert result_data["role"] == "client"

            # Verify client was called correctly
            mock_clio_client.post.assert_called_once()
            args, kwargs = mock_clio_client.post.call_args
            assert args[0] == "matters/67890/participants"

    @pytest.mark.asyncio
    async def test_add_matter_participant_invalid_role(self, mock_tool_context):
        """Test add participant with invalid role."""
        with pytest.raises(ClioValidationError, match="Invalid role"):
            await add_matter_participant(
                context=mock_tool_context, matter_id=67890, contact_id=12345, role="invalid_role"
            )

    @pytest.mark.asyncio
    async def test_remove_matter_participant_success(self, mock_tool_context, mock_clio_client):
        """Test successful matter participant removal."""
        with patch("arcade_clio.tools.matters.ClioClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client

            mock_clio_client.delete.return_value = {}

            result = await remove_matter_participant(
                context=mock_tool_context, matter_id=67890, participant_id=55555
            )

            # Verify result
            result_data = json.loads(result)
            assert result_data["success"] is True

            # Verify client was called correctly
            mock_clio_client.delete.assert_called_once_with("matters/67890/participants/55555")


class TestMatterValidation:
    """Test suite for matter validation functions."""

    def test_validate_matter_status_valid(self):
        """Test matter status validation with valid statuses."""
        from arcade_clio.validation import validate_matter_status

        assert validate_matter_status("open") == "Open"
        assert validate_matter_status("Open") == "Open"
        assert validate_matter_status("closed") == "Closed"
        assert validate_matter_status("pending") == "Pending"

    def test_validate_matter_status_invalid(self):
        """Test matter status validation with invalid status."""
        from arcade_clio.validation import validate_matter_status

        with pytest.raises(ClioValidationError, match="Invalid matter status"):
            validate_matter_status("archived")

    def test_validate_participant_role_valid(self):
        """Test participant role validation with valid roles."""
        from arcade_clio.validation import validate_participant_role

        assert validate_participant_role("client") == "client"
        assert validate_participant_role("responsible_attorney") == "responsible_attorney"
        assert validate_participant_role("originating_attorney") == "originating_attorney"

    def test_validate_participant_role_invalid(self):
        """Test participant role validation with invalid role."""
        from arcade_clio.validation import validate_participant_role

        with pytest.raises(ClioValidationError, match="Invalid role"):
            validate_participant_role("partner")


class TestMatterEdgeCases:
    """Test edge cases and complex scenarios for matter tools."""

    @pytest.mark.asyncio
    async def test_matter_status_transition(self, mock_tool_context, mock_clio_client):
        """Test matter status transition from open to closed."""
        with patch("arcade_clio.tools.matters.ClioClient") as mock_client_class:
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client

            # First, get an open matter
            mock_clio_client.get_matter.return_value = {
                "matter": {"id": 67890, "status": "Open", "open_date": "2024-01-01"}
            }

            # Then close it
            mock_clio_client.patch.return_value = {
                "matter": {
                    "id": 67890,
                    "status": "Closed",
                    "open_date": "2024-01-01",
                    "close_date": "2024-01-31",
                }
            }

            result = await close_matter(
                context=mock_tool_context, matter_id=67890, close_date="2024-01-31"
            )

            result_data = json.loads(result)
            assert result_data["status"] == "Closed"
            assert result_data["close_date"] == "2024-01-31"

    @pytest.mark.asyncio
    async def test_matter_with_multiple_participants(
        self, mock_tool_context, sample_matter_with_participants
    ):
        """Test matter with multiple participants."""
        with patch("arcade_clio.tools.matters.ClioClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_matter.return_value = sample_matter_with_participants
            mock_client_class.return_value.__aenter__.return_value = mock_client

            result = await get_matter(
                context=mock_tool_context, matter_id=67890, include_extra_data=True
            )

            result_data = json.loads(result)

            # Verify participant data is included
            assert "client" in result_data
            assert result_data["client"]["id"] == 12345
            assert "responsible_attorney" in result_data
            assert result_data["responsible_attorney"]["id"] == 11111

            # Verify participants list
            assert "participants" in result_data
            assert len(result_data["participants"]) == 2
