# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Arcade AI is a developer platform for building, deploying, and managing tools for AI agents. The codebase is organized as a monorepo with multiple packages for modularity.

## Development Commands

### Environment Setup
```bash
# Full development setup with all dependencies
make install

# Install dependencies for all toolkits
make install-toolkits

# Complete development setup (alias for install)
make setup
```

### Code Quality
```bash
# Run linting and type checking
make check

# Check specific libs or toolkits
make check-libs
make check-toolkits

# Run linting (alias for check)
make lint

# Install pre-commit hooks
uv run pre-commit install
```

### Testing
```bash
# Run tests for core libraries
make test

# Test individual libraries
make test-libs

# Test all toolkits
make test-toolkits

# Generate coverage report
make coverage

# Run specific test file or test function
pytest -v path/to/test_file.py
pytest -v path/to/test_file.py::TestClass::test_function
pytest -k "test_name_pattern"
```

### Building
```bash
# Build wheel files for all lib packages
make build

# Build all toolkits
make build-toolkits

# Build everything (libs + toolkits)
make full-dist

# Clean build artifacts
make clean-build
make clean-dist
make clean  # Clean all build and dist artifacts
```

### Docker
```bash
# Build and run Docker container with all toolkits
make docker

# Build base image without toolkits
make docker-base

# Publish to GitHub Container Registry
make publish-ghcr
```

### Publishing & Deployment
```bash
# Publish to PyPI (requires PYPI_TOKEN env var)
make publish

# Build and publish in one command
make build-and-publish

# Deploy to Arcade Cloud
arcade deploy --deployment-file worker.toml

# Deploy with custom engine host
arcade deploy -h custom-engine.arcade.dev
```

## Architecture

