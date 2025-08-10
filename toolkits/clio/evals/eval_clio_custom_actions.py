"""LLM evaluation suite for Clio custom actions (UI customization) tools."""

import arcade_clio
from arcade_evals import EvalSuite, ExpectedToolCall, tool_eval
from arcade_tdk import ToolCatalog


@tool_eval()
def eval_clio_custom_actions() -> EvalSuite:
    """Evaluation suite for Clio custom actions functionality."""

    # Create tool catalog
    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)

    # Create evaluation suite
    suite = EvalSuite(
        name="Clio Custom Actions Management",
        catalog=catalog,
    )

    # Test 1: Create custom action for external CRM integration
    suite.add_case(
        name="Create CRM integration action",
        user_message="Add a custom action called 'Export to CRM' that appears on contact pages and sends them to https://crm.lawfirm.com/import?clio_contact_id={contact_id}",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_custom_action,
                args={
                    "label": "Export to CRM",
                    "target_url": "https://crm.lawfirm.com/import?clio_contact_id={contact_id}",
                    "ui_reference": "contacts/show",
                    "description": "Export contact to external CRM system",
                },
            )
        ],
    )

    # Test 2: Create custom action for matter integration
    suite.add_case(
        name="Create matter integration action",
        user_message="Create a custom action 'Open in Case Manager' for matter pages that links to https://cases.mylaw.com/matter/{matter_id}",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_custom_action,
                args={
                    "label": "Open in Case Manager",
                    "target_url": "https://cases.mylaw.com/matter/{matter_id}",
                    "ui_reference": "matters/show",
                    "description": "Open matter in external case management system",
                },
            )
        ],
    )

    # Test 3: List all custom actions
    suite.add_case(
        name="List custom actions",
        user_message="Show me all the custom actions configured in our Clio system",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_custom_actions,
                args={"limit": 50, "offset": 0},
            )
        ],
    )

    # Test 4: Get specific custom action details
    suite.add_case(
        name="Get custom action details",
        user_message="Get the details for custom action ID 12345",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_custom_action,
                args={"custom_action_id": 12345},
            )
        ],
    )

    # Test 5: Update custom action label
    suite.add_case(
        name="Update custom action label",
        user_message="Change the label of custom action 12345 to 'Send to External System'",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.update_custom_action,
                args={
                    "custom_action_id": 12345,
                    "label": "Send to External System",
                },
            )
        ],
    )

    # Test 6: Update custom action URL
    suite.add_case(
        name="Update custom action URL",
        user_message="Update custom action 67890 to use the new URL https://api.newserver.com/clio/matters/{matter_id}",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.update_custom_action,
                args={
                    "custom_action_id": 67890,
                    "target_url": "https://api.newserver.com/clio/matters/{matter_id}",
                },
            )
        ],
    )

    # Test 7: Update custom action description
    suite.add_case(
        name="Update custom action description",
        user_message="Update the description of custom action 11111 to 'Updated integration with new API endpoint'",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.update_custom_action,
                args={
                    "custom_action_id": 11111,
                    "description": "Updated integration with new API endpoint",
                },
            )
        ],
    )

    # Test 8: Delete custom action
    suite.add_case(
        name="Delete custom action",
        user_message="Remove custom action 99999 from our system as it's no longer needed",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.delete_custom_action,
                args={"custom_action_id": 99999},
            )
        ],
    )

    # Test 9: Test custom action URL template
    suite.add_case(
        name="Test URL template",
        user_message="Test this URL template to see how it would work: https://app.example.com/matters/{matter_id}/summary with matter ID 12345",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.test_custom_action_url,
                args={
                    "target_url": "https://app.example.com/matters/{matter_id}/summary",
                    "matter_id": 12345,
                },
            )
        ],
    )

    # Test 10: Test URL template with contact
    suite.add_case(
        name="Test contact URL template",
        user_message="Test how this URL would resolve: https://crm.example.com/contacts/{contact_id}?source=clio with contact ID 67890",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.test_custom_action_url,
                args={
                    "target_url": "https://crm.example.com/contacts/{contact_id}?source=clio",
                    "contact_id": 67890,
                },
            )
        ],
    )

    # Test 11: Create billing integration action
    suite.add_case(
        name="Create billing integration",
        user_message="Add a custom action 'Export to QuickBooks' on bill pages that connects to https://qb.integration.com/import-bill/{bill_id}",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_custom_action,
                args={
                    "label": "Export to QuickBooks",
                    "target_url": "https://qb.integration.com/import-bill/{bill_id}",
                    "ui_reference": "bills/show",
                    "description": "Export bill to QuickBooks accounting system",
                },
            )
        ],
    )

    # Test 12: Create document integration action
    suite.add_case(
        name="Create document integration",
        user_message="Create a 'Send to DocuSign' action for document pages using URL https://docusign.integration.com/send/{document_id}",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_custom_action,
                args={
                    "label": "Send to DocuSign",
                    "target_url": "https://docusign.integration.com/send/{document_id}",
                    "ui_reference": "documents/show",
                    "description": "Send document for e-signature via DocuSign",
                },
            )
        ],
    )

    return suite


