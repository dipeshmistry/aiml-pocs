import pandas as pd
class OrchestratorAgent:
    def __init__(self):
        self.source_agents = []

    def register_agent(self, agent):
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
                            print(f"[{agent.name}] Filled {col} at index {idx} with: {value}")
                            break
                    if not filled:
                        print(f"[Orchestrator] Could not fill {col} at index {idx}")
        return df
