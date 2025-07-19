# Clio Legal Practice Management Toolkit Implementation PRP

## Goal
Complete the implementation of the existing Clio legal practice management toolkit for Arcade AI, ensuring all 21+ tools are fully functional with comprehensive error handling, proper validation, and extensive testing. The toolkit should provide AI agents with full access to Clio's API v4 capabilities including contact management, matter/case management, time tracking, billing, and expense management.

## Why
- **Legal Industry Automation**: Enable AI agents to handle routine legal practice management tasks, freeing lawyers to focus on higher-value legal work
- **Workflow Integration**: Seamlessly integrate with existing legal workflows and document management systems
- **Billing Accuracy**: Provide precise time tracking and billing capabilities essential for legal practice profitability
- **Client Management**: Streamline client intake, case setup, and relationship management processes
- **Compliance**: Ensure all operations respect attorney-client privilege and legal industry regulations

## What
Complete the existing toolkit with 21+ tools across 3 main categories:
- **Contact Management (6 tools)**: Search, create, update contacts; view activities and relationships
- **Matter Management (8 tools)**: List, create, update, close matters; manage participants and activities
- **Time Tracking & Billing (7+ tools)**: Log time entries, track expenses, generate bills with flexible filtering

## Success Criteria
- [ ] All 21 tools functional with comprehensive error handling
- [ ] OAuth 2.0 authentication working with Clio API v4
- [ ] 95%+ test coverage with async test patterns
- [ ] Proper input validation for all tool parameters
- [ ] Comprehensive LLM evaluation suite with legal use cases
- [ ] Production-ready error handling with retry logic
- [ ] Decimal precision for all monetary calculations
- [ ] Full compliance with legal industry data handling standards

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://docs.developers.clio.com/api-reference/
  why: Complete Clio API v4 endpoint documentation and data schemas
  critical: OAuth 2.0 authentication flow, rate limiting, versioning headers

- url: https://docs.developers.clio.com/
  why: Developer onboarding, app creation, and integration patterns
  critical: Trial account setup, sandbox environment, best practices

- file: /Users/steevenchanda/Documents/GitHub/arcade-ai/toolkits/github/arcade_github/tools/repositories.py
  why: Reference pattern for tool structure, error handling, and pagination
  critical: Use of @tool decorator, async patterns, type annotations

- file: /Users/steevenchanda/Documents/GitHub/arcade-ai/toolkits/google/arcade_google/client.py
  why: OAuth 2.0 client implementation pattern with context manager
  critical: Async context manager, token handling, request/response processing

- file: /Users/steevenchanda/Documents/GitHub/arcade-ai/toolkits/slack/arcade_slack/exceptions.py
  why: Custom exception hierarchy for API-specific errors
  critical: HTTP status code mapping, retry logic, error context

- file: /Users/steevenchanda/Documents/GitHub/arcade-ai/libs/arcade-core/arcade_core/auth.py
  why: Clio OAuth 2.0 provider already implemented
  critical: Lines 54-61 show Clio auth provider configuration

- file: /Users/steevenchanda/Documents/GitHub/arcade-ai/toolkits/clio/pyproject.toml
  why: Package configuration, dependencies, and build setup
  critical: Pydantic v2, httpx, strict mypy configuration

- file: /Users/steevenchanda/Documents/GitHub/arcade-ai/toolkits/clio/arcade_clio/models.py
  why: Comprehensive Pydantic models already implemented
  critical: ClioBaseModel, Contact, Matter, Activity, Bill models with proper typing

- docfile: /Users/steevenchanda/Documents/GitHub/arcade-ai/clio-toolkit-feature.md
  why: Complete feature specification with examples and considerations
  critical: Legal industry requirements, security considerations, gotchas
