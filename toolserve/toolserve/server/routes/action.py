import os
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query
from pydantic import ValidationError

from toolserve.server.core.conf import settings
from toolserve.server.core.depends import get_catalog
from toolserve.common.response_code import CustomResponseCode
from toolserve.common.response import ResponseModel, response_base
#from toolserve.utils.openai_tool import schema_to_openai_tool

router = APIRouter()

@router.get(
    '/list',
    summary='List available tools',
)
async def list_tools(catalog=Depends(get_catalog)) -> ResponseModel:
    """List all available actions"""

    tools = catalog.list_tools()
    return await response_base.success(data=tools)

@router.get(
    '/oai_function',
    summary="Get the OpenAI function format of an action"
)
async def get_oai_function(
    action_name: str = Query(..., title="Action Name", description="The name of the action"),
    catalog=Depends(get_catalog)
) -> ResponseModel:
    """Get the OpenAI function format of an action"""

    try:
        # TODO handle keyerror
        action = catalog[action_name]
        json_data = schema_to_openai_tool(action)

        return await response_base.success(data=json_data)
    except ValidationError as e:
        return await response_base.fail(res=CustomResponseCode.HTTP_400, data=str(e))
    except Exception as e:
        return await response_base.fail(res=CustomResponseCode.HTTP_500, data=str(e))
