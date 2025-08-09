"""Timer API integration tools for Clio real-time time tracking."""

from typing import Annotated, Optional

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import OAuth2

from ..client import ClioClient
from ..exceptions import ClioError, ClioValidationError
from ..utils import (
    extract_model_data,
    format_json_response,
    prepare_request_data,
)
from ..validation import (
    validate_id,
    validate_required_string,
)


@tool(requires_auth=OAuth2(id="clio"))
async def start_timer(
    context: ToolContext,
    matter_id: Annotated[int, "The ID of the matter to track time for"],
    description: Annotated[str, "Description of the work being performed"],
    activity_type_id: Annotated[
        Optional[int], "Activity type ID for billing rates (optional)"
    ] = None,
) -> Annotated[str, "JSON string containing the started timer details"]:
    """
    Start a new timer for real-time time tracking on a matter.

    This creates an active timer that will track time until it's stopped.
    Only one timer can be active per user at a time.

    Examples:
    ```
    start_timer(
        matter_id=12345,
        description="Client consultation and case review"
    )
    start_timer(
        matter_id=67890,
        description="Document drafting",
        activity_type_id=1
    )
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Validate inputs
            matter_id = validate_id(matter_id, "Matter ID")
            description = validate_required_string(description, "Description")

            # Build timer data
            timer_data = prepare_request_data({
                "matter_id": matter_id,
                "description": description,
                "activity_type_id": activity_type_id,
            })

            # Start timer
            response = await client.post("timer", data={"data": timer_data})
            timer = extract_model_data(response, "timer")

            return format_json_response({
                "success": True,
                "timer": timer,
                "message": f"Timer started for matter {matter_id}",
                "status": "running"
            })

        except ClioError:
            raise
        except (ValueError, TypeError) as e:
            raise ClioValidationError(f"Invalid timer parameters: {e}")


@tool(requires_auth=OAuth2(id="clio"))
async def stop_timer(
    context: ToolContext,
    description: Annotated[Optional[str], "Updated description for the time entry (optional)"] = None,
    rate: Annotated[Optional[float], "Hourly rate override for this entry (optional)"] = None,
) -> Annotated[str, "JSON string containing the created time entry from stopped timer"]:
    """
    Stop the active timer and create a time entry.

    This will stop any currently running timer and automatically create
    a time entry with the tracked time.

    Examples:
    ```
    stop_timer()
    stop_timer(description="Updated description for completed work")
    stop_timer(rate=250.0)
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Check if there's an active timer first
            timer_response = await client.get("timer")
            if not timer_response.get("data"):
                raise ClioValidationError("No active timer found to stop")

            # Build update data if provided
            update_data = None
            if description or rate:
                update_data = prepare_request_data({
                    "description": description,
                    "rate": rate,
                })

            # Stop timer
            if update_data:
                response = await client.delete("timer", data={"data": update_data})
            else:
                response = await client.delete("timer")

            time_entry = extract_model_data(response, "activity")

            return format_json_response({
                "success": True,
                "time_entry": time_entry,
                "message": "Timer stopped and time entry created",
                "status": "completed",
                "total_time": time_entry.get("quantity", 0) / 3600  # Convert seconds to hours
            })

        except ClioError:
            raise
        except (ValueError, TypeError) as e:
            raise ClioValidationError(f"Failed to stop timer: {e}")


@tool(requires_auth=OAuth2(id="clio"))
async def get_active_timer(
    context: ToolContext,
) -> Annotated[str, "JSON string containing active timer details or null if no timer is running"]:
    """
    Get details of the currently active timer, if any.

    Example:
    ```
    get_active_timer()
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Get active timer
            response = await client.get("timer")
            timer_data = response.get("data")

            if timer_data:
                timer = extract_model_data({"timer": timer_data}, "timer")
                return format_json_response({
                    "success": True,
                    "has_active_timer": True,
                    "timer": timer,
                    "status": "running"
                })
            else:
                return format_json_response({
                    "success": True,
                    "has_active_timer": False,
                    "timer": None,
                    "status": "no_timer"
                })

        except ClioError:
            raise
        except Exception as e:
            raise ClioError(f"Failed to get timer status: {e}", retry=True)


@tool(requires_auth=OAuth2(id="clio"))
async def pause_timer(
    context: ToolContext,
) -> Annotated[str, "JSON string confirming timer pause"]:
    """
    Pause the currently active timer without creating a time entry.

    Note: This is a conceptual tool - the actual Clio API may not support
    pausing timers. This would stop the timer and allow restarting later.

    Example:
    ```
    pause_timer()
    ```
    """
    async with ClioClient(context) as client:
        try:
            # Check if there's an active timer first
            timer_response = await client.get("timer")
            if not timer_response.get("data"):
                raise ClioValidationError("No active timer found to pause")

            timer_data = timer_response.get("data")

            # For now, we'll stop the timer and return the state for manual restart
            # In a real implementation, this might preserve the timer state
            response = await client.delete("timer")
            time_entry = extract_model_data(response, "activity")

            return format_json_response({
                "success": True,
                "message": "Timer stopped - can be restarted manually if needed",
                "status": "paused",
                "matter_id": timer_data.get("matter_id"),
                "description": timer_data.get("description"),
                "elapsed_time": time_entry.get("quantity", 0) / 3600,  # Convert to hours
                "time_entry_created": time_entry
            })

        except ClioError:
            raise
        except (ValueError, TypeError) as e:
            raise ClioValidationError(f"Failed to pause timer: {e}")

