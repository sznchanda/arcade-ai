"""Evaluation suite for Clio document management tools."""

from arcade_evals import EvalSuite, EvalCase, ExpectedToolCall, tool_eval
from arcade_tdk import ToolCatalog

import arcade_clio.tools as clio_tools


@tool_eval()
def eval_clio_documents() -> EvalSuite:
    """Evaluation suite for Clio document management functionality."""
    
    catalog = ToolCatalog()
    catalog.add_module(clio_tools)
    
    suite = EvalSuite(
        name="Clio Document Management",
        catalog=catalog,
    )

    # Document listing and search
    suite.add_case(
        EvalCase(
            name="list_documents_by_matter",
            user_message="Show me all documents for matter ID 12345",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.list_documents,
                    args={"matter_id": "12345"}
                )
            ]
        )
    )

    suite.add_case(
        EvalCase(
            name="list_documents_with_pagination",
            user_message="Get the first 10 documents from the system",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.list_documents,
                    args={"limit": 10, "offset": 0}
                )
            ]
        )
    )

    # Document retrieval
    suite.add_case(
        EvalCase(
            name="get_specific_document",
            user_message="Get details for document ID 567",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.get_document,
                    args={"document_id": "567"}
                )
            ]
        )
    )

    # Document creation
    suite.add_case(
        EvalCase(
            name="create_document_for_matter",
            user_message="Create a new document called 'Employment Contract' for matter 12345",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.create_document,
                    args={
                        "document_data": {
                            "name": "Employment Contract",
                            "matter_id": 12345
                        }
                    }
                )
            ]
        )
    )

    suite.add_case(
        EvalCase(
            name="create_document_folder",
            user_message="Create a folder called 'Contracts' for organizing documents",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.create_document,
                    args={
                        "document_data": {
                            "name": "Contracts",
                            "is_folder": True
                        }
                    }
                )
            ]
        )
    )

    # Document updates
    suite.add_case(
        EvalCase(
            name="update_document_name",
            user_message="Rename document ID 789 to 'Final Contract Version'",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.update_document,
                    args={
                        "document_id": "789",
                        "document_data": {
                            "name": "Final Contract Version"
                        }
                    }
                )
            ]
        )
    )

    # Document deletion
    suite.add_case(
        EvalCase(
            name="delete_document",
            user_message="Delete document ID 999 from the system",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.delete_document,
                    args={"document_id": "999"}
                )
            ]
        )
    )

    # Complex document management workflows
    suite.add_case(
        EvalCase(
            name="document_organization_workflow",
            user_message="Find all PDF documents for matter 54321 and show me their details",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.list_documents,
                    args={"matter_id": "54321"}
                )
            ]
        )
    )

    suite.add_case(
        EvalCase(
            name="document_search_by_contact",
            user_message="Show me all documents associated with contact ID 777",
            expected_tool_calls=[
                ExpectedToolCall(
                    func=clio_tools.list_documents,
                    args={"contact_id": "777"}
                )
            ]
        )
    )

    return suite