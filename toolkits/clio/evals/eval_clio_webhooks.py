"""LLM evaluation suite for Clio webhook management tools."""

import arcade_clio
from arcade_evals import EvalSuite, ExpectedToolCall, tool_eval
from arcade_tdk import ToolCatalog


@tool_eval()
def eval_clio_webhooks() -> EvalSuite:
    """Evaluation suite for Clio webhook management functionality."""

    # Create tool catalog
    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)

    # Create evaluation suite
    suite = EvalSuite(
        name="Clio Webhook Management",
        system_message="You are an assistant helping with legal practice management using Clio tools. Use the available Clio webhook tools to help users set up real-time notifications.",
        catalog=catalog,
    )

    # Test 1: Create webhook for contact events
    suite.add_case(
        name="Create contact webhook",
        user_message="Set up a webhook to notify us at https://myapp.com/webhooks/clio when contacts are created or updated",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_webhook,
                args={
                    "url": "https://myapp.com/webhooks/clio",
                    "events": ["contact"],
                    "description": "Webhook for contact events",
                },
            )
        ],
    )

    # Test 2: Create webhook for multiple events
    suite.add_case(
        name="Create multi-event webhook",
        user_message="Create a webhook at https://api.example.com/clio-events for contact, matter, and bill events with description 'Main integration webhook'",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_webhook,
                args={
                    "url": "https://api.example.com/clio-events",
                    "events": ["contact", "matter", "bill"],
                    "description": "Main integration webhook",
                },
            )
        ],
    )

    # Test 3: List all webhooks
    suite.add_case(
        name="List webhooks",
        user_message="Show me all configured webhooks in our system",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_webhooks,
                args={"limit": 50, "offset": 0},
            )
        ],
    )

    # Test 4: Get specific webhook details
    suite.add_case(
        name="Get webhook details",
        user_message="Get the details of webhook ID 12345",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_webhook,
                args={"webhook_id": 12345},
            )
        ],
    )

    # Test 5: Update webhook URL
    suite.add_case(
        name="Update webhook URL",
        user_message="Change webhook 12345 to use the new URL https://newserver.com/webhooks",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.update_webhook,
                args={
                    "webhook_id": 12345,
                    "url": "https://newserver.com/webhooks",
                },
            )
        ],
    )

    # Test 6: Update webhook events
    suite.add_case(
        name="Update webhook events",
        user_message="Modify webhook 12345 to only listen for contact and activity events",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.update_webhook,
                args={
                    "webhook_id": 12345,
                    "events": ["contact", "activity"],
                },
            )
        ],
    )

    # Test 7: Delete webhook
    suite.add_case(
        name="Delete webhook",
        user_message="Remove webhook 12345 from our system",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.delete_webhook,
                args={"webhook_id": 12345},
            )
        ],
    )

    # Test 8: Create activity-specific webhook
    suite.add_case(
        name="Activity tracking webhook",
        user_message="Set up a webhook for time entry and expense events at https://billing.mycompany.com/clio-activities",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_webhook,
                args={
                    "url": "https://billing.mycompany.com/clio-activities",
                    "events": ["activity"],
                    "description": "Billing system integration",
                },
            )
        ],
    )

    # Test 9: Update webhook description
    suite.add_case(
        name="Update webhook description",
        user_message="Update webhook 67890 description to 'Updated integration for new CRM system'",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.update_webhook,
                args={
                    "webhook_id": 67890,
                    "description": "Updated integration for new CRM system",
                },
            )
        ],
    )

    # Test 10: List webhooks with pagination
    suite.add_case(
        name="Paginated webhook list",
        user_message="Show me the first 10 webhooks in our system",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_webhooks,
                args={"limit": 10, "offset": 0},
            )
        ],
    )

    return suite


@tool_eval()
def eval_clio_webhook_scenarios() -> EvalSuite:
    """Evaluation suite for webhook integration scenarios."""

    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)

    suite = EvalSuite(
        name="Clio Webhook Integration Scenarios",
        system_message="You are an assistant helping with legal practice management using Clio tools. Use the available Clio webhook tools to help users set up real-time notifications.",
        catalog=catalog,
    )

    # Test 1: Complete webhook setup workflow
    suite.add_case(
        name="Complete webhook setup",
        user_message="Set up real-time notifications: create a webhook for all events at https://notifications.lawfirm.com/clio, then show me the webhook details to verify it was created correctly",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_webhook,
                args={
                    "url": "https://notifications.lawfirm.com/clio",
                    "events": ["contact", "matter", "bill", "activity"],
                    "description": "Real-time notifications for all events",
                },
            ),
            # Note: In real usage, the LLM would need to use the webhook ID from the previous response
        ],
    )

    # Test 2: Webhook maintenance workflow
    suite.add_case(
        name="Webhook maintenance",
        user_message="Check all our webhooks and show me their status",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_webhooks,
                args={"limit": 50, "offset": 0},
            )
        ],
    )

    # Test 3: Event-specific webhook setup
    suite.add_case(
        name="Matter-specific webhook",
        user_message="Create a webhook specifically for matter creation and updates to integrate with our case management system at https://cases.lawfirm.com/webhook",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_webhook,
                args={
                    "url": "https://cases.lawfirm.com/webhook",
                    "events": ["matter"],
                    "description": "Case management system integration",
                },
            )
        ],
    )

    # Test 4: Webhook URL validation workflow
    suite.add_case(
        name="Webhook troubleshooting",
        user_message="I need to troubleshoot webhook 99999 - show me its current configuration and then update it to use our backup server at https://backup.api.com/clio",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_webhook,
                args={"webhook_id": 99999},
            ),
            ExpectedToolCall(
                func=arcade_clio.update_webhook,
                args={
                    "webhook_id": 99999,
                    "url": "https://backup.api.com/clio",
                },
            ),
        ],
    )

    # Test 5: Clean up old webhooks
    suite.add_case(
        name="Webhook cleanup",
        user_message="Remove the old webhook 11111 that we no longer need",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.delete_webhook,
                args={"webhook_id": 11111},
            )
        ],
    )

    return suite