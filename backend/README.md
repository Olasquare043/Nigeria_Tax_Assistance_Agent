# Backend (FastAPI)

Start server:
```bash
uvicorn backend.main:app --reload --port 8000
```

Endpoints:
- GET  /health
- POST /ingest  (rebuild index from PDFs in `docs/`)
- POST /chat    (session-based chat)
