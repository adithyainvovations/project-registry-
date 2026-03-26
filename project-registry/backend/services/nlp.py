from sentence_transformers import SentenceTransformer, util
import json
import logging

# Set up simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("NLP Service initialized. Model will be loaded lazily on first request.")

# Lazy initialization to prevent Uvicorn port binding timeout
model = None

def get_model():
    global model
    if model is None:
        logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2' (this may take a minute)...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully.")
    return model

def get_embedding(text: str) -> list[float]:
    """
    Generates an embedding for the given text.
    Returns a list of floats.
    """
    m = get_model()
    embedding = m.encode(text)
    return embedding.tolist()

def serialize_embedding(embedding: list[float]) -> str:
    """
    Serializes a list of floats to a JSON string for DB storage.
    """
    return json.dumps(embedding)

def deserialize_embedding(embedding_str: str) -> list[float]:
    """
    Deserializes a JSON string to a list of floats.
    """
    return json.loads(embedding_str)

def compute_similarity(emb1: list[float], emb2: list[float]) -> float:
    """
    Computes cosine similarity between two embeddings.
    Returns a float between -1 and 1.
    """
    similarity = util.cos_sim(emb1, emb2)
    return similarity.item() # Extract scalar from tensor
