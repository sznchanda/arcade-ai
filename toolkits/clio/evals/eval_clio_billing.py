"""LLM evaluation suite for Clio billing and time tracking tools."""

from arcade_evals import EvalSuite, ExpectedToolCall, tool_eval
from arcade_tdk import ToolCatalog

import arcade_clio


@tool_eval()
def eval_clio_billing() -> EvalSuite:
    """Evaluation suite for Clio billing and time tracking functionality."""
    
    # Create tool catalog
    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)
    
    # Create evaluation suite
    suite = EvalSuite(
        name="Clio Billing and Time Tracking",
        catalog=catalog,
    )
    
    # Test 1: Log time entry
    suite.add_case(
        name="Log billable time",
        user_message="Log 2.5 hours for matter 67890 today for contract review and negotiation",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_time_entry,
                args={
                    "matter_id": 67890,
                    "hours": 2.5,
                    "date": "{{TODAYS_DATE}}",
                    "description": "Contract review and negotiation"
                }
            )
        ]
    )
    
    # Test 2: Log time with specific rate
    suite.add_case(
        name="Log time with custom rate",
        user_message="Record 3 hours at $450/hour for senior partner work on matter 67890 on January 15, 2024",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_time_entry,
                args={
                    "matter_id": 67890,
                    "hours": 3.0,
                    "date": "2024-01-15",
                    "description": "Senior partner work",
                    "rate": 450.0
                }
            )
        ]
    )
    
    # Test 3: Legal billing increments
    suite.add_case(
        name="Six-minute billing increment",
        user_message="Bill 15 minutes (0.25 hours) for a quick client phone call on matter 67890",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_time_entry,
                args={
                    "matter_id": 67890,
                    "hours": 0.25,
                    "date": "{{TODAYS_DATE}}",
                    "description": "Quick client phone call"
                }
            )
        ]
    )
    
    # Test 4: Create expense
    suite.add_case(
        name="Log filing fees expense",
        user_message="Add an expense of $125 for court filing fees paid to County Clerk for matter 67890 on January 20, 2024",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_expense,
                args={
                    "matter_id": 67890,
                    "amount": 125.0,
                    "date": "2024-01-20",
                    "description": "Court filing fees",
                    "vendor": "County Clerk"
                }
            )
        ]
    )
    
    # Test 5: Update time entry
    suite.add_case(
        name="Correct time entry hours",
        user_message="Update time entry 99999 to change the hours from 2.5 to 3.0 and update the description to 'Deposition preparation and attendance'",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.update_time_entry,
                args={
                    "time_entry_id": 99999,
                    "hours": 3.0,
                    "description": "Deposition preparation and attendance"
                }
            )
        ]
    )
    
    # Test 6: Get unbilled time entries
    suite.add_case(
        name="Review unbilled time",
        user_message="Show me all unbilled time entries for matter 67890",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_time_entries,
                args={
                    "matter_id": 67890,
                    "billed": False
                }
            )
        ]
    )
    
    # Test 7: Get time entries by date range
    suite.add_case(
        name="Time entries for date range",
        user_message="Get all time entries for matter 67890 between January 1 and January 31, 2024",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_time_entries,
                args={
                    "matter_id": 67890,
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31"
                }
            )
        ]
    )
    
    # Test 8: Create bill
    suite.add_case(
        name="Generate invoice",
        user_message="Create a bill for matter 67890 including all unbilled time and expenses, issued today, due in 30 days",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_bill,
                args={
                    "matter_id": 67890,
                    "include_unbilled_time": True,
                    "include_unbilled_expenses": True,
                    "issued_date": "{{TODAYS_DATE}}",
                    "due_date": "{{DATE_30_DAYS_FROM_NOW}}"
                }
            )
        ]
    )
    
    # Test 9: Get expenses with vendor filter
    suite.add_case(
        name="Filter expenses by vendor",
        user_message="Show all expenses from FedEx for matter 67890",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_expenses,
                args={
                    "matter_id": 67890,
                    "vendor": "FedEx"
                }
            )
        ]
    )
    
    # Test 10: Complex billing workflow
    suite.add_case(
        name="Complete billing workflow",
        user_message="For matter 67890: 1) Log 1.5 hours for document review, 2) Add $50 copying expense, 3) Generate a bill with all unbilled items",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_time_entry,
                args={
                    "matter_id": 67890,
                    "hours": 1.5,
                    "date": "{{TODAYS_DATE}}",
                    "description": "Document review"
                }
            ),
            ExpectedToolCall(
                func=arcade_clio.create_expense,
                args={
                    "matter_id": 67890,
                    "amount": 50.0,
                    "date": "{{TODAYS_DATE}}",
                    "description": "Copying expense"
                }
            ),
            ExpectedToolCall(
                func=arcade_clio.create_bill,
                args={
                    "matter_id": 67890,
                    "include_unbilled_time": True,
                    "include_unbilled_expenses": True
                }
            )
        ]
    )
    
    # Test 11: Get bills by status
    suite.add_case(
        name="Review sent bills",
        user_message="Show me all bills that have been sent but not paid for matter 67890",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_bills,
                args={
                    "matter_id": 67890,
                    "state": "sent"
                }
            )
        ]
    )
    
    # Test 12: Time entry with activity type
    suite.add_case(
        name="Log research time",
        user_message="Record 4 hours of legal research for matter 67890 with detailed notes about case law review",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_time_entry,
                args={
                    "matter_id": 67890,
                    "hours": 4.0,
                    "date": "{{TODAYS_DATE}}",
                    "description": "Legal research - case law review",
                    "note": "Detailed notes about case law review"
                }
            )
        ]
    )
    
    # Test 13: Expense categories
    suite.add_case(
        name="Categorized expense",
        user_message="Add a $75 expert witness fee expense for Dr. Smith's consultation on matter 67890, categorize as 'Expert Fees'",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_expense,
                args={
                    "matter_id": 67890,
                    "amount": 75.0,
                    "date": "{{TODAYS_DATE}}",
                    "description": "Expert witness fee - Dr. Smith consultation",
                    "vendor": "Dr. Smith",
                    "category": "Expert Fees"
                }
            )
        ]
    )
    
    # Test 14: Detailed bill parameters
    suite.add_case(
        name="Bill with specific parameters",
        user_message="Generate a draft bill for matter 67890 with a 10% discount, include time entries only (no expenses)",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_bill,
                args={
                    "matter_id": 67890,
                    "include_unbilled_time": True,
                    "include_unbilled_expenses": False,
                    "discount_percentage": 10.0,
                    "state": "draft"
                }
            )
        ]
    )
    
    # Test 15: Time tracking patterns
    suite.add_case(
        name="Common legal tasks",
        user_message="Log 0.1 hours for reviewing and responding to client email on matter 67890",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_time_entry,
                args={
                    "matter_id": 67890,
                    "hours": 0.1,
                    "date": "{{TODAYS_DATE}}",
                    "description": "Reviewing and responding to client email"
                }
            )
        ]
    )
    
    return suite


