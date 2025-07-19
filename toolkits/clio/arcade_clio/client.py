"""Core API client for Clio integration."""

import asyncio
from typing import Any, Optional

import httpx
from arcade_tdk import ToolContext

from .exceptions import (
    ClioAuthenticationError,
    ClioError,
    ClioPermissionError,
    ClioRateLimitError,
    ClioResourceNotFoundError,
    ClioServerError,
    ClioTimeoutError,
    ClioValidationError,
)


class ClioClient:
    """Async HTTP client for Clio API v4."""

    BASE_URL = "https://app.clio.com/api/v4/"
    TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0

    def __init__(self, context: ToolContext) -> None:
        """Initialize the Clio client.

        Args:
            context: The tool context containing authorization token
        """
        self.context = context
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "ClioClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=httpx.Timeout(self.TIMEOUT),
            headers=self._get_headers(),
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests."""
        token = self.context.authorization.token if self.context.authorization else ""

        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-VERSION": "4.0.0",  # Critical for Clio API v4
            "User-Agent": "Arcade-Clio-Toolkit/1.0",
        }

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle HTTP error responses by raising appropriate exceptions."""
        if response.status_code == 401:
            raise ClioAuthenticationError("Invalid or expired authentication token")
        elif response.status_code == 403:
            raise ClioPermissionError("Insufficient permissions for this operation")
        elif response.status_code == 404:
            raise ClioResourceNotFoundError("Requested resource not found")
        elif response.status_code == 422:
            try:
                error_data = response.json()
                error_message = error_data.get("message", "Validation error")
            except Exception:
                error_message = "Validation error"
            raise ClioValidationError(error_message)
        elif response.status_code == 429:
            raise ClioRateLimitError("API rate limit exceeded")
        elif response.status_code >= 500:
            raise ClioServerError(f"Server error: {response.status_code}")
        else:
            raise ClioError(f"HTTP {response.status_code}: {response.text}")

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """Make an HTTP request with error handling and retries."""
        if not self._client:
            raise ClioError("Client not initialized. Use as async context manager.")

        try:
            response = await self._client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json_data,
            )

            if response.is_success:
                return response

            # Handle rate limiting with retry
            if response.status_code == 429 and retry_count < self.MAX_RETRIES:
                await asyncio.sleep(self.RETRY_DELAY * (2 ** retry_count))
                return await self._make_request(
                    method, endpoint, params=params, json_data=json_data, retry_count=retry_count + 1
                )

            # Handle server errors with retry
            if response.status_code >= 500 and retry_count < self.MAX_RETRIES:
                await asyncio.sleep(self.RETRY_DELAY * (2 ** retry_count))
                return await self._make_request(
                    method, endpoint, params=params, json_data=json_data, retry_count=retry_count + 1
                )

            # Handle specific errors
            self._handle_error_response(response)

        except httpx.TimeoutException as e:
            if retry_count < self.MAX_RETRIES:
                await asyncio.sleep(self.RETRY_DELAY * (2 ** retry_count))
                return await self._make_request(
                    method, endpoint, params=params, json_data=json_data, retry_count=retry_count + 1
                )
            raise ClioTimeoutError(f"Request timeout: {e!s}")

        except httpx.NetworkError as e:
            if retry_count < self.MAX_RETRIES:
                await asyncio.sleep(self.RETRY_DELAY * (2 ** retry_count))
                return await self._make_request(
                    method, endpoint, params=params, json_data=json_data, retry_count=retry_count + 1
                )
            raise ClioError(f"Network error: {e!s}")

        # Should not reach here due to handle_error_response raising
        raise ClioError("Unexpected response")

    async def get(
        self,
        endpoint: str,
        *,
        params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a GET request."""
        response = await self._make_request("GET", endpoint, params=params)
        return response.json()

    async def post(
        self,
        endpoint: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a POST request."""
        response = await self._make_request("POST", endpoint, params=params, json_data=json_data)
        return response.json()

    async def patch(
        self,
        endpoint: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make a PATCH request."""
        response = await self._make_request("PATCH", endpoint, params=params, json_data=json_data)
        return response.json()

    async def delete(
        self,
        endpoint: str,
        *,
        params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a DELETE request."""
        response = await self._make_request("DELETE", endpoint, params=params)
        try:
            return response.json()
        except Exception:
            # Some DELETE requests return empty responses
            return {}

    # Convenience methods for common endpoints

    async def get_contacts(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **filters: Any
    ) -> dict[str, Any]:
        """Get contacts with optional filtering."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        params.update(filters)

        return await self.get("contacts", params=params)

    async def get_contact(self, contact_id: int) -> dict[str, Any]:
        """Get a specific contact by ID."""
        return await self.get(f"contacts/{contact_id}")

    async def get_matters(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **filters: Any
    ) -> dict[str, Any]:
        """Get matters with optional filtering."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        params.update(filters)

        return await self.get("matters", params=params)

    async def get_matter(self, matter_id: int) -> dict[str, Any]:
        """Get a specific matter by ID."""
        return await self.get(f"matters/{matter_id}")

    async def get_activities(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **filters: Any
    ) -> dict[str, Any]:
        """Get activities with optional filtering."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        params.update(filters)

        return await self.get("activities", params=params)

    async def get_bills(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **filters: Any
    ) -> dict[str, Any]:
        """Get bills with optional filtering."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        params.update(filters)

        return await self.get("bills", params=params)

    async def get_documents(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **filters: Any
    ) -> dict[str, Any]:
        """Get documents with optional filtering."""
        params = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        params.update(filters)

        return await self.get("documents", params=params)
