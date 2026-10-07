# Architecture

Initial architecture for the project:

React UI -> FastAPI API -> LangGraph workflow -> Retrieval -> ChromaDB / embeddings -> LLM -> verification -> response.

The first implementation milestone is the backend health endpoint and repository structure. Retrieval, adaptive routing, query reformulation, and verification will be added incrementally.