```

### Current Codebase Tree (Existing Implementation)
```bash
toolkits/clio/
├── arcade_clio/
│   ├── __init__.py              # ✅ EXISTS - needs completion
│   ├── client.py                # ✅ EXISTS - needs completion  
│   ├── exceptions.py            # ✅ EXISTS - needs completion
│   ├── models.py                # ✅ EXISTS - comprehensive Pydantic models
│   ├── utils.py                 # ✅ EXISTS - needs completion
│   ├── validation.py            # ✅ EXISTS - needs completion
│   └── tools/
│       ├── __init__.py          # ✅ EXISTS - needs exports
│       ├── billing.py           # ✅ EXISTS - 7 tools implemented
│       ├── contacts.py          # ✅ EXISTS - 6 tools implemented  
│       └── matters.py           # ✅ EXISTS - 8 tools implemented
├── tests/
│   ├── __init__.py              # ✅ EXISTS
│   ├── conftest.py              # ✅ EXISTS - basic fixtures
│   ├── test_client.py           # ✅ EXISTS - basic tests
│   ├── test_contacts.py         # ✅ EXISTS - basic tests
│   └── test_validation.py       # ✅ EXISTS - basic tests
├── evals/
│   ├── __init__.py              # ✅ EXISTS  
│   └── eval_clio_contacts.py    # ✅ EXISTS - basic eval
└── pyproject.toml               # ✅ EXISTS - proper configuration
```

### Required Architecture Pattern (Following Slack/Google Pattern)
```bash
# ✅ CORRECT - Current Clio structure matches complex toolkit pattern:
# Similar to: toolkits/slack/, toolkits/google/
toolkits/clio/
├── arcade_clio/
│   ├── models.py                # ✅ At root level (like Slack/Google)
│   ├── client.py                # ✅ HTTP client with async context manager
│   ├── exceptions.py            # ✅ Custom exception hierarchy
│   ├── utils.py                 # ✅ Data processing utilities
│   ├── validation.py            # ✅ Input validation functions
│   └── tools/                   # ✅ Tool modules
└── tests/                       # ✅ Test structure
```

### Known Gotchas of Our Codebase & Library Quirks
```python
# CRITICAL: Clio API v4 specific requirements
# - Always use X-API-VERSION header to specify version (4.0.0)
# - OAuth 2.0 requires specific scope permissions for different endpoints
# - Rate limiting: Respect HTTP 429 responses with exponential backoff
# - Pagination: Use 'offset' and 'limit' parameters, not cursor-based

# CRITICAL: Legal industry data precision
# - Use Decimal type for ALL monetary values (billing rates, amounts)
# - Use Decimal for time quantities (hours) to avoid floating point errors
# - Date format MUST be YYYY-MM-DD for all API calls
# - Time zones: Clio uses firm's local timezone, handle conversion carefully

# CRITICAL: Arcade AI patterns (seen in existing tools)
# - All tools MUST be async functions with proper type annotations
# - Use Annotated[type, "description"] for ALL parameters
# - Return JSON strings, not objects, for consistency across toolkits
# - Context manager pattern required for HTTP clients (async with ClioClient)
# - NEVER log or expose OAuth tokens in any error messages

# CRITICAL: Pydantic v2 patterns (already implemented in models.py)
# - Use model_config = ConfigDict() instead of class Config
# - Field validation with field_validator decorator
# - JSON serialization with custom encoders for datetime/Decimal

# CRITICAL: Legal compliance requirements
# - Attorney-client privilege: No cross-client data exposure
# - Audit trails: All actions must be traceable in Clio
# - Data validation: Strict validation prevents data corruption
# - Error messages: Don't expose sensitive client information

# CRITICAL: Existing implementation has validation patterns
# - validate_id(), validate_date_string(), validate_contact_type() etc.
# - ClioValidationError, ClioError exception hierarchy
# - Decimal precision handling in billing tools
```

## Implementation Blueprint

### Current Status Analysis
The Clio toolkit has substantial implementation already in place:
- ✅ **Models**: Comprehensive Pydantic models with proper typing
- ✅ **Tools**: All 21 tools implemented with @tool decorators
- ✅ **Validation**: Input validation functions with legal industry standards
- ✅ **Structure**: Follows complex toolkit pattern (like Slack/Google)
- 🔄 **Testing**: Basic tests exist, need comprehensive coverage
- 🔄 **Client**: HTTP client exists, needs completion
- 🔄 **Error Handling**: Exception hierarchy exists, needs full implementation
- 🔄 **Evaluations**: Basic eval exists, needs comprehensive legal scenarios

### List of Tasks to be Completed

```yaml
Task 1: Complete HTTP Client Implementation
MODIFY toolkits/clio/arcade_clio/client.py:
  - FOLLOW pattern from: toolkits/google/arcade_google/client.py
  - IMPLEMENT async context manager ClioClient
  - SET base_url = "https://app.clio.com/api/v4/"
  - ADD X-API-VERSION: "4.0.0" header automatically
  - HANDLE token from context.authorization.token
  - IMPLEMENT retry logic with exponential backoff for 429/5xx
  - ADD get_contact(), get_matter(), get_activities() convenience methods

