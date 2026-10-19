import os
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import dotenv
dotenv.load_dotenv()


# ===== CONFIGURATION =====
# os.environ["OPENAI_API_KEY"] = ""  # Replace with your actual key
llm = ChatOpenAI(model_name="gpt-4", temperature=0)

# ===== SOURCE AGENT CLASS =====
class SourceAgent:
    def __init__(self, name, priority, fetch_function):
        self.name = name
        self.priority = priority
        self.fetch = fetch_function

# ===== ORCHESTRATOR CLASS =====
class OrchestratorAgent:
    def __init__(self, source_agents):
        self.source_agents = sorted(source_agents, key=lambda x: x.priority)

    def fill_missing_values(self, df):
        for idx, row in df.iterrows():
            for col in df.columns:
                if pd.isna(row[col]):
                    filled = False
                    for agent in self.source_agents:
                        value = agent.fetch(row['client_id'], col)
                        if value:
                            decision = self.confirm_with_gpt(agent.name, col, value)
                            if decision == "accept":
                                df.at[idx, col] = value
                                filled = True
                                print(f"Filled {col} for client {row['client_id']} using {agent.name}: {value}")
                                break
                            else:
                                print(f"GPT rejected {value} from {agent.name} for {col}")
                    if not filled:
                        print(f"Could not fill {col} for client {row['client_id']}")
        return df

    def confirm_with_gpt(self, source_name, field, value):
        messages = [
            SystemMessage(content="You are an AI assistant helping with data ETL filling."),
            HumanMessage(content=f"A value '{value}' was retrieved from {source_name} for the field '{field}'. Should we accept this value? Respond with 'accept' or 'reject'.")
        ]
        response = llm(messages).content.strip().lower()
        return response if response in ["accept", "reject"] else "reject"

# ===== SOURCE FETCH FUNCTIONS =====
def fetch_from_source_a(client_id, field_name):
    return f"SourceA_value_for_{field_name}" if client_id % 2 == 0 else None

def fetch_from_source_b(client_id, field_name):
    return f"SourceB_value_for_{field_name}" if client_id % 3 == 0 else None

def fetch_from_source_c(client_id, field_name):
    return f"SourceC_value_for_{field_name}" if client_id % 5 == 0 else None

# ===== MAIN SCRIPT =====
if __name__ == "__main__":
    # Example dataset
    data = {
        "client_id": [1, 2, 3, 4, 5],
        "email": [None, None, "abc@x.com", None, None],
        "phone": ["12345", None, None, None, "98765"]
    }
    df = pd.DataFrame(data)

    # Initialize agents
    source_agents = [
        SourceAgent("SourceA", 1, fetch_from_source_a),
        SourceAgent("SourceB", 2, fetch_from_source_b),
        SourceAgent("SourceC", 3, fetch_from_source_c)
    ]

    # Run orchestrator
    orchestrator = OrchestratorAgent(source_agents)
    filled_df = orchestrator.fill_missing_values(df)

    # Show final result
    print("\nFinal Filled DataFrame:")
    print(filled_df)
