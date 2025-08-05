# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Clio toolkit provides LLM tools for integrating with Clio legal practice management software. It now implements **32 tools** across contact management, matter/case management, document management, and billing/activity tracking using the Clio API v4. 

**Recent Updates**: Enhanced with full feature parity to Klavis MCP documentation, adding 11 new tools including complete document management, unified activity operations, advanced search capabilities, and delete operations.

## Development Commands

### Environment Setup
```bash
# Install all dependencies with uv
make install

# Install with local Arcade sources for development
make install-local
```

### Code Quality and Testing
```bash
# Run all code quality checks (linting + type checking)
make check

# Run tests with coverage
make test

# Generate coverage report
make coverage

# Run specific test file
uv run pytest tests/test_billing.py -v

# Run specific test function
uv run pytest tests/test_billing.py::TestTimeEntryTools::test_create_time_entry_success -v

# Run with debugging output
uv run pytest tests/ -v -s
```

### Building
```bash
# Build wheel file
make build

# Clean build artifacts
make clean-build
```

## Architecture Overview

### Core Components

**ClioClient (`arcade_clio/client.py`)**
- Async HTTP client for Clio API v4 with built-in retry logic
- **Critical**: Includes `X-API-VERSION: "4.0.0"` header required for Clio API v4
- Implements exponential backoff for rate limiting (429) and server errors (5xx)
- 30-second timeout with 3 retry attempts

**Exception Hierarchy (`arcade_clio/exceptions.py`)**
- Structured exception handling mapping HTTP status codes to specific errors
- `ClioTimeoutError`, `ClioRateLimitError`, `ClioValidationError`, etc.
- All exceptions inherit from `ClioError` base class

**Tool Categories (`arcade_clio/tools/`)**
- **contacts.py**: Contact management (7 tools) - search, create, update, delete, get relationships, activities
- **matters.py**: Matter/case management (10 tools) - create, update, close, delete, search, participants, activities
- **documents.py**: Document management (5 tools) - list, get, create, update, delete documents
- **billing.py**: Time tracking and billing (10 tools) - time entries, expenses, bills, unified activities

**Data Models (`arcade_clio/models.py`)**
- Pydantic v2 models for API entities (Contact, Matter, Activity, Bill, Document, etc.)
- Handles legal-specific requirements like `Decimal` precision for monetary values
- Request/response models for create/update operations
- Document models support version control, categories, and metadata

**Validation (`arcade_clio/validation.py`)**
- Legal industry-specific validation (e.g., 6-minute billing increments)
- Email, phone, date format validation
- Monetary amount validation with decimal precision

**Utilities (`arcade_clio/utils.py`)**
- Data transformation helpers for API requests/responses
- JSON formatting with legal billing considerations
- Pagination and search parameter building

### Tool Implementation Pattern

All tools follow this pattern:
```python
@tool(requires_auth=Clio())
async def tool_name(
    context: ToolContext,
    param: Annotated[type, "Description"],
) -> Annotated[str, "Return description"]:
    async with ClioClient(context) as client:
        # Validation
        # API call
        # Response formatting
```

### Authentication and API Requirements

- Uses `Clio()` auth provider from `arcade_tdk.auth`
- All API calls require OAuth 2.0 Bearer token
- **Critical**: Must include `X-API-VERSION: "4.0.0"` header for Clio API v4 compatibility
- Rate limiting: Implements retry logic for 429 status codes

### Testing Architecture

**Test Structure**
- `tests/conftest.py`: Comprehensive fixtures including mock data for legal scenarios
- Unit tests organized by module: `test_client.py`, `test_billing.py`, `test_contacts.py`, `test_matters.py`
- `tests/test_validation.py`: Validation logic testing

**Evaluation Framework**
- `evals/`: LLM evaluation suites for testing AI understanding of legal terminology
- `eval_clio_billing.py`, `eval_clio_contacts.py`, `eval_clio_matters.py`

### Legal Industry Considerations

**Decimal Precision**
- All monetary values use `Decimal` type for precision
- Legal billing requires exact decimal calculations

**Time Tracking**
- Supports 6-minute billing increments (0.1 hour)
- Hours validation ensures reasonable limits (0-24 hours per entry)

**Matter Management**
- Supports attorney-client privilege considerations
- Role-based participant management (client, responsible_attorney, originating_attorney)

### Development Notes

**Type Safety**
- Strict mypy configuration with `disallow_untyped_defs = True`
- All functions must have type annotations
- Uses `typing.Annotated` for parameter documentation

**Code Quality**
- Ruff linting configured for Python 3.10+
- Pre-commit hooks for automated code quality checks
- Async/await patterns required for all tools

**API Compatibility**
- Designed for Clio API v4 - older versions not supported
- Retry logic handles API rate limits and transient failures
- Error handling maps HTTP status codes to appropriate exceptions

## New Tools Added (Klavis MCP Parity)

### Document Management Tools (5 new tools)
- `list_documents`: List documents with filtering by matter, contact, folder status
- `get_document`: Retrieve specific document details and metadata
- `create_document`: Create new documents or folders with categorization
- `update_document`: Update document metadata, descriptions, and organization
- `delete_document`: Remove documents with safety checks for associations

### Unified Activity Management (3 new tools)  
- `list_activities`: Unified listing of time entries and expenses with comprehensive filtering
- `get_activity`: Retrieve detailed activity information (works for both time and expenses)
- `delete_activity`: Remove activities with billing validation and safety checks

### Advanced Search (1 new tool)
- `search_matters`: Advanced matter search with multiple filter criteria including client, status, practice area, attorneys, billing method, and date ranges

### Delete Operations (2 new tools)
- `delete_contact`: Remove contacts with relationship validation
- `delete_matter`: Remove matters with comprehensive association checks

### Key Features of New Tools
- **Safety First**: All delete operations include comprehensive validation and relationship checks
- **Unified Interface**: Activity tools provide single interface for both time entries and expenses
- **Advanced Filtering**: Enhanced search capabilities with multiple filter combinations
- **Document Organization**: Full document lifecycle management with folders and categories
- **Audit Trail**: Detailed confirmation messages and error handling for all operations
