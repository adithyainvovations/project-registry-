from sentence_transformers import SentenceTransformer
print("Downloading and caching all-MiniLM-L6-v2...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully!")
