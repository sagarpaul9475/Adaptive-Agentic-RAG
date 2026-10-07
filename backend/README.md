# Backend

FastAPI backend for Adaptive Agentic RAG.

## Local setup

From the backend directory:

python -m venv .venv

Windows PowerShell:

.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload

API: http://127.0.0.1:8000
Swagger UI: http://127.0.0.1:8000/docs

## Current endpoints

- GET /health
- POST /api/documents/upload
- GET /api/documents
- DELETE /api/documents/{document_id}

Supported formats: PDF, TXT, Markdown, DOCX.

The ingestion pipeline validates the upload, stores the file, extracts text, normalizes and chunks it, stores chunk records as JSONL, and writes document metadata.

Vector embeddings and ChromaDB will be added in the next RAG milestone.