@tool_eval()
def eval_clio_custom_action_workflows() -> EvalSuite:
    """Evaluation suite for custom action workflow scenarios."""

    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)

    suite = EvalSuite(
        name="Clio Custom Action Workflows",
        catalog=catalog,
    )

    # Test 1: Complete custom action setup workflow
    suite.add_case(
        name="Complete action setup",
        user_message="Set up a complete integration: create a custom action for exporting contacts to our CRM, test the URL template, then show me the action details",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_custom_action,
                args={
                    "label": "Export to CRM",
                    "target_url": "https://crm.mylaw.com/contacts/import/{contact_id}",
                    "ui_reference": "contacts/show",
                    "description": "Export contact to our CRM system",
                },
            ),
            ExpectedToolCall(
                func=arcade_clio.test_custom_action_url,
                args={
                    "target_url": "https://crm.mylaw.com/contacts/import/{contact_id}",
                    "contact_id": 12345,
                },
            ),
            # Note: In practice, would need to use the ID from the create response
        ],
    )

    # Test 2: Custom action maintenance workflow
    suite.add_case(
        name="Action maintenance",
        user_message="Review all our custom actions and their configurations",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_custom_actions,
                args={"limit": 50, "offset": 0},
            )
        ],
    )

    # Test 3: Update existing integration workflow
    suite.add_case(
        name="Update integration endpoint",
        user_message="Our API endpoint changed - update custom action 55555 to use the new URL https://newapi.mycompany.com/clio/contacts/{contact_id} and update the description",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.update_custom_action,
                args={
                    "custom_action_id": 55555,
                    "target_url": "https://newapi.mycompany.com/clio/contacts/{contact_id}",
                    "description": "Updated integration with new API endpoint",
                },
            )
        ],
    )

    # Test 4: Custom action troubleshooting
    suite.add_case(
        name="Troubleshoot custom action",
        user_message="I need to troubleshoot custom action 77777 - show me its current configuration and test its URL template with sample data",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_custom_action,
                args={"custom_action_id": 77777},
            ),
            # In practice, would extract URL from response for testing
        ],
    )

    # Test 5: Integration cleanup workflow
    suite.add_case(
        name="Clean up old integrations",
        user_message="Remove the old custom action 33333 that we no longer use",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.delete_custom_action,
                args={"custom_action_id": 33333},
            )
        ],
    )

    # Test 6: Multi-system integration setup
    suite.add_case(
        name="Multi-system integration",
        user_message="Set up integrations for our workflow: create actions for CRM, accounting, and document management systems",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_custom_action,
                args={
                    "label": "Export to CRM",
                    "target_url": "https://crm.law.com/import/{contact_id}",
                    "ui_reference": "contacts/show",
                    "description": "Export contact to CRM system",
                },
            ),
            ExpectedToolCall(
                func=arcade_clio.create_custom_action,
                args={
                    "label": "Send to Accounting",
                    "target_url": "https://accounting.law.com/bills/{bill_id}",
                    "ui_reference": "bills/show", 
                    "description": "Send bill to accounting system",
                },
            ),
            ExpectedToolCall(
                func=arcade_clio.create_custom_action,
                args={
                    "label": "Archive Document",
                    "target_url": "https://archive.law.com/store/{document_id}",
                    "ui_reference": "documents/show",
                    "description": "Archive document in external system",
                },
            ),
        ],
    )

    # Test 7: URL template validation workflow
    suite.add_case(
        name="URL template validation",
        user_message="Before deploying this integration, test the URL template https://api.partner.com/sync/{contact_id}/{matter_id} with contact 11111 and matter 22222",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.test_custom_action_url,
                args={
                    "target_url": "https://api.partner.com/sync/{contact_id}/{matter_id}",
                    "contact_id": 11111,
                    "matter_id": 22222,
                },
            )
        ],
    )

    return suite