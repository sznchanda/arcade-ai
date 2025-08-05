"""Document management tools for Clio."""

from typing import Annotated, Optional

from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Clio

from ..client import ClioClient
from ..exceptions import ClioError, ClioValidationError
from ..models import Document, DocumentCreateRequest, DocumentUpdateRequest
from ..utils import (
    build_search_params,
    extract_list_data,
    extract_model_data,
    format_json_response,
    prepare_request_data,
)
from ..validation import (
    validate_id,
    validate_optional_string,
    validate_positive_number,
    validate_required_string,
)


@tool(requires_auth=Clio())
async def list_documents(
    context: ToolContext,
    limit: Annotated[int, "Maximum number of documents to return (default: 50)"] = 50,
    offset: Annotated[int, "Number of documents to skip for pagination (default: 0)"] = 0,
    matter_id: Annotated[Optional[str], "Filter documents by matter ID"] = None,
    contact_id: Annotated[Optional[str], "Filter documents by contact ID"] = None,
    parent_document_id: Annotated[Optional[str], "Filter by parent document ID"] = None,
    is_folder: Annotated[Optional[bool], "Filter by folder status"] = None,
    query: Annotated[Optional[str], "Search query to filter documents by name"] = None,
    fields: Annotated[Optional[str], "Comma-separated list of fields to include"] = None,
) -> Annotated[str, "JSON response with list of documents and pagination info"]:
    """List documents in Clio with optional filtering and pagination.
    
    Supports filtering by matter, contact, parent document, folder status, and search query.
    Returns paginated results with document metadata including name, description, size,
    content type, and relationships to matters and contacts.
    """
    validate_positive_number(limit, "limit")
    validate_positive_number(offset, "offset")
    
    if matter_id:
        validate_id(matter_id, "matter_id")
    if contact_id:
        validate_id(contact_id, "contact_id")
    if parent_document_id:
        validate_id(parent_document_id, "parent_document_id")
    if query:
        validate_optional_string(query, "query")
    if fields:
        validate_optional_string(fields, "fields")

    try:
        async with ClioClient(context) as client:
            # Build query parameters
            params = build_search_params({
                "limit": limit,
                "offset": offset,
                "matter_id": matter_id,
                "contact_id": contact_id,
                "parent_document_id": parent_document_id,
                "is_folder": is_folder,
                "query": query,
                "fields": fields,
            })
            
            response = await client.get("/documents", params=params)
            documents = extract_list_data(response, "documents", Document)
            
            return format_json_response({
                "success": True,
                "documents": documents,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": response.get("meta", {}).get("total_count"),
                }
            })
            
    except ClioError as e:
        raise ClioValidationError(f"Failed to list documents: {e}")


@tool(requires_auth=Clio())
async def get_document(
    context: ToolContext,
    document_id: Annotated[str, "The ID of the document to retrieve"],
    fields: Annotated[Optional[str], "Comma-separated list of fields to include"] = None,
) -> Annotated[str, "JSON response with document details"]:
    """Get a specific document by ID.
    
    Returns detailed document information including metadata, version history,
    relationships to matters and contacts, and file properties like size and content type.
    """
    validate_id(document_id, "document_id")
    if fields:
        validate_optional_string(fields, "fields")

    try:
        async with ClioClient(context) as client:
            params = build_search_params({"fields": fields})
            response = await client.get(f"/documents/{document_id}", params=params)
            document = extract_model_data(response, "document", Document)
            
            return format_json_response({
                "success": True,
                "document": document
            })
            
    except ClioError as e:
        raise ClioValidationError(f"Failed to get document {document_id}: {e}")


