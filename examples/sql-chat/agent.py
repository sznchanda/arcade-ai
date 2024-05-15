import httpx
import json
import time
import openai
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

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
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), description="UUID for the data flow between nodes")

class ToolNode(BaseModel):
    node_id: int = Field(..., description="The ID of the node", ge=0)
    input_name: Optional[str] = Field(None, description="The name of the input data")
    tool_name: str = Field(..., description="The name of the tool to execute")
    output_name: Optional[str] = Field(None, description="The name of the output data")
    predict_args: bool = Field(True, description="Whether to predict the arguments for the tool")
    from_node: Optional[Dict[str, int]] = Field(None, description="The ID of the source node name of the argument to pass to the tool")
    args: Optional[Dict[str, Any]] = Field(None, description="The arguments to pass to the tool")
    allow_extra: bool = Field(False, description="Whether to allow extra arguments to be passed to the tool")

class OutputType(Enum):
    DATA = "data"
    CHAT = "chat"
    ARTIFACT = "artifact"

class FlowSchema(BaseModel):
    """A graph based representation of functions (nodes), and their data flow (edges)"""

    nodes: List[ToolNode] = Field(..., description="The nodes in the flow")
    edges: List[Edge] = Field([], description="The IDs of the adjacent nodes")
    output_type: OutputType = Field(OutputType.CHAT, description="The type of the output")

    def __init__(self, **data):
        super().__init__(**data)
        self.generate_uuids_for_edges()

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True

    def generate_uuids_for_edges(self):
        edge_map = {}
        for edge in self.edges:
            edge_map[(edge.source, edge.target)] = edge.uuid
        for node in self.nodes:
            incoming_edges = [e.uuid for e in self.edges if e.target == node.node_id]
            outgoing_edges = [e.uuid for e in self.edges if e.source == node.node_id]
            if node.from_node:
                node.input_name = None
                node.output_name = None
                # Set the output of the source node and the input of the target node to None
                for edge in self.edges:
                    if edge.target == node.node_id:
                        source_node = next((n for n in self.nodes if n.node_id == edge.source), None)
                        if source_node:
                            source_node.output_name = None
                    if edge.source == node.node_id:
                        target_node = next((n for n in self.nodes if n.node_id == edge.target), None)
                        if target_node:
                            target_node.input_name = None
            else:
                node.input_name = incoming_edges[0] if incoming_edges else None
                node.output_name = outgoing_edges[0] if outgoing_edges else None

class ToolClient:

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(timeout=3000)
        tools, routes = self.__collect_tool_specs()
        self.tools = tools
        self.available_tools = routes


    def __collect_tool_specs(self) -> Dict[str, str]:
        tools_list = self.call_api("GET", "/api/v1/tools/list").get("data", {})
        all_tools = [tool["name"] for tool in tools_list]
        routes = {tool["name"]: tool["endpoint"] for tool in tools_list}
        tools = {}
        for tool_name, endpoint in routes.items():
            openai_spec = self.call_api("GET", "/api/v1/tools/oai_function", params={"tool_name": tool_name}).get("data", {})
            tools[tool_name] = openai_spec
        return tools, routes

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

        return args

    def run_tool(self, tool: ToolNode, user_query: str, **kwargs) -> Any:
        """
        Executes an tool using the Darkstar Toolserver API and an OpenAI model.
        """
        source = None
        if tool.input_name:
            source = tool.input_name
        self.set_source(source)

        if tool.predict_args:
            messages = self.__create_prompt(user_query, source, tool.output_name)
            tool_args = self.get_tool_args(tool.tool_name, messages, tool.output_name)
        else:
            tool_args = kwargs.get("tool_args", {})

        # TODO would something ever have an input_name and not need a data_id?
        if tool.input_name:
            tool_args["data_id"] = self._data_id

        if tool.output_name:
            tool_args["output_name"] = tool.output_name

        if tool.args:
            tool_args.update(tool.args)

        print("Calling tool with args:", tool_args)
        result = self._client.execute_tool(tool.tool_name, tool_args)
        return result

    def get_data_object(self, data_id: int) -> Dict[str, Any]:
        """
        Retrieves a data object from the Darkstar Toolserver API.

        :param data_id: The ID of the data object to retrieve.
        :return: The data object.
        """
        return self._client.call_api("GET", f"/api/v1/data/object/{data_id}")["data"]["json_blob"]




