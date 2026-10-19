# nexsales-agentic-etl-powerbi

Agentic ETL and PowerBI-report-assistant experiments:

- `agentic_etl/` - a small multi-agent pipeline (source agent, ZoomInfo
  enrichment agent, GPT helper, orchestrator).
- `agentic_etl.py`, `agentic_etl_1.py`, `agentic_etl_2.py` - standalone
  iterations of the ETL agent.
- `dynamic_powerbi_filter.py`, `dynamic_powerbi_rag_based.py` - natural-language
  filtering of PowerBI reports (plain and RAG-based).
- `faiss_vs_powerbi.py` - comparing a FAISS vector search approach against a
  direct PowerBI query approach.
- `powerbi_demo.py`, `powerbi_report_helper_agent.py` - PowerBI helper agent demos.
- `powerbi_filter_feedback_log.jsonl` - sample feedback log used by the filter agent.

Copy `.env.example` to `.env` and set `OPENAI_API_KEY` before running.
