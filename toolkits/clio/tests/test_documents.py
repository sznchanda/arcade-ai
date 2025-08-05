"""Tests for document management tools."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from arcade_clio.models import Document
from arcade_clio.tools.documents import (
    create_document,
    delete_document,
    get_document,
    list_documents,
    update_document,
)


@pytest.mark.asyncio
class TestDocumentTools:
    """Test document management tools."""

    async def test_list_documents_success(self, mock_tool_context):
        """Test successful document listing."""
        sample_documents = [
            {
                "id": 1,
                "name": "Contract.pdf",
                "description": "Employment contract",
                "matter": {"id": 12345, "description": "Employment Matter"},
                "size": 256000,
                "content_type": "application/pdf",
            },
            {
                "id": 2,
                "name": "Resume.docx",
                "description": "Client resume",
                "contact": {"id": 67890, "name": "John Doe"},
                "size": 125000,
                "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            },
        ]

        with patch("arcade_clio.tools.documents.ClioClient") as mock_client_class:
            mock_clio_client = AsyncMock()
            mock_clio_client.get.return_value = {
                "documents": sample_documents,
                "meta": {"total_count": 2},
            }
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client

            result = await list_documents(
                context=mock_tool_context,
                limit=50,
                offset=0,
                matter_id="12345",
            )

            # Verify API call
            mock_clio_client.get.assert_called_once_with(
                "/documents",
                params={
                    "limit": 50,
                    "offset": 0,
                    "matter_id": "12345",
                },
            )

            # Verify response structure
            response_data = json.loads(result)
            assert response_data["success"] is True
            assert len(response_data["documents"]) == 2
            assert response_data["pagination"]["total"] == 2

    async def test_get_document_success(self, mock_tool_context):
        """Test successful document retrieval."""
        sample_document = {
            "id": 1,
            "name": "Contract.pdf",
            "description": "Employment contract",
            "matter": {"id": 12345, "description": "Employment Matter"},
            "size": 256000,
            "content_type": "application/pdf",
            "current_version": {
                "id": 1,
                "filename": "contract_v1.pdf",
                "download_url": "https://example.com/download/contract_v1.pdf",
            },
        }

        with patch("arcade_clio.tools.documents.ClioClient") as mock_client_class:
            mock_clio_client = AsyncMock()
            mock_clio_client.get.return_value = {"document": sample_document}
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client

            result = await get_document(
                context=mock_tool_context,
                document_id="1",
            )

            # Verify API call
            mock_clio_client.get.assert_called_once_with("/documents/1", params={})

            # Verify response structure
            response_data = json.loads(result)
            assert response_data["success"] is True
            assert response_data["document"]["name"] == "Contract.pdf"

    async def test_create_document_success(self, mock_tool_context):
        """Test successful document creation."""
        document_data = {
            "name": "New Contract.pdf",
            "description": "New employment contract",
            "matter_id": 12345,
            "document_category_id": 1,
        }

        sample_created = {
            "id": 3,
            "name": "New Contract.pdf",
            "description": "New employment contract",
            "matter": {"id": 12345, "description": "Employment Matter"},
        }

        with patch("arcade_clio.tools.documents.ClioClient") as mock_client_class:
            mock_clio_client = AsyncMock()
            mock_clio_client.post.return_value = {"document": sample_created}
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client

            await create_document(
                context=mock_tool_context,
                document_data=document_data,
            )

            # Verify API call
            mock_clio_client.post.assert_called_once()
            call_args = mock_clio_client.post.call_args
            assert call_args[0][0] == "/documents"
            assert "document" in call_args[1]["json"]

    async def test_update_document_success(self, mock_tool_context):
        """Test successful document update."""
        update_data = {
            "name": "Updated Contract.pdf",
            "description": "Updated employment contract",
        }

        sample_updated = {
            "id": 1,
            "name": "Updated Contract.pdf",
            "description": "Updated employment contract",
            "matter": {"id": 12345, "description": "Employment Matter"},
        }

        with patch("arcade_clio.tools.documents.ClioClient") as mock_client_class:
            mock_clio_client = AsyncMock()
            mock_clio_client.patch.return_value = {"document": sample_updated}
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client

            await update_document(
                context=mock_tool_context,
                document_id="1",
                document_data=update_data,
            )

            # Verify API call
            mock_clio_client.patch.assert_called_once()
            call_args = mock_clio_client.patch.call_args
            assert call_args[0][0] == "/documents/1"
            assert "document" in call_args[1]["json"]

    async def test_delete_document_success(self, mock_tool_context):
        """Test successful document deletion."""
        sample_document = {
            "id": 1,
            "name": "Contract.pdf",
            "description": "Employment contract",
        }

        with patch("arcade_clio.tools.documents.ClioClient") as mock_client_class:
            mock_clio_client = AsyncMock()
            mock_clio_client.get.return_value = {"document": sample_document}
            mock_clio_client.delete.return_value = {}
            mock_client_class.return_value.__aenter__.return_value = mock_clio_client

            result = await delete_document(
                context=mock_tool_context,
                document_id="1",
            )

            # Verify API calls
            mock_clio_client.get.assert_called_once_with("/documents/1")
            mock_clio_client.delete.assert_called_once_with("/documents/1")

            # Verify response
            response_data = json.loads(result)
            assert response_data["success"] is True
            assert "deleted successfully" in response_data["message"]