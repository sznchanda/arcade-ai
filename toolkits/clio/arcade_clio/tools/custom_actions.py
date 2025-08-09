"""Custom Actions tools for Clio UI customization."""

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
async def create_custom_action(
    context: ToolContext,
    label: Annotated[str, "Link text displayed to users in the Clio interface"],
    target_url: Annotated[str, "Destination URL that users will be redirected to"],
    ui_reference: Annotated[str, "UI location where the action appears (e.g., 'matters/show')"],
    description: Annotated[Optional[str], "Description of the custom action (optional)"] = None,
) -> Annotated[str, "JSON string containing the created custom action details"]:
    """
    Create a new custom action for UI customization in Clio.

    Custom actions add links to the Clio interface that redirect users to
    external applications with context about the current record.

    Examples:
    ```
    create_custom_action(
        label="View in External System",
        target_url="https://myapp.com/matters/{matter_id}",
        ui_reference="matters/show"
    )
    create_custom_action(
        label="Send to CRM",
        target_url="https://crm.mycompany.com/contacts/import?clio_id={contact_id}",
        ui_reference="contacts/show",
        description="Export contact to our CRM system"
    )
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate inputs
            label = validate_required_string(label, "Label")
            target_url = validate_required_string(target_url, "Target URL")
            ui_reference = validate_required_string(ui_reference, "UI reference")

            # Build custom action data
            action_data = prepare_request_data({
                "label": label,
                "target_url": target_url,
                "ui_reference": ui_reference,
                "description": description,
            })

            # Create custom action
            response = await client.post("custom_actions", data={"data": action_data})
            custom_action = extract_model_data(response, "custom_action")

            return format_json_response({
                "success": True,
                "custom_action": custom_action,
                "message": f"Custom action '{label}' created successfully"
            })

        except ClioError:
            raise
        except (ValueError, TypeError) as e:
            raise ClioValidationError(f"Invalid custom action parameters: {e}")


@tool(requires_auth=OAuth2(id="clio"))
async def list_custom_actions(
    context: ToolContext,
    limit: Annotated[Optional[int], "Maximum number of custom actions to return (1-200, default: 50)"] = 50,
    offset: Annotated[Optional[int], "Number of custom actions to skip for pagination (default: 0)"] = 0,
    fields: Annotated[
        Optional[str], "Comma-separated list of fields to include in response (e.g. 'id,label,target_url')"
    ] = None,
) -> Annotated[str, "JSON string containing list of custom actions"]:
    """
    List all configured custom actions for the current account.

    Example:
    ```
    list_custom_actions(limit=20)
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

            # Get custom actions
            response = await client.get("custom_actions", params=params)
            actions_data = extract_list_data(response, "custom_actions")

            return format_json_response({
                "success": True,
                "custom_actions": actions_data,
                "count": len(actions_data)
            })

        except ClioError:
            raise
        except (ValueError, TypeError) as e:
            raise ClioValidationError(f"Invalid parameters: {e}")


@tool(requires_auth=OAuth2(id="clio"))
async def get_custom_action(
    context: ToolContext,
    custom_action_id: Annotated[int, "The ID of the custom action to retrieve"],
    fields: Annotated[
        Optional[str], "Comma-separated list of fields to include in response (e.g. 'id,label,target_url')"
    ] = None,
) -> Annotated[str, "JSON string containing the custom action details"]:
    """
    Retrieve details of a specific custom action.

    Example:
    ```
    get_custom_action(custom_action_id=12345)
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate input
            custom_action_id = validate_id(custom_action_id, "Custom Action ID")

            # Build parameters with fields support
            params = build_search_params(fields=fields) if fields else None

            response = await client.get(f"custom_actions/{custom_action_id}", params=params)
            action_data = extract_model_data(response, "custom_action")

            return format_json_response({
                "success": True,
                "custom_action": action_data
            })

        except ClioError:
            raise
        except (ValueError, TypeError) as e:
            raise ClioValidationError(f"Invalid custom action ID {custom_action_id}: {e}")


