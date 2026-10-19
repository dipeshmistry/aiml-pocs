import os
import pandas as pd
from fuzzywuzzy import fuzz
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import cowsay
from dotenv import load_dotenv
load_dotenv()

# ===== CONFIGURE GPT =====
# os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"  # Replace with your GPT API key
llm = ChatOpenAI(model_name="gpt-4", temperature=0)

# ===== ABSTRACT BASE AGENT =====
class BaseAgent:
    def __init__(self, name, priority):
        self.name = name
        self.priority = priority

    def fetch(self, primary_row, field_name):
        raise NotImplementedError("Each agent must implement fetch method")

# ===== SOURCE AGENT =====
class SourceAgent(BaseAgent):
    def __init__(self, name, priority, df, mapping):
        super().__init__(name, priority)
        self.df = df
        self.mapping = mapping

    def fetch(self, primary_row, field_name):
        best_score = 0
        best_candidate = None

        for _, candidate_row in self.df.iterrows():
            score = self.compute_similarity(primary_row, candidate_row)
            if score > best_score:
                best_score = score
                best_candidate = candidate_row

        if best_candidate is not None:
            if self.confirm_with_gpt(primary_row, best_candidate):
                source_col = self.mapping.get(field_name)
                if source_col and source_col in best_candidate.index:
                    val = best_candidate[source_col]
                    return val if pd.notna(val) else None
        return None

    def compute_similarity(self, primary_row, candidate_row):
        score = 0
        # LinkedIn URL
        if pd.notna(primary_row.get("Contact linkedin URL")):
            for col in candidate_row.index:
                if "linkedin" in col.lower():
                    score += fuzz.token_sort_ratio(str(primary_row["Contact linkedin URL"]), str(candidate_row[col]))
        # Email
        if pd.notna(primary_row.get("Email")):
            for col in candidate_row.index:
                if "email" in col.lower():
                    score += fuzz.token_sort_ratio(str(primary_row["Email"]), str(candidate_row[col]))
        # Name
        if pd.notna(primary_row.get("first_name")) and pd.notna(primary_row.get("last_name")):
            candidate_fullname = f"{candidate_row.get('first_name', '')} {candidate_row.get('last_name', '')}"
            primary_fullname = f"{primary_row['first_name']} {primary_row['last_name']}"
            score += fuzz.token_sort_ratio(primary_fullname, candidate_fullname)
        # Company
        if pd.notna(primary_row.get("fnLnCompany")):
            for col in candidate_row.index:
                if "company" in col.lower():
                    score += fuzz.token_sort_ratio(str(primary_row["fnLnCompany"]), str(candidate_row[col]))
        return score

    def confirm_with_gpt(self, primary_row, candidate_row):
        primary_str = primary_row.to_json()
        candidate_str = candidate_row.to_json()

        messages = [
            SystemMessage(content="You are helping match records across different data sources for ETL enrichment."),
            HumanMessage(content=f"Primary record: {primary_str}\nCandidate record: {candidate_str}\nAre these the same client? Respond with 'yes' or 'no'.")
        ]
        response = llm(messages).content.strip().lower()
        return response.startswith("yes")

# ===== ORCHESTRATOR AGENT =====
class OrchestratorAgent:
    def __init__(self):
        self.source_agents = []

    def register_agent(self, agent: BaseAgent):
        self.source_agents.append(agent)
        self.source_agents.sort(key=lambda x: x.priority)

    def fill_missing_values(self, df):
        for idx, row in df.iterrows():
            for col in df.columns:
                if pd.isna(row[col]):
                    filled = False
                    for agent in self.source_agents:
                        value = agent.fetch(row, col)
                        if value:
                            df.at[idx, col] = value
                            filled = True
                            cowsay.cow(f"[{agent.name}] Filled {col} at index {idx} with: {value}")
                            break
                    if not filled:
                        cowsay.cow(f"[Orchestrator] Could not fill {col} at index {idx}")
        return df

# ===== MAIN =====
if __name__ == "__main__":
    # === Simulated source data ===
    source_a_df = pd.DataFrame({
        "LinkedInURL": ["https://linkedin.com/in/john-doe", "https://linkedin.com/in/jane-smith"],
        "first_name": ["John", "Jane"],
        "last_name": ["Doe", "Smith"],
        "Company Name": ["Acme Corp", "Beta LLC"],
        "EmailAddress": ["john@acme.com", "jane@beta.com"]
    })

    source_b_df = pd.DataFrame({
        "LinkedIn": ["https://linkedin.com/in/jdoe", "https://linkedin.com/in/jsmith"],
        "first_name": ["John", "Jane"],
        "last_name": ["Doe", "Smith"],
        "CompanyName": ["Acme Corporation", "Beta Limited"],
        "Email": ["jdoe@acme.com", "jsmith@beta.com"]
    })

    # === Mappings ===
    source_a_mapping = {
        "Contact linkedin URL": "LinkedInURL",
        "first_name": "first_name",
        "last_name": "last_name",
        "fnLnCompany": "Company Name",
        "Email": "EmailAddress"
    }

    source_b_mapping = {
        "Contact linkedin URL": "LinkedIn",
        "first_name": "first_name",
        "last_name": "last_name",
        "fnLnCompany": "CompanyName",
        "Email": "Email"
    }

    # === Create orchestrator ===
    orchestrator = OrchestratorAgent()

    # === Register source agents ===
    orchestrator.register_agent(SourceAgent("SourceA", 1, source_a_df, source_a_mapping))
    orchestrator.register_agent(SourceAgent("SourceB", 2, source_b_df, source_b_mapping))

    # === Primary dataset ===
    df = pd.DataFrame({
        "Contact linkedin URL": ["https://linkedin.com/in/john-doe", None],
        "first_name": ["John", "Jane"],
        "last_name": ["Doe", None],
        "fnLnCompany": [None, "Beta LLC"],
        "Email": [None, None]
    })

    # === Run orchestrator ===
    filled_df = orchestrator.fill_missing_values(df)

    # === Final result ===
    cowsay.cow("\nFinal filled DataFrame:")
    cowsay.cow(filled_df)
