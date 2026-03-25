import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_chat_response(user_query, retrieved_context):
    # Sends user's speech and matched memory context to Groq and returns the response
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI Co-Pilot. Use the provided context to asnwer the user's question concisely. If the context doesn't help, use your general knowledge, but prioritize the context."
                },
                {
                    "role": "user",
                    "content": f"Context: {retrieved_context}\n\nUser Question: {user_query}"
                }
            ],
            max_tokens=150
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"LLM Error: {e}"
    
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

