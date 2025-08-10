# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Clio toolkit provides LLM tools for integrating with Clio legal practice management software. It implements **43+ tools** across contact management, matter/case management, document management, billing/activity tracking, real-time timers, webhooks, and UI customization using the Clio API v4.

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

# Run tests matching pattern
uv run pytest -k "test_create" -v

# Run tests with coverage for specific module
uv run pytest --cov=arcade_clio.tools.billing tests/test_billing.py
```

### Building and Version Management
```bash
# Build wheel file
make build

# Clean build artifacts
make clean-build

# Bump version (patch)
make bump-version

# View available make targets
make help
```

### Linting and Type Checking
```bash
# Run ruff linting directly
uv run ruff check arcade_clio/ --fix

# Run ruff formatting
uv run ruff format arcade_clio/

# Run mypy type checking
uv run mypy arcade_clio/

# Check specific file
uv run mypy arcade_clio/tools/billing.py
```

## Architecture Overview

### Core Components

**ClioClient (`arcade_clio/client.py`)**
- Async HTTP client for Clio API v4 with built-in retry logic
- **Critical**: Must include `X-API-VERSION: "4.0.0"` header for all API calls
- Implements exponential backoff for rate limiting (429) and server errors (5xx)
- 30-second timeout with 3 retry attempts
- Base URL: `https://app.clio.com`

**Exception Hierarchy (`arcade_clio/exceptions.py`)**
- Base class: `ClioError(ToolExecutionError)`
- Mapped by HTTP status: 401→`ClioAuthenticationError`, 429→`ClioRateLimitError`, 422→`ClioValidationError`
- Retry semantics: Rate limit errors retry, auth errors don't

**Tool Categories (`arcade_clio/tools/`)**
- **contacts.py** (7 tools): CRUD operations, relationships, activities
- **matters.py** (10 tools): CRUD, search, participants, activities, close/reopen
- **documents.py** (5 tools): Full document lifecycle management
- **billing.py** (10 tools): Time entries, expenses, bills, unified activities
- **timers.py** (4 tools): Real-time time tracking, start/stop/pause timers
- **webhooks.py** (5 tools): Real-time event notifications, webhook management
- **custom_actions.py** (6 tools): UI customization, external app integration

**Data Models (`arcade_clio/models.py`)**
- Pydantic v2 models with `ConfigDict` for JSON serialization
- Uses `Decimal` type for all monetary values (legal billing precision requirement)
- Separate request/response models for create/update operations
- Models: Contact, Matter, Activity, Bill, Document, TimeEntry, Expense

**Validation (`arcade_clio/validation.py`)**
- 6-minute billing increment validation (0.1 hour minimum)
- Email format: RFC 5322 compliant
- Phone format: Flexible international support
- Monetary amounts: Positive decimals with 2 decimal places

## Enhanced Features (New)

### Field Selection Support
All GET operations now support field selection for optimized responses:
```python
search_contacts(query="smith@law.com", fields="id,name,email,phone")
get_contact(contact_id=12345, fields="id,first_name,last_name,email")
```

### Enhanced Pagination
Support for both offset and cursor pagination:
```python
# Standard offset pagination (up to 10K records)
search_contacts(query="law", limit=50, offset=100)

# Unlimited cursor pagination for large datasets
search_contacts(query="law", limit=200, cursor_pagination=True)
```

### Real-time Timer Integration
Native support for Clio's Timer API:
```python
# Start tracking time
start_timer(matter_id=12345, description="Client consultation")

# Check active timer
get_active_timer()

# Stop timer and create time entry
stop_timer(description="Updated final description")
```

### Webhook Management
Complete webhook lifecycle management:
```python
# Create webhook for real-time notifications
create_webhook(
    url="https://myapp.com/webhooks/clio",
    events=["contact", "matter", "bill"]
)

# List and manage webhooks
list_webhooks()
update_webhook(webhook_id=123, events=["contact", "matter"])
```

### Custom Actions for UI Integration
Integrate external applications into Clio UI:
```python
# Add custom action to matter pages
create_custom_action(
    label="View in External System",
    target_url="https://myapp.com/matters/{matter_id}",
    ui_reference="matters/show"
)

# Test URL templates
test_custom_action_url(
    target_url="https://app.com/matters/{matter_id}",
    matter_id=12345
)
```

## Tool Implementation Pattern

All tools follow this consistent async pattern:

```python
from typing import Annotated
from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Clio

@tool(requires_auth=Clio())
async def tool_name(
    context: ToolContext,
    param: Annotated[str, "Parameter description"],
    optional: Annotated[str | None, "Optional parameter"] = None,
) -> Annotated[str, "JSON formatted response"]:
    """Tool docstring with clear functionality description."""
    async with ClioClient(context) as client:
        # 1. Input validation using validation.py helpers
        # 2. API call with error handling
        # 3. Response formatting with json.dumps
        try:
            response = await client.method(endpoint, data)
            return json.dumps(response, indent=2)
        except ClioError as e:
            # Specific error handling
            raise
```

