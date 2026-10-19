from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

# -------------------------------
# Step 1: Flatten the Data Model
# -------------------------------

def flatten_data_model_to_documents(data_model: dict) -> list[Document]:
    documents = []
    for table in data_model["tables"]:
        table_name = table["name"]
        schema_lines = [f"Table: {table_name}"]
        for col in table["columns"]:
            schema_lines.append(f"- {col['name']} ({col['type']})")
        doc_text = "\n".join(schema_lines)
        documents.append(Document(page_content=doc_text, metadata={"table": table_name}))
    return documents


# -------------------------------
# Step 2: Create Chroma Vector Store
# -------------------------------

def create_vector_store(docs):
    embedding = OpenAIEmbeddings()
    # Automatically persisted when persist_directory is given
    Chroma.from_documents(
        documents=docs,
        embedding=embedding,
        persist_directory="vectorstores/powerbi_schema_chroma"
    )


# -------------------------------
# Step 3: Load and Retrieve
# -------------------------------

def load_vector_store():
    return Chroma(
        persist_directory="vectorstores/powerbi_schema_chroma",
        embedding_function=OpenAIEmbeddings()
    )

def retrive_context(query):
    vectorstore = load_vector_store()
    results = vectorstore.similarity_search(query, k=3)
    return "\n\n".join([doc.page_content for doc in results])


# -------------------------------
# Step 4: Your Data Model
# -------------------------------

DATA_MODEL = {
    "tables": [
        {
            "name": "Consolidated Leads",
            "columns": [
                {"name": "Campaign Source", "type": "string"},
                {"name": "Company / Account", "type": "string"},
                {"name": "County/State/Province (text only)", "type": "string"},
                {"name": "Created Date", "type": "date"},
                {"name": "Email", "type": "string"},
                {"name": "First Name", "type": "string"},
                {"name": "Last Interesting Moment", "type": "string"},
                {"name": "Last Interesting Moment Date", "type": "date"},
                {"name": "Last Name", "type": "string"},
                {"name": "Lead ID", "type": "string"},
                {"name": "Lead Owner", "type": "string"},
                {"name": "Lead Source", "type": "string"},
                {"name": "Lead Status", "type": "string"},
                {"name": "Lead Sub-Stage", "type": "string"},
                {"name": "Phone", "type": "string"},
                {"name": "Proposal Opportunities", "type": "number"},
                {"name": "Source Campaign", "type": "string"},
                {"name": "Source Campaign_1", "type": "string"},
                {"name": "Status", "type": "string"},
                {"name": "Title", "type": "string"}
            ]
        },
        {
            "name": "Opportunity Details",
            "columns": [
                {"name": "Account ID", "type": "string"},
                {"name": "Account Name", "type": "string"},
                {"name": "Age", "type": "number"},
                {"name": "Amount", "type": "number"},
                {"name": "Amount Currency", "type": "string"},
                {"name": "Annual Recurring Revenue", "type": "number"},
                {"name": "Annual Recurring Revenue Currency", "type": "string"},
                {"name": "Billing City", "type": "string"},
                {"name": "Billing Country", "type": "string"},
                {"name": "Billing State/Province", "type": "string"},
                {"name": "Campaign Source", "type": "string"},
                {"name": "Channel Selling Partner", "type": "string"},
                {"name": "Channel Selling Partner_2", "type": "string"},
                {"name": "Close Date", "type": "date"},
                {"name": "Contact: Email", "type": "string"},
                {"name": "Contact: Title", "type": "string"},
                {"name": "Created Date", "type": "date"},
                {"name": "Current CRM System", "type": "string"},
                {"name": "Days Since Last Activity", "type": "number"},
                {"name": "Derived Rep Name", "type": "string"},
                {"name": "Employees", "type": "number"},
                {"name": "Industry", "type": "string"},
                {"name": "Industry_1", "type": "string"},
                {"name": "Last Activity", "type": "date"},
                {"name": "Last Modified Date", "type": "date"},
                {"name": "Last Stage Change Date", "type": "date"},
                {"name": "Lost Reason Details", "type": "string"},
                {"name": "Lost to", "type": "string"},
                {"name": "Next Step", "type": "string"},
                {"name": "Opportunity Geo-Region", "type": "string"},
                {"name": "Opportunity ID", "type": "string"},
                {"name": "Opportunity Name", "type": "string"},
                {"name": "Opportunity Owner", "type": "string"},
                {"name": "Opportunity Url", "type": "string"},
                {"name": "Parent Account", "type": "string"},
                {"name": "Primary Campaign Source", "type": "string"},
                {"name": "Primary Contact", "type": "string"},
                {"name": "Probability (%)", "type": "number"},
                {"name": "Qualified By", "type": "string"},
                {"name": "Qualified By Role", "type": "string"},
                {"name": "Reason for Closed Lost", "type": "string"},
                {"name": "Sequence Name", "type": "string"},
                {"name": "Source", "type": "string"},
                {"name": "Source Campaign", "type": "string"},
                {"name": "Stage", "type": "string"},
                {"name": "Stage Duration", "type": "number"},
                {"name": "Type", "type": "string"},
                {"name": "UC/CC", "type": "string"},
                {"name": "Website", "type": "string"}
            ]
        },
        {
            "name": "Date_table",
            "columns": [
                {"name": "Date", "type": "date"}
            ]
        },
        {
            "name": "Overall Meetings",
            "columns": [
                {"name": "Campaign Source", "type": "string"},
                {"name": "Created Date", "type": "date"},
                {"name": "Current BDR/AE Name", "type": "string"},
                {"name": "Email", "type": "string"},
                {"name": "Email Domain", "type": "string"},
                {"name": "Meeting Account Name", "type": "string"},
                {"name": "Opp ID", "type": "string"},
                {"name": "Sequence Name", "type": "string"},
                {"name": "Total_Meeting", "type": "number"}
            ]
        }
    ]
}

# -------------------------------
# Run once to create and persist
# -------------------------------

docs = flatten_data_model_to_documents(DATA_MODEL)
create_vector_store(docs)

# -------------------------------
# Example usage
# -------------------------------
# context = retrive_context("leads with status closed lost")
# print(context)
