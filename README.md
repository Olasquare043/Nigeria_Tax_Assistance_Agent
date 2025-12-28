# Nigeria Tax Reform Bills (2024) — Q&A Assistant (Dev Mode)

This project is split into 3 parts:

1) **AI Engine** (`ai_engine/`) — ingestion, chunking, ChromaDB indexing, retrieval, and a simple LangGraph agent.
2) **Backend API** (`backend/`) — FastAPI chat API (session-based) that calls the AI engine.
3) **Frontend** (`frontend/`) — React + Tailwind chat UI that shows citations.

✅ **Developer mode only**: Uses **ChromaDB local persistence**.

---
## 0) Put your PDFs in `docs/`

Copy your PDFs into the `docs/` folder. Recommended filenames (but not required):
- `HB-1756-The-Nigeria-Tax-Administration-Bill-2024.pdf`
- `HB-1757-The-Nigeria-Revenue-Service-Establishment-Bill-2024.pdf`
- `HB-1758-The-Joint-Revenue-Board-Establishment-Bill-2024.pdf`
- `HB-1759-The-Nigeria-Tax-Bill-2024.pdf`
- `NASS-Journal_Nigeria-Tax-Bill.pdf`
- `Analysis-of-the-Nigerian-Tax-Reform-Bills.pdf`
- `The-Nigeria-Tax-Bill-2024-An-Intricate-Interrogation.pdf`
- `The-Nigerian-Tax-Reform-Bills-You-Ask-We-Answer.pdf`

---
## 1) Install Python dependencies

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Create `.env` in the project root:
```bash
.env   # Windows
# or:
.env     # Mac/Linux
```

Add your OpenAI key in `.env`.

---
## 2) Build the index (ingest PDFs)

```bash
python ai_engine/scripts/build_index.py
```

This creates/updates a Chroma index in `data/chroma/`.

---
## 3) Run Backend API

```bash
uvicorn backend.main:app --reload --port 8000
```

Health check:
- http://localhost:8000/health

---
## 4) Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:
- http://localhost:5173

---
## What will expect to get

- Answers use retrieved excerpts only.
- If the sources don’t support a claim, the assistant says:
  **"I can't confirm from the available sources."**
- Every factual answer includes citations (source + page + chunk id + short quote).
