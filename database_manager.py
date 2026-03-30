import os
import chromadb
from chromadb.utils import embedding_functions

DB_PATH = "./whisper_memory"
COLLECTION_NAME = "whisper_docs"
EMBED_MODEL = "all-MiniLM-L6-v2"

def get_collection():

    # initialize database
    client = chromadb.PersistentClient(path=DB_PATH)

    # Set Translator to turn my audio in vector form
    model_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

    # Create collection
    collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=model_ef)

    return collection

def ingest_folder(folder_path):
    # Reads .txt files in a folder and adds them to vector database
    collection = get_collection()

    if not os.path.exists(folder_path):
        print(f" Error: Folder '{folder_path}' NOT found.")
        return

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                collection.upsert(
                    documents=[content],
                    ids=[filename],
                    metadatas=[{"source": filename}]
                )
                print(f"Ingested: {filename}")

def ingest_new_file(file_path):
    # Adds a single file to the existing ChromaDB collection
    collection = get_collection()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Access your existing collection
            collection.add(
                documents=[content],
                ids=[os.path.basename(file_path)]
            )
            print(f"{os.path.basename(file_path)} indexed successfully.")
            return True
    except Exception as e:
        print(f"Ingestion Error: {e}")
        return False
    
if __name__ == "__main__":
    kb_folder = "knowledge_base"
    if not os.path.exists(kb_folder):
        os.makedir(kb_folder)
        print(f"Created '{kb_folder}' folder. Add your .txt files there.")
    
    ingest_folder(kb_folder)
    print("Ingestion complete. Your pilot now has more knowledge")
    