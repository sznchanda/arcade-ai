"""Evaluation suite for Clio contact management tools."""

import arcade_clio
from arcade_evals import EvalSuite, ExpectedToolCall, tool_eval
from arcade_tdk import ToolCatalog


@tool_eval()
def eval_clio_contacts() -> EvalSuite:
    """Evaluation suite for Clio contact management functionality."""

    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)

    suite = EvalSuite(
        name="Clio Contact Management",
        system_message="You are an assistant helping with legal practice management using Clio tools. Use the available Clio contact management tools to help users with their requests.",
        catalog=catalog,
    )

    # Test case 1: Search for existing contacts
    suite.add_case(
        name="Search contacts by email",
        user_message="Find contacts with email address john.doe@lawfirm.com",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.search_contacts,
                args={"query": "john.doe@lawfirm.com", "limit": 50, "include_extra_data": False},
            )
        ],
    )

    # Test case 2: Search for contacts by name
    suite.add_case(
        name="Search contacts by name",
        user_message="Search for contacts named Smith in our system",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.search_contacts,
                args={"query": "Smith", "limit": 50, "include_extra_data": False},
            )
        ],
    )

    # Test case 3: Get specific contact details
    suite.add_case(
        name="Get contact details by ID",
        user_message="Show me the details for contact ID 12345",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_contact,
                args={"contact_id": 12345, "include_extra_data": False},
            )
        ],
    )

    # Test case 4: Create a new person contact
    suite.add_case(
        name="Create new person contact",
        user_message="Create a new contact for Sarah Johnson, email sarah.johnson@email.com, phone 555-123-4567, title Small Business Owner",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_contact,
                args={
                    "contact_type": "Person",
                    "first_name": "Sarah",
                    "last_name": "Johnson",
                    "email": "sarah.johnson@email.com",
                    "phone": "555-123-4567",
                    "title": "Small Business Owner",
                },
            )
        ],
    )

    # Test case 5: Create a new company contact
    suite.add_case(
        name="Create new company contact",
        user_message="Add Acme Legal Services as a new company contact with email info@acmelegal.com",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_contact,
                args={
                    "contact_type": "Company",
                    "name": "Acme Legal Services",
                    "email": "info@acmelegal.com",
                },
            )
        ],
    )

    # Test case 6: Update contact information
    suite.add_case(
        name="Update contact email and title",
        user_message="Update contact 12345 to change their email to new.email@example.com and title to Senior Partner",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.update_contact,
                args={
                    "contact_id": 12345,
                    "email": "new.email@example.com",
                    "title": "Senior Partner",
                },
            )
        ],
    )

    # Test case 7: List contact activities
    suite.add_case(
        name="List contact time entries",
        user_message="Show me all time entries for contact 12345",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_contact_activities,
                args={
                    "contact_id": 12345,
                    "activity_type": "TimeEntry",
                    "limit": 50,
                    "include_extra_data": False,
                },
            )
        ],
    )

    # Test case 8: Get contact matter relationships
    suite.add_case(
        name="Get contact matters",
        user_message="What matters is contact 12345 involved in?",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_contact_relationships,
                args={"contact_id": 12345, "limit": 50, "include_extra_data": False},
            )
        ],
    )

    # Test case 9: Complex search with filters
    suite.add_case(
        name="Search company contacts",
        user_message="Find all company contacts in our system, limit to 20 results",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.search_contacts,
                args={
                    "query": "",  # May need adjustment based on actual implementation
                    "contact_type": "Company",
                    "limit": 20,
                    "include_extra_data": False,
                },
            )
        ],
    )

    # Test case 10: Error handling - invalid contact ID
    suite.add_case(
        name="Handle invalid contact ID",
        user_message="Get contact details for contact ID -1",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_contact,
                args={"contact_id": -1, "include_extra_data": False},
            )
        ],
    )

    # Test case 11: Advanced search with field selection
    suite.add_case(
        name="Search with field selection",
        user_message="Find contacts named Johnson and return only their ID, name, and email fields",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.search_contacts,
                args={
                    "query": "Johnson", 
                    "limit": 50, 
                    "fields": "id,name,email",
                    "include_extra_data": False
                },
            )
        ],
    )

    # Test case 12: Create contact with complete information
    suite.add_case(
        name="Create detailed person contact",
        user_message="Create a new contact for Attorney Michael Rodriguez, email michael@legalfirm.com, phone +1-555-789-0123, with address 123 Main St, Suite 400, Chicago, IL 60601",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_contact,
                args={
                    "contact_type": "Person",
                    "first_name": "Michael",
                    "last_name": "Rodriguez", 
                    "email": "michael@legalfirm.com",
                    "phone": "+1-555-789-0123",
                    "title": "Attorney",
                    "address": {
                        "street": "123 Main St, Suite 400",
                        "city": "Chicago",
                        "state": "IL",
                        "zip": "60601"
                    }
                },
            )
        ],
    )

    # Test case 13: Update multiple contact fields
    suite.add_case(
        name="Update contact multiple fields",
        user_message="For contact 12345, update their phone to 555-999-8888, title to Managing Partner, and add note 'Updated contact info on {{TODAYS_DATE}}'",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.update_contact,
                args={
                    "contact_id": 12345,
                    "phone": "555-999-8888",
                    "title": "Managing Partner",
                    "notes": "Updated contact info on {{TODAYS_DATE}}",
                },
            )
        ],
    )

    # Test case 14: Search with pagination
    suite.add_case(
        name="Search with pagination",
        user_message="Search for all contacts with 'Law' in the name, show 10 results starting from result 20",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.search_contacts,
                args={
                    "query": "Law",
                    "limit": 10,
                    "offset": 20,
                    "include_extra_data": False
                },
            )
        ],
    )

    # Test case 15: Get contact activities with filtering
    suite.add_case(
        name="Get contact billable activities",
        user_message="Show me only billable time entries for contact 12345 from the last 30 days",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_contact_activities,
                args={
                    "contact_id": 12345,
                    "activity_type": "TimeEntry",
                    "billable": True,
                    "limit": 50,
                    "include_extra_data": False,
                },
            )
        ],
    )

    return suite


