import chromadb
from chromadb.utils import embedding_functions

# initialize database
client = chromadb.PersistentClient(path="./whisper_memory")

# Set Translator to turn my audio in vector form
model_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Create collection
collection = client.get_or_create_collection(name="whisper_docs", embedding_function=model_ef)

collection.add(
    documents=[
        "WhisperPilot is a real-time AI assisstant using Deepgram for speech and ChromaDB for memory.",
        "The system uses a v3.11.0 Deepgram SDK with a WebCoket connection for low latency.",
        "The microphone setting are configured for 16kHz, mono, linear16 encoding."
    ],
    ids=["doc1", "doc2", "doc3"]
)

print("WhisperPilot memory initialized.")