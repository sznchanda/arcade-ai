import asyncio
from serpapi import GoogleSearch
from typing import List, Dict
import json
from toolserve.sdk import Param, tool, get_secret

async def google_search(
    query: Param(str, "search query for google"),
    num_results: Param(int, "number of results")
    ) -> Param(str, "Json blob of Search results"):
    """
    Perform a Google search using SerpAPI and retrieve a specified number of results.

    Args:
        query (str): The search query.
        num_results (int): The number of search results to retrieve.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing the link and text of each result.
    """
    serpapi_key = get_secret("serp_api_key", None)
    params = {
        "engine": "google",
        "q": query,
        "num": num_results,
        "api_key": serpapi_key
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    json_results = json.dumps(results.get("organic_results"), indent=2)

    return json_results

