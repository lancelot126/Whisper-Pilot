try:
    import chromadb
    from chromadb.utils import embedding_functions
except Exception as e:
    chromadb = None
    embedding_functions = None
    print(f"Chroma import unavailable, using fallback memory mode: {e}")

collection = None
_fallback_docs = [
    "WhisperPilot is a real-time AI assistant using Deepgram for speech and ChromaDB for memory.",
    "The system uses Deepgram SDK with a WebSocket connection for low latency.",
    "The microphone settings are configured for 16kHz, mono, linear16 encoding.",
]

if chromadb is not None:
    try:
        client = chromadb.PersistentClient(path="./whisper_memory")
        model_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        collection = client.get_collection(name="whisper_docs", embedding_function=model_ef)
    except Exception as e:
        print(f"Chroma initialization failed, using fallback memory mode: {e}")
        collection = None

def search_memory(text):
    if collection is not None:
        try:
            results = collection.query(
                query_texts=[text],
                n_results=1
            )
            if not results["documents"] or not results["documents"][0]:
                return None, 1.0

            match = results["documents"][0][0]
            distance = results["distances"][0][0]
            return match, distance
        except Exception as e:
            print(f"Search Error: {e}")
            return None, 1.0

    # Fallback mode if Chroma/Torch native DLLs are unavailable.
    text_tokens = set(text.lower().split())
    best_doc = None
    best_overlap = 0
    for doc in _fallback_docs:
        overlap = len(text_tokens.intersection(set(doc.lower().split())))
        if overlap > best_overlap:
            best_doc = doc
            best_overlap = overlap

    if best_doc and best_overlap > 0:
        distance = max(0.05, 1.0 - min(best_overlap / 8.0, 0.95))
        return best_doc, distance
    return None, 1.0