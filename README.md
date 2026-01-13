# 🇳🇬 Taxify AI Assistant: Nigerian Tax Reform Q&A

Bridging the gap between 500+ pages of tax law and 200 million citizens.

Taxify AI is an Agentic RAG-powered assistant designed to help Nigerians understand the Tax Reform Bills. By transforming dense legal PDFs into a conversational interface, we empower small business owners, employees, and citizens with factual, source-backed answers to complex fiscal questions.

---

## 👥 The Development Team

Our group is structured into two specialized units to ensure high-performance AI and seamless user experience:

- **AI Engineers**: Responsible for the "Brain" of the project: document ingestion, vector database management (ChromaDB), and designing the Agentic workflows in LangGraph.
  - *Team Members*: [ Saheed Olayinka], [Ridwanullah Osho]

- **AI Developers (Full-Stack)**: Responsible for the "Bridge" and "UI": building the FastAPI backend, session management, and the React +tailwind frontend interface.
  - *Team Members*: [Mariam Adesina], [Oluwaseyi Alebiosu]

---

## 🛠️ Technical Stack

- **AI Engine**: LangChain, LangGraph, OpenAI (GPT-4o), ChromaDB
- **Backend**: FastAPI (Python), Database(MYSQL)
- **Frontend**: React , Tailwind CSS

---

## ✨ Key Features

- **Agentic Routing**: Identifies greetings vs. policy questions to save compute and improve accuracy
- **Source Anchoring**: Prevents hallucinations by citing the specific 2024 Bill (e.g., Nigeria Tax Bill or Nigeria Revenue Service Bill)
- **Contextual Memory**: Remembers previous questions in a session for natural follow-up inquiries
- **Mobile-First Design**: Fully responsive UI tailored for the Nigerian mobile-user demographic

---

## 📂 Project Structure

```
taxify-ai-assistant/
├── ai_engine/          # LangGraph agents, ChromaDB scripts, and document processing
├── backend/            # FastAPI server, session management, and API logic
├── frontend/           # React 19 UI (Vite, Tailwind, React Router DOM)
├── docs/               # The 4 official Tax Reform Bill PDFs (2024)
└── data/               # Persistent ChromaDB vector store
```

---

## 📱 Chatinterface for mobile,tablet and desktop view 

### desktop
![destktop](https://github.com/user-attachments/assets/99ba9b21-4f0b-4ec0-94ad-c4b18cdff98b)

### tablet
![tablet](https://github.com/user-attachments/assets/26cb36e1-4326-4a95-a681-161416295fb6)

### Mobile Home
![mobile](https://github.com/user-attachments/assets/8088dbd4-253c-4134-9444-f3f79c7fa885)

### Mobile Dashboard
![mobilechat](https://github.com/user-attachments/assets/2d1986ed-1c1c-44a5-ac88-317b71197d79)


## 🔁 Agentic routing flow
![Langgraph flow](https://github.com/user-attachments/assets/e742aba5-a2aa-4c53-bf06-d8cf034c5447)

## ⚙️ Quick Start (Developer Mode)

### 0️⃣ Prerequisites
- Python 3.10+ & Node.js 18+
- OpenAI API Key

### 1️⃣ Prepare Your Documents
Place your PDFs in the `docs/` folder. Recommended filenames (not required):
- `HB-1756-The-Nigeria-Tax-Administration-Bill-2024.pdf`
- `HB-1757-The-Nigeria-Revenue-Service-Establishment-Bill-2024.pdf`
- `HB-1758-The-Joint-Revenue-Board-Establishment-Bill-2024.pdf`
- `HB-1759-The-Nigeria-Tax-Bill-2024.pdf`
- `NASS-Journal_Nigeria-Tax-Bill.pdf`
- `Analysis-of-the-Nigerian-Tax-Reform-Bills.pdf`
- `The-Nigeria-Tax-Bill-2024-An-Intricate-Interrogation.pdf`
- `The-Nigerian-Tax-Reform-Bills-You-Ask-We-Answer.pdf`

### 2️⃣ Setup AI Engine & Backend
```bash
# Clone and setup environment
git clone <your-repo-link>
cd taxify-ai-assistant
python -m venv .venv


# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
# Create .env file with your OpenAI API key:
# OPENAI_API_KEY=your_key_here

# Ingest PDFs and build vector index
python ai_engine/scripts/build_index.py
# Creates/updates ChromaDB index in data/chroma/

#load database 
python database.py


# Start backend server
uvicorn backend.main:app --reload --port 8000
```


### 3️⃣ Setup Frontend
```bash
cd frontend
npm install 
npm install tailwindcss @tailwindcss/vite
npm install react-router-dom
npm install react-icons
npm run dev
```
Open: http://localhost:5173

---

## ✅ Expected Behavior

- Answers use retrieved excerpts only from the provided sources
- If sources don't support a claim, the assistant responds: **"I can't confirm from the available sources."**
- Every factual answer includes citations with:
  - Source document name
  - Page number
  - Chunk ID
  - Short supporting quote

---

## 🛣️ Roadmap & Future Improvements

- **Technical Pivot**: We migrated from simple sequential chains(langchains) to Agentic Routing to prevent hallucinations with non-tax questions
- **Multilingual Support**: We plan to integrate Hausa, Yoruba, Igbo, and Nigerian Pidgin in the future
- **Accessibility**: We plan to expand to WhatsApp and Telegram for users in low-connectivity regions

---


