import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QThread, QPoint, pyqtSignal
from brain_engine import search_memory, get_chat_response
from deepgram import DeepgramClient, LiveTranscriptionEvents, LiveOptions, Microphone
from dotenv import load_dotenv
from collections import deque
import os
from database_manager import ingest_new_file
load_dotenv()

# Deepgram and microphone run in the background
class TranscriptionWorker(QThread):
    # This signal acts as a pipe to send data to the UI
    # Sends user's transcript and AI's memory match
    data_received = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.context_buffer = deque(maxlen=5)

    def run(self):
        def on_message(self_dg, result, **kwargs):
            try:
                if not result.channel.alternatives:
                    return

                sentence = result.channel.alternatives[0].transcript

                if result.is_final and sentence.strip():
                    self.context_buffer.append(sentence)

                    # Combine the last 5 sentences into the context buffer
                    full_context = " ".join(self.context_buffer)

                    # Search the database
                    match, distance = search_memory(sentence)

                    if match and distance < 0.7:
                        display_match = get_chat_response(full_context, match)
                    else:
                        display_match = "Listening"

                    self.data_received.emit(sentence, display_match)

            except Exception as e:
                print(f"Callback Error: {e}")

        deepgram = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))
        dg_connection = deepgram.listen.websocket.v("1")
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

        options = LiveOptions(
            model="nova-2",
            language="en-US",
            smart_format=True,
            encoding="linear16",
            channels=1,
            sample_rate=16000
        )
        dg_connection.start(options)

        self.micro = Microphone(dg_connection.send)
        self.micro.start()

class WhisperPilotUI(QWidget):
    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(0.85)

        # | ***** UI Layout ***** |
        self.layout = QVBoxLayout()
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border: 2px solid #333;
                border-radius: 10px;
                color: white;
            }
        """)

        # Suggestion Area
        self.suggestion_label = QLabel("WhisperPilot Ready")
        self.suggestion_label.setWordWrap(True)
        self.suggestion_label.setStyleSheet("""
            font-size: 16px;
            color: #4ade80;
            padding: 10px;
            border: none;
        """)

        # Transcript Area
        self.transcript_label = QLabel("Waiting for speech...")
        self.transcript_label.setWordWrap(True)
        self.transcript_label.setStyleSheet("""
            font-size: 12px;
            color: #9ca3af;
            padding: 10px;
            border-top: 1px solid #333;
        """)

        self.layout.addWidget(self.suggestion_label)
        self.layout.addWidget(self.transcript_label)
        self.setLayout(self.layout)

        # Draggable Variables
        self.oldPos = self.pos()

        # Connection
        self.worker = TranscriptionWorker()
        # Connect the pipe to the UI's update function
        self.worker.data_received.connect(self.update_display)
        self.worker.start()

    def update_display(self, transcript, suggestion):
        self.transcript_label.setText(f"{transcript}")
        self.suggestion_label.setText(suggestion)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()

            if file_path.endswith(".txt"):
                import shutil
                dest_dir = "knowledge_base"
                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, os.path.basename(file_path))
                shutil.copy(file_path, dest_path)

                # Trigger ingestion of the new file
                success = ingest_new_file(dest_path)

                if success:
                    self.suggestion_label.setText(f"🧠 Learned: {os.path.basename(file_path)}")
                    self.suggestion_label.setStyleSheet("color: #4ade80; font-size: 16px;") # Turn green for success
                else:
                    self.suggestion_label.setText("⚠️ Failed to index file.")
                    self.suggestion_label.setStyleSheet("color: #f87171; font-size: 16px;") # Turn red for error
                    
    def dragEnterEvent(self, event):
            # This tells Windows "Yes, I am allowed to receive these files"
            if event.mimeData().hasUrls():
                event.accept()
            else:
                event.ignore()
                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhisperPilotUI()
    window.resize(350, 200)
    window.show()
    sys.exit(app.exec())
