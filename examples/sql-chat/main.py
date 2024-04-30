import openai

oai_key = "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"


import json
import logging
import subprocess
import sys
import time
import traceback
import os

import pandas as pd
import streamlit as st
from pydantic import BaseModel
from streamlit_chat import message


from agent import Agent, Toolchain

@st.cache_resource()
def get_agent():
    toolchain = Toolchain(base_url="http://localhost:8000", model="gpt-4-turbo", openai_api_key=oai_key)
    agent = Agent(toolchain)
    agent.set_source("users_db")
    return agent


# From here down is all the StreamLit UI.
st.set_page_config(page_title="Data Chat", page_icon=":robot:", layout="wide")
st.header("Arcade AI Demo")


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



st.subheader("Chat")


chat_container = st.container()
input_container = st.container()

def submit():
    submit_text = st.session_state["input"]
    st.session_state["input"] = ""
    with st.spinner(text="Wait for Agent..."):
        try:
            agent = get_agent()
            res  = agent.query(submit_text)
        except Exception:
            res = traceback.format_exc()
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

            res = st.session_state["generated"][i]

            try:
                json_res = json.loads(res)["data"]
                print(json_res)
            except Exception:
                json_res = None

            if json_res:
                try:
                    res = pd.DataFrame(json_res)
                except Exception:
                    res = json_res

            if isinstance(res, str):
                st.write(res)
            elif isinstance(res, pd.DataFrame):
                st.dataframe(res)
            else:
                st.error("Returned result:")
                st.error(res)
