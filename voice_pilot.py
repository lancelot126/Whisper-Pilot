import os
from dotenv import load_dotenv
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions
)
import chromadb
from chromadb.utils import embedding_functions

load_dotenv()

# Set up vector database
client = chromadb.PersistentClient(path="./whisper_memory")
model_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = get_or_create_collection(name="whisper_docs", embedding_functions=model_ef)

def search_memory(text):
    # Turns text into a vector and finds matching text
    results = collection.query(
        query_texts=[text],
        n_results=1
    )

    match = results["documents"][0][0]
    distance = results["distances"][0][0]

    if distance < 0.7:
        return match, distance
    return None, distance

def main():
    try:
        deepgram = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))
        dg_connection = deepgram.listen.websocket.v("1")

        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence > 0) and result.is_final:
                print(f"\n YOU SAID: {sentence}")

                # Search the database
                match, distance = search_memory(sentence)

                if match:
                    print(f"WHISPERPILOT REMEMBERS: {match} (DISTANCE: {distance:.2f})")
                else:
                    print(f"I heard that, but I don't have a specific memory for it.")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000
        )

        print("WHISPERPILOT IS LIVE. SPEAK NOW...")

        dg_connection.start(options)

        micro = Microphone(dg_connection.send)
        micro.start()

        while True:
            pass
            
    except Exception as e:
        print(f"ErrorL {e}")

if __name__ == "__main__":
    main()


