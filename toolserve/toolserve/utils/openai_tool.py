import json
from typing import Any, Dict, Type, Union, List
from pydantic import BaseModel, Field
from datetime import datetime

from toolserve.server.core.catalog import ParameterSchema

# TODO clean this up

PYTHON_TO_JSON_TYPES = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}

def python_type_to_json_type(python_type: Type) -> Dict[str, Any]:
    """
    Map Python types to JSON Schema types, including handling of complex types such as lists and dictionaries.

    Args:
        python_type (Type): The Python type to be converted to a JSON schema type.

    Returns:
        Dict[str, Any]: A dictionary representing the JSON schema for the given Python type.
    """
    if hasattr(python_type, '__origin__'):  # For generic types like List[str] or Dict[str, int]
        origin = python_type.__origin__
        if origin is list:
            item_type = python_type_to_json_type(python_type.__args__[0])
            return {'type': 'array', 'items': {'type': item_type}}
        elif origin is dict:
            # Handle dictionary with specific key and value types
            key_type = python_type_to_json_type(python_type.__args__[0])
            value_type = python_type_to_json_type(python_type.__args__[1])
            return {'type': 'object', 'additionalProperties': {'type': value_type}}
    #elif issubclass(python_type, BaseModel):  # For Pydantic models
    #    return model_to_json_schema(python_type)
    return PYTHON_TO_JSON_TYPES.get(python_type, "string")

def parameter_schema_to_json(parameter_schema: 'ParameterSchema') -> Dict[str, Any]:
    """Convert a ParameterSchema to a JSON schema property."""
    property_schema = {
        "type": python_type_to_json_type(parameter_schema.dtype),
        "description": parameter_schema.description,
    }
    if parameter_schema.default is not None:
        property_schema["default"] = parameter_schema.default
    return property_schema

def model_to_json_schema(model: Type[BaseModel]) -> Dict[str, Any]:
    """Convert a Pydantic model to a JSON schema."""
    properties = {}
    required = []
    for field_name, model_field in model.model_fields.items():
        field_schema = parameter_schema_to_json(
            ParameterSchema(
                name=field_name,
                dtype=model_field.annotation,
                description=model_field.description or "",
                default=model_field.default,
                required=model_field.required
            )
        )
        properties[field_name] = field_schema
        if model_field.is_required():
            required.append(field_name)
    return {
        "type": "object",
        "properties": properties,
        "required": required,
    }

def schema_to_openai_tool(action_schema: 'ActionSchema') -> str:
    """Convert an ActionSchema object to a JSON schema string in the specified function format.

    Example output format:
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    }

    Args:
        action_schema (ActionSchema): The action schema to convert.

    Returns:
        str: A JSON schema string representing the action in the specified format.
    """
    properties = {}
    required = []
    if action_schema.in_schema:
        for input_param in action_schema.in_schema.inputs:
            param_schema = parameter_schema_to_json(input_param)
            properties[input_param.name] = param_schema
            if input_param.required:
                required.append(input_param.name)

    function_schema = {
        "type": "function",
        "function": {
            "name": action_schema.name,
            "description": action_schema.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        }
    }
    return json.dumps(function_schema, indent=2)
