
from typing import Annotated
from fastapi import APIRouter, Path, Query
from fastapi.responses import StreamingResponse
from toolserve.server.common.response import ResponseModel, response_base
from toolserve.server.common.serializers import select_as_dict

# to take out later
import openai
import json

from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal, Iterable

from openai.types.chat.chat_completion_tool_param import ChatCompletionToolParam
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from openai.types.chat.chat_completion_stream_options_param import ChatCompletionStreamOptionsParam
from openai.types.chat.chat_completion_tool_choice_option_param import ChatCompletionToolChoiceOptionParam
from openai.types.chat.chat_completion_function_call_option_param import ChatCompletionFunctionCallOptionParam
from openai.types import shared_params
from openai.types.chat_model import ChatModel
from fastapi import Request, HTTPException, status, Depends

from toolserve.server.core.depends import get_catalog
from toolserve.utils.openai_tool import schema_to_openai_tool

router = APIRouter()


class FunctionCall(BaseModel):
    type: Literal["none", "auto", "function"]
    function: Optional[ChatCompletionFunctionCallOptionParam]

class Function(BaseModel):
    name: str
    description: Optional[str]
    parameters: Optional[shared_params.FunctionParameters]

class ResponseFormat(BaseModel):
    type: Literal["text", "json_object"]

class CompletionCreateParamsBase(BaseModel):
    messages: List[ChatCompletionMessageParam]
    model: Union[str, ChatModel]
    frequency_penalty: Optional[float] = None
    #function_call: Optional[FunctionCall] = None
    #functions: Optional[List[Function]] = None
    logit_bias: Optional[dict[str, int]] = None
    logprobs: Optional[bool] = None
    max_tokens: Optional[int] = None
    n: Optional[int] = None
    presence_penalty: Optional[float] = None
    response_format: Optional[ResponseFormat] = None
    seed: Optional[int] = None
    stop: Optional[Union[str, List[str]]] = None
    stream_options: Optional[ChatCompletionStreamOptionsParam] = None
    temperature: Optional[float] = None
    tool_choice: Optional[ChatCompletionToolChoiceOptionParam] = None
    tools: Optional[Union[List[ChatCompletionToolParam], List[str]]] = None
    top_logprobs: Optional[int] = None
    top_p: Optional[float] = None
    user: Optional[str] = None

class CompletionCreateParamsNonStreaming(CompletionCreateParamsBase):
    stream: Literal[False]

class CompletionCreateParamsStreaming(CompletionCreateParamsBase):
    stream: Literal[True]

CompletionCreateParams = Union[CompletionCreateParamsNonStreaming, CompletionCreateParamsStreaming]



def get_openai_key(request: Request) -> str:
    """
    Extracts the API key from the Authorization header as a Bearer token.

    Args:
        request (Request): The request object from which the API key is extracted.

    Returns:
        str: The API key extracted from the Authorization header.

    Raises:
        HTTPException: If the Authorization header is missing or improperly formatted.
    """
    auth_header = request.headers.get('Authorization')
    if auth_header is None or not auth_header.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization token is missing or improperly formatted'
        )
    api_key = auth_header.split(' ')[1]
    return api_key


@router.post(
    '/completions',
    summary='Chat Completions Endpoints mimicking OpenAI'
)
async def create_chat_completion(
    completion: CompletionCreateParams,
    api_key: str = Depends(get_openai_key),
    catalog=Depends(get_catalog)
):
    """
    Create a chat completion
    """
    try:
        oai_client = openai.AsyncOpenAI(api_key=api_key)

        if completion.tools:
            if isinstance(completion.tools[0], str):
                specs = []
                for tool in completion.tools:
                    specs.append(json.loads(schema_to_openai_tool(catalog[tool])))
                completion.tool_choice = "required"
                completion.tools = specs

        result = await oai_client.chat.completions.create(**completion.dict())
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))