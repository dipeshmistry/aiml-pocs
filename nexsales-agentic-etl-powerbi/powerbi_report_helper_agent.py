from openai import OpenAI
import json
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
client = OpenAI()  # OR: client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Simulated Power BI data model
DATA_MODEL = {
    "Sales": ["Date", "Region", "Amount", "Category"]
}

# Generate DAX expression
def generate_dax_filter(table, conditions):
    filters = []
    for field, value in conditions.items():
        if field == "Date":
            filters.append(f"YEAR({table}[{field}]) = {value}")
        else:
            filters.append(f'{table}[{field}] = "{value}"')
    return f"CALCULATE(SUM({table}[Amount]), {', '.join(filters)})"

# Generate Power BI embedding filter JSON
def generate_embed_filter_json(table, conditions):
    filters = []
    for field, value in conditions.items():
        filters.append({
            "table": table,
            "column": field,
            "operator": "In",
            "values": [value]
        })
    return json.dumps(filters, indent=2)

# Parse NL to filter conditions using OpenAI
def parse_nl_to_conditions(nl_prompt, table_columns):
    system_prompt = (
        f"You are an AI assistant for writing Power BI filters. "
        f"The table is 'Sales'. Columns are: {', '.join(table_columns)}. "
        f"Given a natural language request, return a JSON object of conditions "
        f"in this format: {{\"Region\": \"West\", \"Date\": 2024}}. "
        f"If a column is not mentioned, don't include it."
    )

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
        return {}

# Main function
def powerbi_filter_writer(nl_prompt):
    table = "Sales"
    columns = DATA_MODEL[table]
    conditions = parse_nl_to_conditions(nl_prompt, columns)
    dax = generate_dax_filter(table, conditions)
    embed_json = generate_embed_filter_json(table, conditions)
    return {
        "conditions": conditions,
        "dax": dax,
        "embed_filter_json": embed_json
    }

# Run demo
if __name__ == "__main__":
    prompt = input("Enter your filter request: ")
    result = powerbi_filter_writer(prompt)

    print("\n✅ Extracted Conditions:")
    print(json.dumps(result["conditions"], indent=2))
    print("\n✅ Generated DAX:")
    print(result["dax"])
    print("\n✅ Generated Embedding Filter JSON:")
    print(result["embed_filter_json"])