@tool_eval()
def eval_clio_billing_edge_cases() -> EvalSuite:
    """Evaluation suite for billing edge cases and complex scenarios."""
    
    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)
    
    suite = EvalSuite(
        name="Clio Billing Edge Cases",
        catalog=catalog,
    )
    
    # Test 1: Natural language time conversion
    suite.add_case(
        name="Convert minutes to hours",
        user_message="Bill 90 minutes of court appearance time for matter 67890",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_time_entry,
                args={
                    "matter_id": 67890,
                    "hours": 1.5,
                    "date": "{{TODAYS_DATE}}",
                    "description": "Court appearance"
                }
            )
        ]
    )
    
    # Test 2: Multiple billing rates
    suite.add_case(
        name="Different staff rates",
        user_message="Log time for matter 67890: 2 hours of paralegal work at $150/hour and 1 hour of partner review at $500/hour",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_time_entry,
                args={
                    "matter_id": 67890,
                    "hours": 2.0,
                    "date": "{{TODAYS_DATE}}",
                    "description": "Paralegal work",
                    "rate": 150.0
                }
            ),
            ExpectedToolCall(
                func=arcade_clio.create_time_entry,
                args={
                    "matter_id": 67890,
                    "hours": 1.0,
                    "date": "{{TODAYS_DATE}}",
                    "description": "Partner review",
                    "rate": 500.0
                }
            )
        ]
    )
    
    # Test 3: Expense reimbursement tracking
    suite.add_case(
        name="Reimbursable expenses",
        user_message="Record $200 in travel expenses (mileage and parking) for client meeting on matter 67890, mark as reimbursable",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_expense,
                args={
                    "matter_id": 67890,
                    "amount": 200.0,
                    "date": "{{TODAYS_DATE}}",
                    "description": "Travel expenses - mileage and parking for client meeting",
                    "category": "Travel"
                }
            )
        ]
    )
    
    # Test 4: Billing cycle management
    suite.add_case(
        name="Monthly billing cycle",
        user_message="Get all unbilled time and expenses for matter 67890 for this month to prepare the monthly invoice",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_time_entries,
                args={
                    "matter_id": 67890,
                    "billed": False,
                    "start_date": "{{FIRST_DAY_OF_MONTH}}",
                    "end_date": "{{LAST_DAY_OF_MONTH}}"
                }
            ),
            ExpectedToolCall(
                func=arcade_clio.get_expenses,
                args={
                    "matter_id": 67890,
                    "billed": False,
                    "start_date": "{{FIRST_DAY_OF_MONTH}}",
                    "end_date": "{{LAST_DAY_OF_MONTH}}"
                }
            )
        ]
    )
    
    # Test 5: Legal terminology for billing
    suite.add_case(
        name="Retainer billing",
        user_message="Apply $1000 from the client's retainer to the outstanding balance on bill 77777",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_bills,
                args={
                    "bill_id": 77777
                }
            )
        ]
    )
    
    return suite