## Testing Patterns

### Unit Testing
```python
from unittest.mock import AsyncMock, patch
import pytest

@pytest.fixture
def mock_context():
    context = AsyncMock()
    context.authorization.token = "test_token"
    return context

@pytest.mark.asyncio
async def test_tool(mock_context):
    with patch("arcade_clio.client.ClioClient") as MockClient:
        mock_client = AsyncMock()
        MockClient.return_value.__aenter__.return_value = mock_client
        # Test implementation
```

### Running Evaluation Suites
```bash
# Run all evaluations
uv run arcade evals run evals/

# Run specific evaluation suite
uv run arcade evals run evals/eval_clio_billing.py

# Run with specific model
uv run arcade evals run evals/ --model gpt-4o
```

## Legal Industry Considerations

### Decimal Precision
- All monetary values must use `Decimal` type
- Format: `Decimal("100.50")` not `float(100.50)`
- JSON serialization handles Decimal→string conversion

### Time Tracking Requirements
- Minimum billing increment: 0.1 hours (6 minutes)
- Maximum hours per entry: 24
- Duration validation in `validation.py`

### Matter Status Workflow
- Open→Closed: Use `close_matter` tool
- Closed→Open: Use `reopen_matter` tool
- Pending state requires special handling

### Document Management
- Documents can be files or folders
- Folders: `is_folder=True` in creation
- Categories support legal document classification
- Version control through document history

## API Integration Notes

### Authentication
- OAuth 2.0 Bearer token via `context.authorization.token`
- Token passed in `Authorization: Bearer {token}` header
- Refresh handled by Arcade platform

### Rate Limiting
- Clio API rate limit: 500 requests per minute
- Automatic retry with exponential backoff
- `ClioRateLimitError` raised after max retries

### Pagination
- Default page size: 25
- Maximum page size: 100
- Use `offset` parameter for pagination
- Total count in `meta.count` field

### Date/Time Formatting
- Dates: ISO 8601 format (YYYY-MM-DD)
- Datetimes: ISO 8601 with timezone (YYYY-MM-DDTHH:MM:SSZ)
- All times in UTC

## Code Style Standards

### Type Annotations
- Required for all function parameters and returns
- Use `typing.Annotated` for parameter descriptions
- Prefer `X | None` over `Optional[X]`
- No untyped functions (enforced by mypy)

### Async Patterns
- All tools must be async functions
- Use `async with` for client context managers
- Handle `httpx.HTTPStatusError` exceptions
- Proper cleanup in finally blocks

### Error Messages
- Include specific field names in validation errors
- Provide actionable error messages
- Include Clio error details when available

### Linting Configuration
- Ruff rules: E, F, I, N, UP, RUF (ignore E501 for line length)  
- Line length: 100 characters
- Target Python: 3.10+
- Format with `ruff format`
- MyPy: Strict mode with `disallow_untyped_defs = true`

## Common Development Tasks

### Adding a New Tool
1. Add async function in appropriate `tools/` module
2. Use `@tool(requires_auth=Clio())` decorator
3. Follow existing validation patterns
4. Add comprehensive unit tests
5. Add evaluation cases if applicable
6. Update `__init__.py` exports

### Debugging API Issues
```python
# Enable httpx debugging
import httpx
import logging
logging.basicConfig(level=logging.DEBUG)

# Log API requests/responses
async with ClioClient(context) as client:
    client._client.event_hooks["request"].append(log_request)
    client._client.event_hooks["response"].append(log_response)
```

### Testing Against Live API
```bash
# Set environment variables
export CLIO_TOKEN="your_token"

# Run integration test
uv run python -c "
import asyncio
from arcade_clio.client import ClioClient
# Test code here
"
```

## Recent Enhancements

### Major Platform Upgrade (11 new tools + enhanced features)
- **Real-time Integration**: Timer API and Webhook support for live updates
- **Field Selection**: Optimized API responses with configurable field selection
- **Enhanced Pagination**: Both offset (10K limit) and unlimited cursor pagination
- **UI Customization**: Custom Actions for seamless external app integration
- **Document Management**: Full lifecycle with folders and categories
- **Unified Activities**: Single interface for time entries and expenses
- **Advanced Search**: Multi-criteria matter search with performance optimization

### Key Platform Features
- **Performance**: Field selection reduces response sizes by 40-60%
- **Real-time**: Webhook notifications enable instant workflow automation
- **Scalability**: Cursor pagination handles unlimited record sets
- **Integration**: Custom Actions embed external tools in Clio UI
- **Safety**: Delete operations validate relationships and billing status
- **Precision**: All monetary values use Decimal for legal billing accuracy