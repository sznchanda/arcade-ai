"""LLM evaluation suite for Clio timer API integration tools."""

import arcade_clio
from arcade_evals import EvalSuite, ExpectedToolCall, tool_eval
from arcade_tdk import ToolCatalog


@tool_eval()
def eval_clio_timers() -> EvalSuite:
    """Evaluation suite for Clio timer functionality."""

    # Create tool catalog
    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)

    # Create evaluation suite
    suite = EvalSuite(
        name="Clio Timer Management",
        system_message="You are an assistant helping with legal practice management using Clio tools. Use the available Clio timer tools to help users track their time.",
        catalog=catalog,
    )

    # Test 1: Start timer for client consultation
    suite.add_case(
        name="Start client consultation timer",
        user_message="Start a timer for matter 67890 for client consultation and case review",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.start_timer,
                args={
                    "matter_id": 67890,
                    "description": "Client consultation and case review",
                },
            )
        ],
    )

    # Test 2: Start timer with activity type
    suite.add_case(
        name="Start timer with activity type",
        user_message="Begin timing document drafting work for matter 12345 using activity type 5",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.start_timer,
                args={
                    "matter_id": 12345,
                    "description": "Document drafting",
                    "activity_type_id": 5,
                },
            )
        ],
    )

    # Test 3: Check active timer
    suite.add_case(
        name="Check active timer",
        user_message="Is there a timer currently running? Show me the current timer status",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_active_timer,
                args={},
            )
        ],
    )

    # Test 4: Stop timer with default settings
    suite.add_case(
        name="Stop current timer",
        user_message="Stop the current timer and create a time entry",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.stop_timer,
                args={},
            )
        ],
    )

    # Test 5: Stop timer with updated description
    suite.add_case(
        name="Stop timer with new description",
        user_message="Stop the timer and update the description to 'Completed contract review and client meeting'",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.stop_timer,
                args={
                    "description": "Completed contract review and client meeting",
                },
            )
        ],
    )

    # Test 6: Stop timer with custom rate
    suite.add_case(
        name="Stop timer with custom rate",
        user_message="Stop the timer and apply a rate of $350 per hour for this entry",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.stop_timer,
                args={
                    "rate": 350.0,
                },
            )
        ],
    )

    # Test 7: Stop timer with both description and rate
    suite.add_case(
        name="Stop timer with description and rate",
        user_message="Stop the current timer, set the description to 'Senior partner deposition preparation' and rate to $500/hour",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.stop_timer,
                args={
                    "description": "Senior partner deposition preparation",
                    "rate": 500.0,
                },
            )
        ],
    )

    # Test 8: Pause timer
    suite.add_case(
        name="Pause timer",
        user_message="Pause the current timer - I need to take a break",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.pause_timer,
                args={},
            )
        ],
    )

    # Test 9: Start timer for research work
    suite.add_case(
        name="Start legal research timer",
        user_message="Start tracking time for legal research on precedent cases for matter 99888",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.start_timer,
                args={
                    "matter_id": 99888,
                    "description": "Legal research on precedent cases",
                },
            )
        ],
    )

    # Test 10: Check timer status before starting new one
    suite.add_case(
        name="Check before starting new timer",
        user_message="Check if I have any active timer before starting new work on matter 55555",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_active_timer,
                args={},
            )
        ],
    )

    return suite


@tool_eval()
def eval_clio_timer_workflows() -> EvalSuite:
    """Evaluation suite for timer workflow scenarios."""

    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)

    suite = EvalSuite(
        name="Clio Timer Workflows",
        system_message="You are an assistant helping with legal practice management using Clio tools. Use the available Clio timer tools to help users track their time.",
        catalog=catalog,
    )

    # Test 1: Full timer workflow
    suite.add_case(
        name="Complete timer workflow",
        user_message="I'm starting work on matter 77777 for contract negotiation. Start the timer, then when I'm done, stop it and create the time entry",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.start_timer,
                args={
                    "matter_id": 77777,
                    "description": "Contract negotiation",
                },
            )
            # Note: In real usage, there would be a time gap, then stop_timer would be called
        ],
    )

    # Test 2: Timer interruption workflow
    suite.add_case(
        name="Timer interruption handling",
        user_message="I need to pause my current timer for an urgent call, then I'll resume later",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.pause_timer,
                args={},
            )
        ],
    )

    # Test 3: Timer status check workflow
    suite.add_case(
        name="Timer status monitoring",
        user_message="Show me what timer is currently running so I can track my billable hours",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_active_timer,
                args={},
            )
        ],
    )

    # Test 4: Task switching workflow
    suite.add_case(
        name="Task switching with timers",
        user_message="I need to switch from my current task to urgent work on matter 11111 for motion filing - handle the timer transition",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_active_timer,
                args={},
            ),
            # In practice, this would be followed by stop_timer, then start_timer for new matter
        ],
    )

    # Test 5: End of day timer cleanup
    suite.add_case(
        name="End of day timer cleanup",
        user_message="I'm done for the day - check if I have any running timers and stop them",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_active_timer,
                args={},
            )
        ],
    )

    # Test 6: Detailed timer with specific activity
    suite.add_case(
        name="Specific activity timer",
        user_message="Start timing my work on matter 33333 for court filing preparation, use activity type 8 for court-related work",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.start_timer,
                args={
                    "matter_id": 33333,
                    "description": "Court filing preparation",
                    "activity_type_id": 8,
                },
            )
        ],
    )

    # Test 7: Emergency timer stop
    suite.add_case(
        name="Emergency timer stop",
        user_message="I need to immediately stop my timer and record the time with a note that it was interrupted for an emergency",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.stop_timer,
                args={
                    "description": "Work interrupted due to emergency",
                },
            )
        ],
    )

    return suite
