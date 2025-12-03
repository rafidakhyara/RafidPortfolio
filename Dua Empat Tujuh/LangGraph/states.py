from dataclasses import dataclass, field
import pandas as pd

@dataclass(kw_only=True)
class DashboardState:
    user_input: str = field(default=None) # User input
    database: str = field(default=None)
    processed_input : str = field(default=None)
    sql_query: list = field(default=None)
    query_df:pd.DataFrame = field(default=None)
    query_columns: str = field(default=None)
    query_data: str = field(default=None)
    query_number: int = 1
    query_error: bool = False
    query_error_message: str = field(default=None)
    graph_code:str=field(default=None)
    graph_error:bool=False
    graph_error_message:str=field(default=None)
    joined_schema:str=field(default=None)


@dataclass(kw_only=True)
class DashboardStateInput:
    user_input: str = field(default=None) 
    database: str = field(default=None)


@dataclass(kw_only=True)
class DashboardStateOutput:
    final_message: str = field(default=None)
