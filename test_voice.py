import asyncio
import os
from dotenv import load_dotenv
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions, Microphone

load_dotenv()

async def main():
    try:
        client = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))
        dg_connection = client.listen.websocket.v("1")

        def on_message(self, result, **kwargs):
            # Safe extraction
            transcript = result.channel.alternatives[0].transcript
            if transcript:
                print(f"🎤 Heard: {transcript}")

        def on_metadata(self, metadata, **kwargs):
            print(f"📡 Connection confirmed: {metadata.request_id}")

        def on_error(self, error, **kwargs):
            print(f"❌ SDK Error: {error}")

        # Bind all handlers
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            encoding="linear16", # Common for PyAudio
            channels=1,
            sample_rate=16000
        )
        
        print("🚀 System Online. START SPEAKING...")
        dg_connection.start(options)

        # Start the mic
        micro = Microphone(dg_connection.send)
        micro.start()

        while True:
            await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Main Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())