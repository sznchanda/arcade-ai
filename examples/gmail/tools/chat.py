

from toolserve.sdk import Param, tool, get_secret
from toolserve.sdk.dataframe import get_df

import openai

@tool
def summarize(
    text: Param(str, "Text to summarize"),
    system_prompt: Param(str, "System prompt to use") = "Summarize the following text",
    max_tokens: Param(int, "Maximum number of tokens to generate") = 1000,
    ) -> Param(str, "Summarized text"):
    """Summarize a piece of text using OpenAI's GPT-3 model.

    Args:
        text (str): The text to summarize.
        max_tokens (int): The maximum number of tokens to generate.

    Returns:
        str: The summarized text.
    """
    api_key = get_secret("openai_api_key")
    # Call the OpenAI model with the tools and messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]

    client = openai.Client(api_key=api_key)
    completion = openai.chat.completions.create(
        model=self.model,
        messages=messages,
    )
    summary = completion.choices[0].message.content
    return summary
