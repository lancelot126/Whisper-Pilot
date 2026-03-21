import chromadb
from chromadb.utils import embedding_functions

# Connect to the existing database
client = chromadb.PersistentClient(path="./whisper_memory")

# Use the same embedding function as the one used to build the database
model_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Access the collection
collection = client.get_collection(name="whisper_docs", embedding_function=model_ef)

def search_memory(question):
    # The Query
    results = collection.query(
        query_texts=[question],
        n_results=1
    )

    # Extract results
    document = results["documents"][0][0]
    distance = results["distances"][0][0]

    print(f"\n You asked: {question}")
    print(f"Brain Found: {document}")
    print(f"Distance: {distance:.4f}")

if __name__ == "__main__":
    search_memory("How is the audio being recorded?")