Task 2: Complete Exception Hierarchy
MODIFY toolkits/clio/arcade_clio/exceptions.py:
  - FOLLOW pattern from: toolkits/slack/arcade_slack/exceptions.py
  - COMPLETE ClioError base class with retry logic
  - MAP HTTP status codes: 401→Auth, 403→Permission, 404→NotFound, 422→Validation, 429→RateLimit
  - INCLUDE error context for debugging without exposing tokens
  - ADD ClioServerError, ClioTimeoutError for comprehensive coverage

Task 3: Complete Utility Functions
MODIFY toolkits/clio/arcade_clio/utils.py:
  - PATTERN: Data processing and response formatting
  - COMPLETE extract_model_data() - handle nested response format
  - COMPLETE format_json_response() - consistent JSON output with datetime/Decimal encoding
  - COMPLETE build_search_params() - pagination and filtering
  - COMPLETE prepare_request_data() - clean None values, convert types
  - ADD parse_decimal() for financial precision

Task 4: Complete Validation Functions
MODIFY toolkits/clio/arcade_clio/validation.py:
  - EXTEND existing validation functions
  - ADD validate_email(), validate_phone() for contact validation
  - ADD validate_positive_number(), validate_amount() for billing
  - ADD validate_participant_role() for matter management
  - INCLUDE business logic: Person contacts need first/last name
  - ENSURE all validations raise ClioValidationError with descriptive messages

Task 5: Enhance Tool Implementations
MODIFY toolkits/clio/arcade_clio/tools/contacts.py:
MODIFY toolkits/clio/arcade_clio/tools/matters.py:
MODIFY toolkits/clio/arcade_clio/tools/billing.py:
  - REVIEW existing tool implementations for completeness
  - ENSURE all inputs use validation functions
  - VERIFY proper error handling with try/catch blocks
  - CONFIRM async with ClioClient(context) pattern usage
  - VALIDATE return format_json_response() consistency

Task 6: Complete Package Exports
MODIFY toolkits/clio/arcade_clio/__init__.py:
  - EXPORT all tool functions from tools submodules
  - EXPORT main classes: ClioClient, exceptions
  - PATTERN: Follow toolkits/slack/arcade_slack/__init__.py structure

Task 7: Enhance Test Infrastructure
MODIFY toolkits/clio/tests/conftest.py:
  - EXPAND existing fixtures with comprehensive mock data
  - ADD mock_clio_client with httpx response mocking
  - INCLUDE legal-specific test data (mock contacts, matters, bills)
  - ADD async test utilities and context managers

Task 8: Write Comprehensive Unit Tests
CREATE/MODIFY test files for each module:
  - EXPAND toolkits/clio/tests/test_contacts.py
  - CREATE toolkits/clio/tests/test_matters.py
  - CREATE toolkits/clio/tests/test_billing.py
  - PATTERN: pytest-asyncio with @pytest.mark.asyncio
  - TEST both success and error cases for each tool
  - MOCK HTTP responses with realistic Clio API data
  - VALIDATE input validation and error handling
  - TEST edge cases: Person vs Company contacts, matter status transitions

Task 9: Create Comprehensive LLM Evaluations
MODIFY/CREATE toolkits/clio/evals/ files:
  - EXPAND eval_clio_contacts.py with more scenarios
  - CREATE eval_clio_matters.py for matter management
  - CREATE eval_clio_billing.py for time tracking and billing
  - PATTERN: Follow toolkits/github/evals/ structure
  - SCENARIOS: Legal workflow chains (intake→matter→time→bill)
  - TEST AI understanding of legal concepts and terminology
  - VALIDATE proper tool selection for complex legal tasks

Task 10: Integration Testing and Final Validation
RUN complete validation suite:
  - EXECUTE all unit tests with pytest
  - RUN mypy type checking (must pass with strict mode)
  - TEST with actual Clio sandbox account (if available)
  - VALIDATE OAuth flow end-to-end
  - CONFIRM proper error handling and retry logic
  - VERIFY decimal precision in billing calculations
