# AI/ML POCs

A collection of proof-of-concept projects and course exercises from exploring
LLMs, LangChain, LangGraph, and RAG/vector-search patterns.

## Projects

- **nexsales-agentic-etl-powerbi** - agentic ETL pipeline and PowerBI report
  assistants (natural-language filtering over PowerBI reports, FAISS vs. PowerBI
  comparisons, a ZoomInfo-enrichment agent).
- **langgraph-agentic-chatbot** - LangGraph-based agent experiments: a basic
  chatbot, a multi-agent graph, and an Ollama-backed cloud agent.
- **langchain-basics** - small LangChain chat-model examples.
- **langchain-masterclass-labs** - exercises from the "ChatGPT and LangChain:
  The Complete Developer's Masterclass" course (adding tools, output parsing,
  securing API keys, connecting chains, chaining prompts).
- **misc-notebooks** - standalone notebooks/scripts: a sales-data analysis
  notebook and a small image-analysis demo.

## Notes

- Datasets, pretrained model files, vector stores, and virtual environments
  are intentionally excluded - only source code and notebooks are kept here.
- No `.env` files or API keys are committed. Set `OPENAI_API_KEY` (and any
  other required secret) in your own environment before running any of these.
- `langchain-masterclass-labs` is course-exercise code; the course's own
  slide/diagram material is not included here.
