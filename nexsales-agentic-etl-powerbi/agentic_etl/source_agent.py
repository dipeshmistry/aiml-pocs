from fuzzywuzzy import fuzz
from base_agent import BaseAgent
from gpt_helper import confirm_with_gpt
import pandas as pd

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
            if confirm_with_gpt(primary_row, best_candidate):
                source_col = self.mapping.get(field_name)
                if source_col and source_col in best_candidate.index:
                    val = best_candidate[source_col]
                    return val if pd.notna(val) else None
        return None

    def compute_similarity(self, primary_row, candidate_row):
        score = 0
        if pd.notna(primary_row.get("Contact linkedin URL")):
            for col in candidate_row.index:
                if "linkedin" in col.lower():
                    score += fuzz.token_sort_ratio(str(primary_row["Contact linkedin URL"]), str(candidate_row[col]))
        if pd.notna(primary_row.get("Email")):
            for col in candidate_row.index:
                if "email" in col.lower():
                    score += fuzz.token_sort_ratio(str(primary_row["Email"]), str(candidate_row[col]))
        if pd.notna(primary_row.get("first_name")) and pd.notna(primary_row.get("last_name")):
            candidate_fullname = f"{candidate_row.get('first_name', '')} {candidate_row.get('last_name', '')}"
            primary_fullname = f"{primary_row['first_name']} {primary_row['last_name']}"
            score += fuzz.token_sort_ratio(primary_fullname, candidate_fullname)
        if pd.notna(primary_row.get("fnLnCompany")):
            for col in candidate_row.index:
                if "company" in col.lower():
                    score += fuzz.token_sort_ratio(str(primary_row["fnLnCompany"]), str(candidate_row[col]))
        return score
