import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
from datetime import datetime
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# Local import
from faiss_vs_powerbi import flatten_data_model_to_documents, retrive_context

# Setup
load_dotenv()
client = OpenAI()
st.set_page_config(page_title="Interactive Power BI Filter Prompt Builder", page_icon="🧠")

st.title("🧠 Interactive Power BI Filter Prompt Builder")
st.markdown("Start with your vague or partial request:")

# ---- Define RAG Clarifier ----
def clarify_user_prompt(user_input: str, schema_context: str, history: list) -> str:

    relationship_info = """
Table Relationships:
- 'Consolidated Leads' ↔ 'Opportunity Details' joined by 'Campaign Source'.
- 'Consolidated Leads' ↔ 'Date_table' joined by 'Created Date' and 'Date'.
- 'Consolidated Leads' ↔ 'Overall Meetings' joined by 'Campaign Source'.

Use these relationships to reason about valid filters involving multiple tables.
For example, if the user asks about filtering by a date range, it's likely from 'Date_table' via 'Consolidated Leads'.
"""


    messages = [
        {"role": "system", "content": f"""
You are a smart Power BI assistant that helps users write clear and correct filter requests.

Instructions:
- Use the schema context below to correct or clarify vague, incorrect, or incomplete requests.
- Use only columns and tables from the schema. Ask clarification questions if needed.
- Do NOT output Power BI filter JSON — only respond in natural language.
- This is part of an iterative prompt improvement chat. Be helpful and specific.

Schema:
{schema_context}

{relationship_info}
"""}]

    for turn in history:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["assistant"]})

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.4
    )

    return response.choices[0].message.content.strip()


# ---- Prompt Session Handling ----
if "history" not in st.session_state:
    st.session_state.history = []
if "final_prompt" not in st.session_state:
    st.session_state.final_prompt = ""

user_input = st.chat_input("💬 Type your request...")

if user_input:
    schema_context = retrive_context(user_input)
    assistant_response = clarify_user_prompt(user_input, schema_context, st.session_state.history)

    st.session_state.history.append({
        "user": user_input,
        "assistant": assistant_response
    })

# ---- Chat Display ----
for i, turn in enumerate(st.session_state.history):
    with st.chat_message("user", avatar="📩"):
        st.markdown(turn["user"])
    with st.chat_message("assistant", avatar="💡"):
        st.markdown(turn["assistant"])

# ---- Final Prompt Acceptance ----
# if st.session_state.history:
#     st.markdown("### ✅ Finalize Your Prompt")
#     final_input = st.text_input("If you're happy with the last suggestion, confirm or edit it below:", key="final_approval")

#     if final_input:
#         st.session_state.final_prompt = final_input
#         st.success("🎉 Final prompt accepted and saved for filter generation!")
#         st.write("**Final Prompt:**", st.session_state.final_prompt)
