"""Evaluation suite for Clio activity management tools."""

import arcade_clio
from arcade_evals import EvalSuite, ExpectedToolCall, tool_eval
from arcade_tdk import ToolCatalog


@tool_eval()
def eval_clio_activities() -> EvalSuite:
    """Evaluation suite for Clio unified activity management functionality."""
    
    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)
    
    suite = EvalSuite(
        name="Clio Activity Management",
        system_message="You are an assistant helping with legal practice management using Clio tools. Use the available Clio activity management tools to help users with their requests.",
        catalog=catalog,
    )

    # Activity listing and filtering
    suite.add_case(
        name="list_all_activities",
        user_message="Show me all time entries and expenses in the system",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={}
            )
        ]
    )

    suite.add_case(
        name="list_activities_by_matter",
        user_message="Get all activities for matter ID 12345",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={"matter_id": 12345}
            )
        ]
    )

    suite.add_case(
        name="list_time_entries_only",
        user_message="Show me only time entries from the last month",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={"activity_type": "TimeEntry"}
            )
        ]
    )

    suite.add_case(
        name="list_unbilled_activities",
        user_message="Find all unbilled activities that need to be invoiced",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={"billed": False}
            )
        ]
    )

    # Activity retrieval
    suite.add_case(
        name="get_specific_activity",
        user_message="Get details for activity ID 567",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_activity,
                args={"activity_id": 567}
            )
        ]
    )

    # Activity deletion
    suite.add_case(
        name="delete_activity",
        user_message="Delete activity ID 999 from the system",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.delete_activity,
                args={"activity_id": 999}
            )
        ]
    )

    # Date range filtering
    suite.add_case(
        name="activities_date_range",
        user_message="Show me all activities from January 1st to January 31st, 2024",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={
                    "date_from": "2024-01-01",
                    "date_to": "2024-01-31"
                }
            )
        ]
    )

    # User-specific activities
    suite.add_case(
        name="activities_by_user",
        user_message="Get all activities by user ID 456",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={"user_id": 456}
            )
        ]
    )

    # Complex filtering
    suite.add_case(
        name="billable_time_entries_by_matter",
        user_message="Find all billable time entries for matter 789 that haven't been billed yet",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={
                    "matter_id": 789,
                    "activity_type": "TimeEntry",
                    "billable": True,
                    "billed": False
                }
            )
        ]
    )

    # Expense-specific queries
    suite.add_case(
        name="expense_entries_only",
        user_message="Show me all expense entries from this quarter",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={"activity_type": "ExpenseEntry"}
            )
        ]
    )

    # Test 13: Activities with date range and pagination
    suite.add_case(
        name="activities_with_date_and_pagination",
        user_message="Show me the next 25 activities (skip first 50) from March 2024",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={
                    "date_from": "2024-03-01",
                    "date_to": "2024-03-31",
                    "limit": 25,
                    "offset": 50
                }
            )
        ]
    )

    # Test 14: Activities with field selection
    suite.add_case(
        name="activities_with_field_selection",
        user_message="Get all activities for matter 12345 but only return their ID, date, description, and hours fields",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={
                    "matter_id": 12345,
                    "fields": "id,date,description,hours"
                }
            )
        ]
    )

    # Test 15: Complex multi-filter query
    suite.add_case(
        name="complex_activity_filtering",
        user_message="Find all billable time entries by user 123 for matter 789 that are not yet billed, from January 2024",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={
                    "matter_id": 789,
                    "user_id": 123,
                    "activity_type": "TimeEntry",
                    "billable": True,
                    "billed": False,
                    "date_from": "2024-01-01",
                    "date_to": "2024-01-31"
                }
            )
        ]
    )

    return suite


@tool_eval()
def eval_clio_activity_edge_cases() -> EvalSuite:
    """Evaluation suite for activity management edge cases and error scenarios."""
    
    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)
    
    suite = EvalSuite(
        name="Clio Activity Management Edge Cases",
        system_message="You are an assistant helping with legal practice management using Clio tools. Use the available Clio activity management tools to help users with their requests.",
        catalog=catalog,
    )

    # Test 1: Very large date range
    suite.add_case(
        name="large_date_range_query",
        user_message="Get all activities from the past 5 years (2019 to 2024)",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={
                    "date_from": "2019-01-01",
                    "date_to": "2024-12-31"
                }
            )
        ]
    )

    # Test 2: Invalid activity ID
    suite.add_case(
        name="invalid_activity_id",
        user_message="Try to get details for activity ID -1 (invalid)",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_activity,
                args={"activity_id": -1}
            )
        ]
    )

    # Test 3: Delete non-existent activity
    suite.add_case(
        name="delete_nonexistent_activity",
        user_message="Delete activity ID 99999999 that doesn't exist",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.delete_activity,
                args={"activity_id": 99999999}
            )
        ]
    )

    # Test 4: Empty filters
    suite.add_case(
        name="empty_filter_handling",
        user_message="List all activities without any filters - just the default view",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={}
            )
        ]
    )

    # Test 5: Maximum pagination
    suite.add_case(
        name="maximum_pagination",
        user_message="Get activities starting at position 1000 with limit 200",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={
                    "limit": 200,
                    "offset": 1000
                }
            )
        ]
    )

    # Test 6: Future date filtering
    suite.add_case(
        name="future_date_filtering",
        user_message="Find activities scheduled for next year (2025)",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={
                    "date_from": "2025-01-01",
                    "date_to": "2025-12-31"
                }
            )
        ]
    )

    # Test 7: Contradictory filters
    suite.add_case(
        name="contradictory_filters",
        user_message="Find activities that are both billed and unbilled (contradictory request)",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_activities,
                args={
                    "billed": True
                }
            )
        ]
    )

    return suite