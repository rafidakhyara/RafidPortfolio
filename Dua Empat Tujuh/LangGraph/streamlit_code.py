from graph_dashboard import dashboard_graph
import json
import pandas as pd
import streamlit as st

user_input = st.text_input("What would you like to visualize?")

st.header(user_input)

st.set_page_config(layout="wide")

if user_input!="":
    dashboard_graph.invoke({"user_input": user_input, "database":"sqlite:///chinook.db"}, config={"recursion_limit": 25})    

if user_input!="":
    with open('/data/faruq/dashboard/queries.json', 'r') as f:
        data=json.load(f)
    st.markdown(data["query1"])

    csv1=pd.read_csv("/data/faruq/dashboard/query_df/csv1.csv")
    st.dataframe(csv1, height=200, hide_index=True)

    with open("/data/faruq/dashboard/graphs/plot1.html",'r') as f: 
        html_data = f.read()
    st.components.v1.html(html_data, scrolling=True, height=500)
