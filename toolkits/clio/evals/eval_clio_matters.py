"""LLM evaluation suite for Clio matter management tools."""

import arcade_clio
from arcade_evals import EvalSuite, ExpectedToolCall, tool_eval
from arcade_tdk import ToolCatalog


@tool_eval()
def eval_clio_matters() -> EvalSuite:
    """Evaluation suite for Clio matter management functionality."""

    # Create tool catalog
    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)

    # Create evaluation suite
    suite = EvalSuite(
        name="Clio Matter Management",
        catalog=catalog,
    )

    # Test 1: List open matters
    suite.add_case(
        name="List all open matters",
        user_message="Show me all open matters in our system",
        expected_tool_calls=[
            ExpectedToolCall(func=arcade_clio.list_matters, args={"status": "open"})
        ],
    )

    # Test 2: Create a new matter
    suite.add_case(
        name="Create personal injury matter",
        user_message="Create a new personal injury matter for client John Doe (ID: 12345). The case is Smith vs. Acme Corp, billable hourly, opening today.",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_matter,
                args={
                    "description": "Smith vs. Acme Corp",
                    "client_id": 12345,
                    "billable": True,
                    "billing_method": "hourly",
                    "open_date": "{{TODAYS_DATE}}",  # Template will be replaced
                },
            )
        ],
    )

    # Test 3: Update matter information
    suite.add_case(
        name="Update matter description",
        user_message="Update matter 67890 to change the description to 'Johnson vs. XYZ Corp - Personal Injury Claim'",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.update_matter,
                args={
                    "matter_id": 67890,
                    "description": "Johnson vs. XYZ Corp - Personal Injury Claim",
                },
            )
        ],
    )

    # Test 4: Close a matter
    suite.add_case(
        name="Close completed matter",
        user_message="Close matter 67890 as of January 31st, 2024",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.close_matter, args={"matter_id": 67890, "close_date": "2024-01-31"}
            )
        ],
    )

    # Test 5: Complex multi-step workflow
    suite.add_case(
        name="Complex matter workflow",
        user_message="For matter 67890, I need to: 1) Add contact 99999 as the responsible attorney, 2) Get all time entries for this matter, 3) List all participants",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.add_matter_participant,
                args={"matter_id": 67890, "contact_id": 99999, "role": "responsible_attorney"},
            ),
            ExpectedToolCall(
                func=arcade_clio.get_matter_activities,
                args={"matter_id": 67890, "activity_type": "TimeEntry"},
            ),
            ExpectedToolCall(
                func=arcade_clio.get_matter, args={"matter_id": 67890, "include_extra_data": True}
            ),
        ],
    )

    # Test 6: Filter matters by client
    suite.add_case(
        name="Get matters for specific client",
        user_message="Show me all matters for client ID 12345",
        expected_tool_calls=[
            ExpectedToolCall(func=arcade_clio.list_matters, args={"client_id": 12345})
        ],
    )

    # Test 7: Legal terminology understanding
    suite.add_case(
        name="Legal terminology - retainer",
        user_message="Create a new retainer agreement matter for the Smith family (client ID 55555), non-billable",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_matter,
                args={
                    "description": "Smith family retainer agreement",
                    "client_id": 55555,
                    "billable": False,
                },
            )
        ],
    )

    # Test 8: Date handling variations
    suite.add_case(
        name="Various date formats",
        user_message="Get all matters opened between January 1, 2024 and March 31, 2024",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_matters,
                args={"open_date_from": "2024-01-01", "open_date_to": "2024-03-31"},
            )
        ],
    )

    # Test 9: Pagination handling
    suite.add_case(
        name="Paginated matter listing",
        user_message="Show me the next 25 matters after the first 100",
        expected_tool_calls=[
            ExpectedToolCall(func=arcade_clio.list_matters, args={"limit": 25, "offset": 100})
        ],
    )

    # Test 10: Remove participant
    suite.add_case(
        name="Remove matter participant",
        user_message="Remove participant 55555 from matter 67890",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.remove_matter_participant,
                args={"matter_id": 67890, "participant_id": 55555},
            )
        ],
    )

    # Test 11: Status-based filtering
    suite.add_case(
        name="Filter by multiple criteria",
        user_message="Find all closed billable matters for client 12345",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_matters,
                args={"status": "closed", "billable": True, "client_id": 12345},
            )
        ],
    )

    # Test 12: Get specific matter details
    suite.add_case(
        name="Get detailed matter information",
        user_message="Get all the details for matter 67890 including participant information",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_matter, args={"matter_id": 67890, "include_extra_data": True}
            )
        ],
    )

    # Test 13: Legal workflow - case setup
    suite.add_case(
        name="Complete case setup workflow",
        user_message="Set up a new workers compensation case: Create matter for John Smith (client 12345), add attorney Sarah Johnson (ID 11111) as responsible attorney, matter is billable at standard hourly rate",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_matter,
                args={
                    "description": "John Smith workers compensation case",
                    "client_id": 12345,
                    "billable": True,
                    "billing_method": "hourly",
                },
            ),
            ExpectedToolCall(
                func=arcade_clio.add_matter_participant,
                args={
                    "matter_id": "{{MATTER_ID_FROM_PREVIOUS}}",
                    "contact_id": 11111,
                    "role": "responsible_attorney",
                },
            ),
        ],
    )

    # Test 14: Activities retrieval with filtering
    suite.add_case(
        name="Get matter expenses",
        user_message="Show me all expenses logged for matter 67890",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_matter_activities,
                args={"matter_id": 67890, "activity_type": "ExpenseEntry"},
            )
        ],
    )

    # Test 15: Matter status understanding
    suite.add_case(
        name="Matter status variations",
        user_message="List all pending matters that need attention",
        expected_tool_calls=[
            ExpectedToolCall(func=arcade_clio.list_matters, args={"status": "pending"})
        ],
    )

    return suite


