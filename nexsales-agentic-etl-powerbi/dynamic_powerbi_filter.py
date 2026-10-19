from datetime import datetime
from openai import OpenAI
import json
import os
import streamlit as st
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
client = OpenAI()

st.title("Filters Generation For - Inbound Leads Performance Dashboard")

def collect_feedback_and_log(prompt, response, log_file="powerbi_filter_feedback_log.jsonl"):
    st.write("\n🤖 Were you satisfied with the result? (yes/no)")
    satisfied = st.text_input("Provide confirmation",key="confirmation").strip().lower()

    feedback = ""
    if satisfied == "no":
        st.write("\n📝 Please describe what went wrong or how it can be improved:")
        feedback = st.text_input("Provide Feedback",key="feedback").strip()

        if satisfied=='yes' or feedback:
        # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "llm_response": response,
                "satisfied": satisfied,
                "feedback": feedback
            }

            # Append to log file in JSONL format
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")

            st.write("\n✅ Feedback saved. Thank you!")



def generate_dax_filter_expression_from_embed_json(embed_filters: list) -> list:
    """
    Converts Power BI JavaScript SDK filter JSON into a list of DAX FILTER() expressions.
    
    Args:
        embed_filters (list): List of filter dicts from GPT/JavaScript SDK
    
    Returns:
        List of strings, each representing a DAX FILTER(...) expression
    """
    filter_expressions = []

    for f in embed_filters:
        table = f["target"]["table"]
        column = f["target"]["column"]
        operator = f["operator"]
        values = f["values"]

        full_col = f"'{table}'[{column}]"

        if operator == "In":
            val_str = ", ".join(f'"{v}"' if isinstance(v, str) else str(v) for v in values)
            expr = f"FILTER(\n    '{table}',\n    {full_col} IN {{{val_str}}}\n)"
        
        elif operator == "NotIn":
            val_str = ", ".join(f'"{v}"' if isinstance(v, str) else str(v) for v in values)
            expr = f"FILTER(\n    '{table}',\n    NOT {full_col} IN {{{val_str}}}\n)"
        
        elif operator == "Equals":
            v = values[0]
            v_str = f'"{v}"' if isinstance(v, str) else str(v)
            expr = f"FILTER(\n    '{table}',\n    {full_col} = {v_str}\n)"

        elif operator == "GreaterThan":
            expr = f"FILTER(\n    '{table}',\n    {full_col} > {values[0]}\n)"

        elif operator == "LessThan":
            expr = f"FILTER(\n    '{table}',\n    {full_col} < {values[0]}\n)"

        elif operator == "GreaterThanOrEqual":
            expr = f"FILTER(\n    '{table}',\n    {full_col} >= {values[0]}\n)"

        elif operator == "LessThanOrEqual":
            expr = f"FILTER(\n    '{table}',\n    {full_col} <= {values[0]}\n)"

        elif operator == "Between":
            start, end = values
            expr = f"FILTER(\n    '{table}',\n    {full_col} >= {start} && {full_col} <= {end}\n)"

        else:
            expr = f"-- Unsupported operator: {operator} on {full_col}"

        filter_expressions.append(expr)

    return filter_expressions


