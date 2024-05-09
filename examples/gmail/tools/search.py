


import faiss
import numpy as np

from typing import List
from fastembed import TextEmbedding
from toolserve.sdk import Param, tool, get_secret
from toolserve.sdk.dataframe import get_df


@tool
async def vector_search(
    data_id: Param(int, "The ID of the data source containing the documents"),
    query: Param(str, "The text to find within the documents"),
    column_name: Param(str, "The name of the column containing the documents"),
    n_results: Param(int, "The number of top results to return") = 5
) -> Param(List[str], "The documents most similar to the query"):
    """Create a FAISS index from a list of documents and search for the query, returning the most similar documents.

    Args:
        query (str): The text query to search for. Should be written like a document.
        column_name (str): The name of the column containing the documents.
        n_results (int, optional): The number of top results to return. Defaults to 5.

    Returns:
        List[str]: The documents most similar to the query based on the search.
    """
    # Get the data
    df = await get_df(data_id)
    docs = df[column_name].tolist()

    # Initialize the embedding model
    embedding_tool = TextEmbedding()

    # Embed all documents
    embeddings = []
    for doc in docs:
        # Get the generator from the embed method
        doc_embedding_generator = embedding_tool.embed([doc])
        # Convert the generator to a list and take the first element
        doc_embedding = list(doc_embedding_generator)[0]
        embeddings.append(doc_embedding)

    # Convert list of embeddings to a numpy array and ensure type float32
    embeddings = np.vstack(embeddings).astype('float32')

    # Create a flat L2 index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)  # Add embeddings to the index

    # Embed the query
    query_embedding_generator = embedding_tool.embed([query])
    query_embedding = list(query_embedding_generator)[0]
    query_embedding = np.array(query_embedding, dtype='float32').reshape(1, -1)

    # Search the index
    distances, indices = index.search(query_embedding, n_results)

    # Fetch the documents corresponding to the top indices
    top_docs = [docs[i] for i in indices.flatten().tolist()]

    return top_docs