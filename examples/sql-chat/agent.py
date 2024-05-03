import httpx
import json
import time
import openai
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from typing import List, Dict
from textwrap import dedent

from pydantic import BaseModel, Field
from enum import Enum
from typing import Type
from toolserve.utils.openai_tool import model_to_json_schema

from typing import Dict, Any, Optional
import json
from collections import deque



class ToolClient:

    available_tools = {
        "query_sql": "/tool/query/query_sql",
        "list_data_sources": "/tool/query/list_data_sources",
        "get_data_schema": "/tool/query/get_data_schema",
        "PlotDataframe": "/tool/gmailer/PlotDataframe",
        "ReadEmail": "/tool/gmailer/ReadEmail",
        "Summarize": "/tool/chat/Summarize",
    }

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30)
        self.tools = self.__collect_tool_specs()

    def __collect_tool_specs(self) -> Dict[str, str]:
        tools = {}
        for tool_name, endpoint in self.available_tools.items():
            openai_spec = self.call_api("GET", "/api/v1/tools/oai_function", params={"tool_name": tool_name}).get("data", {})
            tools[tool_name] = openai_spec
        return tools

    def call_api(self, method: str, endpoint: str, params: dict = {}, data: dict = {}, json_data: dict = {}) -> Dict[str, Any]:
        """Call the Darkstar Toolserver API with the given parameters.

        Args:
            method (str): The HTTP method to use for the request.
            endpoint (str): The endpoint to call.
            params (dict): The query parameters for the request.
            data (dict): The data to send in the request body.
            json_data (dict): The JSON data to send in the request body.

        Returns:
            Dict[str, Any]: The response from the API.
        """
        url = f"{self.base_url}{endpoint}"
        response = self.client.request(method, url, params=params, json=json_data, data=data)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e}")
        result = response.json()
        return result

    def execute_tool(self, tool_name: str, tool_args: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes an tool using the Darkstar Toolserver API and an OpenAI model.

        :param tool_name: The name of the tool to execute.
        :return: The result of the tool
        """

        # Prepare the input message for the OpenAI model
        endpoint = self.available_tools[tool_name]
        result = self.call_api("POST", endpoint, json_data=tool_args)
        return result




class ToolRunner:

    tool_prompt = dedent("""
    Given a user query and the schema of the fields in a dataframe, generate the arguments for a tool to execute.

    YOU MUST CALL THE TOOL.

    The schema of the fields in the dataframe is as follows:
    {schema}

    If needed, the data_id for the source is: {data_id}
    If needed, the output_name should be: {output_name}
    """)

    def __init__(self, base_url: str, model: str, api_key: str):
        """
        Initialize the ToolRunner with necessary configurations.

        Args:
            base_url (str): The base URL for the API calls.
            model (str): The model identifier to be used for queries.
            api_key (str): The API key for authentication.
        """
        self._client = ToolClient(base_url)

        self._model = model
        self._openai_client = openai.Client(api_key=api_key)

        self._data_sources = self.__get_data_sources()
        self._source = None
        self._data_schema = None
        self._data_id = None

    def set_source(self, source: str):
        self._data_sources = self.__get_data_sources()

        if not source:
            return

        retries = 3
        data_id = None
        while retries > 0:
            try:
                data_id = self._data_sources[source]
                break
            except KeyError:
                retries -= 1
                time.sleep(1)
                self._data_sources = self.__get_data_sources()

        if data_id is None:
            raise ValueError(f"Data source '{source}' not found.")

        # get the schema
        schema = self._client.call_api("POST", "/tool/query/get_data_schema", json_data={"data_id": data_id})
        self._source = source
        self._data_schema = schema
        self._data_id = data_id

    def __get_data_sources(self) -> Dict[str, Dict[str, str]]:
        response = self._client.call_api("POST", "/tool/query/list_data_sources")
        sources = {}
        for _id, source_data in response["data"]["result"].items():
            sources[source_data["file_name"]] = _id
        return sources

    def __create_prompt(self, user_query: str, input_name: str, output_name: str) -> List[Dict[str, str]]:
        schema = self._data_schema
        data_id = "No input"
        if input_name:
            data_id = self._data_sources[input_name]
        prompt = self.tool_prompt.format(schema=schema, data_id=data_id, output_name=output_name)

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query}
        ]
        return messages

    def get_tool_args(self, tool_name: str, messages: List[Dict[str, str]], output_name: str) -> Dict[str, Any]:
        """
        Retrieves the required arguments for an tool from the Darkstar Toolserver API and
        uses them to call an OpenAI model with predefined tools and messages.

        :param tool_name: The name of the tool to execute.
        :param messages: A list of messages to provide to the model.
        :return: The result of the OpenAI model call.
        """
        func_spec = self._client.tools.get(tool_name, {})
        if not func_spec:
            raise ValueError(f"Tool '{tool_name}' not found in available tools.")

        tool = json.loads(func_spec)
        print(tool)
        # Call the OpenAI model with the tools and messages
        completion = self._openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            tools=[tool],
            tool_choice="required"
        )
        predicted_args = completion.choices[0].message.tool_calls[0].function.arguments

        args = json.loads(predicted_args)
        if "params" in args:
            params = args.get("params", [])
            if params:
                if isinstance(params, dict):
                    args["params"] = list(params.values())
                elif isinstance(params, str):
                    args["params"] = [params]
                elif isinstance(params, list):
                    args["params"] = params
                else:
                    raise ValueError(f"Invalid params type: {type(params)}")

        if "output_name" in args and output_name != "None":
            args["output_name"] = output_name
        if "data_id" in args:
            args["data_id"] = self._data_id

        return args

    def run_tool(self, tool_name: str, user_query: str, source: str, output_name: str) -> Any:
        """
        Executes an tool using the Darkstar Toolserver API and an OpenAI model.

        :param tool_name: The name of the tool to execute.
        :param user_query: The user query to provide to the model.
        :return: The result of the tool
        """
        self.set_source(source)
        print(f"Tool Name: {tool_name}")
        print(f"Data ID: {self._data_id}")
        print(f"Sourcing data from {source}")
        messages = self.__create_prompt(user_query, source, output_name)
        tool_args = self.get_tool_args(tool_name, messages, output_name)
        result = self._client.execute_tool(tool_name, tool_args)
        return result

    def get_data_object(self, data_id: int) -> Dict[str, Any]:
        """
        Retrieves a data object from the Darkstar Toolserver API.

        :param data_id: The ID of the data object to retrieve.
        :return: The data object.
        """
        return self._client.call_api("GET", f"/api/v1/data/object/{data_id}")["data"]["json_blob"]


def pydantic_to_openai_tool(model: Type[BaseModel]) -> str:
    """
    Convert a Pydantic model to an OpenAI tool schema.

    Args:
        model (Type[BaseModel]): The Pydantic model to convert.

    Returns:
        str: The OpenAI tool schema.
    """
    schema = model_to_json_schema(model)
    tool_schema = {
        "type": "function",
        "function": {
            "name": model.__name__,
            "description": model.__doc__ or "",
            "parameters": schema
        }
    }
    return json.dumps(tool_schema)

class Edge(BaseModel):
    source: int = Field(..., description="The ID of the source node")
    target: int = Field(..., description="The ID of the target node")

class ToolNode(BaseModel):
    node_id: int = Field(..., description="The ID of the node", ge=0)
    input_name: Optional[str] = Field(None, description="The name of the input data")
    tool_name: str = Field(..., description="The name of the tool to execute")
    output_name: Optional[str] = Field(..., description="The name of the output data")

class OutputType(Enum):
    DATA = "data"
    CHAT = "chat"
    ARTIFACT = "artifact"

class FlowSchema(BaseModel):
    """A graph based representation of functions (nodes), and their data flow (edges)"""

    nodes: List[ToolNode] = Field(..., description="The nodes in the flow")
    edges: List[Edge] = Field([], description="The IDs of the adjacent nodes")
    output_type: OutputType = Field(OutputType.CHAT, description="The type of the output")

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True

class ToolFlow:

    tools = {
        "query_sql": (OutputType.DATA, True, False),
        "PlotDataframe": (OutputType.ARTIFACT, False, True),
        "ReadEmail": (OutputType.CHAT, True, False),
        "Summarize": (OutputType.CHAT, False, True),

    }

    def __init__(
        self,
        name: str,
        description: str,
        prompt: str,
        base_url: str = "http://localhost:8000",
        model: str = "gpt-4-turbo",
        model_api_key: Optional[str] = None
        ):
        self.name = name
        self.description = description
        self.prompt = prompt
        self.runner = ToolRunner(base_url, model, model_api_key)
        self.model = model
        self.openai_client = openai.Client(api_key=model_api_key)


    def __create_prompt(self, user_query: str) -> List[Dict[str, str]]:
        tool_list = ""
        for tool, spec in self.tools.items():
            tool_list += f"- Name: {tool}\n"
            tool_list += f" - Output Type: {spec[0].value}\n"
            tool_list += f" - Can be source node: {spec[1]}\n"
            tool_list += f" - Can be sink node: {spec[2]}\n"

        source_list = "\n".join(self.runner._data_sources.keys())

        prompt = self.prompt.format(nodes=tool_list, sources=source_list)

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query}
        ]
        return messages

    def infer_flow(self, user_query: str) -> FlowSchema:
        """
        Infer the tool flow based on the user query.

        Args:
            user_query (str): The user's query string.

        Returns:
            FlowSchema: The inferred tool flow schema.
        """
        messages = self.__create_prompt(user_query)

        func_spec = pydantic_to_openai_tool(FlowSchema)
        tool = json.loads(func_spec)

        # Call the OpenAI model with the tools and messages
        completion = self.openai_client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=[tool],
            tool_choice="required"
        )
        predicted_args = completion.choices[0].message.tool_calls[0].function.arguments
        print(predicted_args)
        return predicted_args


    def execute_flow(self, flow_schema: Dict[str, Any], user_query: str) -> Any:
        """
        Executes the tool flow based on the provided schema. This method performs a breadth-first search (BFS)
        on the graph defined by the flow schema and executes each node according to the order determined by the BFS.

        Args:
            flow_schema (Dict[str, Any]): The schema representing the tool flow to be executed.
            user_query (str): The user's query string that may influence tool execution.

        Returns:
            Any: The result of executing the tool flow.
        """


        # Initialize a queue for BFS
        execution_queue = deque([flow_schema['nodes'][0]])  # Start BFS from the source node
        visited = set()
        results = {}

        while execution_queue:
            current_node = execution_queue.popleft()
            node_id = current_node['node_id']

            if node_id in visited:
                continue
            visited.add(node_id)

            # Execute the current node's operation using runner.run_tool
            operation_result = self.runner.run_tool(
                current_node['tool_name'],
                user_query,
                current_node['input_name'],
                current_node['output_name']
            )
            results[node_id] = operation_result

            # Enqueue all adjacent nodes
            for edge in flow_schema.get('edges', []):
                if edge['source'] == node_id:
                    target_node_id = edge['target']
                    target_node = next(node for node in flow_schema['nodes'] if node['node_id'] == target_node_id)
                    if target_node_id not in visited:
                        execution_queue.append(target_node)

        # Assuming the last node processed is the sink node
        sink_node = flow_schema['nodes'][-1]
        sink_tool_name = sink_node['tool_name']
        sink_node_id = sink_node['node_id']
        sink_output_type = self.tools[sink_tool_name][0]
        if sink_output_type == OutputType.DATA:
            data = self.runner.get_data_object(self.runner._data_id)
        elif sink_output_type == OutputType.CHAT:
            data = results[sink_node_id]["data"]["result"]
        else:
            data = results[sink_node_id]

        return (data, results, sink_output_type)


def summarize_flow_results(model_client, flow_results: Dict[str, Any], flow_schema) -> str:
    """
    Summarizes the results of a tool flow execution using an OpenAI model to generate a chat response.

    Args:
        model_client (openai.Client): The OpenAI client to use for generating chat responses.
        flow_results (Dict[str, Any]): The results of the tool flow execution.
        flow_schema (Dict[str, Any]): The schema representing the tool flow.


    Returns:
        Dict[str, str]: A dictionary containing the chat response under the key "data".
    """
    try:
        # Check if flow_results is already a JSON string, otherwise convert it
        if isinstance(flow_results, str):
            flow_summary = flow_results
        else:
            flow_summary = json.dumps(flow_results, indent=2)

        # Construct a concise and informative prompt for the chat model
        prompt_content = dedent(f"""
            Please review the tool execution results and the flow schema provided below.
            Use the results of the final tool to describe the outcomes. Be concise and only use the provided information.
            If the results seem incorrect or incomplete, kindly ask the user to reformulate their query for better accuracy.

            The execution path, expressed a a JSON object where nodes represent tools and edges represent data flow:
            {flow_schema}

            The results of the execution, expressed as a JSON object:
            {flow_summary}

        """)

        messages = [
            {"role": "system", "content": prompt_content}
        ]

        # Call the OpenAI chat model
        response = model_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages
        )

        # Extract the chat response
        chat_response = response.choices[0].message.content
        return chat_response
    except Exception as e:
        print(f"Error in summarizing flow results: {e}")
        return "Error: Failed to generate summary due to an internal error."





email_flow = FlowSchema(
    nodes=[
        ToolNode(node_id=0, input_name=None, tool_name="ReadEmail", output_name="email_data_1"),
        ToolNode(node_id=1, input_name="email_data_1", tool_name="Summarize", output_name=None),
    ],
    edges=[
        Edge(source=0, target=1)
    ],
    output_type=OutputType.CHAT
)


class Agent:

    def __init__(self, flows: Dict[str, FlowSchema]):
        self.flows = flows








#flow_schema = tf.infer_flow("Plot the users' age distribution")
#from pprint import pprint
#flow = json.loads(flow_schema)
#pprint(flow)
#result = tf.execute_flow(flow, "Plot the users' age distribution")
#print(result)
