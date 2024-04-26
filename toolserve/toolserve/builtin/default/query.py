from typing import Any, Dict, Optional
import io

from toolserve.sdk.client import list_data, log
from toolserve.sdk.dataframe import get_df, save_df
from toolserve.sdk.tool import tool, Param
import duckdb
import pandas as pd

@tool
async def list_data_sources() -> Dict[str, Dict[str, str]]:
    """List all data sources.

    Returns:
        Dict[str, str]: A dictionary mapping data source IDs to their details.
    """
    data = await list_data()
    return {str(item["id"]): {
        "file_name": item["file_name"],
        "created_at": item["created_time"],
        "updated_at": item["updated_time"]
    } for item in data}

@tool
async def get_data_schema(
    data_id: Param(int, "id of the data source"),
    ) -> Param(str, "schema of the data source"):
    """Get the schema of the data source by id.

    Args:
        data_id (int): The id of the data source to get the schema of.

    Returns:
        str: The schema of the data source.
    """
    # TODO read in only a few lines
    df = await get_df(data_id)
    return get_df_info(df)


@tool
async def query_sql(
    data_id: Param(int, "id of the data source"),
    sql: Param(str, "parameterized SQL query to execute"),
    params: Param(Optional[Dict[str, Any]], "parameters to pass to the SQL query") = None,
    ) -> Param(str, "schema of the data source after executing the query"):
    """Query a data source using SQL

    The SQL query should be parameterized with Python's named parameter syntax,
    e.g. `SELECT * FROM table WHERE column = :value`.

    After the query, a new data source at a new id will be created with the results and
    the schema of the data source will be returned.

    Args:
        data_id (int): The id of the data source to query.
        sql (str): The parameterized SQL query to execute.
        params (Optional[Dict[str, Any]]): Parameters to pass to the SQL query.

    Returns:
        str: The schema of the data source after executing the query.
    """
    try:
        # Retrieve the DataFrame and execute the SQL query using DuckDB
        import duckdb
        df = await get_df(data_id)
        con = duckdb.connect(database=':memory:', read_only=False)
        con.register('df_table', df)
        if params:
            result_df = con.execute(sql, params).fetchdf()
        else:
            result_df = con.execute(sql).fetchdf()

        # Save the resulting DataFrame and create a new data source
        result = await save_df(result_df, f"query_result_{data_id}")
        result_id = result["id"]
        # Retrieve and return the schema of the new data source
        return get_df_info(result_df, data_id=result_id)

    except Exception as e:
        # Log the error and raise an exception
        await log(f"Failed to execute query: {str(e)}", level="ERROR")
        raise RuntimeError(f"Query execution failed: {str(e)}")


def get_df_info(df: pd.DataFrame, data_id: Optional[int]=None) -> str:
    """
    Generate a compact string representation of a DataFrame including the count of columns,
    rows, overall size, and details for each column such as name and datatype.

    Parameters:
    df (pd.DataFrame): The Pandas DataFrame to describe.

    Returns:
    str: A string that contains the compact representation of the DataFrame.
    """

    # Create an output stream to collect strings
    output = io.StringIO()

    # Write general information about the DataFrame
    if data_id:
        output.write(f"Result Data ID: {data_id}\n")
    output.write("Table Name: df\n")
    output.write(f"Columns: {len(df.columns)}\n")
    output.write(f"Rows: {len(df.index)}\n")
    output.write(f"Size: {df.memory_usage(deep=True).sum()} bytes\n")

    # Iterate through each column to get details
    for column in df.columns:
        output.write("---\n")
        output.write(f"Column: {column}\n")
        output.write(f"type: {df[column].dtype}\n")

    # Get the complete string from the output stream
    result = output.getvalue()
    output.close()

    return result