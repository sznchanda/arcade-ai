import httpx
import json
import openai
from typing import Any, Dict, List, Optional

class Toolchain:

    available_tools = {
        "query_sql": "/tool/query/query_sql",
        "list_data_sources": "/tool/query/list_data_sources",
        "get_data_schema": "/tool/query/get_data_schema"
    }

    def __init__(self, base_url: str, openai_api_key: str, model: str = "gpt-4-turbo"):
        self.base_url = base_url
        self.client = httpx.Client()
        self.openai_client = openai.Client(api_key=openai_api_key)
        self.model = model
        self.tools = self.__collect_tool_specs()

    def __collect_tool_specs(self) -> Dict[str, str]:
        tools = {}
        for tool_name, endpoint in self.available_tools.items():
            openai_spec = self.call_api("GET", "/api/v1/tools/oai_function", params={"tool_name": tool_name}).get("data", {})
            tools[tool_name] = openai_spec
        return tools

    def call_api(self, method: str, endpoint: str, params: dict = {}, data: dict = {}, json_data: dict = {}) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        response = self.client.request(method, url, params=params, json=json_data, data=data)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error: {e}")
        result = response.json()
        return result

    def get_tool_args(self, tool_name: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Retrieves the required arguments for an tool from the Darkstar Toolserver API and
        uses them to call an OpenAI model with predefined tools and messages.

        :param tool_name: The name of the tool to execute.
        :param messages: A list of messages to provide to the model.
        :return: The result of the OpenAI model call.
        """
        func_spec = self.tools.get(tool_name, {})
        if not func_spec:
            raise ValueError(f"Tool '{tool_name}' not found in available tools.")

        tool = json.loads(func_spec)
        # Call the OpenAI model with the tools and messages
        completion = self.openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            tools=[tool],
            tool_choice="auto"
        )
        predicted_args = completion.choices[0].message.tool_calls[0].function.arguments
        print(predicted_args)
        print("-----")
        return predicted_args

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


from pydantic import BaseModel
from typing import List, Dict
from textwrap import dedent

class Agent:

    prompt = dedent("""Given a user query and a schema of a table, generate the SQL query to answer the user query.


    The generated SQL query should only refer to columns in the table schema list below. The table schema is as follows:
    {schema}

    The data_id of this source is: {data_id}
    """)


    def __init__(self, toolchain: Toolchain):
        self.toolchain = toolchain
        self.data_sources = self.__get_data_sources()
        self._source = None
        self._data_schema = None

    def set_source(self, source: str):
        if source not in self.data_sources.keys():
            raise ValueError(f"Data source '{source}' not found.")
        else:
            data_id = self.data_sources[source]
            # get the schema
            schema = self.toolchain.call_api("POST", "/tool/query/get_data_schema", json_data={"data_id": data_id})
            self._source = source
            self._data_schema = schema

    def get_source(self) -> str:
        return self._source

    def __get_data_sources(self) -> Dict[str, Dict[str, str]]:
        response = self.toolchain.call_api("POST", "/tool/query/list_data_sources")
        sources = {}
        for _id, source_data in response["data"]["result"].items():
            sources[source_data["file_name"]] = _id
        return sources


    def query(self, user_query: str) -> str:
        if not self._source:
            raise ValueError("Data source not set. Please set a data source before querying.")
        schema = self._data_schema
        prompt = self.prompt.format(schema=schema, data_id=self.data_sources[self._source])

        # Prepare the input message for the OpenAI model
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_query}]

        tool_args = self.toolchain.get_tool_args("query_sql", messages)
        args = json.loads(tool_args)
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


        response = self.toolchain.execute_tool("query_sql", args)
        if response["code"] != 200:
            raise ValueError(f"Error executing tool: {response['message']}")
        data_id = response["data"]["result"]["data_id"]

        # get the data
        data_response = self.toolchain.call_api("GET", f"/api/v1/data/object/{data_id}")
        if data_response["code"] != 200:
            raise ValueError(f"Error retrieving data: {data_response['message']}")
        data = data_response["data"]["json_blob"]
        return data


from pydantic import BaseModel, Field
from enum import Enum

class ToolNode:
    pass

class ToolFlow:

    def __init__(
        self,
        name,
        description,
        sources,
        ):
        pass




""" # Example usage:
oai_key = "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"
toolchain = Toolchain(base_url="http://localhost:8000", model="gpt-4-turbo", openai_api_key=oai_key)
agent = Agent(toolchain)
agent.set_source("users_db")

while True:
    user_query = input("Enter a query: ")
    result = agent.query(user_query)
    print(result)
 """