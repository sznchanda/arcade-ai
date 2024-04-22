import os
import sys
import inspect
from textwrap import dedent
from typing import List, Optional, Type, Annotated, Dict
from pathlib import Path

from fastapi import APIRouter, Body, Depends, Path, HTTPException
from pydantic import BaseModel, ValidationError, create_model
from importlib import import_module

from toolserve.server.core.catalog import ToolSchema
from toolserve.server.core.conf import settings
from toolserve.common.response_code import CustomResponseCode
from toolserve.common.response import ResponseModel, response_base


def create_endpoint_function(name, description, func, input_model, output_model):
    """
    Factory function to create endpoint functions with 'frozen' schema and input_model values.
    """

    async def run(body: input_model):
        try:
            # Execute the action
            result = await func(**body.dict())
            valid_result = output_model(**result)
            return await response_base.success(data=valid_result.dict())
        except ValidationError as e:
            return await response_base.fail(res=CustomResponseCode.HTTP_400, msg=str(e))
        except Exception as e:
            return await response_base.fail(res=CustomResponseCode.HTTP_500, msg=str(e))

    run.__name__ = name
    run.__doc__ = description

    return run


def create_response_model(name: str, output_model: Type[BaseModel]) -> Type[ResponseModel]:
    """
    Create a response model for the given schema.
    """
    # Create a new response model
    response_model = create_model(
        f"{name}Response",
        code=(int, CustomResponseCode.HTTP_200.code),
        msg=(str, CustomResponseCode.HTTP_200.msg),
        data=(output_model, None)
    )

    return response_model

def generate_endpoint(schemas: List[ToolSchema]) -> APIRouter:
    routers = []
    top_level_router = APIRouter(prefix=settings.API_ACTION_STR)

    for schema in schemas:
        router = APIRouter(prefix="/" + schema.meta.module)


        # Create the endpoint function
        run = create_endpoint_function(
            name=schema.name,
            description=schema.description,
            func=schema.tool,
            input_model=schema.input_model,
            output_model=schema.output_model
        )

        response_model = create_response_model(schema.name, schema.output_model)

        # Add the endpoint to the FastAPI app
        router.post(
            f"/{schema.name}",
            name=schema.name,
            summary=schema.description,
            tags=[schema.meta.module],
            response_model=response_model,
            response_description=create_output_description(schema.output_model)
            )(run)

        routers.append(router)
    for router in routers:
        top_level_router.include_router(router)
    return top_level_router



def create_output_description(output_model: Type[BaseModel]) -> str:
    """
    Create a description string for the output model.
    """
    if not output_model:
        return None

    output_description = dedent(output_model.__doc__ or "")
    output_description += "\n\n**Attributes:**\n\n"

    for name, field in output_model.model_fields.items():
        output_description += f"- **{name}** ({field.annotation.__name__}): {field.description}\n"

    return output_description