```

### Per Task Pseudocode

```python
# Task 1: Complete HTTP Client Implementation
class ClioClient:
    BASE_URL = "https://app.clio.com/api/v4/"
    
    def __init__(self, context: ToolContext) -> None:
        self.context = context
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "ClioClient":
        headers = {
            "Authorization": f"Bearer {self.context.authorization.token}",
            "X-API-VERSION": "4.0.0",
            "Content-Type": "application/json",
        }
        
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=httpx.Timeout(30.0),
            headers=headers,
        )
        return self
    
    async def get(self, endpoint: str, *, params: Dict[str, Any] = None):
        """GET request with automatic retry for rate limits."""
        for attempt in range(3):  # Retry logic
            try:
                response = await self._client.get(endpoint, params=params)
                
                if response.status_code == 429:  # Rate limited
                    delay = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(delay)
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                # Map to specific Clio exceptions
                if e.response.status_code == 401:
                    raise ClioAuthenticationError("Invalid or expired token")
                elif e.response.status_code == 404:
                    raise ClioResourceNotFoundError(f"Resource not found: {endpoint}")
                # ... other mappings
                
        raise ClioRateLimitError("Rate limit exceeded after retries")

# Task 4: Enhanced Validation Functions
def validate_contact_type(value: str) -> str:
    """Validate and normalize contact type following legal standards."""
    if not value or not isinstance(value, str):
        raise ClioValidationError("Contact type is required")
    
    normalized = value.strip().title()  # "person" → "Person"
    if normalized not in ["Person", "Company"]:
        raise ClioValidationError("Contact type must be 'Person' or 'Company'")
    
    return normalized

def validate_hours(value: float) -> float:
    """Validate billable hours with legal industry standards."""
    if not isinstance(value, (int, float)):
        raise ClioValidationError("Hours must be a number")
    
    if value <= 0:
        raise ClioValidationError("Hours must be greater than 0")
    
    if value > 24:
        raise ClioValidationError("Hours cannot exceed 24 per day")
    
    # Legal industry often uses 6-minute increments (0.1 hour)
    return round(float(value), 1)

# Task 5: Enhanced Tool Pattern (already implemented but verify)
@tool(requires_auth=Clio())
async def create_contact(
    context: ToolContext,
    contact_type: Annotated[str, "Contact type: 'Person' or 'Company'"],
    # ... other parameters
) -> Annotated[str, "JSON string containing the created contact"]:
    """Create a new contact in Clio."""
    async with ClioClient(context) as client:
        try:
            # Validate inputs using validation functions
            contact_type = validate_contact_type(contact_type)
            # ... other validations
            
            # Business logic validation (already implemented)
            if contact_type == "Person" and not (first_name or last_name):
                raise ClioValidationError("Person contacts require first or last name")
            
            # Make API call with proper error handling
            response = await client.post("contacts", json_data=payload)
            contact_data = extract_model_data(response, Contact)
            
            return format_json_response(contact_data, include_extra_data=True)
            
        except ClioError:
            raise  # Re-raise Clio-specific errors
        except Exception as e:
            raise ClioError(f"Failed to create contact: {str(e)}")
```

### Integration Points
```yaml
AUTHENTICATION:
  - provider: "Clio OAuth 2.0 already configured in libs/arcade-core/auth.py"
  - scopes: "read:contacts write:contacts read:matters write:matters read:activities write:activities"
  - token_handling: "Automatic via ToolContext.authorization.token"

MAKEFILE:
  - auto_discovery: "Root Makefile automatically includes clio/ in install-toolkits, check-toolkits"
  - commands: "make install-toolkits, make check-toolkits, make test-toolkits"
  - pattern: "Already configured - no changes needed"

PACKAGE_STRUCTURE:
  - follows_pattern: "Complex toolkit pattern like Slack/Google with root-level models.py"
  - exports: "All tools exported from arcade_clio/__init__.py"
  - imports: "Consistent with other toolkits"
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
cd toolkits/clio
uv run ruff check arcade_clio/ --fix      # Auto-fix style issues
uv run mypy arcade_clio/                  # Type checking (MUST pass with strict mode)
uv run ruff format arcade_clio/           # Format code consistently

# Expected: No errors. Mypy strict mode MUST pass for legal industry standards.
```

### Level 2: Unit Tests
```python
# Enhanced test patterns for legal-specific scenarios
def test_create_contact_person_validation(mock_tool_context):
    """Test Person contact requires name fields."""
    with pytest.raises(ClioValidationError, match="Person contacts require"):
        await create_contact(
            mock_tool_context,
            contact_type="Person"
            # Missing first_name AND last_name
        )

