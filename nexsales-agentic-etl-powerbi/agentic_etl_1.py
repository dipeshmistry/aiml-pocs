import os
import pandas as pd
from fuzzywuzzy import fuzz
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import dotenv
dotenv.load_dotenv()
import cowsay

cowsay.cow("Good Mooooorning!\n Welcome to AgenticETL")

# ===== CONFIGURE GPT =====
# os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"  # Replace with your GPT API key
llm = ChatOpenAI(model_name="gpt-4", temperature=0)

# ===== SOURCE AGENT =====
class SourceAgent:
    def __init__(self, name, priority, df, mapping):
        self.name = name
        self.priority = priority
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
        if pd.notna(primary_row.get("email")):
            for col in candidate_row.index:
                if "email" in col.lower():
                    score += fuzz.token_sort_ratio(str(primary_row["email"]), str(candidate_row[col]))
        if pd.notna(primary_row.get("phone")):
            for col in candidate_row.index:
                if "phone" in col.lower():
                    score += fuzz.token_sort_ratio(str(primary_row["phone"]), str(candidate_row[col]))
        return score

    def confirm_with_gpt(self, primary_row, candidate_row):
        primary_str = primary_row.to_json()
        candidate_str = candidate_row.to_json()

        messages = [
            SystemMessage(content="You are helping match records across different data sources for ETL."),
            HumanMessage(content=f"Primary record: {primary_str}\nCandidate record: {candidate_str}\nAre these the same client? Respond with 'yes' or 'no'.")
        ]
        response = llm(messages).content.strip().lower()
        return response.startswith("yes")

# ===== ORCHESTRATOR AGENT =====
class OrchestratorAgent:
    def __init__(self, source_agents):
        self.source_agents = sorted(source_agents, key=lambda x: x.priority)

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
                            # print(f"Filled {col} for client {row.get('email', row.get('phone'))} using {agent.name}: {value}")
                            cowsay.cow(f"Filled {col} for client {row.get('email', row.get('phone'))} using {agent.name}: {value}")
                            break
                    if not filled:
                        cowsay.cow(f"Could not fill {col} for client {row.get('email', row.get('phone'))}")
        return df

# ===== MAIN =====
if __name__ == "__main__":
    # === Load sources (replace with real files) ===
    source_a_df = pd.DataFrame({
        "email_address": ["john@example.com", "jane@abc.com"],
        "contact_number": ["12345", "67890"]
    })
    source_b_df = pd.DataFrame({
        "EmailID": ["jdoe@example.com", "janedoe@abc.com"],
        "PhoneNum": ["12345", "54321"]
    })
    source_c_df = pd.DataFrame({
        "E-mail": ["doe.john@example.com", "jane_d@abc.com"],
        "Phone": ["11111", "22222"]
    })

    # === Mappings ===
    source_a_mapping = {"email": "email_address", "phone": "contact_number"}
    source_b_mapping = {"email": "EmailID", "phone": "PhoneNum"}
    source_c_mapping = {"email": "E-mail", "phone": "Phone"}

    # === Define agents ===
    source_agents = [
        SourceAgent("SourceA", 1, source_a_df, source_a_mapping),
        SourceAgent("SourceB", 2, source_b_df, source_b_mapping),
        SourceAgent("SourceC", 3, source_c_df, source_c_mapping)
    ]

    # === Primary data (with missing values) ===
    df = pd.DataFrame({
        "email": [None, "jane@abc.com"],
        "phone": ["12345", None]
    })

    # === Run orchestrator ===
    orchestrator = OrchestratorAgent(source_agents)
    filled_df = orchestrator.fill_missing_values(df)

    # === Final result ===
    cowsay.cow("\nFinal filled DataFrame:")
    print(filled_df)
