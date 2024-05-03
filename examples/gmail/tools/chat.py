

from toolserve.sdk import Param, tool, get_secret
from toolserve.sdk.dataframe import get_df
import pandas as pd
import openai

@tool
async def summarize(
    #text: Param(str, "Text to summarize"),
    data_id: Param(int, "ID of the data to summarize"),
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
    df = await get_df(data_id)
    text = df.to_json(orient='records')
    api_key = get_secret("openai_api_key", None)
    model = get_secret("openai_model_summarize", "gpt-4-turbo")
    # Call the OpenAI model with the tools and messages
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
