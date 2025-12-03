from langgraph.graph import StateGraph, START, END
from states import DashboardState, DashboardStateInput, DashboardStateOutput
from langchain.chat_models import init_chat_model
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import (InfoSQLDatabaseTool, QuerySQLDatabaseTool)
import re
from typing import Literal
import json
import pandas as pd

from sql_agent import sql_crew

llm = init_chat_model(
    model="openai:gpt-4o-mini",
    api_key="OPENAI_API_KEY"
)

#Process user input and dataframe to create a list of what should be included in the dashboard
def process_user_input(state:DashboardState):
    db = SQLDatabase.from_uri(state.database)    

    for table in db.get_usable_table_names():
        print(table)

    schema = []

    for table in db.get_usable_table_names():
        info = InfoSQLDatabaseTool(db=db)._run(table)
        schema.append(re.findall(r"CREATE TABLE.*\)\n\)",info, re.S)[0])

    joined_schema = "\n\n".join(schema)
    
    resp = llm.invoke(f"Based on {state.user_input} and the schema: {joined_schema}, what kind of graphs do you think would be appropriate? Suggest just 1 graph based on the user's input.")

    with open('/data/faruq/dashboard/queries.json', "w") as f:
        json.dump({}, f, indent=4)
        f.close()
    return {"processed_input": resp.content, "joined_schema":joined_schema}

def create_sql_query(state:DashboardState):
    resp=[]

    resp = sql_crew.kickoff(inputs={"input":f"Based on user input:{state.user_input}, processed input: {state.processed_input} and the the schema itself: {state.joined_schema}, write the SQL queries needed to create each of the graphs mentioned. Make sure the queries are cross-database safe and are compatible with most SQL dialects. You are allowed to make subqueries or use common table expressions when necessary. Column names should be exact like in the dataframe. Column names should use quotation marks (\"ColumnName\") and not other markers like square brackets. No need to provide any explanation. Mark the beginning of the query with 'Query:' and the end of a query with '(Query End)'. Provide these queries as the final answer."}).raw
    resp=resp.replace("```sql", "").replace("```", "")
    resp=re.findall(r".*?Query:\s*\n*(.+?)\(Query End\)", resp, re.S)
    return {"sql_query": resp}

def run_sql_query(state:DashboardState):
    db = SQLDatabase.from_uri(state.database)

    try:
        data = QuerySQLDatabaseTool(db=db)._run(state.sql_query[state.query_number-1])
        columns = llm.invoke(f"Get the column names from the query: {state.sql_query[state.query_number-1]}, return in the form of a list of column names using square brackets '[]'.")
        columns = columns.content
        columns = re.findall(r"\[.+\]", columns, re.S)[0]
        
        query_df = pd.DataFrame(eval(data), columns=eval(columns))
        print(query_df)
        print(state.sql_query)
        return {"query_df": query_df, "query_error":False}
    except:
        print(data)
        return {"query_error": True, "query_error_message": data}

def query_validator(state:DashboardState) -> Literal["fix_sql_query", "create_graph"]:
    if state.query_error==True:
        state.query_error=False
        return "fix_sql_query"
    else:
        with open('/data/faruq/dashboard/queries.json', "r") as f:
            try:
                data=json.load(f)
            except:
                data={}
            
            f.close()
        with open('/data/faruq/dashboard/queries.json', "w") as f:    
            data.update({f"query{state.query_number}":state.sql_query[state.query_number-1]})
            json.dump(data, f, indent=4)

            f.close()

        print("Queries stored.")
        
        state.query_df.to_csv(f'/data/faruq/dashboard/query_df/csv{state.query_number}.csv', index=False)
        return "create_graph"

