import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QScrollArea
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class ChatUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BOX IA - Chatbot")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.setGeometry(100, 100, 900, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Top bar
        top_bar = QHBoxLayout()
        logo = QLabel("🧠 BOX IA")
        logo.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        logo.setStyleSheet("color: #00BFFF;")

        clear_btn = QPushButton("Limpiar chat")
        clear_btn.setStyleSheet("background-color: white; color: black; padding: 6px 12px; border-radius: 8px;")
        clear_btn.clicked.connect(self.clear_chat)

        top_bar.addWidget(logo)
        top_bar.addStretch()
        top_bar.addWidget(clear_btn)
        layout.addLayout(top_bar)

        # Scrollable chat area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch()
        self.scroll_area.setWidget(self.chat_container)
        layout.addWidget(self.scroll_area)

        # Input area
        input_layout = QHBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.setFixedHeight(60)
        self.input_box.setPlaceholderText("Escribe tu pregunta aquí...")
        self.input_box.setStyleSheet("background-color: #2a2a2a; border: 2px solid white; border-radius: 15px; padding: 10px; color: white;")
        input_layout.addWidget(self.input_box)

        send_btn = QPushButton("➤")
        send_btn.setFixedSize(40, 40)
        send_btn.setStyleSheet("background-color: white; color: black; border-radius: 20px;")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)

    def add_message(self, sender, text):
        message = QLabel()
        message.setWordWrap(True)
        message.setText(text)
        message.setStyleSheet("padding: 10px; border-radius: 10px;")

        if sender == "user":
            message.setStyleSheet("background-color: #3a3a3a; padding: 10px; border-radius: 10px; margin: 10px;")
            message.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            message.setStyleSheet("background-color: transparent; padding: 10px; margin: 10px;")
            icon = QLabel("🤖")
            icon.setStyleSheet("font-size: 24px; margin-right: 6px;")
            row = QHBoxLayout()
            row.addWidget(icon)
            row.addWidget(message)
            row.addStretch()
            container = QWidget()
            container.setLayout(row)
            self.chat_layout.insertWidget(self.chat_layout.count()-1, container)
            return

        self.chat_layout.insertWidget(self.chat_layout.count()-1, message)

    def send_message(self):
        user_text = self.input_box.toPlainText().strip()
        if not user_text:
            return
        self.add_message("user", user_text)
        self.input_box.clear()

        try:
            response = requests.post("http://localhost:8000/preguntar", json={"pregunta": user_text})
            respuesta_ia = response.json().get("respuesta", "Error en la respuesta de la IA")
        except Exception as e:
            respuesta_ia = f"Error al conectarse con el servidor: {str(e)}"

        self.add_message("bot", respuesta_ia)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def clear_chat(self):
        for i in reversed(range(self.chat_layout.count() - 1)):
            widget = self.chat_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatUI()
    window.show()
    sys.exit(app.exec())
