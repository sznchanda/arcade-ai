"""Evaluation suite for Clio activity management tools."""

from arcade_evals import EvalSuite, EvalCase, ExpectedToolCall, tool_eval
from arcade_tdk import ToolCatalog

import arcade_clio.tools as clio_tools


@tool_eval()
def eval_clio_activities() -> EvalSuite:
    """Evaluation suite for Clio unified activity management functionality."""
    
    catalog = ToolCatalog()
    catalog.add_module(clio_tools)
    
    suite = EvalSuite(
        name="Clio Activity Management",
        catalog=catalog,
    )

    # Activity listing and filtering
    suite.add_case(
        EvalCase(
            name="list_all_activities",
            user_message="Show me all time entries and expenses in the system",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.list_activities,
                    args={}
                )
            ]
        )
    )

    suite.add_case(
        EvalCase(
            name="list_activities_by_matter",
            user_message="Get all activities for matter ID 12345",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.list_activities,
                    args={"matter_id": "12345"}
                )
            ]
        )
    )

    suite.add_case(
        EvalCase(
            name="list_time_entries_only",
            user_message="Show me only time entries from the last month",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.list_activities,
                    args={"type": "TimeEntry"}
                )
            ]
        )
    )

    suite.add_case(
        EvalCase(
            name="list_unbilled_activities",
            user_message="Find all unbilled activities that need to be invoiced",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.list_activities,
                    args={"billed": False}
                )
            ]
        )
    )

    # Activity retrieval
    suite.add_case(
        EvalCase(
            name="get_specific_activity",
            user_message="Get details for activity ID 567",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.get_activity,
                    args={"activity_id": "567"}
                )
            ]
        )
    )

    # Activity deletion
    suite.add_case(
        EvalCase(
            name="delete_activity",
            user_message="Delete activity ID 999 from the system",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.delete_activity,
                    args={"activity_id": "999"}
                )
            ]
        )
    )

    # Date range filtering
    suite.add_case(
        EvalCase(
            name="activities_date_range",
            user_message="Show me all activities from January 1st to January 31st, 2024",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.list_activities,
                    args={
                        "date_from": "2024-01-01",
                        "date_to": "2024-01-31"
                    }
                )
            ]
        )
    )

    # User-specific activities
    suite.add_case(
        EvalCase(
            name="activities_by_user",
            user_message="Get all activities by user ID 456",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.list_activities,
                    args={"user_id": "456"}
                )
            ]
        )
    )

    # Complex filtering
    suite.add_case(
        EvalCase(
            name="billable_time_entries_by_matter",
            user_message="Find all billable time entries for matter 789 that haven't been billed yet",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.list_activities,
                    args={
                        "matter_id": "789",
                        "type": "TimeEntry",
                        "billable": True,
                        "billed": False
                    }
                )
            ]
        )
    )

    # Expense-specific queries
    suite.add_case(
        EvalCase(
            name="expense_entries_only",
            user_message="Show me all expense entries from this quarter",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.list_activities,
                    args={"type": "ExpenseEntry"}
                )
            ]
        )
    )

    return suite