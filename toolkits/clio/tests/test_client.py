"""Tests for Clio API client."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from arcade_clio.client import ClioClient
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


class TestClioClient:
    """Test suite for ClioClient."""

    @pytest.fixture
    def client(self, mock_tool_context):
        """Create a ClioClient instance for testing."""
        return ClioClient(mock_tool_context)

    @pytest.mark.asyncio
    async def test_client_context_manager(self, client):
        """Test ClioClient as async context manager."""
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_httpx.return_value = AsyncMock()

            async with client as c:
                assert c is client
                assert client._client is not None

            # Verify client was closed
            client._client.aclose.assert_called_once()

    def test_get_headers(self, client):
        """Test HTTP headers generation."""
        headers = client._get_headers()

        assert headers["Authorization"] == "Bearer test_token_12345"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert headers["X-API-VERSION"] == "4.0.0"
        assert headers["User-Agent"] == "Arcade-Clio-Toolkit/1.0"

    def test_handle_error_response_401(self, client):
        """Test error handling for 401 Unauthorized."""
        mock_response = MagicMock()
        mock_response.status_code = 401

        with pytest.raises(ClioAuthenticationError):
            client._handle_error_response(mock_response)

    def test_handle_error_response_403(self, client):
        """Test error handling for 403 Forbidden."""
        mock_response = MagicMock()
        mock_response.status_code = 403

        with pytest.raises(ClioPermissionError):
            client._handle_error_response(mock_response)

    def test_handle_error_response_404(self, client):
        """Test error handling for 404 Not Found."""
        mock_response = MagicMock()
        mock_response.status_code = 404

        with pytest.raises(ClioResourceNotFoundError):
            client._handle_error_response(mock_response)

    def test_handle_error_response_422(self, client):
        """Test error handling for 422 Validation Error."""
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.json.return_value = {"message": "Validation failed"}

        with pytest.raises(ClioValidationError, match="Validation failed"):
            client._handle_error_response(mock_response)

    def test_handle_error_response_429(self, client):
        """Test error handling for 429 Rate Limited."""
        mock_response = MagicMock()
        mock_response.status_code = 429

        with pytest.raises(ClioRateLimitError):
            client._handle_error_response(mock_response)

    def test_handle_error_response_500(self, client):
        """Test error handling for 500 Server Error."""
        mock_response = MagicMock()
        mock_response.status_code = 500

        with pytest.raises(ClioServerError):
            client._handle_error_response(mock_response)

    @pytest.mark.asyncio
    async def test_make_request_success(self, client):
        """Test successful API request."""
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.json.return_value = {"data": "test"}

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = AsyncMock()
            mock_client.request.return_value = mock_response
            mock_httpx.return_value = mock_client
            client._client = mock_client

            response = await client._make_request("GET", "test-endpoint")

            assert response.json() == {"data": "test"}
            mock_client.request.assert_called_once_with(
                method="GET", url="test-endpoint", params=None, json=None
            )

    @pytest.mark.asyncio
    async def test_make_request_timeout_retry(self, client):
        """Test request timeout with retry logic."""
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = AsyncMock()
            mock_client.request.side_effect = [
                httpx.TimeoutException("Timeout"),
                httpx.TimeoutException("Timeout"),
                AsyncMock(is_success=True, json=lambda: {"data": "success"}),
            ]
            mock_httpx.return_value = mock_client
            client._client = mock_client

            with patch("asyncio.sleep") as mock_sleep:
                response = await client._make_request("GET", "test-endpoint")
                assert response.json() == {"data": "success"}
                assert mock_client.request.call_count == 3
                assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_make_request_timeout_max_retries(self, client):
        """Test request timeout exceeding max retries."""
        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = AsyncMock()
            mock_client.request.side_effect = httpx.TimeoutException("Timeout")
            mock_httpx.return_value = mock_client
            client._client = mock_client

            with patch("asyncio.sleep"):
                with pytest.raises(ClioTimeoutError):
                    await client._make_request("GET", "test-endpoint")

    @pytest.mark.asyncio
    async def test_make_request_rate_limit_retry(self, client):
        """Test rate limit (429) retry logic."""
        mock_responses = [
            AsyncMock(is_success=False, status_code=429),
            AsyncMock(is_success=False, status_code=429),
            AsyncMock(is_success=True, json=lambda: {"data": "success"}),
        ]

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = AsyncMock()
            mock_client.request.side_effect = mock_responses
            mock_httpx.return_value = mock_client
            client._client = mock_client

            with patch("asyncio.sleep") as mock_sleep:
                response = await client._make_request("GET", "test-endpoint")
                assert response.json() == {"data": "success"}
                assert mock_client.request.call_count == 3
                assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_make_request_server_error_retry(self, client):
        """Test server error (5xx) retry logic."""
        mock_responses = [
            AsyncMock(is_success=False, status_code=500),
            AsyncMock(is_success=False, status_code=503),
            AsyncMock(is_success=True, json=lambda: {"data": "success"}),
        ]

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = AsyncMock()
            mock_client.request.side_effect = mock_responses
            mock_httpx.return_value = mock_client
            client._client = mock_client

            with patch("asyncio.sleep") as mock_sleep:
                response = await client._make_request("GET", "test-endpoint")
                assert response.json() == {"data": "success"}
                assert mock_client.request.call_count == 3
                assert mock_sleep.call_count == 2

    @pytest.mark.asyncio
    async def test_make_request_rate_limit_max_retries(self, client):
        """Test rate limit exceeding max retries."""
        mock_response = AsyncMock(is_success=False, status_code=429)

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_client = AsyncMock()
            mock_client.request.return_value = mock_response
            mock_httpx.return_value = mock_client
            client._client = mock_client

            with patch("asyncio.sleep"):
                with pytest.raises(ClioRateLimitError):
                    await client._make_request("GET", "test-endpoint")

    @pytest.mark.asyncio
    async def test_get_request(self, client):
        """Test GET request wrapper."""
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.json.return_value = {"result": "success"}

        with patch.object(client, "_make_request", return_value=mock_response) as mock_make_request:
            result = await client.get("test-endpoint", params={"limit": 10})

            assert result == {"result": "success"}
            mock_make_request.assert_called_once_with("GET", "test-endpoint", params={"limit": 10})

    @pytest.mark.asyncio
    async def test_post_request(self, client):
        """Test POST request wrapper."""
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.json.return_value = {"id": 123}

        with patch.object(client, "_make_request", return_value=mock_response) as mock_make_request:
            result = await client.post("test-endpoint", json_data={"name": "test"})

            assert result == {"id": 123}
            mock_make_request.assert_called_once_with(
                "POST", "test-endpoint", params=None, json_data={"name": "test"}
            )

    @pytest.mark.asyncio
    async def test_patch_request(self, client):
        """Test PATCH request wrapper."""
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.json.return_value = {"updated": True}

        with patch.object(client, "_make_request", return_value=mock_response) as mock_make_request:
            result = await client.patch("test-endpoint", json_data={"field": "updated"})

            assert result == {"updated": True}
            mock_make_request.assert_called_once_with(
                "PATCH", "test-endpoint", params=None, json_data={"field": "updated"}
            )

    @pytest.mark.asyncio
    async def test_delete_request(self, client):
        """Test DELETE request wrapper."""
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.json.return_value = {}

        with patch.object(client, "_make_request", return_value=mock_response) as mock_make_request:
            result = await client.delete("test-endpoint")

            assert result == {}
            mock_make_request.assert_called_once_with("DELETE", "test-endpoint", params=None)

    @pytest.mark.asyncio
    async def test_delete_request_empty_response(self, client):
        """Test DELETE request with empty response."""
        mock_response = AsyncMock()
        mock_response.is_success = True
        mock_response.json.side_effect = Exception("No JSON content")

        with patch.object(client, "_make_request", return_value=mock_response):
            result = await client.delete("test-endpoint")

            assert result == {}

    @pytest.mark.asyncio
    async def test_get_contacts_convenience_method(self, client):
        """Test get_contacts convenience method."""
        expected_result = {"contacts": [{"id": 123}]}

        with patch.object(client, "get", return_value=expected_result) as mock_get:
            result = await client.get_contacts(limit=10, offset=20, status="active")

            assert result == expected_result
            mock_get.assert_called_once_with(
                "contacts", params={"limit": 10, "offset": 20, "status": "active"}
            )

    @pytest.mark.asyncio
    async def test_get_contact_convenience_method(self, client):
        """Test get_contact convenience method."""
        expected_result = {"contact": {"id": 123}}

        with patch.object(client, "get", return_value=expected_result) as mock_get:
            result = await client.get_contact(123)

            assert result == expected_result
            mock_get.assert_called_once_with("contacts/123")

    @pytest.mark.asyncio
    async def test_get_matters_convenience_method(self, client):
        """Test get_matters convenience method."""
        expected_result = {"matters": [{"id": 456}]}

        with patch.object(client, "get", return_value=expected_result) as mock_get:
            result = await client.get_matters(limit=5, client_id=123)

            assert result == expected_result
            mock_get.assert_called_once_with("matters", params={"limit": 5, "client_id": 123})

    @pytest.mark.asyncio
    async def test_get_matter_convenience_method(self, client):
        """Test get_matter convenience method."""
        expected_result = {"matter": {"id": 456}}

        with patch.object(client, "get", return_value=expected_result) as mock_get:
            result = await client.get_matter(456)

            assert result == expected_result
            mock_get.assert_called_once_with("matters/456")

    @pytest.mark.asyncio
    async def test_get_activities_convenience_method(self, client):
        """Test get_activities convenience method."""
        expected_result = {"activities": [{"id": 789}]}

        with patch.object(client, "get", return_value=expected_result) as mock_get:
            result = await client.get_activities(matter_id=456, limit=25)

            assert result == expected_result
            mock_get.assert_called_once_with("activities", params={"matter_id": 456, "limit": 25})

    @pytest.mark.asyncio
    async def test_client_not_initialized_error(self, client):
        """Test error when client is not used as context manager."""
        with pytest.raises(ClioError, match="Client not initialized"):
            await client._make_request("GET", "test")


class TestClioClientNetworkHandling:
    """Test network-specific client behavior."""

    @pytest.mark.asyncio
    async def test_network_error_retry(self, mock_tool_context):
        """Test network error retry logic."""
        client = ClioClient(mock_tool_context)

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_http_client = AsyncMock()
            mock_http_client.request.side_effect = [
                httpx.NetworkError("Connection failed"),
                AsyncMock(is_success=True, json=lambda: {"data": "success"}),
            ]
            mock_httpx.return_value = mock_http_client
            client._client = mock_http_client

            with patch("asyncio.sleep"):
                response = await client._make_request("GET", "test-endpoint")
                assert response.json() == {"data": "success"}
                assert mock_http_client.request.call_count == 2

    @pytest.mark.asyncio
    async def test_network_error_max_retries(self, mock_tool_context):
        """Test network error exceeding max retries."""
        client = ClioClient(mock_tool_context)

        with patch("httpx.AsyncClient") as mock_httpx:
            mock_http_client = AsyncMock()
            mock_http_client.request.side_effect = httpx.NetworkError("Connection failed")
            mock_httpx.return_value = mock_http_client
            client._client = mock_http_client

            with patch("asyncio.sleep"):
                with pytest.raises(ClioTimeoutError):
                    await client._make_request("GET", "test-endpoint")
