# Intelligent Research Assistant — RAG with ChromaDB

A RAG-based research assistant that lets you upload academic PDFs and ask questions about them. It uses **ChromaDB** as the persistent vector database for semantic search and **Llama 3.1** (via Groq) for generating answers with page-level citations.

---

## Demo

🔗 Google Drive Demo: https://drive.google.com/file/d/11UGEhl7fCkm1TP3Kiatr184JePkf4LuU/view?usp=sharing

## Problem

Searching through long academic papers manually is slow. Keyword search doesn't understand context or intent. This project uses semantic search + RAG to give you precise, cited answers from your documents.

---

## Architecture

```
User (Streamlit UI)
    │
    ├── Upload PDF ──→ FastAPI /upload
    │                      │
    │                      └── Ingestion Pipeline
    │                              ├── Extract text (pypdf)
    │                              ├── Chunk text (500 chars, 50 overlap)
    │                              ├── Generate embeddings (MiniLM)
    │                              └── Store in ChromaDB
    │
    └── Ask Question ──→ FastAPI /chat
                             │
                             └── Retrieval Pipeline
                                     ├── Embed query (MiniLM)
                                     ├── Search ChromaDB (top 5 similar chunks)
                                     └── Generate answer (Llama 3.1 via Groq)
                                          └── Return answer + citations
```

---

## How ChromaDB is Used

ChromaDB is the core vector database in this project. Here's what it does:

- **Stores** 384-dimensional embeddings for each document chunk.
- **Indexes** vectors with metadata (filename, page number, chunk ID).
- **Searches** using cosine similarity to find the most relevant chunks for a query.
- **Persistence**: Data is saved locally in the `backend/chroma_db` directory, so it survives application restarts.

---

## Project Structure

```
├── backend/
│   ├── main.py            # FastAPI app + routes
│   ├── models.py          # Request/response schemas
│   ├── embeddings.py      # Sentence-transformers utility
│   ├── chroma_store.py    # ChromaDB client and persistence
│   └── pipeline/          # Modularized RAG components
│       ├── ingestion.py   # PDF extraction, chunking, and storage
│       └── retrieval.py   # Query processing and answer generation
├── frontend/
│   └── app.py             # Streamlit chat UI
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── Makefile
├── .env.example
└── README.md
```

---

## Tech Stack

| Component | Tech |
|-----------|------|
| Vector DB | ChromaDB |
| LLM | Llama 3.1 8B (Groq) |
| Embeddings | all-MiniLM-L6-v2 |
| Backend | FastAPI |
| Frontend | Streamlit |
| Containerization | Docker |

---

## Setup

### Prerequisites
- Docker
- Python 3.9+
- [Groq API key](https://console.groq.com/keys) (free)

### 1. Clone this project

```bash
git clone <your-fork-url>
cd Endee-Assignment
cp .env.example .env
# edit .env and add your GROQ_API_KEY
```

### 2. Run with Docker (recommended)

```bash
docker-compose up --build
```

This starts both the backend (port 8000) and frontend (port 8501).

### 2b. Or run manually

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# terminal 1 (Backend)
uvicorn backend.main:app --reload --port 8000

# terminal 2 (Frontend)
streamlit run frontend/app.py
```

### 3. Use it

1. Open `http://localhost:8501`
2. Upload a PDF in the sidebar
3. Ask questions in the chat

---

## API

| Endpoint | Method | What it does |
|----------|--------|-------------|
| `/upload` | POST | Upload and process a PDF |
| `/chat` | POST | Ask a question, get formatted answer + citations |
| `/health` | GET | Health check (reports vector store status) |

---

## Limitations

- Only works with text-based PDFs (no OCR for scanned docs).
- Single collection — all documents are stored in the same index.
- Chat history resets on page reload.
- Optimized for English text processing.
