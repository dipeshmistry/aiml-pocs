import pandas as pd
from source_agent import SourceAgent
from orchestrator import OrchestratorAgent
import json

if __name__ == "__main__":
    
    # Load ZoomInfo JSON
    with open("zoominfo_data.json", "r") as f:
        zoominfo_json = json.load(f)
    
    # source_a_df = pd.DataFrame({
    #     "LinkedInURL": ["https://linkedin.com/in/john-doe", "https://linkedin.com/in/jane-smith"],
    #     "first_name": ["John", "Jane"],
    #     "last_name": ["Doe", "Smith"],
    #     "Company Name": ["Acme Corp", ""],
    #     "EmailAddress": ["john@acme.com", "jane@beta.com"]
    # })

    # source_b_df = pd.DataFrame({
    #     "LinkedIn": ["https://linkedin.com/in/jdoe", "https://linkedin.com/in/jsmith"],
    #     "first_name": ["John", "Jane"],
    #     "last_name": ["Doe", "Smith"],
    #     "CompanyName": ["Acme Corporation", "Beta Limited"],
    #     "Email": ["jdoe@acme.com", "jsmith@beta.com"]
    # })

    # source_a_mapping = {
    #     "Contact linkedin URL": "LinkedInURL",
    #     "first_name": "first_name",
    #     "last_name": "last_name",
    #     "fnLnCompany": "Company Name",
    #     "Email": "EmailAddress"
    # }

    # source_b_mapping = {
    #     "Contact linkedin URL": "LinkedIn",
    #     "first_name": "first_name",
    #     "last_name": "last_name",
    #     "fnLnCompany": "CompanyName",
    #     "Email": "Email"
    # }

    orchestrator = OrchestratorAgent()
    orchestrator.register_agent(zoominfo_agent("ZoomInfo", 1, zoominfo_json))
    # orchestrator.register_agent(SourceAgent("SourceA", 1, source_a_df, source_a_mapping))
    # orchestrator.register_agent(SourceAgent("SourceB", 2, source_b_df, source_b_mapping))

    df = pd.read_csv('../Data/Contact Master Client Delivery 31st Jan.csv')

    filled_df = orchestrator.fill_missing_values(df)
    print("\nFinal filled DataFrame:")
    print(filled_df)
