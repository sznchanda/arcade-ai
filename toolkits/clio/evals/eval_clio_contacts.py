"""Evaluation suite for Clio contact management tools."""

from arcade_evals import EvalSuite, ExpectedToolCall, tool_eval
from arcade_tdk import ToolCatalog

import arcade_clio.tools.contacts as contact_tools


@tool_eval()
def eval_clio_contacts() -> EvalSuite:
    """Evaluation suite for Clio contact management functionality."""
    
    catalog = ToolCatalog()
    catalog.add_module(contact_tools)
    
    suite = EvalSuite(
        name="Clio Contact Management",
        catalog=catalog,
    )
    
    # Test case 1: Search for existing contacts
    suite.add_case(
        name="Search contacts by email",
        user_message="Find contacts with email address john.doe@lawfirm.com",
        expected_tool_calls=[
            ExpectedToolCall(
                func=contact_tools.search_contacts,
                args={
                    "query": "john.doe@lawfirm.com",
                    "limit": 50,
                    "include_extra_data": False
                }
            )
        ]
    )
    
    # Test case 2: Search for contacts by name
    suite.add_case(
        name="Search contacts by name",
        user_message="Search for contacts named Smith in our system",
        expected_tool_calls=[
            ExpectedToolCall(
                func=contact_tools.search_contacts,
                args={
                    "query": "Smith",
                    "limit": 50,
                    "include_extra_data": False
                }
            )
        ]
    )
    
    # Test case 3: Get specific contact details
    suite.add_case(
        name="Get contact details by ID",
        user_message="Show me the details for contact ID 12345",
        expected_tool_calls=[
            ExpectedToolCall(
                func=contact_tools.get_contact,
                args={
                    "contact_id": 12345,
                    "include_extra_data": False
                }
            )
        ]
    )
    
    # Test case 4: Create a new person contact
    suite.add_case(
        name="Create new person contact",
        user_message="Create a new contact for Sarah Johnson, email sarah.johnson@email.com, phone 555-123-4567, title Small Business Owner",
        expected_tool_calls=[
            ExpectedToolCall(
                func=contact_tools.create_contact,
                args={
                    "contact_type": "Person",
                    "first_name": "Sarah",
                    "last_name": "Johnson",
                    "email": "sarah.johnson@email.com",
                    "phone": "555-123-4567",
                    "title": "Small Business Owner"
                }
            )
        ]
    )
    
    # Test case 5: Create a new company contact
    suite.add_case(
        name="Create new company contact",
        user_message="Add Acme Legal Services as a new company contact with email info@acmelegal.com",
        expected_tool_calls=[
            ExpectedToolCall(
                func=contact_tools.create_contact,
                args={
                    "contact_type": "Company",
                    "name": "Acme Legal Services",
                    "email": "info@acmelegal.com"
                }
            )
        ]
    )
    
    # Test case 6: Update contact information
    suite.add_case(
        name="Update contact email and title",
        user_message="Update contact 12345 to change their email to new.email@example.com and title to Senior Partner",
        expected_tool_calls=[
            ExpectedToolCall(
                func=contact_tools.update_contact,
                args={
                    "contact_id": 12345,
                    "email": "new.email@example.com",
                    "title": "Senior Partner"
                }
            )
        ]
    )
    
    # Test case 7: List contact activities
    suite.add_case(
        name="List contact time entries",
        user_message="Show me all time entries for contact 12345",
        expected_tool_calls=[
            ExpectedToolCall(
                func=contact_tools.list_contact_activities,
                args={
                    "contact_id": 12345,
                    "activity_type": "TimeEntry",
                    "limit": 50,
                    "include_extra_data": False
                }
            )
        ]
    )
    
    # Test case 8: Get contact matter relationships
    suite.add_case(
        name="Get contact matters",
        user_message="What matters is contact 12345 involved in?",
        expected_tool_calls=[
            ExpectedToolCall(
                func=contact_tools.get_contact_relationships,
                args={
                    "contact_id": 12345,
                    "limit": 50,
                    "include_extra_data": False
                }
            )
        ]
    )
    
    # Test case 9: Complex search with filters
    suite.add_case(
        name="Search company contacts",
        user_message="Find all company contacts in our system, limit to 20 results",
        expected_tool_calls=[
            ExpectedToolCall(
                func=contact_tools.search_contacts,
                args={
                    "query": "",  # May need adjustment based on actual implementation
                    "contact_type": "Company",
                    "limit": 20,
                    "include_extra_data": False
                }
            )
        ]
    )
    
    # Test case 10: Error handling - invalid contact ID
    suite.add_case(
        name="Handle invalid contact ID",
        user_message="Get contact details for contact ID -1",
        expected_tool_calls=[],  # Should not call the tool due to validation
        should_error=True
    )
    
    return suite


if __name__ == "__main__":
    # Run the evaluation
    suite = eval_clio_contacts()
    print(f"Created evaluation suite '{suite.name}' with {len(suite.cases)} test cases")
    
    # Print test case names
    for i, case in enumerate(suite.cases, 1):
        print(f"{i}. {case.name}")