@tool(requires_auth=OAuth2(id="clio"))
async def update_custom_action(
    context: ToolContext,
    custom_action_id: Annotated[int, "The ID of the custom action to update"],
    label: Annotated[Optional[str], "New link text displayed to users (optional)"] = None,
    target_url: Annotated[Optional[str], "New destination URL (optional)"] = None,
    ui_reference: Annotated[Optional[str], "New UI location reference (optional)"] = None,
    description: Annotated[Optional[str], "New description of the custom action (optional)"] = None,
) -> Annotated[str, "JSON string containing the updated custom action details"]:
    """
    Update an existing custom action configuration.

    Examples:
    ```
    update_custom_action(custom_action_id=12345, label="Updated Action Label")
    update_custom_action(
        custom_action_id=12345,
        target_url="https://newdomain.com/matters/{matter_id}",
        description="Updated integration endpoint"
    )
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate inputs
            custom_action_id = validate_id(custom_action_id, "Custom Action ID")

            # Build update data
            update_data = prepare_request_data({
                "label": label,
                "target_url": target_url,
                "ui_reference": ui_reference,
                "description": description,
            })

            if not update_data:
                raise ClioValidationError("At least one field must be provided to update")

            # Update custom action
            response = await client.patch(f"custom_actions/{custom_action_id}", data={"data": update_data})
            custom_action = extract_model_data(response, "custom_action")

            return format_json_response({
                "success": True,
                "custom_action": custom_action,
                "message": f"Custom action {custom_action_id} updated successfully"
            })

        except ClioError:
            raise
        except (ValueError, TypeError) as e:
            raise ClioValidationError(f"Invalid update parameters for custom action {custom_action_id}: {e}")


@tool(requires_auth=OAuth2(id="clio"))
async def delete_custom_action(
    context: ToolContext,
    custom_action_id: Annotated[int, "The ID of the custom action to delete"],
) -> Annotated[str, "JSON string confirming custom action deletion"]:
    """
    Delete a custom action and remove it from the Clio interface.

    Example:
    ```
    delete_custom_action(custom_action_id=12345)
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate input
            custom_action_id = validate_id(custom_action_id, "Custom Action ID")

            # Delete custom action
            await client.delete(f"custom_actions/{custom_action_id}")

            return format_json_response({
                "success": True,
                "message": f"Custom action {custom_action_id} deleted successfully",
                "custom_action_id": custom_action_id
            })

        except ClioError:
            raise
        except (ValueError, TypeError) as e:
            raise ClioValidationError(f"Failed to delete custom action {custom_action_id}: {e}")


@tool(requires_auth=OAuth2(id="clio"))
async def test_custom_action_url(
    context: ToolContext,
    target_url: Annotated[str, "The URL template to test (e.g., 'https://app.com/matters/{matter_id}')"],
    matter_id: Annotated[Optional[int], "Sample matter ID for URL testing (optional)"] = None,
    contact_id: Annotated[Optional[int], "Sample contact ID for URL testing (optional)"] = None,
) -> Annotated[str, "JSON string showing how the URL would be resolved with sample data"]:
    """
    Test how a custom action URL template would be resolved with sample data.

    This is a utility function to help design custom action URLs by showing
    how placeholder variables would be substituted.

    Examples:
    ```
    test_custom_action_url(
        target_url="https://myapp.com/matters/{matter_id}/summary",
        matter_id=12345
    )
    test_custom_action_url(
        target_url="https://crm.com/contacts/{contact_id}?source=clio",
        contact_id=67890
    )
    ```
    """
    try:
        # Validate input
        target_url = validate_required_string(target_url, "Target URL")

        # Create sample substitutions
        substitutions = {}
        if matter_id:
            substitutions["matter_id"] = matter_id
        if contact_id:
            substitutions["contact_id"] = contact_id

        # Add some common placeholder examples if not provided
        if not substitutions:
            substitutions = {
                "matter_id": "12345",
                "contact_id": "67890",
                "user_id": "11111",
                "bill_id": "54321"
            }

        # Attempt to format the URL
        resolved_url = target_url
        for key, value in substitutions.items():
            placeholder = f"{{{key}}}"
            if placeholder in resolved_url:
                resolved_url = resolved_url.replace(placeholder, str(value))

        # Check for remaining placeholders
        remaining_placeholders = []
        import re
        placeholder_pattern = r'\{([^}]+)\}'
        for match in re.finditer(placeholder_pattern, resolved_url):
            remaining_placeholders.append(match.group(1))

        return format_json_response({
            "success": True,
            "original_url": target_url,
            "resolved_url": resolved_url,
            "substitutions_applied": substitutions,
            "remaining_placeholders": remaining_placeholders,
            "is_valid": len(remaining_placeholders) == 0
        })

    except Exception as e:
        raise ClioValidationError(f"Invalid URL template: {e}")

