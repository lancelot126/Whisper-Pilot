import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject

class OverlayWindow(QWidget):
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
        self.suggestion_label = QLabel("Waiting for speech...")
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
            fonrt-size: 12px;
            color: $9ca3af;
            padding: 10px;
            border-top: 1px solid #333;
        """)

        self.layout.addWidget(self.suggestion_label)
        self.layout.addWidget(self.transcript_label)
        self.setLayout(self.layout)

        # Draggable Variables
        self.oldPos = self.pos()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OverlayWindow()
    window.resize(350, 200)
    window.show()
    sys.exit(app.exec())
