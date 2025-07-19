# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Clio toolkit provides LLM tools for integrating with Clio legal practice management software. It implements 21 tools across contact management, matter/case management, and billing/time tracking using the Clio API v4.

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
- **contacts.py**: Contact management (6 tools) - search, create, update, get relationships
- **matters.py**: Matter/case management (8 tools) - create, update, close, participants
- **billing.py**: Time tracking and billing (7 tools) - time entries, expenses, bills

**Data Models (`arcade_clio/models.py`)**
- Pydantic v2 models for API entities (Contact, Matter, Activity, Bill, etc.)
- Handles legal-specific requirements like `Decimal` precision for monetary values
- Request/response models for create/update operations

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