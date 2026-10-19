import re
import pandas as pd
from fuzzywuzzy import fuzz
from base_agent import BaseAgent
from gpt_helper import confirm_with_gpt, extract_info_with_gpt

class ZoomInfoAgent(BaseAgent):
    def __init__(self, name, priority, json_data):
        super().__init__(name, priority)
        self.df = pd.DataFrame(json_data)

    def fetch(self, primary_row, field_name):
        best_score = 0
        best_candidate = None
        target_company = primary_row.get("fnLnCompany")

        if pd.isna(target_company):
            return None

        for _, candidate_row in self.df.iterrows():
            score = fuzz.token_sort_ratio(str(target_company), str(candidate_row["name"]))
            if score > best_score:
                best_score = score
                best_candidate = candidate_row

        if best_candidate is not None and confirm_with_gpt(primary_row, best_candidate):
            return self.extract_field(best_candidate, field_name)
        return None

    def extract_field(self, candidate_row, field_name):
        desc = candidate_row["description"]
        if field_name == "Zoominfo Company Name":
            return candidate_row["name"]
        if field_name == "Zoominfo Revenue Actual":
            return candidate_row["revenue"]
        if field_name == "Zoominfo Company URL":
            return candidate_row["url"]
        if field_name == "Zoominfo Description":
            return desc
        if field_name == "Zoominfo Industry":
            return self.extract_industry(desc)
        if field_name == "Zoominfo Company City":
            return self.extract_location(desc)
        if field_name == "Zoominfo Employee Range":
            return self.extract_size(desc)
        return None

    def extract_industry(self, desc):
        match = re.search(r'in the (.*?) industry', desc, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        gpt_data = extract_info_with_gpt(desc)
        return gpt_data.get("industry")

    def extract_location(self, desc):
        match = re.search(r'is (.*?)\'s largest', desc, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        gpt_data = extract_info_with_gpt(desc)
        return gpt_data.get("location")

    def extract_size(self, desc):
        match = re.search(r'employs (\d+\w*to*\w*\d*) people', desc, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        gpt_data = extract_info_with_gpt(desc)
        return gpt_data.get("size")