### Package Structure
- **libs/arcade-core**: Core platform functionality and schemas
- **libs/arcade-tdk**: Tool Development Kit with `@tool` decorator
- **libs/arcade-serve**: Serving infrastructure for workers and MCP servers
- **libs/arcade-cli**: Command-line interface
- **libs/arcade-evals**: Evaluation framework for testing tool performance
- **toolkits/**: Individual tool integrations (GitHub, Google, Slack, etc.)
- **contrib/**: Integration libraries (LangChain, CrewAI)

### Tool Development Pattern
Tools are defined using the `@tool` decorator from `arcade_tdk`:

```python
from typing import Annotated
from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import GitHub  # or Google, Slack, etc.

@tool(requires_auth=GitHub())
async def example_tool(
    context: ToolContext,
    param: Annotated[str, "Parameter description"],
    optional_param: Annotated[int | None, "Optional parameter"] = None,
) -> Annotated[str, "Return value description"]:
    """Tool docstring explaining functionality."""
    # Implementation using context.authorization for auth
    pass
```

### Toolkit Structure
Each toolkit follows this directory structure:
```
toolkits/<name>/
├── arcade_<name>/
│   ├── tools/          # Tool implementations
│   ├── models.py       # Pydantic models (optional)
│   ├── client.py       # API client (optional)
│   └── utils.py        # Utilities (optional)
├── tests/              # Unit tests
├── evals/              # LLM evaluation suites
└── pyproject.toml      # Package configuration
```

### Testing Patterns
Tests use pytest with async support and mocking:

```python
from unittest.mock import AsyncMock, patch
import pytest

@pytest.fixture
def mock_context():
    context = AsyncMock()
    context.authorization.token = "mock_token"
    return context

@pytest.mark.asyncio
async def test_tool(mock_context):
    # Test implementation
```

### Evaluation Framework
Use arcade_evals for testing LLM tool usage:

```python
from arcade_evals import EvalSuite, ExpectedToolCall, tool_eval
from arcade_tdk import ToolCatalog

@tool_eval()
def eval_suite() -> EvalSuite:
    catalog = ToolCatalog()
    catalog.add_module(arcade_toolkit)
    
    suite = EvalSuite(
        name="Suite Name",
        catalog=catalog,
    )
    
    suite.add_case(
        name="Test case",
        user_message="User request",
        expected_tool_calls=[
            ExpectedToolCall(func=tool_function, args={...})
        ]
    )
    return suite
```

## Code Style and Standards

### Python Version
- Target: Python 3.10+
- Supported: 3.10, 3.11, 3.12, 3.13

### Formatting and Linting
- **Ruff**: Fast Python linter and formatter
  - Line length: 100 characters
  - Rules: E, F, I, N, UP, RUF
- **MyPy**: Static type checking with strict mode
  - `disallow_untyped_defs = true`

### Type Annotations
- Use `typing.Annotated` for parameter descriptions
- All function parameters and returns must be typed
- Prefer `X | None` over `Optional[X]`

### Async Best Practices
- All tools must be async functions
- Use `httpx.AsyncClient` for HTTP requests
- Handle context managers properly with `async with`

### Authentication
- Use built-in auth providers: `GitHub()`, `Google(scopes=[...])`, `Slack(scopes=[...])`
- Access tokens via `context.authorization.token`
- Never log or expose authentication tokens

## Development Workflow

1. **Adding a new tool to existing toolkit**:
   - Add async function with `@tool` decorator in `toolkits/<name>/arcade_<name>/tools/`
   - Add comprehensive unit tests in `tests/`
   - Add evaluation cases in `evals/`
   - Run `make check-toolkits` and `make test-toolkits`

2. **Creating a new toolkit**:
   - Copy structure from existing toolkit (e.g., GitHub)
   - Update pyproject.toml with correct dependencies
   - Implement tools following the standard pattern
   - Add to `make install-toolkits` if needed

3. **Before committing**:
   - Run `make check` to ensure code quality
   - Run `make test` to ensure all tests pass
   - Update version in pyproject.toml if releasing

## Key Dependencies
- **Core**: Pydantic, PyYAML, Loguru, PyJWT, OpenTelemetry
- **HTTP**: HTTPX for async requests
- **CLI**: Typer, Rich
- **Testing**: Pytest, pytest-asyncio, pytest-mock
- **Build**: UV (package manager), Hatchling (build backend)

## Documentation
Generate toolkit documentation:
```bash
arcade generate-toolkit-docs --toolkit-name <name> --toolkit-dir <dir> --docs-dir <output>
```

## MCP Server Support
Arcade supports Model Context Protocol (MCP) servers. Tools can be served via MCP using arcade-serve:
```bash
# Run as MCP server over stdio
arcade serve --mcp

# Run with debug mode
arcade serve --mcp --debug
```

## Development Server & Debugging

### Running Local Development Server
```bash
# Start local worker server with auto-reload
arcade serve --reload

# Run with specific host/port
arcade serve --host 0.0.0.0 --port 8002

# Disable authentication for local development
arcade serve --no-auth

# Enable debug logging
arcade serve --debug

# Enable OpenTelemetry
arcade serve --otel-enable
```

### Interactive Tool Testing
```bash
# Start interactive chat to test tools
arcade chat

# Use specific model
arcade chat --model gpt-4o

# Stream tool output
arcade chat --stream

# Connect to custom engine
arcade chat --host localhost --port 9099
```

### Viewing Available Tools
```bash
# Show all toolkits
arcade show

# Show tools in specific toolkit
arcade show --toolkit github

# Show specific tool details
arcade show --toolkit github --tool list_repos

# Show local environment's catalog
arcade show --local
```

### Dashboard
```bash
# Open Arcade Dashboard in browser
arcade dashboard

# Open local dashboard
arcade dashboard --local
```

## Environment Variables

### Authentication
- `ARCADE_API_KEY`: API key for Arcade services
- `OPENAI_API_KEY`: OpenAI API key for LLM operations

### Google Toolkit Defaults
- `ARCADE_GOOGLE_LANGUAGE`: Default language for Google services (default: "en")
- `ARCADE_GOOGLE_COUNTRY`: Default country for Google services
- `ARCADE_GOOGLE_MAPS_DISTANCE_UNIT`: Distance unit for Maps (km/mi)
- `ARCADE_GOOGLE_MAPS_TRAVEL_MODE`: Default travel mode

### Worker Configuration
- `ARCADE_WORKER_SECRET`: Secret for worker authentication (default: "dev")
- `ARCADE_DEBUG_MODE`: Enable debug mode
- `ARCADE_OTEL_ENABLE`: Enable OpenTelemetry
- `ARCADE_DISABLE_AUTH`: Disable authentication

### Engine Configuration
- `ARCADE_BASE_URL`: Base URL for Arcade Engine

## Pre-commit Hooks
The project uses pre-commit hooks for code quality:
- `check-case-conflict`: Check for case conflicts
- `check-merge-conflict`: Check for merge conflicts
- `check-toml`/`check-yaml`: Validate config files
- `end-of-file-fixer`: Fix missing newlines
- `trailing-whitespace`: Remove trailing whitespace
- `ruff`: Python linting and formatting

Install hooks: `uv run pre-commit install`
Run manually: `uv run pre-commit run -a`

## Single Test Running Patterns
```bash
# Run specific test file
pytest path/to/test_file.py

# Run specific test class
pytest path/to/test_file.py::TestClassName

# Run specific test method
pytest path/to/test_file.py::TestClassName::test_method_name

# Run tests matching pattern
pytest -k "pattern"

# Run with verbose output
pytest -v

# Run with stdout capture disabled
pytest -s

# Run with specific markers
pytest -m "not slow"

# Run with coverage for specific module
pytest --cov=arcade_toolkit_name tests/
```

## Release Process
1. Update version in `pyproject.toml` files
2. Commit changes
3. GitHub Actions will automatically:
   - Run tests on version change
   - Build and publish to PyPI
   - Create GitHub release

## Debugging Tips

### Enable Debug Logging
```python
import logging
from loguru import logger

# Enable debug logging
logger.enable("arcade")
logger.add(sys.stderr, level="DEBUG")
```

### Test Tool Locally
```python
from arcade_tdk import ToolCatalog
from arcade_<toolkit>.tools import <tool_name>

catalog = ToolCatalog()
catalog.add_tool(<tool_name>)

# Test tool execution
result = await catalog.call_tool("<tool_name>", {"param": "value"})
```

### Environment File
Create `arcade.env` in project root or `~/.arcade/arcade.env`:
```env
ARCADE_API_KEY=your_api_key
OPENAI_API_KEY=your_openai_key
ARCADE_WORKER_SECRET=dev
```

## MCP Server Support
Arcade supports Model Context Protocol (MCP) servers:

```bash
# Run as MCP server
arcade serve --mcp

# Run specific toolkit as MCP server
arcade serve --mcp --filter github

# Run with custom stdio transport
arcade serve --mcp --transport stdio
```

## Common Development Patterns

### Error Handling in Tools
```python
from arcade_tdk import ToolError

@tool
async def my_tool(context: ToolContext, ...) -> str:
    try:
        # Tool implementation
        pass
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise ToolError("Resource not found", retry=False)
        raise ToolError(f"API error: {e}", retry=True)
```

### Using Tool Context
```python
# Access authorization
token = context.authorization.token

# Get user info
user_id = context.authorization.user_id

# Use context for logging
context.logger.info("Processing request")
```

### Batch Operations
Many toolkits support batch operations for efficiency:
```python
# Example: GitHub batch operations
from arcade_github.tools.batch import batch_create_issues

results = await batch_create_issues(
    context,
    repo="owner/repo",
    issues=[
        {"title": "Issue 1", "body": "Description 1"},
        {"title": "Issue 2", "body": "Description 2"},
    ]
)
```