# Simulated Power BI data model
DATA_MODEL = {
  "tables": [
    {
      "name": "Consolidated Leads",
      "columns": [
        { "name": "Campaign Source", "type": "string" },
        { "name": "Company / Account", "type": "string" },
        { "name": "County/State/Province (text only)", "type": "string" },
        { "name": "Created Date", "type": "date" },
        { "name": "Email", "type": "string" },
        { "name": "First Name", "type": "string" },
        { "name": "Last Interesting Moment", "type": "string" },
        { "name": "Last Interesting Moment Date", "type": "date" },
        { "name": "Last Name", "type": "string" },
        { "name": "Lead ID", "type": "string" },
        { "name": "Lead Owner", "type": "string" },
        { "name": "Lead Source", "type": "string" },
        { "name": "Lead Status", "type": "string" },
        { "name": "Lead Sub-Stage", "type": "string" },
        { "name": "Phone", "type": "string" },
        { "name": "Proposal Opportunities", "type": "number" },
        { "name": "Source Campaign", "type": "string" },
        { "name": "Source Campaign_1", "type": "string" },
        { "name": "Status", "type": "string" },
        { "name": "Title", "type": "string" }
      ]
    },
    {
      "name": "Opportunity Details",
      "columns": [
        { "name": "Account ID", "type": "string" },
        { "name": "Account Name", "type": "string" },
        { "name": "Age", "type": "number" },
        { "name": "Amount", "type": "number" },
        { "name": "Amount Currency", "type": "string" },
        { "name": "Annual Recurring Revenue", "type": "number" },
        { "name": "Annual Recurring Revenue Currency", "type": "string" },
        { "name": "Billing City", "type": "string" },
        { "name": "Billing Country", "type": "string" },
        { "name": "Billing State/Province", "type": "string" },
        { "name": "Campaign Source", "type": "string" },
        { "name": "Channel Selling Partner", "type": "string" },
        { "name": "Channel Selling Partner_2", "type": "string" },
        { "name": "Close Date", "type": "date" },
        { "name": "Contact: Email", "type": "string" },
        { "name": "Contact: Title", "type": "string" },
        { "name": "Created Date", "type": "date" },
        { "name": "Current CRM System", "type": "string" },
        { "name": "Days Since Last Activity", "type": "number" },
        { "name": "Derived Rep Name", "type": "string" },
        { "name": "Employees", "type": "number" },
        { "name": "Industry", "type": "string" },
        { "name": "Industry_1", "type": "string" },
        { "name": "Last Activity", "type": "date" },
        { "name": "Last Modified Date", "type": "date" },
        { "name": "Last Stage Change Date", "type": "date" },
        { "name": "Lost Reason Details", "type": "string" },
        { "name": "Lost to", "type": "string" },
        { "name": "Next Step", "type": "string" },
        { "name": "Opportunity Geo-Region", "type": "string" },
        { "name": "Opportunity ID", "type": "string" },
        { "name": "Opportunity Name", "type": "string" },
        { "name": "Opportunity Owner", "type": "string" },
        { "name": "Opportunity Url", "type": "string" },
        { "name": "Parent Account", "type": "string" },
        { "name": "Primary Campaign Source", "type": "string" },
        { "name": "Primary Contact", "type": "string" },
        { "name": "Probability (%)", "type": "number" },
        { "name": "Qualified By", "type": "string" },
        { "name": "Qualified By Role", "type": "string" },
        { "name": "Reason for Closed Lost", "type": "string" },
        { "name": "Sequence Name", "type": "string" },
        { "name": "Source", "type": "string" },
        { "name": "Source Campaign", "type": "string" },
        { "name": "Stage", "type": "string" },
        { "name": "Stage Duration", "type": "number" },
        { "name": "Type", "type": "string" },
        { "name": "UC/CC", "type": "string" },
        { "name": "Website", "type": "string" }
      ]
    },
    {
      "name": "Date_table",
      "columns": [
        { "name": "Date", "type": "date" }
      ]
    },
    {
      "name": "Overall Meetings",
      "columns": [
        { "name": "Campaign Source", "type": "string" },
        { "name": "Created Date", "type": "date" },
        { "name": "Current BDR/AE Name", "type": "string" },
        { "name": "Email", "type": "string" },
        { "name": "Email Domain", "type": "string" },
        { "name": "Meeting Account Name", "type": "string" },
        { "name": "Opp ID", "type": "string" },
        { "name": "Sequence Name", "type": "string" },
        { "name": "Total_Meeting", "type": "number" }
      ]
    }
  ]
}

# Convert NL → Filter JSON using OpenAI
def parse_nl_to_conditions(nl_prompt):
    relationship_info = """
Table Relationships:
- 'Consolidated Leads' ↔ 'Opportunity Details' joined by 'Campaign Source'.
- 'Consolidated Leads' ↔ 'Date_table' joined by 'Created Date' and 'Date'.
- 'Consolidated Leads' ↔ 'Overall Meetings' joined by 'Campaign Source'.
"""
    system_prompt = f"""
You are an assistant that converts natural language into structured Power BI filters using the Power BI JavaScript SDK format.

Instructions:
- By default, output filters with "scope": "page" unless the user explicitly says things like "for the entire report", "across all pages", or "global filter", in which case use "scope": "report".
- Use only the tables and columns provided in the schema below.
- Do not hallucinate column names or values. If the column name or value is not mentioned in the schema, exclude it from the result.
- Match the values exactly and use the appropriate operator such as "In", "NotIn", "GreaterThan", "LessThan", "Between", etc.
- Output a list of filters in JSON format. Each filter must include:
  - target → table, column
  - operator
  - values
  - scope ("page" by default)
- do not use lead sub stage column

Schema:
{json.dumps(DATA_MODEL, indent=2)}
{relationship_info}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": nl_prompt}
        ],
        temperature=0
    )

    text_response = response.choices[0].message.content

    try:
        return json.loads(text_response)
    except json.JSONDecodeError:
        print("❌ Failed to parse AI output. Raw response:")
        print(text_response)
        return []

# Generate embedding filter JSON
def generate_embed_filter_json(conditions):
    return json.dumps(conditions, indent=2)

# Main function
def powerbi_filter_writer(nl_prompt):
    conditions = parse_nl_to_conditions(nl_prompt)
    embed_json = generate_embed_filter_json(conditions)
    return {
        "conditions": conditions,
        "embed_filter_json": embed_json
    }

# Run demo
prompt = st.text_input("💬 Enter your filter request: ",placeholder="type your text based filter prompt here !",key="prompt")
if __name__ == "__main__" and prompt:
    result = powerbi_filter_writer(prompt)
    dax = generate_dax_filter_expression_from_embed_json(json.loads(result["embed_filter_json"]))

    st.write("\n✅ Extracted Filter Conditions:")
    st.write(json.dumps(result["conditions"], indent=2))

    st.write("\n✅ Embedding Filter JSON:")
    st.write(result["embed_filter_json"])

    st.write("\n DAX")
    for f in dax:
        st.write(f + "\n")

    # Log feedback
    collect_feedback_and_log(prompt, result["embed_filter_json"])
