import os
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from models import ChatRequest, ChatResponse
from chroma_store import ChromaVectorStore
from pipeline.ingestion import process_and_store_document
from pipeline.retrieval import RetrievalPipeline

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit

vector_store = None
retrieval_pipeline = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize ChromaDB and RAG pipeline on application startup."""
    global vector_store, retrieval_pipeline

    groq_key = os.getenv("GROQ_API_KEY")

    if not groq_key:
        logger.warning("GROQ_API_KEY not set — chat won't work")

    # Use a persistent ChromaDB store
    persist_dir = os.path.join(os.path.dirname(__file__), "chroma_db")
    vector_store = ChromaVectorStore(persist_directory=persist_dir)
    retrieval_pipeline = RetrievalPipeline(api_key=groq_key, vector_store=vector_store)
    
    logger.info("App ready")
    yield


app = FastAPI(title="Chroma RAG API", version="1.0.0", lifespan=lifespan)

# Configure CORS to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF, extract and chunk text, generate embeddings, and store in ChromaDB."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files supported")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    logger.info(f"Upload: '{file.filename}' ({len(content) / 1024:.1f} KB)")

    try:
        num_chunks = process_and_store_document(content, file.filename, vector_store)
        return {"message": f"Processed {num_chunks} chunks from {file.filename}", "chunks": num_chunks}
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail="Failed to process and store document")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process user query, retrieve relevant documents, and generate a cited response."""
    try:
        response = retrieval_pipeline.run(request.message, top_k=5)
        return response
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=400, detail="Couldn't process your query. Check that GROQ_API_KEY is valid and documents are uploaded.")


@app.get("/health")
def health():
    return {"status": "ok", "vector_store": "chromadb"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
