
from typing import List, Dict, Any

from toolserve.sdk.dataframe import get_df, save_df
from toolserve.sdk.tool import tool, Param

@tool
async def get(
    data_id: Param(int, "ID of the data")
    ) -> Param(str, "data"):
    """Get data by ID"""
    df = await get_df(data_id)
    return df.to_json(orient='records')

@tool
async def select_columns(
    data_id: Param(int, "ID of the data"),
    columns: Param(List[str], "Columns to select")
    ) -> Param(str, "data"):
    """Select columns from a DataFrame"""
    df = await get_df(data_id)
    df = df[columns]
    return df.to_json(orient='records')

@tool
async def filter_rows(
    data_id: Param(int, "ID of the data"),
    column: Param(str, "Column to filter"),
    value: Param(str, "Value to filter by")
    ) -> Param(str, "data"):
    """Filter rows in a DataFrame"""
    df = await get_df(data_id)
    df = df[df[column] == value]
    return df.to_json(orient='records')

@tool
async def sort(
    data_id: Param(int, "ID of the data"),
    column: Param(str, "Column to sort by"),
    ascending: Param(bool, "Sort ascending or descending") = True
    ) -> Param(str, "data"):
    """Sort a DataFrame by a column"""
    df = await get_df(data_id)
    df = df.sort_values(by=column, ascending=ascending)
    return df.to_json(orient='records')

@tool
async def group_by(
    data_id: Param(int, "ID of the data"),
    columns: Param(List[str], "Columns to group by"),
    aggregations: Param(Dict[str, str], "Aggregations to perform")
    ) -> Param(str, "data"):
    """Group by columns and perform aggregations"""
    df = await get_df(data_id)
    df = df.groupby(columns).agg(aggregations)
    return df.to_json(orient='records')

@tool
async def join(
    data_id1: Param(int, "ID of the first data"),
    data_id2: Param(int, "ID of the second data"),
    on: Param(str, "Column to join on"),
    how: Param(str, "Type of join") = "inner"
    ) -> Param(str, "data"):
    """Join two DataFrames"""
    df1 = await get_df(data_id1)
    df2 = await get_df(data_id2)
    df = df1.merge(df2, on=on, how=how)
    return df.to_json(orient='records')

@tool
async def search_text_columns(
    data_id: Param(int, "ID of the data"),
    query: Param(str, "Text to search for"),
    column: Param(str, "Column to search in"),
    max_rows: Param(int, "Maximum number of rows to return") = 50
    ) -> Param(str, "data"):
    """Search text in columns

    Search for a text query in a specific column of a DataFrame.

    Args:
        data_id (int): The ID of the data source to search in.
        query (str): The text to search for.
        column (str): The column to search in.

    Returns:
        str: The data source after filtering for the text query, limited to a maximum number of rows.
    """
    df = await get_df(data_id)
    # Ensure the column data is treated as string
    df[column] = df[column].astype(str)
    # Use regex=False to treat the query as a literal string, avoiding any regex special character issues
    mask = df[column].str.contains(query, case=False, na=False, regex=False)
    df = df[mask]
    # Limit the number of rows returned
    df = df.head(max_rows)
    return df.to_json(orient='records')


@tool
def combine_results(
    result_1: Param(str, "First result"),
    result_2: Param(str, "Second result")
    ) -> Param(str, "data"):
    """Combine two results"""
    return str(result_1) + str(result_2)
