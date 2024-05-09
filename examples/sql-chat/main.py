import openai

oai_key = "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"


import json
import logging
import subprocess
import sys
import time
import traceback
import os

from typing import Dict, Any
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from pydantic import BaseModel
from streamlit_chat import message
import streamlit.components.v1 as components
from textwrap import dedent
import plotly.express as px
from agent import ToolFlow, email_flow, plotting_flow, review_flow, customer_flow



PROMPT = dedent("""Given a user query, construct a graph based representation of functions (nodes), and their data flow (edges) such that
the graph can be executed to supply the user query enough information to answer their query.

You must construct the graph with the following constraints:
- There can only be 1 source node and 1 sink node.
- There should be no leaf nodes besides the sink node.
- The source and sink can be the same node.

Only use the available nodes and their output types as edges. Create unique ids for each node starting from 0.

The available nodes are:
{nodes}

The available input names for the source are:
{sources}
""")


def plot_flow(data: Dict[str, Any]):
    """
    Plot the flow of data using a directed graph.

    Args:
        data (Dict[str, Any]): A dictionary containing 'nodes' and optionally 'edges'.
    """
    # Create a directed graph
    G = nx.DiGraph()

    # Add nodes
    for node in data['nodes']:
        G.add_node(node['node_id'], label=node['tool_name'])

    # Add edges
    if 'edges' in data:
        for edge in data['edges']:
            G.add_edge(edge['source'], edge['target'])

    # Node labels with specific formatting
    labels = {node['node_id']: f"{node['tool_name']}\n({node['input_name']} -> {node['output_name']})" for node in data['nodes']}

    # Check if there are any nodes to determine a start node for bfs_layout
    if G.nodes:
        #start_node = next(iter(G.nodes))  # Get an arbitrary start node
        #pos = nx.bfs_layout(G, start_node)
        pos = nx.spring_layout(G)
    else:
        pos = {}

    plt.figure(figsize=(7, 7))
    nx.draw(G, pos, with_labels=False, node_size=3000, node_color='skyblue', font_size=9, font_weight='bold')
    nx.draw_networkx_labels(G, pos, labels, font_size=8)

    # Use Streamlit's function to display the plot
    st.sidebar.pyplot(plt, use_container_width=True)


@st.cache_resource()
def get_agent():
    AnalysisTool = ToolFlow(
        name="data_analysis",
        description="A tool flow for data analysis",
        prompt=PROMPT,
        model_api_key=oai_key
    )
    return AnalysisTool


# From here down is all the StreamLit UI.
st.set_page_config(page_title="Arcade AI Demo", page_icon=":robot:", layout="wide")

dropdown_options = ["Gmailer", "PlotBot", "ReviewChat", "CustomerService"]
selected_option = st.sidebar.selectbox("Select an App:", dropdown_options)
st.sidebar.write(f"Selected App: {selected_option}")

def initialize_logger():
    logger = logging.getLogger("root")
    handler = logging.StreamHandler(sys.stdout)
    logger.setLevel(logging.INFO)
    logger.handlers = [handler]
    return True

if "logger" not in st.session_state:
    st.session_state["logger"] = initialize_logger()
if "past" not in st.session_state:
    st.session_state["past"] = []
if "generated" not in st.session_state:
    st.session_state["generated"] = []



st.subheader("Arcade AI Agent Demo")


chat_container = st.container()
input_container = st.container()

def submit():
    submit_text = st.session_state["input"]
    st.session_state["input"] = ""
    with st.spinner(text="Wait for Agent..."):
        try:
            agent = get_agent()
            #flow  = agent.infer_flow(submit_text)
            #json_flow = json.loads(flow)
            if selected_option == "Gmailer":
                json_flow = email_flow.dict()
            elif selected_option == "PlotBot":
                json_flow = plotting_flow.dict()
            elif selected_option == "ReviewChat":
                json_flow = review_flow.dict()
            elif selected_option == "CustomerService":
                json_flow = customer_flow.dict()
            else:
                st.error("Invalid option selected")
                return

            plot_flow(json_flow)
            res = agent.execute_flow(json_flow, submit_text)
        except Exception:
            st.error("Error executing the flow:")
            st.error(traceback.format_exc())
            return
    st.session_state.past.append(submit_text)
    st.session_state.generated.append(res)

def get_text():
    input_text = st.text_input("You: ", key="input", on_change=submit)
    return input_text

with input_container:
    user_input = get_text()

if st.session_state["generated"]:
    with chat_container:
        for i in range(
            len(st.session_state["generated"])
        ):  # range(len(st.session_state["generated"]) - 1, -1, -1):
            message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")

            result = st.session_state["generated"][i]
            result_tab, all_results_tab, times_tab = st.tabs(["Result", "All Results", "Execution Times"])

            res, all_results, output_type, timings = result

            with all_results_tab:
                st.write(all_results)
            with times_tab:
                st.write(timings)
            with result_tab:
                output_type = output_type.value
                if output_type == "artifact":
                    # plot the json returned in res
                    fig_json = res["data"]["result"]
                    # plot the json with ploylu atream lit
                    st.plotly_chart(json.loads(fig_json))
                elif output_type == "chat":
                    st.write(res)
                elif output_type == "data":
                    json_res = json.loads(res)["data"]
                    st.dataframe(json_res)
                else:
                    st.error("Returned result:")
                    st.error(res)

