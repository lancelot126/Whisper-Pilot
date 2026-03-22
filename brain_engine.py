import chromadb
from chromadb.utils import embedding_functions

# Connect to the existing database
client = chromadb.PersistentClient(path="./whisper_memory")

# Use the same embedding function as the one used to build the database
model_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Access the collection
collection = client.get_collection(name="whisper_docs", embedding_function=model_ef)

def search_memory(text):
    try: 
        # Turns text into a vector and finds matching text
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