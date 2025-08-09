"""Webhook management tools for Clio."""

from typing import Annotated, Optional

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import OAuth2

from ..client import ClioClient
from ..exceptions import ClioError, ClioValidationError
from ..utils import (
    build_search_params,
    extract_list_data,
    extract_model_data,
    format_json_response,
    prepare_request_data,
)
from ..validation import (
    validate_id,
    validate_limit_offset,
    validate_required_string,
)


@tool(requires_auth=OAuth2(id="clio"))
async def create_webhook(
    context: ToolContext,
    url: Annotated[str, "Webhook endpoint URL that will receive event notifications"],
    events: Annotated[list[str], "List of events to subscribe to (e.g. ['contact', 'matter', 'activity'])"],
    description: Annotated[Optional[str], "Description of the webhook (optional)"] = None,
) -> Annotated[str, "JSON string containing the created webhook details"]:
    """
    Create a new webhook for receiving real-time notifications from Clio.

    Examples:
    ```
    create_webhook(
        url="https://myapp.com/webhooks/clio",
        events=["contact", "matter", "bill"]
    )
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate inputs
            url = validate_required_string(url, "URL")
            if not events:
                raise ClioValidationError("Events list cannot be empty")

            # Build webhook data
            webhook_data = prepare_request_data({
                "url": url,
                "events": events,
                "description": description,
            })

            # Create webhook
            response = await client.post("webhooks", data={"data": webhook_data})
            webhook = extract_model_data(response, "webhook")

            return format_json_response({
                "success": True,
                "webhook": webhook,
                "message": f"Webhook created successfully for {len(events)} event(s)"
            })

        except ClioError:
            raise
        except (ValueError, TypeError) as e:
            raise ClioValidationError(f"Invalid webhook parameters: {e}")


@tool(requires_auth=OAuth2(id="clio"))
async def list_webhooks(
    context: ToolContext,
    limit: Annotated[Optional[int], "Maximum number of webhooks to return (1-200, default: 50)"] = 50,
    offset: Annotated[Optional[int], "Number of webhooks to skip for pagination (default: 0)"] = 0,
    fields: Annotated[
        Optional[str], "Comma-separated list of fields to include in response (e.g. 'id,url,events')"
    ] = None,
) -> Annotated[str, "JSON string containing list of webhooks"]:
    """
    List all configured webhooks for the current account.

    Example:
    ```
    list_webhooks(limit=10)
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate pagination
            limit, offset = validate_limit_offset(limit, offset)

            # Build search parameters
            params = build_search_params(
                limit=limit,
                offset=offset,
                fields=fields,
            )

            # Get webhooks
            response = await client.get("webhooks", params=params)
            webhooks_data = extract_list_data(response, "webhooks")

            return format_json_response({
                "success": True,
                "webhooks": webhooks_data,
                "count": len(webhooks_data)
            })

        except ClioError:
            raise
        except (ValueError, TypeError) as e:
            raise ClioValidationError(f"Invalid parameters: {e}")


@tool(requires_auth=OAuth2(id="clio"))
async def get_webhook(
    context: ToolContext,
    webhook_id: Annotated[int, "The ID of the webhook to retrieve"],
    fields: Annotated[
        Optional[str], "Comma-separated list of fields to include in response (e.g. 'id,url,events')"
    ] = None,
) -> Annotated[str, "JSON string containing the webhook details"]:
    """
    Retrieve details of a specific webhook.

    Example:
    ```
    get_webhook(webhook_id=12345)
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate input
            webhook_id = validate_id(webhook_id, "Webhook ID")

            # Build parameters with fields support
            params = build_search_params(fields=fields) if fields else None

            response = await client.get(f"webhooks/{webhook_id}", params=params)
            webhook_data = extract_model_data(response, "webhook")

            return format_json_response({
                "success": True,
                "webhook": webhook_data
            })

        except ClioError:
            raise
        except (ValueError, TypeError) as e:
            raise ClioValidationError(f"Invalid webhook ID {webhook_id}: {e}")


@tool(requires_auth=OAuth2(id="clio"))
async def update_webhook(
    context: ToolContext,
    webhook_id: Annotated[int, "The ID of the webhook to update"],
    url: Annotated[Optional[str], "New webhook endpoint URL (optional)"] = None,
    events: Annotated[Optional[list[str]], "New list of events to subscribe to (optional)"] = None,
    description: Annotated[Optional[str], "New description of the webhook (optional)"] = None,
) -> Annotated[str, "JSON string containing the updated webhook details"]:
    """
    Update an existing webhook configuration.

    Examples:
    ```
    update_webhook(webhook_id=12345, url="https://newapp.com/webhooks/clio")
    update_webhook(webhook_id=12345, events=["contact", "matter", "bill", "activity"])
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate inputs
            webhook_id = validate_id(webhook_id, "Webhook ID")

            if url:
                url = validate_required_string(url, "URL")

            # Build update data
            update_data = prepare_request_data({
                "url": url,
                "events": events,
                "description": description,
            })

            if not update_data:
                raise ClioValidationError("At least one field must be provided to update")

            # Update webhook
            response = await client.patch(f"webhooks/{webhook_id}", data={"data": update_data})
            webhook = extract_model_data(response, "webhook")

            return format_json_response({
                "success": True,
                "webhook": webhook,
                "message": f"Webhook {webhook_id} updated successfully"
            })

        except ClioError:
            raise
        except (ValueError, TypeError) as e:
            raise ClioValidationError(f"Invalid update parameters for webhook {webhook_id}: {e}")


@tool(requires_auth=OAuth2(id="clio"))
async def delete_webhook(
    context: ToolContext,
    webhook_id: Annotated[int, "The ID of the webhook to delete"],
) -> Annotated[str, "JSON string confirming webhook deletion"]:
    """
    Delete a webhook and stop receiving notifications.

    Example:
    ```
    delete_webhook(webhook_id=12345)
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate input
            webhook_id = validate_id(webhook_id, "Webhook ID")

            # Delete webhook
            await client.delete(f"webhooks/{webhook_id}")

            return format_json_response({
                "success": True,
                "message": f"Webhook {webhook_id} deleted successfully",
                "webhook_id": webhook_id
            })

        except ClioError:
            raise
        except (ValueError, TypeError) as e:
            raise ClioValidationError(f"Failed to delete webhook {webhook_id}: {e}")

