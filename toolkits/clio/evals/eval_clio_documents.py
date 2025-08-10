"""Evaluation suite for Clio document management tools."""

import arcade_clio
from arcade_evals import EvalSuite, ExpectedToolCall, tool_eval
from arcade_tdk import ToolCatalog


@tool_eval()
def eval_clio_documents() -> EvalSuite:
    """Evaluation suite for Clio document management functionality."""
    
    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)
    
    suite = EvalSuite(
        name="Clio Document Management",
        catalog=catalog,
    )

    # Document listing and search
    suite.add_case(
        name="list_documents_by_matter",
        user_message="Show me all documents for matter ID 12345",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_documents,
                args={"matter_id": 12345}
            )
        ]
    )

    suite.add_case(
        name="list_documents_with_pagination",
        user_message="Get the first 10 documents from the system",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_documents,
                args={"limit": 10, "offset": 0}
            )
        ]
    )

    # Document retrieval
    suite.add_case(
        name="get_specific_document",
        user_message="Get details for document ID 567",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.get_document,
                args={"document_id": 567}
            )
        ]
    )

    # Document creation
    suite.add_case(
        name="create_document_for_matter",
        user_message="Create a new document called 'Employment Contract' for matter 12345",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_document,
                args={
                    "name": "Employment Contract",
                    "matter_id": 12345
                }
            )
        ]
    )

    suite.add_case(
        name="create_document_folder",
        user_message="Create a folder called 'Contracts' for organizing documents",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_document,
                args={
                    "name": "Contracts",
                    "is_folder": True
                }
            )
        ]
    )

    # Document updates
    suite.add_case(
        name="update_document_name",
        user_message="Rename document ID 789 to 'Final Contract Version'",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.update_document,
                args={
                    "document_id": 789,
                    "name": "Final Contract Version"
                }
            )
        ]
    )

    # Document deletion
    suite.add_case(
        name="delete_document",
        user_message="Delete document ID 999 from the system",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.delete_document,
                args={"document_id": 999}
            )
        ]
    )

    # Complex document management workflows
    suite.add_case(
        name="document_organization_workflow",
        user_message="Find all PDF documents for matter 54321 and show me their details",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_documents,
                args={"matter_id": 54321}
            )
        ]
    )

    suite.add_case(
        name="document_search_by_contact",
        user_message="Show me all documents associated with contact ID 777",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_documents,
                args={"contact_id": 777}
            )
        ]
    )

    # Test 12: Document creation with category
    suite.add_case(
        name="create_document_with_category",
        user_message="Create a new contract document 'Non-Disclosure Agreement' for matter 12345 in the 'Contracts' category",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_document,
                args={
                    "name": "Non-Disclosure Agreement",
                    "matter_id": 12345,
                    "category": "Contracts",
                    "description": "Standard NDA template"
                }
            )
        ]
    )

    # Test 13: Document listing with field selection
    suite.add_case(
        name="list_documents_with_fields",
        user_message="Get all documents for matter 54321 but only return their ID, name, and created date",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_documents,
                args={
                    "matter_id": 54321,
                    "fields": "id,name,created_at"
                }
            )
        ]
    )

    # Test 14: Document filtering by type
    suite.add_case(
        name="filter_documents_by_type",
        user_message="Show me only folder-type documents in the system",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_documents,
                args={"is_folder": True}
            )
        ]
    )

    # Test 15: Bulk document operations workflow
    suite.add_case(
        name="bulk_document_workflow",
        user_message="Create a folder called 'Discovery Documents', then create a document 'Witness Statement' inside it for matter 99999",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_document,
                args={
                    "name": "Discovery Documents",
                    "is_folder": True
                }
            ),
            ExpectedToolCall(
                func=arcade_clio.create_document,
                args={
                    "name": "Witness Statement",
                    "matter_id": 99999,
                    "description": "Primary witness testimony",
                    "parent_folder_id": "{{FOLDER_ID_FROM_PREVIOUS}}"
                }
            )
        ]
    )

    return suite


@tool_eval()
def eval_clio_document_edge_cases() -> EvalSuite:
    """Evaluation suite for document management edge cases and error scenarios."""
    
    catalog = ToolCatalog()
    catalog.add_module(arcade_clio)
    
    suite = EvalSuite(
        name="Clio Document Management Edge Cases",
        catalog=catalog,
    )

    # Test 1: Very long document name
    suite.add_case(
        name="long_document_name",
        user_message="Create a document with a very long name 'Comprehensive Analysis of Employment Law Regulations and Compliance Requirements for Multi-State Operations Including Federal Guidelines'",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_document,
                args={
                    "name": "Comprehensive Analysis of Employment Law Regulations and Compliance Requirements for Multi-State Operations Including Federal Guidelines",
                    "matter_id": 12345
                }
            )
        ]
    )

    # Test 2: Document with special characters
    suite.add_case(
        name="special_characters_document",
        user_message="Create a document named 'Smith v. ABC Corp - Settlement Agreement (Final)' for matter 56789",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_document,
                args={
                    "name": "Smith v. ABC Corp - Settlement Agreement (Final)",
                    "matter_id": 56789
                }
            )
        ]
    )

    # Test 3: Update non-existent document
    suite.add_case(
        name="update_nonexistent_document",
        user_message="Try to update document 99999999 (which doesn't exist) with new name",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.update_document,
                args={
                    "document_id": 99999999,
                    "name": "New Name"
                }
            )
        ]
    )

    # Test 4: Large pagination request
    suite.add_case(
        name="large_document_pagination",
        user_message="Get documents 500-600 from the system for archival",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_documents,
                args={
                    "limit": 100,
                    "offset": 500
                }
            )
        ]
    )

    # Test 5: Delete folder with contents
    suite.add_case(
        name="delete_folder_with_contents",
        user_message="Delete folder 11111 (which may contain documents)",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.delete_document,
                args={"document_id": 11111}
            )
        ]
    )

    # Test 6: Empty search query
    suite.add_case(
        name="empty_document_search",
        user_message="List all documents without any filters - show me everything",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.list_documents,
                args={}
            )
        ]
    )

    # Test 7: Document with minimal data
    suite.add_case(
        name="minimal_document_creation",
        user_message="Create a document with just the name 'Temp'",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_document,
                args={"name": "Temp"}
            )
        ]
    )

    # Test 8: International characters
    suite.add_case(
        name="international_document_name",
        user_message="Create a document named 'Contrato de Trabajo - José María González' for matter 77777",
        expected_tool_calls=[
            ExpectedToolCall(
                func=arcade_clio.create_document,
                args={
                    "name": "Contrato de Trabajo - José María González",
                    "matter_id": 77777
                }
            )
        ]
    )

    return suite