@tool_eval()
def eval_clio_matter_edge_cases() -> EvalSuite:
    """Evaluation suite for edge cases and error scenarios."""

    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)

    suite = EvalSuite(
        name="Clio Matter Edge Cases",
        catalog=catalog,
    )

    # Test 1: Ambiguous participant role
    suite.add_case(
        name="Ambiguous attorney role",
        user_message="Add the attorney who originated this case (contact 11111) to matter 67890",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.add_matter_participant,
                args={"matter_id": 67890, "contact_id": 11111, "role": "originating_attorney"},
            )
        ],
    )

    # Test 2: Date format variations
    suite.add_case(
        name="Natural language date",
        user_message="Close matter 67890 as of today",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.close_matter,
                args={"matter_id": 67890, "close_date": "{{TODAYS_DATE}}"},
            )
        ],
    )

    # Test 3: Billing method inference
    suite.add_case(
        name="Infer billing method",
        user_message="Create a new contingency fee case for client 12345 regarding a car accident claim",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_matter,
                args={
                    "description": "Car accident claim",
                    "client_id": 12345,
                    "billable": True,
                    "billing_method": "contingency",
                },
            )
        ],
    )

    # Test 4: Multiple matters handling
    suite.add_case(
        name="Batch matter operations",
        user_message="Get the details for matters 67890, 67891, and 67892",
        expected_tool_calls=[
            ExpectedToolCall(func=arcade_clio.get_matter, args={"matter_id": 67890}),
            ExpectedToolCall(func=arcade_clio.get_matter, args={"matter_id": 67891}),
            ExpectedToolCall(func=arcade_clio.get_matter, args={"matter_id": 67892}),
        ],
    )

    # Test 5: Legal jargon understanding
    suite.add_case(
        name="Legal terminology - pro bono",
        user_message="Create a pro bono matter for the homeless shelter organization (client 99999)",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_matter,
                args={
                    "description": "Pro bono matter for homeless shelter organization",
                    "client_id": 99999,
                    "billable": False,
                },
            )
        ],
    )

    return suite
