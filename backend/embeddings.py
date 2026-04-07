import logging
from sentence_transformers import SentenceTransformer
from typing import List

logger = logging.getLogger(__name__)

# Use the MiniLM model; it provides 384-dimensional vectors and performs well for retrieval tasks
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class EmbeddingModel:
    """Utility class for generating text embeddings using SentenceTransformers."""

    def __init__(self, model_name: str = MODEL_NAME):
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

    def generate(self, text: str) -> List[float]:
        """Calculate the embedding for a single text string."""
        if not text or not text.strip():
            return []
        return self.model.encode(text).tolist()

    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """Calculate embeddings for an array of text strings efficiently."""
        valid = [t for t in texts if t and t.strip()]
        if not valid:
            return []
        logger.info(f"Embedding {len(valid)} chunks")
        return self.model.encode(valid).tolist()


# Initialize a shared instance of the model to avoid redundant loading overhead
embedding_model = EmbeddingModel()
