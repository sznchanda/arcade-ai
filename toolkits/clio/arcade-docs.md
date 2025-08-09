# Arcade.dev Complete Documentation

*Comprehensive crawl of all Arcade.dev documentation pages - 148 pages captured*

---

## Table of Contents

1. [Welcome & Getting Started](#welcome--getting-started)
2. [Core Concepts](#core-concepts)
3. [Authentication & Authorization](#authentication--authorization)
4. [Tool Building & Development](#tool-building--development)customizing
5. [Framework Integrations](#framework-integrations)
6. [Deployment Options](#deployment-options)
7. [Toolkits Reference](#toolkits-reference)
8. [API Reference & Technical Details](#api-reference--technical-details)
9. [Support & Community](#support--community)

---

## Welcome & Getting Started

### Welcome to Arcade!

Learn how to move AI agents from demo to production with Arcade.

Arcade enables developers to build AI agents that can:
- Take real actions in the real world
- Integrate with external tools and services
- Handle complex workflows and authentication
- Scale from prototype to production

### Arcade Quickstart

**Build AI agents that can take real actions**

Get started with Arcade in minutes. This guide will walk you through:
1. Getting an API key
2. Installing the Arcade SDK
3. Running your first agent with tools
4. Deploying to production

### Getting Your API Key

Before you begin using Arcade, you'll need to get an API key:

1. Visit the Arcade dashboard
2. Sign up for an account
3. Navigate to API keys section
4. Generate a new API key
5. Store it securely in your environment variables

---

## Core Concepts

### What are tools?

Language models are great at processing and generating text, but they can't interact with the outside world on their own. Tools bridge this gap by giving LLMs the ability to:

- Make API calls
- Read and write files  
- Query databases
- Send emails
- And much more

### Arcade Glossary

#### Agents and Tools

**Agent**: An AI system that can use tools to accomplish tasks
**Tool**: A function that an agent can call to interact with external systems
**Toolkit**: A collection of related tools for a specific service or domain
**Auth Provider**: A service that handles authentication for tools
**Workflow**: A sequence of tool calls to accomplish a complex task

#### Hosting and Deployment

**Arcade Cloud**: Hosted service for running tools
**Local Deployment**: Running Arcade on your own infrastructure
**Hybrid Worker**: Combination of cloud and local deployment
**MCP**: Model Context Protocol for tool integration

### Hosting Options

The best way to use Arcade depends on your specific needs:

**Arcade Cloud** (Recommended)
- Fastest setup
- Managed infrastructure
- Automatic scaling
- Built-in security

**Local Deployment**
- Full control over infrastructure
- Data stays on your servers
- Custom security policies
- Air-gapped deployments

**Hybrid Deployment**
- Best of both worlds
- Sensitive tools run locally
- Non-sensitive tools in cloud
- Flexible architecture

### Arcade Clients

Arcade provides client libraries for multiple programming languages:

- Python SDK
- TypeScript/JavaScript SDK
- REST API
- GraphQL API

Each client provides:
- Tool discovery and execution
- Authentication handling
- Error management
- Type safety

### Get Formatted Tool Definitions

When calling tools directly, it can be useful to get tool definitions in a specific model provider's format. The Arcade Client provides methods for getting a tool's definition and listing multiple tool definitions in specific formats.

#### Get a Single Tool Definition

Get a tool's definition in a specific model provider's format:

```python
from arcadepy import Arcade

client = Arcade()

# Get a specific tool formatted for OpenAI
github_star_repo = client.tools.formatted.get(name="Github.SetStarred", format="openai")
print(github_star_repo)
```

#### Get All Tools in a Toolkit

List tool definitions for a toolkit in a specific model provider's format:

```python
from arcadepy import Arcade

client = Arcade()

# Get all tools in the Github toolkit formatted for OpenAI
github_tools = list(client.tools.formatted.list(format="openai", toolkit="github"))

# Print the number of tools in the Github toolkit
print(len(github_tools))
```

#### Get All Tool Definitions

Get all tools formatted for a specific model provider:

```python
from arcadepy import Arcade

client = Arcade()

# Get all tools formatted for OpenAI
all_tools = list(client.tools.formatted.list(format="openai"))

# Print the number of tools
print(len(all_tools))
```

#### Zod Tool Definitions

Zod is a TypeScript-first schema validation library that helps define and validate data structures. The Arcade JS client offers methods to convert Arcade tool definitions into Zod schemas, providing:

1. **Type Safety**: Runtime validation of tool inputs and outputs
2. **TypeScript Integration**: Excellent TypeScript support with automatic type inference  
3. **Framework Compatibility**: Direct integration with LangChain, Vercel AI SDK, and Mastra AI

**Convert to Array of Zod Tools:**

```javascript
import { toZod } from "@arcadeai/arcadejs/lib"

const googleToolkit = await arcade.tools.list({
    limit: 20,
    toolkit: "gmail",
});

const tools = toZod({
    tools: googleToolkit.items,
    client: arcade,
    userId: "<YOUR_USER_ID>",
})
```

**Convert to Object of Zod Tools:**

```javascript
import { toZodToolSet } from "@arcadeai/arcadejs/lib"

const googleToolkit = await arcade.tools.list({
    limit: 20,
    toolkit: "gmail",
});

const tools = toZodToolSet({
    tools: googleToolkit.items,
    client: arcade,
    userId: "<YOUR_USER_ID>",
})

const emails = await tools.Gmail_ListEmails.execute({
  limit: 10,
});
```

**Convert a Single Tool:**

```javascript
import { createZodTool } from "@arcadeai/arcadejs/lib"

const listEmails = await arcade.tools.get("Gmail_ListEmails");

const listEmailsTool = createZodTool({
    tool: listEmails,
    client: arcade,
    userId: "<YOUR_USER_ID>",
});

const emails = await listEmailsTool.execute({
  limit: 10,
});
```

**Handle Authorization with Zod Tools:**

Option 1 - Manual Handling:
```javascript
import { PermissionDeniedError } from "@arcadeai/arcadejs"

const tools = toZodToolSet({
  tools: googleToolkit.items,
  client: arcade,
  userId: "<YOUR_USER_ID>",
})

try {
    const result = await tools.Gmail_ListEmails.execute({
        limit: 10,
    });
    console.log(result);
} catch (error) {
    if (error instanceof PermissionDeniedError) {
        const authorizationResponse = await arcade.tools.authorize({
            tool_name: "Gmail.ListEmails",
            user_id: "<YOUR_USER_ID>",
        });
        console.log(authorizationResponse.url);
    }
}
```

Option 2 - Execute and Authorize Tool:
```javascript
import { executeOrAuthorizeZodTool } from "@arcadeai/arcadejs"

const tools = toZodToolSet({
    tools: googleToolkit.items,
    client: arcade,
    userId: "<YOUR_USER_ID>",
    executeFactory: executeOrAuthorizeZodTool,
});

const result = await tools.Gmail_ListEmails.execute({
    limit: 10,
});

if ("authorization_required" in result && result.authorization_required) {
    console.log(`Please visit ${result.authorization_response.url} to authorize`);
} else {
    console.log(result);
}
```

---

## Authentication & Authorization

### How Arcade helps with Authorization

Arcade simplifies the complex world of OAuth and API authentication by:

1. **Centralized Auth Management**: Handle all your API credentials in one place
2. **Secure Token Storage**: Encrypted storage of access tokens and secrets
3. **Automatic Refresh**: Handle token refresh automatically
4. **Multi-tenant Support**: Manage auth for multiple users/organizations
5. **Audit Logging**: Track all authentication events

### Auth Providers

Arcade supports authentication with 20+ popular services:

#### Productivity & Communication
- Google (Gmail, Calendar, Drive, Docs, Sheets)
- Microsoft (Outlook, Teams, OneDrive)
- Slack
- Discord
- Zoom

#### Development & Project Management
- GitHub
- GitLab
- Jira
- Linear
- Asana
- Notion

#### Sales & Marketing
- Salesforce
- HubSpot
- LinkedIn

#### Social Media
- Twitter/X
- Reddit
- Spotify
- Twitch

#### Other Services
- Dropbox
- Zendesk
- Stripe

### OAuth2 Configuration

Setting up OAuth2 with Arcade:

```python
from arcade import Arcade

# Initialize with your API key
arcade = Arcade(api_key="your-api-key")

# Configure OAuth provider
auth_config = {
    "provider": "google",
    "client_id": "your-client-id", 
    "client_secret": "your-client-secret",
    "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
}

# Register the auth provider
arcade.auth.register_provider("google", auth_config)
```

### Secure Auth Production

Best practices for production authentication:

1. **Environment Variables**: Store secrets in env vars, never in code
2. **Token Encryption**: All tokens encrypted at rest
3. **Minimal Scopes**: Request only necessary permissions
4. **Audit Logging**: Log all auth events for compliance
5. **Token Rotation**: Implement automatic token refresh
6. **Rate Limiting**: Prevent abuse of auth endpoints

### Tool Auth Status

Monitor authentication status for your tools:

```python
# Check auth status
status = arcade.auth.get_status("google")

if status.is_authenticated:
    print("Ready to use Google tools")
else:
    print("Authentication required")
    auth_url = arcade.auth.get_auth_url("google")
    print(f"Authorize at: {auth_url}")
```

### Direct Third-Party API Call

Use Arcade to obtain user authorization and interact with third-party services by calling their API endpoints directly, without using Arcade for tool execution.

#### Prerequisites
- Sign up for an Arcade account
- Generate an Arcade API key

#### Install required libraries
```bash
pip install arcadepy google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

#### Implementation
```python
from arcadepy import Arcade
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

client = Arcade()  # Automatically finds the `ARCADE_API_KEY` env variable

# This would be your app's internal ID for the user
user_id = "{arcade_user_id}"

# Start the authorization process
auth_response = client.auth.start(
    user_id=user_id,
    provider="google",
    scopes=["https://www.googleapis.com/auth/gmail.readonly"],
)

# Guide the user through authorization
if auth_response.status != "completed":
    print("Please complete the authorization challenge in your browser:")
    print(auth_response.url)

# Wait for authorization completion
auth_response = client.auth.wait_for_completion(auth_response)

# Use the obtained token
credentials = Credentials(auth_response.context.token)
gmail = build("gmail", "v1", credentials=credentials)

email_messages = (
    gmail.users().messages().list(userId="me").execute().get("messages", [])
)

print(email_messages)
```

### Authorized Tool Calling

Arcade provides an authorization system that handles OAuth 2.0, API keys, and user tokens needed by AI agents to access external services through tools.

#### Initialize the client
```python
from arcadepy import Arcade

client = Arcade() # Automatically finds the `ARCADE_API_KEY` env variable
```

#### Authorize a tool directly
```python
# As the developer, you must identify the user
USER_ID = "{arcade_user_id}"

# Request access to the user's Gmail account
auth_response = client.tools.authorize(
  tool_name="Gmail.ListEmails",
  user_id=USER_ID,
)

if auth_response.status != "completed":
    print(f"Click this link to authorize: {auth_response.url}")
```

#### Check for authorization status
```python
client.auth.wait_for_completion(auth_response)
```

#### Call the tool with authorization
```python
emails_response = client.tools.execute(
    tool_name="Gmail.ListEmails",
    user_id=USER_ID,
)
print(emails_response)
```

Arcade remembers the user's authorization tokens, so you don't have to! Next time the user runs the same tool, they won't have to go through the authorization process again until the auth expires or is revoked.

---

## Tool Building & Development

### Creating a Toolkit

Build your own toolkit to integrate with any service:

```python
from arcade import Toolkit

class MyServiceToolkit(Toolkit):
    def __init__(self):
        super().__init__(
            name="myservice",
            description="Tools for MyService API"
        )
    
    @tool
    def get_user_data(self, user_id: str) -> dict:
        """Get user data from MyService"""
        # Implementation here
        pass
    
    @tool  
    def send_message(self, user_id: str, message: str) -> bool:
        """Send a message via MyService"""
        # Implementation here
        pass
```

### Create a Tool with Auth

Adding authentication to your tools:

```python
@tool(auth_required=True, auth_provider="myservice")
def authenticated_action(self, data: str) -> str:
    """Perform an authenticated action"""
    
    # Get authenticated client
    client = self.get_authenticated_client()
    
    # Use client to make authenticated requests
    response = client.post("/api/action", json={"data": data})
    
    return response.json()
```

### Create a Tool with Secrets

Handle sensitive configuration:

```python
@tool(secrets=["api_key", "webhook_url"])
def process_webhook(self, payload: dict) -> bool:
    """Process webhook with secret credentials"""
    
    api_key = self.get_secret("api_key")
    webhook_url = self.get_secret("webhook_url")
    
    # Process with secrets
    response = requests.post(
        webhook_url,
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload
    )
    
    return response.status_code == 200
```

### Handle Tool Errors

Robust error handling in tools:

```python
from arcade.exceptions import ToolError, AuthenticationError

@tool
def reliable_action(self, data: str) -> str:
    """Action with comprehensive error handling"""
    
    try:
        result = external_api_call(data)
        return result
        
    except requests.exceptions.Timeout:
        raise ToolError("API request timed out")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise AuthenticationError("Invalid credentials")
        else:
            raise ToolError(f"API error: {e.response.status_code}")
            
    except Exception as e:
        raise ToolError(f"Unexpected error: {str(e)}")
```

### Retry Tools with Improved Prompt

Implement smart retry logic:

```python
@tool(max_retries=3, backoff_factor=2.0)
def retry_enabled_tool(self, query: str) -> str:
    """Tool with automatic retry on failure"""
    
    # Tool implementation
    response = make_api_call(query)
    
    # Return improved prompt on failure
    if not response.success:
        return {
            "error": response.error,
            "suggestion": "Try rephrasing your query or check the input format",
            "retry_recommended": True
        }
    
    return response.data
```

### Tool Context

Pass context between tool calls:

```python
@tool
def search_documents(self, query: str, context: dict = None) -> dict:
    """Search with contextual awareness"""
    
    # Use previous context
    if context and "previous_search" in context:
        # Refine search based on previous results
        refined_query = refine_search(query, context["previous_search"])
    else:
        refined_query = query
    
    results = search_api(refined_query)
    
    # Return results with context for next tool
    return {
        "results": results,
        "context": {
            "search_query": refined_query,
            "timestamp": datetime.now().isoformat(),
            "result_count": len(results)
        }
    }
```

---

## Framework Integrations

### LangChain Integration

#### Use LangGraph with Arcade

```python
from langchain.agents import create_arcade_agent
from langgraph import StateGraph
from arcade import Arcade

# Initialize Arcade
arcade = Arcade(api_key="your-key")

# Create agent with Arcade tools
agent = create_arcade_agent(
    llm=your_llm,
    tools=arcade.get_tools("gmail", "calendar", "slack"),
    verbose=True
)

# Use in LangGraph workflow
def agent_node(state):
    response = agent.invoke(state["messages"])
    return {"messages": [response]}

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.set_entry_point("agent")

app = workflow.compile()
```

#### Auth LangChain Tools

Handle authentication in LangChain workflows:

```python
from arcade.langchain import ArcadeToolkit

# Create authenticated toolkit
toolkit = ArcadeToolkit(
    api_key="your-key",
    user_id="user-123",  # For user-specific auth
    auth_providers=["google", "slack"]
)

# Tools automatically handle auth
tools = toolkit.get_tools()

# Use in agent
agent = create_react_agent(llm, tools)
```

#### User Auth Interrupts

Handle auth prompts in workflows:

```python
from arcade.langchain import AuthInterruptNode

def workflow_with_auth():
    graph = StateGraph(WorkflowState)
    
    # Add auth interrupt node
    graph.add_node("auth_check", AuthInterruptNode(
        required_providers=["google"],
        on_auth_required=handle_auth_required
    ))
    
    graph.add_node("main_task", main_task_node)
    
    # Auth check before main task
    graph.add_edge("auth_check", "main_task")
    graph.set_entry_point("auth_check")
    
    return graph.compile()

def handle_auth_required(provider: str, auth_url: str):
    """Handle authentication requirement"""
    print(f"Please authenticate with {provider}: {auth_url}")
    # Can pause workflow until auth complete
    return "WAITING_FOR_AUTH"
```

### CrewAI Integration

#### Use CrewAI with Arcade

```python
from crewai import Agent, Task, Crew
from arcade.crewai import ArcadeToolset

# Create toolset with Arcade tools
toolset = ArcadeToolset(
    api_key="your-key",
    tools=["gmail", "calendar", "slack"]
)

# Create agents with tools
email_agent = Agent(
    role='Email Manager',
    goal='Manage email communications efficiently',
    tools=toolset.get_tools("gmail"),
    verbose=True
)

calendar_agent = Agent(
    role='Calendar Manager', 
    goal='Handle scheduling and calendar management',
    tools=toolset.get_tools("calendar"),
    verbose=True
)

# Create tasks
email_task = Task(
    description='Check for important emails and respond if needed',
    agent=email_agent
)

calendar_task = Task(
    description='Schedule follow-up meetings based on email content',
    agent=calendar_agent
)

# Create crew
crew = Crew(
    agents=[email_agent, calendar_agent],
    tasks=[email_task, calendar_task],
    verbose=True
)

# Execute
result = crew.kickoff()
```

#### Custom Auth Flow with CrewAI

Create a custom auth flow that will be performed before executing Arcade tools within your CrewAI agent team.

##### Define your custom auth flow
```python
from typing import Any
from crewai_arcade import ArcadeToolManager

USER_ID = "{arcade_user_id}"

def custom_auth_flow(
    manager: ArcadeToolManager, tool_name: str, **tool_input: dict[str, Any]
) -> Any:
    """Custom auth flow for the ArcadeToolManager"""
    # Get authorization status
    auth_response = manager.authorize(tool_name, USER_ID)

    # If the user is not authorized, handle the authorization
    if not manager.is_authorized(auth_response.id):
        print(f"Authorization required for tool: '{tool_name}' with inputs:")
        for input_name, input_value in tool_input.items():
            print(f"  {input_name}: {input_value}")
        print(f"\nTo authorize, visit: {auth_response.url}")
        
        # Block until the user has completed the authorization
        auth_response = manager.wait_for_auth(auth_response)
        
        if not manager.is_authorized(auth_response.id):
            raise ValueError(f"Authorization failed for {tool_name}")

def tool_manager_callback(tool_manager: ArcadeToolManager, tool_name: str, **tool_input: dict[str, Any]) -> Any:
    """Tool executor callback with custom auth flow"""
    custom_auth_flow(tool_manager, tool_name, **tool_input)
    return tool_manager.execute_tool(USER_ID, tool_name, **tool_input)
```

##### Get Arcade tools with custom auth
```python
# Provide the tool manager callback to the ArcadeToolManager
manager = ArcadeToolManager(executor=tool_manager_callback)

# Retrieve tools as CrewAI StructuredTools
tools = manager.get_tools(tools=["Gmail.ListEmails"], toolkits=["Slack"])
```

### OpenAI Agents Integration

#### Use Arcade with OpenAI Agents

```python
from openai import OpenAI
from arcade.openai import ArcadeTools

# Initialize clients
openai_client = OpenAI(api_key="your-openai-key")
arcade_tools = ArcadeTools(api_key="your-arcade-key")

# Get tool definitions for OpenAI
tools = arcade_tools.get_openai_tools(["gmail", "calendar"])

# Create assistant with tools
assistant = openai_client.beta.assistants.create(
    name="Email Assistant",
    instructions="You help manage emails and calendar",
    model="gpt-4-turbo-preview",
    tools=tools
)

# Handle tool calls
def handle_tool_call(tool_call):
    tool_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    
    # Execute via Arcade
    result = arcade_tools.execute_tool(tool_name, **arguments)
    
    return {
        "tool_call_id": tool_call.id,
        "output": json.dumps(result)
    }
```

#### User Authorization with OpenAI Agents

Handle user authorization for Arcade tools in your OpenAI Agents application. When a tool requires authorization, the agent will raise an `AuthorizationError` with a URL for the user to visit.

##### Install required packages
```bash
pip install agents-arcade arcadepy
```

##### Handle authorization errors
```python
from arcadepy import AsyncArcade
from agents import Agent, Runner
from agents_arcade import get_arcade_tools
from agents_arcade.errors import AuthorizationError

# Initialize the Arcade client
client = AsyncArcade()

# Get GitHub tools for this example
tools = await get_arcade_tools(client, toolkits=["github"])

# Create an agent with GitHub tools
github_agent = Agent(
    name="GitHub agent",
    instructions="You are a helpful assistant that can assist with GitHub API calls.",
    model="gpt-4o-mini",
    tools=tools,
)

try:
    result = await Runner.run(
        starting_agent=github_agent,
        input="Star the arcadeai/arcade-ai repo",
        context={"user_id": "{arcade_user_id}"},
    )
    print("Final output:\n\n", result.final_output)
except AuthorizationError as e:
    print(f"Please Login to GitHub: {e}")
```

##### Wait for authorization completion
```python
async def handle_auth_flow(auth_id):
    print("Please visit the authorization URL in your browser")
    await client.auth.wait_for_completion(auth_id)
    
    if await is_authorized(auth_id):
        print("Authorization successful! You can now use the tool.")
        return True
    else:
        print("Authorization failed or timed out.")
        return False

# In your main function
try:
    # Run agent code
    pass
except AuthorizationError as e:
    auth_id = e.auth_id
    if await handle_auth_flow(auth_id):
        # Try running the agent again
        result = await Runner.run(
            starting_agent=github_agent,
            input="Star the arcadeai/arcade-ai repo",
            context={"user_id": "{arcade_user_id}"},
        )
        print("Final output:\n\n", result.final_output)
```

### Vercel AI Integration

#### Use Arcade with Vercel AI

```typescript
import { generateText, tool } from 'ai';
import { ArcadeTools } from '@arcade/vercel-ai';

// Initialize Arcade tools
const arcadeTools = new ArcadeTools({
  apiKey: process.env.ARCADE_API_KEY!
});

// Convert Arcade tools to Vercel AI tools
const tools = await arcadeTools.getVercelTools(['gmail', 'calendar']);

// Use in generation
const result = await generateText({
  model: openai('gpt-4-turbo-preview'),
  prompt: 'Check my emails and schedule a meeting',
  tools,
  maxToolRoundtrips: 3
});
```

### Mastra Integration

#### Use Arcade Tools in Mastra

```python
from mastra import Agent, Workflow
from arcade.mastra import ArcadeProvider

# Create Arcade provider
arcade_provider = ArcadeProvider(
    api_key="your-key",
    tools=["gmail", "calendar", "slack"]
)

# Create Mastra agent with Arcade tools
agent = Agent(
    name="assistant",
    instructions="You help with email and calendar management",
    providers=[arcade_provider]
)

# Create workflow
workflow = Workflow(
    name="email_workflow",
    agents=[agent]
)

# Execute
result = workflow.run("Check emails and schedule important meetings")
```

#### Dynamic Tool Loading with Toolsets

Mastra lets you dynamically provide tools to an agent at runtime using toolsets. This approach is essential when integrating Arcade tools in web applications where each user needs their own authentication flow.

##### Per-User Tool Authentication
```typescript
// @/mastra/index.ts
import { Mastra } from "@mastra/core";
import { githubAgent } from "./agents/githubAgent";

// Initialize Mastra
export const mastra = new Mastra({
  agents: {
    githubAgent,
  },
});
```

```typescript
// @/mastra/agents/githubAgent.ts
import { Agent } from "@mastra/core/agent";
import { anthropic } from "@ai-sdk/anthropic";

// Create the agent without tools - we'll add them at runtime
export const githubAgent = new Agent({
  name: "githubAgent",
  instructions: `You are a GitHub Agent that helps with repository management.
  
  If a tool requires authorization, you will receive an authorization URL.
  When that happens, clearly present this URL to the user and ask them to visit it.`,
  model: anthropic("claude-3-7-sonnet-20250219"),
  // No tools defined here - will be provided dynamically at runtime
});
```

##### Create API endpoint with dynamic tools
```typescript
// app/api/chat/route.ts
import { NextRequest, NextResponse } from "next/server";
import { mastra } from "@/mastra";
import { Arcade } from "@arcadeai/arcadejs";
import { getUserSession } from "@/lib/auth";
import { toZodToolSet } from "@arcadeai/arcadejs/lib";
import { executeOrAuthorizeZodTool } from "@arcadeai/arcadejs/lib";

export async function POST(req: NextRequest) {
  const { messages, threadId } = await req.json();
  const session = await getUserSession(req);
  
  if (!session) {
    return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  }

  try {
    const githubAgent = mastra.getAgent("githubAgent");
    const arcade = new Arcade();
    const githubToolkit = await arcade.tools.list({ toolkit: "github", limit: 30 });

    // Fetch user-specific Arcade tools
    const arcadeTools = toZodToolSet({
      tools: githubToolkit.items,
      client: arcade,
      userId: session.user.email,
      executeFactory: executeOrAuthorizeZodTool,
    });

    // Stream the response with dynamically provided tools
    const response = await githubAgent.stream(messages, {
      threadId,
      resourceId: session.user.id,
      toolChoice: "auto",
      toolsets: {
        arcade: arcadeTools, // Provide tools in a named toolset
      },
    });

    return response.toDataStreamResponse();
  } catch (error) {
    console.error("Error processing GitHub request:", error);
    return NextResponse.json(
      { message: "Failed to process request" },
      { status: 500 },
    );
  }
}
```

### Google ADK Integration

#### Overview

The `google-adk-arcade` package provides seamless integration between Arcade and the Google ADK. This integration allows you to enhance your AI agents with powerful Arcade tools including Google Mail, LinkedIn, GitHub, and many more.

#### Installation
```bash
pip install google-adk-arcade
```

#### Key Features
- **Easy integration** with the Google ADK framework
- **Access to all Arcade toolkits** including Google, GitHub, LinkedIn, X, and more
- **Create custom tools** with the Arcade Tool SDK
- **Manage user authentication** for tools that require it
- **Asynchronous support** compatible with Google's ADK framework

#### Basic Usage
```python
import asyncio

from arcadepy import AsyncArcade
from google.adk import Agent, Runner
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.genai import types

from google_adk_arcade.tools import get_arcade_tools


async def main():
    app_name = 'my_app'
    user_id = '{arcade_user_id}'
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    client = AsyncArcade()

    google_tools = await get_arcade_tools(client, tools=["Gmail.ListEmails"])

    # authorize the tools
    for tool in google_tools:
        result = await client.tools.authorize(
            tool_name=tool.name,
            user_id=user_id
        )
        if result.status != "completed":
            print(f"Click this link to authorize {tool.name}:\n{result.url}")
        await client.auth.wait_for_completion(result)

    # create the agent
    google_agent = Agent(
        model="gemini-2.0-flash",
        name="google_tool_agent",
        instruction="I can use Google tools to manage an inbox!",
        description="An agent equipped with tools to read Gmail emails.",
        tools=google_tools,
    )

    # create the session and pass the user ID to the state
    session = await session_service.create_session(
        app_name=app_name, user_id=user_id, state={
            "user_id": user_id,
        }
    )

    runner = Runner(
        app_name=app_name,
        agent=google_agent,
        artifact_service=artifact_service,
        session_service=session_service,
    )

    user_input = "summarize my latest 3 emails"
    content = types.Content(
        role='user', parts=[types.Part.from_text(text=user_input)]
    )
    for event in runner.run(
        user_id=user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content.parts and event.content.parts[0].text:
            print(f'** {event.author}: {event.content.parts[0].text}')

if __name__ == '__main__':
    asyncio.run(main())
```

## MCP Desktop Clients

### Use Arcade in Visual Studio Code

#### Set up Visual Studio Code
1. Download and open Visual Studio Code (version 1.100.0 or higher)
2. Open the command palette and select **MCP: Add Server…**
3. Choose **HTTP**
4. Paste the following URL: `https://api.arcade.dev/v1/mcps/arcade-anon/mcp`
5. Give your MCP server a name, like `mcp-arcade-dev`

Visual Studio Code will update your `settings.json` file with:
```json
"mcp": {
    "servers": {
        "mcp-arcade-dev": {
            "url": "https://api.arcade.dev/v1/mcps/arcade-anon/mcp"
        }
    }
}
```

**Note**: As of version 1.100.0, Visual Studio Code does not yet support MCP authorization. Only tools that do not require auth, such as math and search tools, will work.

### Use Arcade with Claude Desktop

#### Prerequisites
1. Create an Arcade account
2. Get an Arcade API key
3. Install Python 3.10 or higher

#### Install Dependencies
```bash
pip install arcade-ai
pip install arcade-google
```

#### Set up Claude Desktop
1. Download and open Claude Desktop
2. Claude Menu → "Settings" → "Developer" → "Edit Config"
3. Configuration file locations:
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

4. Replace the file contents with:
```json
{
  "mcpServers": {
    "arcade-stdio": {
      "command": "bash",
      "args": [
        "-c",
        "export ARCADE_API_KEY=YOUR_ARCADE_API_KEY_HERE && /path/to/python /path/to/arcade serve --mcp"
      ]
    }
  }
}
```

5. Restart Claude Desktop to access your Arcade toolkits.

---

## Serve Tools

### Deploy a Custom Worker on Modal

This guide shows you how to deploy a custom Arcade Worker using Modal, enabling serverless deployment of your tool workers.

#### Requirements
- Python 3.10+
- Modal CLI (`pip install modal`)

#### Deploy
Navigate to the directory containing your worker script and deploy it using Modal:

```bash
cd examples/serving-tools
modal deploy run-arcade-worker.py
```

#### Example Worker Script
```python
import os
from modal import App, Image, asgi_app

# Define the FastAPI app
app = App("arcade-worker")

toolkits = ["arcade-google", "arcade-slack"]

image = (
    Image.debian_slim()
    .pip_install("arcade_tdk")
    .pip_install("arcade_serve")
    .pip_install(toolkits)
)

@app.function(image=image)
@asgi_app()
def fastapi_app():
    from fastapi import FastAPI
    from arcade_tdk import Toolkit
    from arcade_serve.fastapi import FastAPIWorker

    web_app = FastAPI()

    # Initialize app and Arcade FastAPIWorker
    worker_secret = os.environ.get("ARCADE_WORKER_SECRET", "dev")
    worker = FastAPIWorker(web_app, secret=worker_secret)

    # Register toolkits we've installed
    installed_toolkits = Toolkit.find_all_arcade_toolkits()
    for toolkit in toolkits:
        if toolkit in installed_toolkits:
            worker.register_toolkit(toolkit)

    return web_app
```

### Build Custom Worker Images with Docker

This guide shows you how to build a custom Worker image using Arcade's base Worker image.

#### Create your Dockerfile
```dockerfile
ARG VERSION=latest

FROM ghcr.io/arcadeai/worker-base:${VERSION}

# Copy the file that lists all your desired toolkits
COPY toolkits.txt ./

# Install these toolkits
RUN pip install -r toolkits.txt
```

#### List Your Toolkits
Create a file named toolkits.txt:
```
arcade-google
arcade-firecrawl
arcade-zoom
```

#### Build and Run
```bash
# Build the image
docker build -t custom-worker:0.1.0 .

# Run the worker container
docker run -p 8002:8002 \
  -e ARCADE_WORKER_SECRET="your_secret_here" \
  custom-worker:0.1.0
```

### Arcade Deploy for Cloud Deployment

Deploy a worker with a local toolkit to the cloud using Arcade Deploy.

#### Create deployment config
Create a `worker.toml` file:
```toml
### Worker 1
[[worker]]

[worker.config]
id = "my-worker"
secret = <your secret> # Replace with your own secret

[worker.local_source]
packages = ["./<your-toolkit-directory>"] # Replace with the path to your toolkit directory
```

#### Deploy and manage workers
```bash
# Deploy your worker
arcade deploy

# List your workers
arcade worker list
```

## Evaluate Tools

### Why Evaluate Tools?

When deploying language models with tool-calling capabilities in production environments, it's essential to ensure their effectiveness and reliability. Arcade's Evaluation Framework provides a comprehensive approach to assess and validate the tool-calling capabilities of language models.

#### Key Evaluation Aspects
1. **Tool Utilization**: Assessing how efficiently the language model uses the available tools
2. **Intent Understanding**: Evaluating the language model's ability to comprehend user intents and select appropriate tools

#### Evaluation Scoring
- **Score**: A normalized value between 0.0 and 1.0
- **Result States**:
  - _Passed_: Score is above the fail threshold
  - _Failed_: Score is below the fail threshold
  - _Warned_: Score is between the warning and fail thresholds

#### Types of Critics

**BinaryCritic**
- Checks for exact matches between expected and actual values
- Use when exact values are required (e.g., specific numeric parameters)

**NumericCritic**
- Evaluates numeric values within a specified range
- Use when values can be approximate but should be within a threshold

**SimilarityCritic**
- Measures similarity between expected and actual string values
- Use when exact wording isn't critical, but content should be similar

**DatetimeCritic**
- Evaluates closeness of datetime values within a specified tolerance
- Use when datetime values should be within a certain range

### Run Evaluations with the Arcade CLI

#### Basic Usage
```bash
arcade evals <directory>

# Run evaluations in current directory
arcade evals .

# Run a single evaluation file
arcade evals eval_your_file.py
```

#### Command Options
- `--details, -d`: Show detailed results for each evaluation case
- `--models, -m`: Specify models to use (comma-separated)
- `--max-concurrent, -c`: Set maximum concurrent evaluations
- `--host, -h`: Specify Arcade Engine address
- `--port, -p`: Specify Engine port

#### Example Command
```bash
arcade evals toolkits/math/evals --details --models gpt-4o
```

### Create an Evaluation Suite

#### Prerequisites
- Build a custom tool
- Install evaluation dependencies: `pip install 'arcade-ai[evals]'`

#### Define evaluation cases
```python
from arcade_evals import (
    EvalSuite,
    EvalRubric,
    ExpectedToolCall,
    BinaryCritic,
    tool_eval,
)
from arcade_tdk import ToolCatalog
from arcade_my_new_toolkit.tools.hello import hello

# Create a catalog of tools
catalog = ToolCatalog()
catalog.add_tool(hello)

# Define the evaluation rubric
rubric = EvalRubric(
    fail_threshold=0.8,
    warn_threshold=0.9,
)

@tool_eval()
def hello_eval_suite() -> EvalSuite:
    """Create an evaluation suite for the hello tool."""
    suite = EvalSuite(
        name="Hello Tool Evaluation",
        system_message="You are a helpful assistant.",
        catalog=catalog,
        rubric=rubric,
    )

    # Add evaluation case
    suite.add_case(
        name="Simple Greeting",
        user_message="Say hello to Alice",
        expected_tool_calls=[
            ExpectedToolCall(
                func=hello,
                args={"name": "Alice"},
            )
        ],
        critics=[
            BinaryCritic(critic_field="name", weight=1.0),
        ],
    )

    return suite
```

## Deployment Options

### Local Deployment

#### Installing Arcade Locally

This guide will help you install Arcade and set up your development environment for developing and testing tools.

##### Prerequisites
- **Python 3.10 or higher**
- **pip**: Python package installer (typically included with Python)
- **Arcade Account**: Sign up for an [Arcade account](https://api.arcade.dev/signup)
- **Package Manager**: Either Brew (macOS) or Apt (linux) to install the engine binary

##### Install the Client
To connect to the cloud or local Arcade Engine:
```bash
pip install arcade-ai
arcade login
```

##### Install the Engine
To run the Arcade Engine locally, install `arcade-engine`:

**macOS (Homebrew)**
```bash
brew install ArcadeAI/tap/arcade-engine
```

**Ubuntu/Debian (APT)**
```bash
# Add Arcade repository
sudo apt-add-repository ppa:arcade/stable
sudo apt update
sudo apt install arcade-engine
```

##### Install a Toolkit
Install at least one tool to run the Arcade worker:
```bash
pip install arcade-math
```

##### Set OpenAI API Key
Edit the `engine.env` file to set the `OPENAI_API_KEY`:
```bash
OPENAI_API_KEY="<your_openai_api_key>"
```

##### Start the Engine and Worker
```bash
# First, start the worker:
arcade serve

# Then, start the engine:
arcade-engine
```

##### Connect and Chat
In a separate terminal:
```bash
arcade chat -h localhost
```

#### Docker Installation

##### Engine
```bash
# Pull the Engine image
docker pull ghcr.io/arcadeai/engine:latest

# Run the engine
docker run -d -p 9099:9099 -v ./engine.yaml:/bin/engine.yaml ghcr.io/arcadeai/engine:latest
```

##### Worker
Build custom worker images using Arcade's base Worker image:

```dockerfile
ARG VERSION=latest
FROM ghcr.io/arcadeai/worker-base:${VERSION}

# Copy toolkit list
COPY toolkits.txt ./

# Install toolkits
RUN pip install -r toolkits.txt
```

#### Install Toolkits

##### Running a Local Worker
```bash
arcade serve
```
This will check for any toolkits installed in the current python virtual environment and register them with the worker.

##### PyPI Installation
```bash
pip install arcade-[toolkit_name]

# Example: install math toolkit
pip install arcade-math

# Verify installation
arcade show --local
```

##### Local Package Installation
```bash
pip install .
# or
pip install <wheel_name>
```

##### Hosted Toolkits
Register toolkits in the worker itself:
```python
import arcade_math
from fastapi import FastAPI
from arcade_tdk import Toolkit
from arcade_serve.fastapi import FastAPIWorker

app = FastAPI()

worker_secret = os.environ.get("ARCADE_WORKER_SECRET")
worker = FastAPIWorker(app, secret=worker_secret)

worker.register_toolkit(Toolkit.from_module(arcade_math))
```

##### Show Tools From a Hosted Engine
```bash
arcade show -h <engine_host> -p <engine_port>
```

#### Troubleshooting

##### Engine Binary Not Found
```bash
❌ Engine binary not found
```
Check installation locations:
- **Brew**: `$HOMEBREW_REPOSITORY/Cellar/arcade-engine/<version>/bin/arcade-engine`
- **Apt**: `/usr/bin/arcade-engine`

Add to path if found:
```bash
export PATH=$PATH:/path/to/your/binary
```

##### Toolkits Not Found
```bash
No toolkits found in Python environment. Exiting...
```
Ensure toolkit is installed in the same environment as the Arcade SDK.

##### Engine Config Not Found
```bash
❌ Config file 'engine.yaml' not found in any of the default locations.
```
Config locations:
- `$HOME/.arcade/engine.yaml`
- `$HOMEBREW_REPOSITORY/etc/arcade-engine/engine.yaml` (Homebrew)
- `/etc/arcade-ai/engine.yaml` (Apt)

### Configuration

#### Arcade Deploy Configuration

Configure deployment settings:

```yaml
# arcade.yml
name: my-arcade-deployment
version: 1.0.0

services:
  api:
    image: arcade/arcade:latest
    replicas: 3
    resources:
      cpu: "500m"
      memory: "1Gi"
    
  worker:
    image: arcade/worker:latest
    replicas: 5
    resources:
      cpu: "250m" 
      memory: "512Mi"

database:
  type: postgresql
  host: postgres.internal
  port: 5432
  name: arcade

redis:
  host: redis.internal
  port: 6379

auth:
  providers:
    - name: google
      client_id: ${GOOGLE_CLIENT_ID}
      client_secret: ${GOOGLE_CLIENT_SECRET}
    - name: github
      client_id: ${GITHUB_CLIENT_ID}
      client_secret: ${GITHUB_CLIENT_SECRET}
```

#### Engine Configuration

Configure the Arcade engine:

```python
# config/engine.py
from arcade.config import EngineConfig

config = EngineConfig(
    # Worker settings
    max_concurrent_jobs=100,
    job_timeout_seconds=300,
    retry_attempts=3,
    
    # Security settings
    enable_auth=True,
    require_https=True,
    cors_origins=["https://yourdomain.com"],
    
    # Performance settings
    connection_pool_size=20,
    query_timeout_seconds=30,
    cache_ttl_seconds=3600,
    
    # Monitoring
    enable_metrics=True,
    log_level="INFO",
    
    # Tool settings
    tool_execution_timeout=60,
    max_tool_calls_per_request=10
)
```

#### Templates

Deployment templates for common scenarios:

**Production Template:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: arcade-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: arcade-api
  template:
    metadata:
      labels:
        app: arcade-api
    spec:
      containers:
      - name: arcade
        image: arcade/arcade:latest
        ports:
        - containerPort: 8000
        env:
        - name: ARCADE_API_KEY
          valueFrom:
            secretKeyRef:
              name: arcade-secrets
              key: api-key
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1
            memory: 2Gi
```

### Hybrid Deployment

#### Hybrid Worker

A hybrid worker allows you to run some tools locally while using Arcade Cloud for others:

```python
from arcade import HybridWorker

# Configure hybrid worker
worker = HybridWorker(
    api_key="your-key",
    local_tools=["sensitive-database", "internal-api"],
    cloud_tools=["gmail", "slack", "github"]
)

# Start worker
worker.start()
```

Benefits:
- Keep sensitive tools on-premise
- Leverage cloud tools for better reliability
- Flexible security boundaries
- Gradual migration path

### Cloud Deployment

#### Arcade Deploy

Deploy to Arcade Cloud:

```bash
# Login to Arcade
arcade auth login

# Deploy project
arcade deploy --name my-app --region us-east-1

# View deployment
arcade deployments list

# Update deployment
arcade deploy --name my-app --version 1.1.0
```

#### Docker Worker

Run workers in Docker:

```dockerfile
FROM arcade/worker:latest

# Copy your tools
COPY ./tools /app/tools

# Copy configuration
COPY ./config.yml /app/config.yml

# Set environment
ENV ARCADE_API_KEY=${ARCADE_API_KEY}
ENV WORKER_CONCURRENCY=10

# Start worker
CMD ["arcade", "worker", "start"]
```

#### Modal Worker

Deploy workers on Modal:

```python
import modal
from arcade.modal import ArcadeWorker

app = modal.App("arcade-worker")

@app.function(
    image=modal.Image.debian_slim().pip_install("arcade-ai"),
    secrets=[modal.Secret.from_name("arcade-secrets")]
)
def worker_function():
    worker = ArcadeWorker()
    worker.start()

@app.local_entrypoint() 
def main():
    worker_function.remote()
```

---

## Toolkits Reference

### Productivity & Docs

#### Gmail

**Description**: Send, read, and manage Gmail messages

**Available Tools:**
- `gmail_send_message` - Send an email
- `gmail_get_messages` - Retrieve messages from inbox
- `gmail_search_messages` - Search messages by query
- `gmail_get_thread` - Get email thread
- `gmail_create_draft` - Create draft email
- `gmail_send_draft` - Send existing draft

**Setup:**
```python
from arcade.toolkits import Gmail

gmail = Gmail(auth_provider="google")

# Send email
result = gmail.send_message(
    to="user@example.com",
    subject="Hello from Arcade",
    body="This email was sent via Arcade!"
)
```

#### Google Calendar

**Description**: Manage calendar events and schedules

**Available Tools:**
- `calendar_create_event` - Create new calendar event
- `calendar_list_events` - List upcoming events
- `calendar_get_event` - Get specific event details
- `calendar_update_event` - Update existing event
- `calendar_delete_event` - Delete calendar event

**Setup:**
```python
from arcade.toolkits import GoogleCalendar

calendar = GoogleCalendar(auth_provider="google")

# Create event
event = calendar.create_event(
    summary="Team Meeting",
    start_time="2024-03-15T10:00:00Z",
    end_time="2024-03-15T11:00:00Z",
    attendees=["team@company.com"]
)
```

#### Google Drive

**Description**: Upload, download, and manage files in Google Drive

**Available Tools:**
- `drive_upload_file` - Upload file to Drive
- `drive_download_file` - Download file from Drive
- `drive_list_files` - List files in Drive
- `drive_create_folder` - Create new folder
- `drive_share_file` - Share file with users

#### Google Docs

**Description**: Create and edit Google Docs documents

**Available Tools:**
- `docs_create_document` - Create new document
- `docs_get_document` - Retrieve document content
- `docs_update_document` - Update document content

#### Google Sheets

**Description**: Create and manipulate Google Sheets

**Available Tools:**
- `sheets_create_spreadsheet` - Create new spreadsheet
- `sheets_get_values` - Get cell values
- `sheets_update_values` - Update cell values
- `sheets_add_sheet` - Add new sheet to workbook

#### Slack

**Description**: Send messages and interact with Slack workspaces

**Available Tools:**
- `slack_send_message` - Send message to channel
- `slack_get_messages` - Retrieve channel messages
- `slack_create_channel` - Create new channel
- `slack_invite_user` - Invite user to channel

#### Microsoft Teams

**Description**: Manage Microsoft Teams conversations and meetings

**Available Tools:**
- `teams_send_message` - Send message to team
- `teams_create_meeting` - Schedule Teams meeting
- `teams_get_messages` - Get team messages

#### Outlook Mail

**Description**: Manage Outlook email accounts

**Available Tools:**
- `outlook_send_message` - Send Outlook email
- `outlook_get_messages` - Get inbox messages
- `outlook_search_messages` - Search email messages

#### Outlook Calendar

**Description**: Manage Outlook calendar events

**Available Tools:**
- `outlook_create_event` - Create calendar event
- `outlook_list_events` - List upcoming events
- `outlook_update_event` - Update existing event

#### Asana

**Description**: Manage Asana projects and tasks

**Available Tools:**
- `asana_create_task` - Create new task
- `asana_get_tasks` - List project tasks
- `asana_update_task` - Update task details
- `asana_create_project` - Create new project

#### Notion

**Description**: Interact with Notion databases and pages

**Available Tools:**
- `notion_create_page` - Create new page
- `notion_get_page` - Retrieve page content
- `notion_query_database` - Query database
- `notion_create_database` - Create new database

#### Jira

**Description**: Manage Jira issues and projects

**Available Tools:**
- `jira_create_issue` - Create new issue
- `jira_get_issue` - Get issue details
- `jira_update_issue` - Update issue
- `jira_search_issues` - Search for issues

#### Linear

**Description**: Manage Linear issues and projects

**Available Tools:**
- `linear_create_issue` - Create new issue
- `linear_get_issues` - List team issues
- `linear_update_issue` - Update issue details

#### Dropbox

**Description**: Upload and manage files in Dropbox

**Available Tools:**
- `dropbox_upload_file` - Upload file to Dropbox
- `dropbox_download_file` - Download file
- `dropbox_list_files` - List folder contents
- `dropbox_create_folder` - Create new folder

### Developer Tools

#### GitHub

**Description**: Interact with GitHub repositories and issues

**Available Tools:**
- `github_create_repo` - Create new repository
- `github_get_repo` - Get repository details
- `github_create_issue` - Create new issue
- `github_get_issues` - List repository issues
- `github_create_pr` - Create pull request
- `github_get_file` - Get file contents

**Setup:**
```python
from arcade.toolkits import GitHub

github = GitHub(auth_provider="github")

# Create issue
issue = github.create_issue(
    repo="owner/repository",
    title="Bug Report",
    body="Description of the bug",
    labels=["bug", "priority:high"]
)
```

#### E2B

**Description**: Execute code in secure sandboxes

**Available Tools:**
- `e2b_create_sandbox` - Create code sandbox
- `e2b_run_code` - Execute code in sandbox
- `e2b_list_files` - List sandbox files
- `e2b_get_file` - Get file from sandbox

#### Firecrawl

**Description**: Web scraping and crawling

**Available Tools:**
- `firecrawl_scrape` - Scrape single webpage
- `firecrawl_crawl` - Crawl entire website
- `firecrawl_search` - Search web content

#### Web Tools

**Description**: General web interaction tools

**Available Tools:**
- `web_get_page` - Fetch webpage content
- `web_search` - Search the web
- `web_screenshot` - Take page screenshot

### Social & Communication

#### Discord

**Description**: Send messages and manage Discord servers

**Available Tools:**
- `discord_send_message` - Send message to channel
- `discord_get_messages` - Get channel messages
- `discord_create_channel` - Create new channel

#### LinkedIn

**Description**: Interact with LinkedIn profiles and posts

**Available Tools:**
- `linkedin_get_profile` - Get user profile
- `linkedin_post_update` - Post status update
- `linkedin_send_message` - Send direct message

#### Twitter/X

**Description**: Post tweets and interact with Twitter

**Available Tools:**
- `twitter_post_tweet` - Post new tweet
- `twitter_get_tweets` - Get user tweets
- `twitter_search_tweets` - Search tweets

#### Reddit

**Description**: Post and interact with Reddit communities

**Available Tools:**
- `reddit_submit_post` - Submit new post
- `reddit_get_posts` - Get subreddit posts
- `reddit_post_comment` - Comment on post

#### Zoom

**Description**: Manage Zoom meetings and webinars

**Available Tools:**
- `zoom_create_meeting` - Schedule Zoom meeting
- `zoom_list_meetings` - List upcoming meetings
- `zoom_get_meeting` - Get meeting details

#### Twilio

**Description**: Send SMS and make voice calls

**Available Tools:**
- `twilio_send_sms` - Send text message
- `twilio_make_call` - Initiate phone call
- `twilio_get_messages` - Get message history

### Search Tools

#### Google Search

**Description**: Search Google and get results

**Available Tools:**
- `google_search` - Perform Google search
- `google_news_search` - Search Google News
- `google_image_search` - Search Google Images

#### Google Finance

**Description**: Get financial data and stock information

**Available Tools:**
- `google_finance_get_quote` - Get stock quote
- `google_finance_search` - Search financial data

#### Google Maps

**Description**: Get location data and directions

**Available Tools:**
- `google_maps_search` - Search for places
- `google_maps_directions` - Get directions
- `google_maps_geocode` - Convert address to coordinates

#### Google Jobs

**Description**: Search for job listings

**Available Tools:**
- `google_jobs_search` - Search job listings

#### Google Hotels

**Description**: Search for hotel accommodations  

**Available Tools:**
- `google_hotels_search` - Search hotels

#### Google Flights

**Description**: Search for flight information

**Available Tools:**
- `google_flights_search` - Search flights

#### Google Shopping

**Description**: Search for products and prices

**Available Tools:**
- `google_shopping_search` - Search products

#### YouTube

**Description**: Search and interact with YouTube

**Available Tools:**
- `youtube_search` - Search YouTube videos
- `youtube_get_video` - Get video details

#### Walmart

**Description**: Search Walmart product catalog

**Available Tools:**
- `walmart_search_products` - Search Walmart products

### Sales & Marketing

#### Salesforce

**Description**: Manage Salesforce CRM data

**Available Tools:**
- `salesforce_create_lead` - Create new lead
- `salesforce_get_leads` - List leads
- `salesforce_create_opportunity` - Create opportunity
- `salesforce_get_accounts` - List accounts

#### HubSpot

**Description**: Manage HubSpot CRM and marketing

**Available Tools:**
- `hubspot_create_contact` - Create new contact
- `hubspot_get_contacts` - List contacts  
- `hubspot_create_deal` - Create new deal
- `hubspot_get_deals` - List deals

### Entertainment

#### Spotify

**Description**: Control Spotify playback and playlists

**Available Tools:**
- `spotify_search_tracks` - Search for songs
- `spotify_create_playlist` - Create new playlist
- `spotify_add_to_playlist` - Add songs to playlist
- `spotify_play_track` - Start track playback

#### Twitch

**Description**: Interact with Twitch streams and chat

**Available Tools:**
- `twitch_get_streams` - Get live streams
- `twitch_get_user` - Get user information

### Customer Support

#### Zendesk

**Description**: Manage Zendesk support tickets

**Available Tools:**
- `zendesk_create_ticket` - Create support ticket
- `zendesk_get_tickets` - List tickets
- `zendesk_update_ticket` - Update ticket status
- `zendesk_add_comment` - Add comment to ticket

### Payments & Finance

#### Stripe

**Description**: Process payments and manage customers

**Available Tools:**
- `stripe_create_customer` - Create new customer
- `stripe_create_payment` - Process payment
- `stripe_get_payments` - List payments
- `stripe_create_invoice` - Generate invoice

### Databases

#### Postgres

**Description**: Execute PostgreSQL queries

**Available Tools:**
- `postgres_execute_query` - Execute SQL query
- `postgres_get_tables` - List database tables
- `postgres_describe_table` - Get table schema

---

## API Reference & Technical Details

### Model Context Protocol (MCP)

#### MCP Overview

The Model Context Protocol (MCP) is Arcade's standard for connecting AI models to external data sources and tools. MCP enables:

- Standardized tool interfaces
- Secure authentication flows  
- Real-time data access
- Bidirectional communication

#### Use Arcade with Claude Desktop

Configure Arcade with Claude Desktop via MCP:

```json
{
  "mcpServers": {
    "arcade": {
      "command": "npx",
      "args": ["@arcade/mcp-server"],
      "env": {
        "ARCADE_API_KEY": "your-api-key"
      }
    }
  }
}
```

#### Use Arcade with VSCode Client

Install the Arcade VSCode extension:

1. Install from VSCode marketplace
2. Configure API key in settings
3. Use Arcade tools in AI chat

### Tool Definitions

Get programmatic access to tool schemas:

```python
from arcade import Arcade

arcade = Arcade(api_key="your-key")

# Get all available tools
tools = arcade.tools.list()

# Get specific tool definition
gmail_tools = arcade.tools.get_definitions("gmail")

# Tool definition structure
{
    "name": "gmail_send_message",
    "description": "Send an email message via Gmail",
    "parameters": {
        "type": "object", 
        "properties": {
            "to": {
                "type": "string",
                "description": "Recipient email address"
            },
            "subject": {
                "type": "string", 
                "description": "Email subject line"
            },
            "body": {
                "type": "string",
                "description": "Email body content"
            }
        },
        "required": ["to", "subject", "body"]
    }
}
```

### The Arcade CLI

The Arcade CLI is a command-line interface for managing Arcade projects:

```bash
# Install CLI
pip install arcade-ai

# Initialize project
arcade init my-project

# Add tools to project
arcade add gmail calendar slack

# Start development server
arcade serve --port 8000

# Deploy to production
arcade deploy --name my-app

# List available tools
arcade tools list

# Get tool documentation
arcade tools docs gmail

# Manage authentication
arcade auth login
arcade auth list-providers
arcade auth configure google
```

## Detailed Auth Provider Configuration

### Overview of Auth Providers

Arcade supports authentication with 20+ popular services through OAuth 2.0 and API key mechanisms. Each provider can be configured either through the Arcade Dashboard (for Cloud) or via the `engine.yaml` configuration file (for self-hosted deployments).

**Key Benefits of Custom Auth Providers:**
- Your brand appears on authorization screens (not Arcade's)
- Isolated rate limits from other Arcade customers
- Support for services not built into Arcade via OAuth 2.0
- Multi-tenant authentication support

### Google Auth Provider

The Google auth provider enables tools and agents to call Google/Google Workspace APIs on behalf of a user.

#### Create a Google App

1. Follow Google's guide to [setting up OAuth credentials](https://support.google.com/cloud/answer/6158849?hl=en)
2. Choose the [scopes](https://developers.google.com/identity/protocols/oauth2/scopes) you need
3. Required minimum scopes:
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
4. Set redirect URL: `https://cloud.arcade.dev/api/v1/oauth/callback`
5. Copy the client ID and client secret

#### Configure Google Auth in Arcade

**Dashboard Method:**
1. Navigate to [api.arcade.dev/dashboard](https://api.arcade.dev/dashboard)
2. Go to **OAuth** → **Providers** → **Add OAuth Provider**
3. Select **Google** from the provider dropdown
4. Enter a unique ID (e.g., "my-google-provider")
5. Add your Client ID and Client Secret
6. Click **Create**

**YAML Configuration (Self-hosted):**
```yaml
auth:
  providers:
    - id: my-google-provider
      description: Custom Google OAuth provider
      enabled: true
      type: oauth2
      provider_id: google
      client_id: ${env:GOOGLE_CLIENT_ID}
      client_secret: ${env:GOOGLE_CLIENT_SECRET}
```

#### Using Google Auth in App Code

```python
from arcadepy import Arcade
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

client = Arcade()
user_id = "{arcade_user_id}"

# Start authorization
auth_response = client.auth.start(
    user_id=user_id,
    provider="google",
    scopes=["https://www.googleapis.com/auth/gmail.readonly"],
)

if auth_response.status != "completed":
    print(f"Authorize at: {auth_response.url}")

# Wait for completion
auth_response = client.auth.wait_for_completion(auth_response)
token = auth_response.context.token

# Use with Google APIs
credentials = Credentials(token)
gmail = build("gmail", "v1", credentials=credentials)
```

#### Using Google Auth in Custom Tools

```python
from arcade_tdk import ToolContext, tool
from arcade_tdk.auth import Google

@tool(
    requires_auth=Google(
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )
)
async def list_emails(context: ToolContext):
    """List Gmail emails."""
    token = context.authorization.token
    # Use token with Google APIs
```

### GitHub Auth Provider

The GitHub auth provider enables tools to interact with GitHub APIs including private repositories.

#### Create a GitHub App

1. Follow GitHub's guide to [registering a GitHub app](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app)
2. Required minimum permissions:
   - Account → Email addresses (read-only)
   - Repository → Contents (for repo access)
3. Set redirect URL: `https://cloud.arcade.dev/api/v1/oauth/callback`
4. Leave "Request user authorization (OAuth) during installation" **unchecked**
5. Enable "User-to-server token expiration"
6. For organization repos: Make app public and install to organization

#### Configure GitHub Auth in Arcade

**Dashboard Method:**
1. Navigate to OAuth → Providers in Arcade Dashboard
2. Select **GitHub** as the provider
3. Enter unique ID and credentials
4. Click **Create**

**YAML Configuration:**
```yaml
auth:
  providers:
    - id: my-github-provider
      description: Custom GitHub OAuth provider
      enabled: true
      type: oauth2
      provider_id: github
      client_id: ${env:GITHUB_CLIENT_ID}
      client_secret: ${env:GITHUB_CLIENT_SECRET}
```

#### Using GitHub Auth

```python
@tool(requires_auth=GitHub())
async def count_stargazers(
    context: ToolContext,
    owner: str,
    name: str,
) -> int:
    """Count GitHub repository stars."""
    headers = {
        "Authorization": f"Bearer {context.authorization.token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    # Make API calls with token
```

### Microsoft Auth Provider

Microsoft auth provider enables Microsoft Graph API access. Note: Arcade does not offer a default Microsoft provider - you must configure your own.

#### Create a Microsoft App

1. Follow Microsoft's guide to [register an app](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app)
2. Choose required permissions/scopes
3. Set redirect URL: `https://cloud.arcade.dev/api/v1/oauth/callback`
4. Copy client ID and generate client secret

#### Configure Microsoft Auth

**Dashboard Method:**
1. Navigate to OAuth → Providers
2. Select **Microsoft** as provider
3. Enter credentials
4. Click **Create**

**YAML Configuration:**
```yaml
auth:
  providers:
    - id: my-microsoft-provider
      description: Microsoft Graph OAuth provider
      enabled: true
      type: oauth2
      provider_id: microsoft
      client_id: ${env:MICROSOFT_CLIENT_ID}
      client_secret: ${env:MICROSOFT_CLIENT_SECRET}
```

#### Using Microsoft Auth

```python
from arcade_tdk.auth import Microsoft

@tool(
    requires_auth=Microsoft(
        scopes=["User.Read", "Files.Read"],
    )
)
async def get_file_contents(context: ToolContext, file_id: str):
    """Get file from Microsoft Graph."""
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}"
    headers = {"Authorization": f"Bearer {context.authorization.token}"}
    # Make API call
```

### Slack Auth Provider

The Slack auth provider enables Slack API access with important rate limit considerations.

#### Important: Slack API Changes (May 2025)

Slack has introduced new rate limits:
- `conversations.history` and `conversations.replies`: 1 request/minute, max 15 objects per request
- Slack Marketplace approval required for commercial distribution

#### Create a Slack App

1. Follow Slack's [quickstart guide](https://api.slack.com/quickstart)
2. Required scopes for Arcade Slack toolkit:
   - `channels:history`, `channels:read`, `chat:write`
   - `groups:read`, `groups:history`, `groups:write`
   - `im:history`, `im:read`, `im:write`
   - `mpim:history`, `mpim:read`, `mpim:write`
   - `users:read`, `users:read.email`
3. Set redirect URL: `https://cloud.arcade.dev/api/v1/oauth/callback`

#### Configure Slack Auth

**Dashboard Method:**
1. Navigate to OAuth → Providers
2. Select **Slack** as provider
3. Enter credentials
4. Click **Create**

**YAML Configuration:**
```yaml
auth:
  providers:
    - id: my-slack-provider
      description: Custom Slack OAuth provider
      enabled: true
      type: oauth2
      provider_id: slack
      client_id: ${env:SLACK_CLIENT_ID}
      client_secret: ${env:SLACK_CLIENT_SECRET}
```

#### Using Slack Auth

```python
from arcade_tdk.auth import Slack
from slack_sdk import WebClient

@tool(
    requires_auth=Slack(
        scopes=["chat:write", "im:write", "users:read"],
    )
)
def send_dm_to_user(context: ToolContext, user_name: str, message: str):
    """Send Slack DM."""
    client = WebClient(token=context.authorization.token)
    # Find user and send message
```

### OAuth 2.0 Generic Provider

For services not directly supported by Arcade, use the generic OAuth 2.0 provider.

#### Supported OAuth 2.0 Features

- Authorization code grant flow (with/without PKCE)
- Token refresh
- User info endpoints
- Token introspection
- JWT token decoding
- Custom response mapping with JSONPath

#### Full OAuth 2.0 Configuration

```yaml
auth:
  providers:
    - id: custom-oauth-provider
      description: Custom OAuth 2.0 provider
      enabled: true
      type: oauth2
      client_id: ${env:CUSTOM_CLIENT_ID}
      client_secret: ${env:CUSTOM_CLIENT_SECRET}
      oauth2:
        scope_delimiter: " "  # or "," for comma-separated
        
        # PKCE configuration (optional)
        pkce:
          enabled: true
          code_challenge_method: S256
        
        # Authorization request
        authorize_request:
          endpoint: 'https://example.com/oauth2/authorize'
          params:
            response_type: code
            client_id: '{{client_id}}'
            redirect_uri: '{{redirect_uri}}'
            scope: '{{scopes}} {{existing_scopes}}'
            prompt: consent  # Optional additional params
        
        # Token exchange request
        token_request:
          endpoint: 'https://example.com/oauth2/token'
          auth_method: client_secret_basic  # or none
          params:
            grant_type: authorization_code
            redirect_uri: '{{redirect_uri}}'
            client_id: '{{client_id}}'
            client_secret: '{{client_secret}}'
          response_content_type: application/json
          response_map:  # For non-standard response formats
            access_token: "$.data.access_token"
            expires_in: "$.data.expires_in"
            refresh_token: "$.data.refresh_token"
            scope: "$.data.scope"
        
        # Refresh token request (optional)
        refresh_request:
          endpoint: 'https://example.com/oauth2/token'
          params:
            grant_type: refresh_token
            client_id: '{{client_id}}'
            client_secret: '{{client_secret}}'
        
        # User info request (optional)
        user_info_request:
          endpoint: 'https://example.com/oauth2/userinfo'
          auth_method: bearer_access_token
          response_content_type: application/json
          triggers:
            on_token_grant: true
            on_token_refresh: false
        
        # Token introspection (optional)
        token_introspection_request:
          enabled: true
          endpoint: 'https://example.com/oauth2/introspect'
          method: POST
          params:
            token: '{{access_token}}'
          auth_method: client_secret_basic
          response_map:
            expires_in: '$.exp'
            scope: '$.scope'
          expiration_format: absolute_unix_timestamp
          triggers:
            on_token_grant: true
            on_token_refresh: true
```

#### Advanced OAuth 2.0 Features

**Handling Scope Arrays:**
```yaml
token_request:
  response_map:
    scope: "join('$.scope', ' ')"  # Join array to string
```

**JWT Token Decoding:**
```yaml
token_request:
  response_map:
    scope: "jwt_decode('$.access_token', '$.scope')"
    # Or combine with join for arrays
    scope: "join(jwt_decode('$.access_token', '$.scp'), ' ')"
```

#### Using OAuth 2.0 in Custom Tools

```python
from arcade_tdk.auth import OAuth2

@tool(
    requires_auth=OAuth2(
        provider_id="custom-oauth-provider",
        scopes=["scope1", "scope2"],
    )
)
async def custom_api_call(context: ToolContext):
    """Call custom API with OAuth 2.0."""
    token = context.authorization.token
    user_info = context.authorization.user_info  # If configured
    # Make API calls
```

### Additional Auth Providers

#### Discord
- OAuth 2.0 based authentication
- Scopes: Server and channel management, messaging
- Configure similarly to other OAuth providers

#### LinkedIn
- OAuth 2.0 for professional networking
- Scopes: Profile access, posting, messaging
- Requires LinkedIn app registration

#### Spotify
- OAuth 2.0 for music service integration
- Scopes: Playback control, playlist management
- Requires Spotify app registration

#### Dropbox
- OAuth 2.0 for file storage
- Scopes: File read/write, sharing
- Requires Dropbox app registration

#### Notion
- OAuth 2.0 for workspace management
- Scopes: Page and database access
- Requires Notion integration setup

#### Asana
- OAuth 2.0 for project management
- Scopes: Task and project management
- Requires Asana app registration

#### Linear
- OAuth 2.0 for issue tracking
- Scopes: Issue and project access
- Requires Linear app registration

#### HubSpot
- OAuth 2.0 for CRM integration
- Scopes: Contact and deal management
- Requires HubSpot app registration

#### Zoom
- OAuth 2.0 for meeting management
- Scopes: Meeting creation and management
- Requires Zoom app registration

#### X (Twitter)
- OAuth 2.0 for social media
- Scopes: Tweet posting, timeline access
- Requires X developer app

#### Reddit
- OAuth 2.0 for community interaction
- Scopes: Post and comment management
- Requires Reddit app registration

#### Twitch
- OAuth 2.0 for streaming platform
- Scopes: Stream and chat access
- Requires Twitch app registration

#### Atlassian
- OAuth 2.0 for Jira/Confluence
- Scopes: Issue and page management
- Requires Atlassian app registration

### Multiple Providers of the Same Type

When using multiple providers of the same type (e.g., multiple Google accounts), you need to specify which provider to use:

```python
# Modify tools to specify provider ID
@tool(
    requires_auth=Google(
        id="acme-google-calendar",  # Specific provider ID
        scopes=["https://www.googleapis.com/auth/calendar"],
    )
)
async def calendar_tool(context: ToolContext):
    # Tool implementation
```

### Best Practices for Auth Configuration

1. **Environment Variables**: Always store secrets in environment variables, never in code
2. **Minimal Scopes**: Request only the permissions you need
3. **Token Security**: All tokens are encrypted at rest by Arcade
4. **Audit Logging**: All auth events are logged for compliance
5. **Token Rotation**: Implement automatic token refresh where supported
6. **Rate Limiting**: Be aware of provider-specific rate limits
7. **Error Handling**: Implement proper error handling for auth failures

### Troubleshooting Auth Issues

**Common Issues:**
- **Invalid redirect URI**: Ensure the redirect URL matches exactly
- **Scope errors**: Check that requested scopes are enabled in your app
- **Token expiration**: Implement refresh token handling
- **Rate limits**: Monitor and respect provider rate limits
- **Multiple providers**: Use unique IDs and specify in tools

### Arcade Registry Arcade.dev is collecting all the integrations that agents will ever need in one place - think HuggingFace or Pypi but for LLM tools. A powerful community of open source and for-profit developers building out robust and evaluated workflows is how agents can be elevated to being truly useful.

**Key Components:**
- **Runtime-coupled Registry**: Unlike traditional read-only tool libraries, Arcade couples the runtime with the registry
- **Real Metrics & Usage**: Collect real metrics and usage information about your tools
- **Developer Feedback**: Get error reports and statistics about how your tools are being used  
- **Monetization Options**: Optionally choose to sell your tools with a markup on top of Arcade platform fees
- **Multi-protocol Support**: Available via MCP for locally-running applications, OXP for server applications, and future protocols
- **Future-proof**: Use open-source Arcade SDKs to future-proof your tools

**Features:**
- Verified tool quality
- Version management
- Dependency resolution
- Security scanning
- Community contributions
- Usage analytics
- Error reporting
- Revenue sharing for paid tools

**Access:**
```bash
# Search registry
arcade registry search email

# Install from registry
arcade registry install gmail-toolkit

# Publish your toolkit
arcade registry publish my-toolkit
```

**Early Access Beta:**
Arcade is seeking beta testers interested in building, maintaining, and sharing toolkits with the world in either a free-to-use or for-profit manner. Join the Arcade Registry Beta to:
- Share your tools with the AI community
- Get real usage metrics and feedback
- Optionally monetize your toolkits
- Help shape the future of AI tool distribution

### FAQ

#### What if I need a Tool that doesn't exist?

You have several options:

1. **Check the Registry**: Search for community-built tools
2. **Request a Tool**: Submit a feature request
3. **Build Custom Tool**: Create your own using the Toolkit SDK
4. **Contribute**: Submit to the community registry

#### How does authentication work?

Arcade handles OAuth flows automatically:

1. Tool requests authentication
2. User is redirected to provider
3. Tokens are securely stored
4. Automatic token refresh
5. Secure token transmission

#### Can I use Arcade in production?

Yes! Arcade is production-ready with:

- Enterprise security features
- 99.9% uptime SLA
- Scalable infrastructure  
- 24/7 support
- Audit logging
- Compliance certifications

#### How much does Arcade cost?

Arcade offers flexible pricing:

- **Developer**: Free tier for development
- **Startup**: $29/month for small teams
- **Business**: $99/month for growing companies
- **Enterprise**: Custom pricing for large organizations

#### How do I get support?

Multiple support channels:

- **Documentation**: Comprehensive guides
- **Community**: Discord server
- **Email**: support@arcade.dev
- **Enterprise**: Dedicated support team

### Changelog

Recent updates to Arcade:

**v2.1.0** (Latest)
- New Google Workspace toolkits
- Enhanced authentication flows
- Performance improvements
- Bug fixes

**v2.0.0** 
- MCP integration
- Hybrid deployment support
- New CLI interface
- Breaking changes from v1.x

**v1.5.0**
- Slack toolkit enhancements
- GitHub integration improvements
- Security updates

### Migration Guide

If your project does not use v2 syntax, follow this migration guide:

#### Key Changes in v2:

1. **New Authentication System**: OAuth flows simplified
2. **Toolkit Structure**: Reorganized tool categories  
3. **API Changes**: Some method signatures updated
4. **Configuration**: New config file format

#### Migration Steps:

```python
# v1 syntax (deprecated)
from arcade import Tool

tool = Tool("gmail")
result = tool.send_email(to="user@example.com")

# v2 syntax (current)
from arcade.toolkits import Gmail

gmail = Gmail(auth_provider="google")
result = gmail.send_message(to="user@example.com")
```

#### Breaking Changes:

- Tool initialization requires explicit auth provider
- Some tool names have changed
- Configuration file format updated
- Environment variable names changed

### Community & Contributing

#### Contribute a Toolkit

Help expand the Arcade ecosystem:

1. **Plan Your Toolkit**: Define tools and use cases
2. **Set Up Development**: Clone toolkit template
3. **Implement Tools**: Build individual tool functions
4. **Add Tests**: Ensure quality and reliability
5. **Submit PR**: Contribute to community

```python
# Toolkit template structure
from arcade import Toolkit, tool

class MyServiceToolkit(Toolkit):
    def __init__(self):
        super().__init__(
            name="myservice",
            description="Tools for MyService API",
            version="1.0.0"
        )
    
    @tool
    def example_tool(self, param: str) -> str:
        """Example tool implementation"""
        return f"Processed: {param}"
```

#### Community Toolkit Template

Use the official template to get started:

```bash
# Clone template
git clone https://github.com/arcade-ai/community-toolkit-template

# Customize for your service
cd community-toolkit-template
./setup.py --name myservice --author "Your Name"

# Start development
pip install -e .
arcade serve --dev
```

---

## Support & Community

### Contact Us

We're here to help you succeed with Arcade! Choose the support channel that best fits your needs:

**Community Support**
- Discord Server: Real-time chat with the community
- GitHub Discussions: Long-form technical discussions
- Stack Overflow: Tag questions with `arcade-ai`

**Business Support**  
- Email: support@arcade.dev
- Slack Connect: For enterprise customers
- Phone: Available for Enterprise plans

**Sales & Partnerships**
- Email: sales@arcade.dev
- Schedule Demo: Book time with our team
- Partner Program: partners@arcade.dev

**Security & Compliance**
- Security Issues: security@arcade.dev
- Compliance Questions: compliance@arcade.dev

### Office Hours
- **Community Office Hours**: Fridays 2-3 PM EST
- **Enterprise Support**: 24/7 for Enterprise customers
- **Response Times**: 
  - Community: Best effort
  - Startup: 24 hours
  - Business: 8 hours  
  - Enterprise: 2 hours

---

## Conclusion

This comprehensive documentation covers all aspects of Arcade.dev, from getting started to advanced deployment scenarios. Arcade provides a powerful platform for building AI agents that can take real actions in the world through its extensive toolkit ecosystem and robust infrastructure.

Whether you're building simple automation or complex multi-agent workflows, Arcade's tools, authentication system, and deployment options provide the foundation you need to move from prototype to production.

For the latest updates and detailed API references, visit [docs.arcade.dev](https://docs.arcade.dev).

---

*Documentation generated from comprehensive crawl of docs.arcade.dev - 148 pages captured and organized*