@tool_eval()
def eval_clio_contact_edge_cases() -> EvalSuite:
    """Evaluation suite for contact management edge cases and error scenarios."""
    
    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)
    
    suite = EvalSuite(
        name="Clio Contact Management Edge Cases",
        system_message="You are an assistant helping with legal practice management using Clio tools. Use the available Clio contact management tools to help users with their requests.",
        catalog=catalog,
    )

    # Test 1: Empty search query
    suite.add_case(
        name="Empty search handling",
        user_message="Search for contacts with empty criteria - just show me the first 25 contacts",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.search_contacts,
                args={"query": "", "limit": 25, "include_extra_data": False},
            )
        ],
    )

    # Test 2: Special characters in search
    suite.add_case(
        name="Special characters search",
        user_message="Find contacts with the email address that contains '@law-firm.com' domain",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.search_contacts,
                args={"query": "@law-firm.com", "limit": 50, "include_extra_data": False},
            )
        ],
    )

    # Test 3: International phone numbers
    suite.add_case(
        name="International contact creation",
        user_message="Create a contact for Maria Gonzalez in Mexico with phone +52-555-123-4567",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_contact,
                args={
                    "contact_type": "Person",
                    "first_name": "Maria",
                    "last_name": "Gonzalez",
                    "phone": "+52-555-123-4567",
                },
            )
        ],
    )

    # Test 4: Large pagination request
    suite.add_case(
        name="Large pagination request",
        user_message="Get contacts 500-600 from our database for data export",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.search_contacts,
                args={
                    "query": "",
                    "limit": 100,
                    "offset": 500,
                    "include_extra_data": False
                },
            )
        ],
    )

    # Test 5: Contact with minimal information
    suite.add_case(
        name="Minimal contact creation",
        user_message="Create a company contact for 'ABC Corp' with just the name",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_contact,
                args={
                    "contact_type": "Company",
                    "name": "ABC Corp",
                },
            )
        ],
    )

    # Test 6: Update non-existent contact
    suite.add_case(
        name="Update non-existent contact",
        user_message="Try to update contact ID 99999999 (which doesn't exist) with new email",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.update_contact,
                args={
                    "contact_id": 99999999,
                    "email": "new@email.com",
                },
            )
        ],
    )

    # Test 7: Long text fields
    suite.add_case(
        name="Long text in contact fields",
        user_message="Create a contact with a very long title: 'Senior Partner and Head of Corporate Litigation Department specializing in International Commercial Disputes'",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_contact,
                args={
                    "contact_type": "Person",
                    "first_name": "John",
                    "last_name": "Smith",
                    "title": "Senior Partner and Head of Corporate Litigation Department specializing in International Commercial Disputes",
                },
            )
        ],
    )

    return suite


if __name__ == "__main__":
    # Run the evaluation
    suite = eval_clio_contacts()
    print(f"Created evaluation suite '{suite.name}' with {len(suite.cases)} test cases")

    # Print test case names
    for i, case in enumerate(suite.cases, 1):
        print(f"{i}. {case.name}")
