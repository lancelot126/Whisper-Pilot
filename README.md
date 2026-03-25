🎙️ Whisper-Pilot
A Real-Time AI Co-Pilot for Meetings and Technical Interviews.

Whisper-Pilot is a local desktop application that "listens" to your microphone, transcribes speech in real-time, and uses Retrieval-Augmented Generation (RAG) to provide instant talking points or factual corrections based on your private knowledge base.

✨ Key Features
Real-Time Transcription: Powered by Deepgram's WebSocket API for ultra-low latency.

Intelligent Memory: Uses ChromaDB (Vector Database) to store and search through your personal .txt notes.

Contextual Suggestions: Matches your live speech against your local "Knowledge Base" to whisper relevant facts.

Hybrid Brain Engine: Includes a robust fallback mode using keyword matching if AI hardware acceleration (Torch/CUDA) is unavailable.

Modern UI: Built with PyQt6 for a sleek, non-intrusive desktop experience.

🏗️ Architecture
The project is split into three main components:

pilot_ui.py: The "Face" — Handles the GUI and real-time audio streaming.

brain_engine.py: The "Logic" — Coordinates the search between the Vector DB and the fallback engine.

database_manager.py: The "Librarian" — Ingests your local documents into the AI's memory.

🚀 Getting Started
Prerequisites
Python 3.12 (Recommended for stability with AI libraries)

Deepgram API Key (Sign up at deepgram.com)

C++ Redistributable (Required for ChromaDB's Rust bindings)

Installation
Clone the repository:

Bash
git clone https://github.com/yourusername/Whisper-Pilot.git
cd Whisper-Pilot
Set up the Virtual Environment:

PowerShell
py -3.12 -m venv venv
.\venv\Scripts\activate
Install Dependencies:

PowerShell
python -m pip install -r requirements.txt
Configure Environment Variables:
Create a .env file in the root directory:

Code snippet
DEEPGRAM_API_KEY=your_actual_key_here
📖 Usage
Populate your Knowledge Base: Place any .txt files (meeting notes, technical docs, etc.) into the /knowledge_base folder.

Ingest Data:

PowerShell
python database_manager.py
Launch the Pilot:

PowerShell
python pilot_ui.py
🛠️ Tech Stack
Language: Python 3.12

Speech-to-Text: Deepgram SDK

Vector Database: ChromaDB

Embeddings: Sentence-Transformers (all-MiniLM-L6-v2)

GUI: PyQt6
