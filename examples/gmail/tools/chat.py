

from typing import (
    IO,
    Union,
    List,
    Dict,
    Optional,
    Any,
    Type,
)
import io
import requests
from os import PathLike
import base64

from toolserve.sdk import Param, tool, get_secret
from toolserve.sdk.dataframe import get_df
from typing import List
import pandas as pd
import openai



@tool
async def summarize(
    text: Param(str, "Text to summarize"),
    #data_id: Param(int, "ID of the data to summarize"),
    system_prompt: Param(str, "System prompt to use") = "Summarize the following text",
    max_tokens: Param(int, "Maximum number of tokens to generate") = 1000,
    ) -> Param(str, "Summarized text"):
    """Summarize a piece of text using OpenAI Language models.

    Args:
        text (str): The text to summarize.
        max_tokens (int): The maximum number of tokens to generate.

    Returns:
        str: The summarized text.
    """
    #df = await get_df(data_id)
    #text = df.to_json(orient='records')
    api_key = get_secret("openai_api_key", None)
    model = get_secret("openai_model_summarize", "gpt-4-turbo")
    # Call the OpenAI model with the tools and messages

    if isinstance(text, list):
        text = "\n".join(text)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]

    client = openai.Client(api_key=api_key)
    completion =  openai.chat.completions.create(
        model=model,
        messages=messages,
    )
    summary = completion.choices[0].message.content
    return summary


@tool
async def transcribe_text(
    audio_file: Param(str, "Audio file bytes"),
    system_prompt: Param(str, "System prompt to use") = "Transcribe the following audio files",
) -> Param(str, "Transcribed text"):
    """Use OpenAI to translate audio to text using the Whisper model.

    Args:
        audio_file_bytes (str): The bytes of the audio file to transcribe.
        system_prompt (str): The system prompt to use for guiding the transcription.

    Returns:
        str: The transcribed text.
    """
    api_key = get_secret("openai_api_key", None)
    model = get_secret("openai_model_whisper", "whisper-1")

    if audio_file is None:
        raise ValueError("No audio file provided")

    # Decode the base64 audio file
    audio_file_bytes = base64.b64decode(audio_file)
    file = io.BytesIO(audio_file_bytes)

    # Prepare the headers
    headers = {
        'Authorization': f'Bearer {api_key}',
    }

    # Prepare the files parameter
    files = {
        'file': ('audio.mp3', file, 'audio/mp3')
    }

    # Prepare the data parameter
    data = {
        'model': model,
        'prompt': system_prompt,
        'response_format': 'text'
    }

    # Send the request to the OpenAI Whisper API
    response = requests.post(
        'https://api.openai.com/v1/audio/transcriptions',
        headers=headers,
        files=files,
        data=data
    )

    # Check if the request was successful
    if response.status_code == 200:
        # Return the plain text response directly
        return response.text
    else:
        # Handle errors
        raise Exception(f"Error: {response.status_code} - {response.text}")