@tool(requires_auth=Clio())
async def create_document(
    context: ToolContext,
    document_data: Annotated[dict, "Document data including name, parent, and metadata"],
) -> Annotated[str, "JSON response with created document details"]:
    """Create a new document in Clio.
    
    Creates a new document entry with specified name, description, and relationships.
    Can be associated with matters, contacts, or organized within document folders.
    Document categories can be assigned for better organization.
    
    Required fields:
    - name: Document name
    
    Optional fields:
    - description: Document description
    - matter_id: Associate with specific matter
    - contact_id: Associate with specific contact
    - parent_document_id: Place in document folder
    - document_category_id: Assign document category
    - is_folder: Create as folder (default: False)
    - public: Make publicly accessible (default: False)
    - tags: List of tags for organization
    """
    if not isinstance(document_data, dict):
        raise ClioValidationError("document_data must be a dictionary")
    
    # Validate required fields
    name = document_data.get("name")
    if not name:
        raise ClioValidationError("Document name is required")
    validate_required_string(name, "name")
    
    # Validate optional fields
    if "description" in document_data:
        validate_optional_string(document_data["description"], "description")
    if "matter_id" in document_data and document_data["matter_id"]:
        validate_id(str(document_data["matter_id"]), "matter_id")
    if "contact_id" in document_data and document_data["contact_id"]:
        validate_id(str(document_data["contact_id"]), "contact_id")
    if "parent_document_id" in document_data and document_data["parent_document_id"]:
        validate_id(str(document_data["parent_document_id"]), "parent_document_id")

    try:
        # Create request model for validation
        create_request = DocumentCreateRequest(**document_data)
        
        async with ClioClient(context) as client:
            request_data = prepare_request_data(create_request.model_dump(exclude_none=True))
            response = await client.post("/documents", json={"document": request_data})
            document = extract_model_data(response, "document", Document)
            
            return format_json_response({
                "success": True,
                "message": f"Document '{name}' created successfully",
                "document": document
            })
            
    except ClioError as e:
        raise ClioValidationError(f"Failed to create document: {e}")


@tool(requires_auth=Clio())
async def update_document(
    context: ToolContext,
    document_id: Annotated[str, "The ID of the document to update"],
    document_data: Annotated[dict, "Updated document data"],
) -> Annotated[str, "JSON response with updated document details"]:
    """Update an existing document.
    
    Updates document metadata including name, description, category, parent folder,
    public access settings, and tags. Cannot modify file content - use document
    versions for file updates.
    
    Updatable fields:
    - name: Document name
    - description: Document description
    - document_category_id: Document category
    - parent_document_id: Parent folder
    - public: Public access setting
    - tags: Document tags
    """
    validate_id(document_id, "document_id")
    
    if not isinstance(document_data, dict):
        raise ClioValidationError("document_data must be a dictionary")
    
    # Validate optional fields
    if "name" in document_data:
        validate_optional_string(document_data["name"], "name")
    if "description" in document_data:
        validate_optional_string(document_data["description"], "description")
    if "parent_document_id" in document_data and document_data["parent_document_id"]:
        validate_id(str(document_data["parent_document_id"]), "parent_document_id")

    try:
        # Create request model for validation
        update_request = DocumentUpdateRequest(**document_data)
        
        async with ClioClient(context) as client:
            request_data = prepare_request_data(update_request.model_dump(exclude_none=True))
            response = await client.patch(f"/documents/{document_id}", json={"document": request_data})
            document = extract_model_data(response, "document", Document)
            
            return format_json_response({
                "success": True,
                "message": f"Document {document_id} updated successfully",
                "document": document
            })
            
    except ClioError as e:
        raise ClioValidationError(f"Failed to update document {document_id}: {e}")


@tool(requires_auth=Clio())
async def delete_document(
    context: ToolContext,
    document_id: Annotated[str, "The ID of the document to delete"],
) -> Annotated[str, "JSON response confirming document deletion"]:
    """Delete a document.
    
    Permanently removes a document from Clio. This action cannot be undone.
    If the document is a folder, all contained documents will also be deleted.
    Ensure proper authorization and backup before deletion.
    
    Note: This will delete all versions of the document and cannot be reversed.
    """
    validate_id(document_id, "document_id")

    try:
        async with ClioClient(context) as client:
            # First get document info for confirmation message
            doc_response = await client.get(f"/documents/{document_id}")
            document = extract_model_data(doc_response, "document", Document)
            doc_name = document.get("name", f"Document {document_id}")
            
            # Delete the document
            await client.delete(f"/documents/{document_id}")
            
            return format_json_response({
                "success": True,
                "message": f"Document '{doc_name}' (ID: {document_id}) deleted successfully"
            })
            
    except ClioError as e:
        raise ClioValidationError(f"Failed to delete document {document_id}: {e}")