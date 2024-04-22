

import os
import sys
import inspect
from datetime import datetime
from typing import List, Optional, Type, Dict, Annotated, Any, Callable, Tuple
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel, ValidationError, Field, create_model
from importlib import import_module

from toolserve.server.core.conf import settings
from toolserve.common.response_code import CustomResponseCode
from toolserve.common.response import ResponseModel, response_base
from toolserve.apm.base import ToolPack
from toolserve.sdk import Param, Secret

class ToolMeta(BaseModel):
    module: str
    path: str
    date_added: datetime = Field(default_factory=datetime.now)
    date_updated: datetime = Field(default_factory=datetime.now)


class ToolSchema(BaseModel):
    name: str
    description: str
    version: str
    tool: Callable

    input_model: Type[BaseModel]
    output_model: Type[BaseModel]

    meta: ToolMeta


class ToolCatalog:
    def __init__(self, tools_dir: str = settings.TOOLS_DIR):
        self.tools = self.read_tools(tools_dir)

    @staticmethod
    def read_tools(directory: str) -> List[ToolSchema]:
        toolpack = ToolPack.from_lock_file(directory)
        sys.path.append(str(Path(directory).resolve() / 'tools'))

        tools = {}
        for name, tool_spec in toolpack.tools.items():
            module_name, versioned_tool = tool_spec.split('.', 1)
            func_name, version = versioned_tool.split('@')

            module = import_module(module_name)
            tool = getattr(module, func_name)

            tool_meta = ToolMeta(
                module=module_name,
                path=module.__file__
            )
            input_model, output_model = create_pydantic_models_for_ds_tool(tool)
            tool_schema = ToolSchema(
                name=name,
                description=tool.__doc__,
                version=version,
                tool=tool,
                input_model=input_model,
                output_model=output_model,
                meta=tool_meta
            )
            tools[name] = tool_schema

        return tools

    def __getitem__(self, name: str) -> Optional[ToolSchema]:
        #TODO error handling
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def get_tool(self, name: str) -> Optional[Callable]:
        for tool in self.tools:
            if tool.name == name:
                return tool.tool
        return None

    def list_tools(self) -> List[Dict[str, str]]:
        return [{'name': t.name, 'description': t.description} for t in self.tools]

# ActionCatalog class
def create_pydantic_models_for_ds_tool(func: Callable) -> Tuple[Type[BaseModel], Type[BaseModel]]:
    """
    Dynamically create Pydantic models for the input and output of a function decorated with "@ds.tool".

    Parameters:
    - func: The function to analyze and create models for.

    Returns:
    - A tuple containing the original function, the input Pydantic model, and the output Pydantic model.
    """
    # Extract the function signature
    sig = inspect.signature(func)
    input_fields = {}
    for name, param in sig.parameters.items():
        # Determine the type of parameter, handling special types like Param and Secret
        annotation = param.annotation
        if hasattr(annotation, '__origin__') and annotation.__origin__ in [Param, Secret]:
            # Extract the inner type and description from Param/Secret
            field_type = annotation.__args__[0]
            description = annotation.__metadata__[0] if annotation.__metadata__ else ""
            default = param.default if param.default is not inspect.Parameter.empty else ...
            input_fields[name] = (field_type, default, description)
        else:
            input_fields[name] = (param.annotation, param.default)

    # Create the input model dynamically
    input_model = create_model(f"{func.__name__}Input", **input_fields)

    # Dynamically create the output model, handling complex return types with appropriate annotations
    output_fields = {}
    return_annotation = sig.return_annotation
    if not return_annotation is inspect.Signature.empty:
        if hasattr(return_annotation, '__args__'):  # Check if it's a generic type (e.g., List[int])
            output_fields = {'result': (return_annotation.__args__[0], ...)}
        else:
            output_fields = {'result': (return_annotation, ...)}
    output_model = create_model(f"{func.__name__}Output", **output_fields)
    return input_model, output_model