def test_billing_decimal_precision(mock_tool_context, mock_clio_client):
    """Test that monetary values maintain legal billing precision."""
    # This is CRITICAL for legal billing accuracy
    result = await create_time_entry(
        mock_tool_context,
        matter_id=123,
        hours=2.5,
        rate=Decimal("350.75"),  # Test exact decimal precision
        date="2024-01-15",
        description="Contract review"
    )
    
    # Verify Decimal precision preserved
    data = json.loads(result)
    assert data["price"] == "350.75"  # String representation of Decimal
    assert data["quantity"] == "2.5"

def test_matter_status_transition_validation():
    """Test matter closure requires close_date."""
    with pytest.raises(ClioValidationError):
        await update_matter(
            mock_context,
            matter_id=123,
            status="Closed"
            # Missing close_date
        )
```

```bash
# Run comprehensive test suite
cd toolkits/clio
uv run pytest tests/ -v --cov=arcade_clio --cov-report=term-missing

# Expected: 95%+ coverage, all tests passing
# Critical: All legal industry edge cases covered
```

### Level 3: Integration Test with Clio Sandbox
```bash
# Setup Clio trial/sandbox account (if available)
export CLIO_TEST_TOKEN="your_sandbox_token"

# Test complete legal workflow
python -c "
import asyncio
from arcade_clio.tools.contacts import create_contact
from arcade_clio.tools.matters import create_matter
from arcade_clio.tools.billing import create_time_entry, create_bill

async def test_legal_workflow():
    # 1. Create client contact
    client = await create_contact(context, contact_type='Person', first_name='Test', last_name='Client')
    
    # 2. Create matter for client
    matter = await create_matter(context, description='Test Case', client_id=client_id)
    
    # 3. Log billable time
    time_entry = await create_time_entry(context, matter_id=matter_id, hours=2.5, date='2024-01-15')
    
    # 4. Generate bill
    bill = await create_bill(context, matter_id=matter_id, include_unbilled_time=True)
    
    print('Legal workflow test successful')

asyncio.run(test_legal_workflow())
"

# Expected: Complete workflow succeeds with accurate billing
```

### Final Validation Checklist
- [ ] All unit tests pass: `uv run pytest tests/ -v`
- [ ] 95%+ test coverage: `uv run pytest --cov=arcade_clio --cov-report=term-missing`
- [ ] No linting errors: `uv run ruff check arcade_clio/`
- [ ] No type errors: `uv run mypy arcade_clio/` (strict mode)
- [ ] All 21 tools functional with proper error handling
- [ ] OAuth 2.0 flow working end-to-end
- [ ] Decimal precision maintained for all monetary values
- [ ] Legal workflow chain complete: Contact→Matter→Time→Bill
- [ ] Error handling graceful with informative messages
- [ ] No sensitive data exposure in logs or errors
- [ ] LLM evaluation suite validates AI understanding of legal concepts
- [ ] Integration with Makefile commands working

## Anti-Patterns to Avoid
- ❌ Don't use float for monetary values - MUST use Decimal for legal billing accuracy
- ❌ Don't ignore Clio API versioning - always set X-API-VERSION header
- ❌ Don't expose OAuth tokens in error messages or logs
- ❌ Don't create sync functions - legal workflows must be async
- ❌ Don't skip input validation - legal data corruption has serious consequences
- ❌ Don't hardcode API URLs - use configurable base URL for sandbox/production
- ❌ Don't ignore rate limits - implement exponential backoff for API 429 responses
- ❌ Don't mix contact types - Person vs Company have different required fields
- ❌ Don't allow matter closure without close_date - violates legal practice standards
- ❌ Don't change existing models.py structure - follows correct complex toolkit pattern

## Critical Context to Include
- **Existing Implementation**: Substantial toolkit already exists with proper structure
- **Legal Industry Requirements**: Decimal precision, audit trails, confidentiality
- **Clio API Specifics**: v4 versioning, OAuth scopes, response format patterns
- **Arcade Patterns**: Async tools, type annotations, error handling hierarchy
- **Complex Toolkit Pattern**: models.py at root level (like Slack/Google), not sub-modules

**PRP Confidence Score: 9.5/10** - Comprehensive context provided with accurate analysis of existing implementation. The toolkit already follows correct patterns and has substantial code in place. Focus is on completion and testing rather than greenfield development, which increases success probability significantly.