import streamlit as st
import json
from datetime import date
from dotenv import load_dotenv

load_dotenv()

# --------------- MOCK OpenAI Filter Parsing ----------------
def mock_parse_prompt(nl_prompt):
    # Replace with actual OpenAI call in production
    if "proposal" in nl_prompt.lower():
        return {
            "Opportunity Details": {"Stage": "Proposal"},
            "Overall Meetings": {
                "Created Date": {
                    "between": ["2024-04-01", "2024-06-30"]
                }
            }
        }
    else:
        return {
            "Consolidated Leads": {
                "Lead Owner": "John Doe",
                "Campaign Source": "Email Campaign"
            }
        }

# --------------- DAX Generator ----------------
def generate_dax(table, conditions):
    filters = []
    for field, value in conditions.items():
        if isinstance(value, dict) and "between" in value:
            from_date = value["between"][0].replace("-", ",")
            to_date = value["between"][1].replace("-", ",")
            filters.append(f'{table}[{field}] >= DATE({from_date}) && {table}[{field}] <= DATE({to_date})')
        else:
            filters.append(f'{table}[{field}] = "{value}"')
    return f"CALCULATE(COUNTROWS('{table}'), " + ", ".join(filters) + ")"

# --------------- Power BI Embed Filter JSON ----------------
def generate_embed_json(table, conditions):
    filters = []
    for field, value in conditions.items():
        if isinstance(value, dict) and "between" in value:
            filters.append({
                "$schema": "http://powerbi.com/product/schema#advanced",
                "target": {"table": table, "column": field},
                "filterType": 1,
                "logicalOperator": "And",
                "conditions": [
                    {"operator": "GreaterThanOrEqual", "value": value["between"][0]},
                    {"operator": "LessThanOrEqual", "value": value["between"][1]}
                ]
            })
        else:
            filters.append({
                "$schema": "http://powerbi.com/product/schema#basic",
                "target": {"table": table, "column": field},
                "filterType": 1,
                "operator": "In",
                "values": [value]
            })
    return json.dumps(filters, indent=2)

# --------------- Streamlit UI ----------------
st.set_page_config(page_title="Power BI Filter Generator", page_icon="📊")
st.title("🧠 Natural Language to Power BI Filter Generator")

nl_prompt = st.text_input("""

        You are an AI assistant for writing Power BI filters.
        Given a natural language request, return a JSON object of conditions 
        If a column is not mentioned, don't include it.

## ✅ Correct DAX Syntax

Here’s the fixed version of your DAX expression:

```dax
Filtered Opportunities :=
CALCULATE(
    COUNTROWS('Opportunity Details'),
    'Opportunity Details'[Stage] = "Proposal"
)
```

🔹 **Key Rules to Remember:**

* Always wrap table names in **single quotes** if they contain spaces.
* Column references must be prefixed with the table name like `'Opportunity Details'[Stage]`
* Filter expressions inside `CALCULATE` **must be logical expressions** (like `=`, `<`, etc.) or use `FILTER(...)`

---

### ✅ For More Complex Filters (e.g. Date Range):

```dax
Filtered Opportunities :=
CALCULATE(
    COUNTROWS('Opportunity Details'),
    'Opportunity Details'[Stage] = "Proposal",
    'Opportunity Details'[Close Date] >= DATE(2024, 4, 1),
    'Opportunity Details'[Close Date] <= DATE(2024, 6, 30)
)
```

---

## ⚠️ Common Errors to Avoid

| Error                           | Fix                                                           |
| ------------------------------- | ------------------------------------------------------------- |
| `Details` is incorrect          | Use full table name in single quotes: `'Opportunity Details'` |
| Column not recognized           | Always prefix with table: `'Opportunity Details'[ColumnName]` |
| Multiple filters without commas | Separate all filters inside `CALCULATE` with commas           |

---

## 🧪 Want to Test?

Paste the corrected measure in Power BI:

1. Go to **Modeling > New Measure**
2. Name it: `Filtered Opportunities`
3. Paste:

   ```dax
   Filtered Opportunities :=
   CALCULATE(
       COUNTROWS('Opportunity Details'),
       'Opportunity Details'[Stage] = "Proposal"
   )
   ```
4. Add it to a **Card visual** — it will show how many opportunities are in "Proposal" stage

---

Let me know if you want to:

* Add dynamic **date filters** (like last 30 days)
* Filter by meetings using `TREATAS`
* Embed this logic in a slicer-like experience

I'm ready to help build those too.

                          Enter your filter request:
                          """, placeholder="e.g. Show opportunities in Proposal stage in Q2 2024")

if nl_prompt:
    parsed_conditions = mock_parse_prompt(nl_prompt)

    st.subheader("🔍 Parsed Filter Conditions")
    st.json(parsed_conditions)

    for table, conditions in parsed_conditions.items():
        st.markdown(f"### 📊 Table: `{table}`")

        dax = generate_dax(table, conditions)
        embed_json = generate_embed_json(table, conditions)

        st.markdown("#### 🧠 Generated DAX Expression")
        st.code(dax, language="dax")

        st.markdown("#### 🧩 Power BI Embed Filter JSON")
        st.code(embed_json, language="json")

    st.success("✅ Filters generated successfully!")

else:
    st.info("Enter a filter prompt above to begin.")
