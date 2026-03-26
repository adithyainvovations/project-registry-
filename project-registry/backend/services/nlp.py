import json
import logging

# Set up simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("NLP Service initialized. PyTorch & Model will be loaded lazily on first request.")

# Lazy initialization to prevent Uvicorn port binding timeout and swap-death on free tier.
model_instance = None
model_util = None

def get_model():
    global model_instance, model_util
    if model_instance is None:
        logger.info("Importing heavy PyTorch & SentenceTransformers libraries into memory...")
        from sentence_transformers import SentenceTransformer, util
        model_util = util
        logger.info("Downloading/Loading the model weights 'all-MiniLM-L6-v2' (approx 80MB)...")
        model_instance = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("Model loaded successfully.")
    return model_instance, model_util

def get_embedding(text: str) -> list[float]:
    """
    Generates an embedding for the given text.
    Returns a list of floats.
    """
    m, _ = get_model()
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
    _, u = get_model()
    similarity = u.cos_sim(emb1, emb2)
    return similarity.item() # Extract scalar from tensor
