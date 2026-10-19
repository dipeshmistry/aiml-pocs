import os
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import json
from dotenv import load_dotenv
load_dotenv()

# os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"  # Replace with your API key
llm = ChatOpenAI(model_name="gpt-4", temperature=0)

def confirm_with_gpt(primary_row, candidate_row):
    primary_str = primary_row.to_json()
    candidate_str = candidate_row.to_json()

    messages = [
        SystemMessage(content="You are helping match records across different data sources for ETL enrichment."),
        HumanMessage(content=f"Primary record: {primary_str}\nCandidate record: {candidate_str}\nAre these the same client? Respond with 'yes' or 'no'.")
    ]
    response = llm.invoke(messages).content.strip().lower()
    return response.startswith("yes")


def extract_info_with_gpt(description):
    messages = [
        SystemMessage(content="You extract structured company info from text."),
        HumanMessage(content=f"Extract industry, location, size from this description: {description}. Respond as JSON with keys: industry, location, size.")
    ]
    response = llm.invoke(messages).content.strip()
    try:
        data = json.loads(response)
        return data
    except:
        return {}