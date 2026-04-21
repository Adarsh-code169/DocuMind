# DocuMind Knowledge Engine 🧠

DocuMind is an intelligent RAG (Retrieval-Augmented Generation) application designed to turn static academic papers and technical documents into conversational knowledge. It leverages **ChromaDB** for high-performance vector search and **Llama 3.1** (via Groq) for lightning-fast, cited answers.

---

## ✨ Features

*   **Semantic Search**: Finds relevant information based on meaning, not just keywords.
*   **Page-Level Citations**: Every answer includes the exact file and page number used as a source.
*   **Modern React UI**: A premium, dark-mode-first interface built with Tailwind CSS and Lucide.
*   **FastAPI Backend**: High-performance streaming responses for a real-time chat experience.
*   **ChromaDB Persistence**: Your knowledge base survives restarts using local vector storage.

---

## 🏛️ Architecture

```
User (React UI)  <─── Served from Root (/) ───  FastAPI (Backend)
     │                                            │
     ├── Upload PDF  ──────────→  /upload  ───────┤
     │                              │             │
     │                              └── Ingestion Pipeline
     │                                      ├── Extract (PyPDF)
     │                                      ├── Chunk (Recursive)
     │                                      ├── Embed (MiniLM)
     │                                      └── Index (ChromaDB)
     │
     └── Ask Question ─────────→  /chat  ─────────┤
                                    │             │
                                    └── Retrieval Pipeline
                                            ├── Embed Query
                                            ├── Neural Search
                                            └── GenAI (Groq)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React (Vanilla JS), Tailwind CSS, Lucide Icons |
| **Backend** | FastAPI (Python 3.11/3.12) |
| **Vector DB** | ChromaDB |
| **Embeddings** | all-MiniLM-L6-v2 (sentence-transformers) |
| **LLM** | Llama 3.1 8B/70B (via Groq) |
| **Deployment** | Hugging Face Spaces (Free) / Render |

---

## 🚀 Deployment (Keep the React UI)

### Option 1: Hugging Face Spaces (100% Free) 🌟
This is the recommended way to host DocuMind for free.

1.  Log in to [Hugging Face](https://huggingface.co/) and click **New Space**.
2.  Select **Docker** as the SDK and choose the **Blank** template.
3.  Once the Space is created, upload your files or connect your GitHub.
4.  **Important**: Go to **Settings** -> **Variables and Secrets** and add your `GROQ_API_KEY`.

### Option 2: Render
1.  Create a **New Web Service** and connect your repo.
2.  **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
3.  **Environment Variables**:
    *   `PYTHON_VERSION`: `3.11.9`
    *   `GROQ_API_KEY`: (Your Key)

*Note: On both free tiers, documents are deleted when the server restarts.*

---

---

## 💻 Local Setup

1.  **Clone & Install**:
    ```bash
    git clone https://github.com/adarsh-code169/DocuMind.git
    cd DocuMind
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    pip install -r requirements.txt
    ```

2.  **Env Config**:
    Create a `.env` file and add:
    ```
    GROQ_API_KEY=your_key_here
    ```

3.  **Run**:
    ```bash
    uvicorn backend.main:app --reload
    ```
    Open **`http://localhost:8000`** to see your app!

---

## 📁 Project Structure

```
├── backend/
│   ├── main.py            # FastAPI Entry Point
│   ├── models.py          # Pydantic Schemas
│   ├── chroma_store.py    # ChromaDB Wrapper
│   ├── pipeline/          # RAG Pipelines (Ingest/Retrieve)
│   └── static/            # React Code (index.html, assets)
├── app.py                 # Streamlit Backup Version
├── requirements.txt       # Dependencies
└── runtime.txt            # Python Version Meta
```

---