def fix_sql_query(state:DashboardState):
    resp=[]

    resp = llm.invoke(f"Fix this query: {state.sql_query[state.query_number-1]} so that it may be used to query using SQL. This was the error message: {state.query_error_message}. Keep in mind the schema: {state.joined_schema}. Do not use Python at any point. Make sure it will not result in any more errors. Make sure the query is cross-database safe and is compatible with most SQL dialects. Column names should be exact like in the dataframe. Column names should use quotation marks (\"ColumnName\") and not other markers like square brackets. No need to provide any explanation. Mark the beginning of the query with 'Query:' and the end of a query with '(Query End)'. Provide the query as the final answer.")
    resp = resp.content.replace("```sql", "").replace("```", "")
    resp = re.findall(r".*?Query:\s*\n*(.+?)\(Query End\)", resp, re.S)

    qlist=state.sql_query.copy()
    qlist[state.query_number-1]=resp[0]

    return {"sql_query": qlist}

def create_graph(state:DashboardState):
    df=state.query_df

    resp = llm.invoke(f"Based on the dataframe's columns:{df.columns} and data types:{df.dtypes} and these instructions: {state.processed_input}, write code for an appropriate graph using the Plotly Python package. Only write the code for graph number {state.query_number}. Do not define a new dataframe or I will smite you and your family. It is already defined as df. Use the name 'df' for the dataframe. If you want to add a description use a # at the beginning of the line, as if you were writing python script. Include the code in the final answer.")

    resp=resp.content
    resp = resp.replace("fig.show()", f"fig.write_html(\"/data/faruq/dashboard/graphs/plot{state.query_number}.html\")")
    resp = re.findall(r".*?```python\s*\n(.+?)```", resp, re.S)[0]


    return {"graph_code":resp}

def run_graph(state:DashboardState):
    try:
        print(state.graph_code)
        print(state.graph_error)
        exec(state.graph_code)
        return {"query_number": state.query_number+1, "graph_error":False}
    except Exception as e:
        return {"graph_error":True, "graph_error_message":e}


def fix_graph(state:DashboardState):
    resp = llm.invoke(f"Fix this code: {state.graph_error} based on this error message {state.graph_error_message}. write code for an appropriate graph using the Plotly Python package. Do not define a new dataframe. If you want to add a description use a # at the beginning of the line, as if you were writing python script. Include the code in the final answer.")

    resp=resp.content
    resp = resp.replace("fig.show()", f"fig.write_html(\"plot{state.query_number}.html\")")
    resp = re.findall(r".*?```python\s*\n(.+?)```", resp, re.S)[0]
        
    return {"graph_code":resp}

def looping_validator(state:DashboardState) -> Literal["run_sql_query", "assemble_dashboard", "fix_graph"]:
    if state.graph_error==True:
        return "fix_graph"
    else:
        if state.query_number-1 < len(state.sql_query):
            return "run_sql_query"
        else:
            return "assemble_dashboard"

def assemble_dashboard(state:DashboardState):
    return {"final_message": "Run dashboard using streamlit!"}

builder = StateGraph(DashboardState, input_schema=DashboardStateInput, output_schema=DashboardStateOutput)

builder.add_node("process_user_input", process_user_input)
builder.add_node("create_sql_query", create_sql_query)
builder.add_node("run_sql_query", run_sql_query)
builder.add_node("fix_sql_query", fix_sql_query)
builder.add_node("create_graph", create_graph)
builder.add_node("run_graph", run_graph)
builder.add_node("fix_graph", fix_graph)
builder.add_node("assemble_dashboard", assemble_dashboard)

builder.add_edge(START, "process_user_input")
builder.add_edge("process_user_input", "create_sql_query")
builder.add_edge("create_sql_query", "run_sql_query")
builder.add_conditional_edges("run_sql_query", query_validator)
builder.add_edge("fix_sql_query", "run_sql_query")
builder.add_edge("create_graph", "run_graph")
builder.add_conditional_edges("run_graph", looping_validator)
builder.add_edge("fix_graph", "run_graph")
builder.add_edge("assemble_dashboard", END)

dashboard_graph = builder.compile()
