import io
import logging
from pypdf import PdfReader
from typing import List, Dict

# Use the existing embeddings model wrapper
from embeddings import embedding_model

logger = logging.getLogger(__name__)

# Configure chunking for the text data
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def extract_text_from_pdf(file_content: bytes, filename: str) -> List[Dict]:
    """Extract page text from a PDF file."""
    reader = PdfReader(io.BytesIO(file_content))
    pages = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text and text.strip():
            pages.append({
                "text": text.strip(),
                "page_number": i + 1,
                "filename": filename
            })
        else:
            logger.warning(f"Skipping page {i+1} of '{filename}' — no text found")

    logger.info(f"Extracted {len(pages)}/{len(reader.pages)} pages from '{filename}'")
    return pages


def chunk_text(pages: List[Dict], chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[Dict]:
    """Chunk text documents into overlapping segments."""
    chunks = []
    chunk_id = 0

    for page in pages:
        text = page["text"]
        start = 0

        # Use a sliding window to create overlapping text segments
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append({
                "id": f"{page['filename']}_p{page['page_number']}_{chunk_id}",
                "text": text[start:end],
                "metadata": {
                    "filename": page["filename"],
                    "page_number": page["page_number"],
                    "chunk_id": chunk_id
                }
            })
            chunk_id += 1
            start += (chunk_size - overlap)

    logger.info(f"Created {len(chunks)} chunks from {len(pages)} pages")
    return chunks

def process_and_store_document(file_content: bytes, filename: str, vector_store) -> int:
    """Execute the document ingestion pipeline: extraction, chunking, embedding, and storage."""
    pages = extract_text_from_pdf(file_content, filename)
    if not pages:
        return 0
    
    chunks = chunk_text(pages)
    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    embeddings = embedding_model.generate_batch(texts)

    success = vector_store.insert(embeddings, chunks)
    if not success:
        raise Exception("Failed to store chunks in Vector Store")

    return len(chunks)