class ToolFlow:

    def __init__(
        self,
        name: str,
        description: str,
        base_url: str = "http://localhost:8000",
        model: str = "gpt-4-turbo",
        model_api_key: Optional[str] = None
        ):
        self.name = name
        self.description = description

        self.runner = ToolRunner(base_url, model, model_api_key)
        self.model = model
        self.openai_client = openai.Client(api_key=model_api_key)


    def execute_flow(self, flow_schema: Dict[str, Any], user_query: str, user_args: Dict[str, Any] = {}) -> Any:
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
        # Queue up all nodes which don't have incoming edges
        incoming_edges = {node['node_id']: 0 for node in flow_schema['nodes']}
        for edge in flow_schema.get('edges', []):
            incoming_edges[edge['target']] += 1
        execution_queue = deque([node for node in flow_schema['nodes'] if incoming_edges[node['node_id']] == 0])

        visited = set()
        results = {}
        timings = {}

        flow_start_time = time.time()
        while execution_queue:
            current_node = execution_queue.popleft()
            node_id = current_node['node_id']

            if node_id in visited:
                continue
            visited.add(node_id)

            exec_start_time = time.time()

            tool_args = {}
            # Execute the current node's operation using runner.run_tool
            current_tool = ToolNode(**current_node)
            if current_tool.from_node:
                tool_args = {}
                for arg_name, from_node_id in current_tool.from_node.items():
                    from_node_result = results[from_node_id]["data"]["result"]
                    tool_args[arg_name] = from_node_result
            if current_tool.allow_extra:
                tool_args.update(user_args)
            operation_result = self.runner.run_tool(current_tool, user_query, tool_args=tool_args)

            results[node_id] = operation_result
            exec_end_time = time.time()
            timings[current_tool.tool_name] = exec_end_time - exec_start_time

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
        # TODO: Tools need to specify output type
        #sink_output_type = self.tools[sink_tool_name][0]
        sink_output_type = OutputType(flow_schema['output_type'])

        flow_end_time = time.time()
        timings['total'] = flow_end_time - flow_start_time

        if sink_output_type == OutputType.DATA:
            data = self.runner.get_data_object(self.runner._data_id)
        elif sink_output_type == OutputType.CHAT:
            data = results[sink_node_id]["data"]["result"]
        else:
            data = results[sink_node_id]

        return (data, results, sink_output_type, timings)


review_db = "/Users/spartee/Dropbox/Arcade/platform/toolserver/examples/data/food-reviews/database.sqlite"
review_flow = FlowSchema(
    nodes=[
        ToolNode(node_id=0, tool_name="ReadSqlite", args={"table_name": "Reviews", "file_path": review_db}, predict_args=False),
        ToolNode(node_id=1, tool_name="query_sql"),
        ToolNode(node_id=2, tool_name="search_text_columns"),
        ToolNode(node_id=3, tool_name="Summarize", from_node={"text": 2}, predict_args=False),
    ],
    edges=[
        Edge(source=0, target=1),
        Edge(source=1, target=2),
        Edge(source=2, target=3)
    ],
    output_type=OutputType.CHAT
)

plotting_flow = FlowSchema(
    nodes=[
        ToolNode(node_id=0, tool_name="ReadSqlite", args={"table_name": "Reviews", "file_path": review_db}, predict_args=False),
        ToolNode(node_id=1, tool_name="query_sql"),
        ToolNode(node_id=2, tool_name="PlotDataframe"),
    ],
    edges=[
        Edge(source=0, target=1),
        Edge(source=1, target=2)
    ],
    output_type=OutputType.ARTIFACT
)


email_flow = FlowSchema(
    nodes=[
        ToolNode(node_id=0, tool_name="ReadEmail"),
        ToolNode(node_id=1, tool_name="Summarize", from_node={"text": 0}, predict_args=False),
    ],
    edges=[
        Edge(source=0, target=1)
    ],
    output_type=OutputType.CHAT
)



shopify_db = "/Users/spartee/Dropbox/Arcade/platform/toolserver/examples/data/olist.sqlite"
customer_flow = FlowSchema(
    nodes=[
        ToolNode(node_id=0, tool_name="ReadSqlite", args={"table_name": "customers", "file_path": shopify_db}, predict_args=False),
        ToolNode(node_id=1, tool_name="ReadSqlite", args={"table_name": "orders", "file_path": shopify_db}, predict_args=False),
        ToolNode(node_id=2, tool_name="query_sql"),
        ToolNode(node_id=3, tool_name="query_sql"),
        ToolNode(node_id=4, tool_name="get"),
        ToolNode(node_id=5, tool_name="get"),
        ToolNode(node_id=6, tool_name="combine_results", from_node={"result_1": 4, "result_2": 5}, predict_args=False),
        ToolNode(node_id=7, tool_name="Summarize", from_node={"text": 6}, predict_args=False)
    ],
    edges=[
        Edge(source=0, target=2),
        Edge(source=1, target=3),
        Edge(source=2, target=4),
        Edge(source=3, target=5),
        Edge(source=4, target=6),
        Edge(source=5, target=6),
        Edge(source=6, target=7)
    ],
    output_type=OutputType.CHAT
)


audio_files = ["/Users/spartee/Desktop/notes.mp3"]
notetaker = FlowSchema(
    nodes=[
        ToolNode(node_id=0, tool_name="TranscribeText", predict_args=False, allow_extra=True),
        ToolNode(node_id=1, tool_name="Summarize", from_node={"text": 0}, predict_args=False),
    ],
    edges=[
        Edge(source=0, target=1)
    ],
    output_type=OutputType.CHAT
)


def print_flow_as_yaml(data: Dict[str, Any]):

    data_dict = data.dict(exclude_unset=True) if isinstance(data, BaseModel) else data
    # Convert the dictionary to a YAML formatted string
    yaml_str = yaml.dump(data_dict, sort_keys=False)

    # Print the YAML string
    print(yaml_str)








#flow_schema = tf.infer_flow("Plot the users' age distribution")
#from pprint import pprint
#flow = json.loads(flow_schema)
#pprint(flow)
#result = tf.execute_flow(flow, "Plot the users' age distribution")
#print(result)
