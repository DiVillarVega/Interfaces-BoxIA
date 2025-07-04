import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QScrollArea, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap

class ChatUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BOX IA - Chatbot")
        self.setGeometry(100, 100, 900, 600)
        self.ultima_pregunta = ""
        self.ultima_respuesta = ""
        self.init_ui()
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
            }
            QScrollBar:vertical {
                border: none;
                background: #2a2a2a;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #888;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #aaa;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar:horizontal {
                border: none;
                background: #2a2a2a;
                height: 10px;
                margin: 0px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background: #888;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #aaa;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Top bar
        top_bar = QHBoxLayout()
        logo = QLabel("BoxIA")
        logo.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        logo.setStyleSheet("color: #ffffff; padding: 5px;")

        clear_btn = QPushButton("Limpiar chat")
        clear_btn.setStyleSheet("background-color: white; color: black; padding: 6px 12px; border-radius: 8px;")
        clear_btn.clicked.connect(self.clear_chat)

        top_bar.addWidget(logo)
        top_bar.addStretch()
        top_bar.addWidget(clear_btn)
        layout.addLayout(top_bar)

        # Chat area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch()
        self.scroll_area.setWidget(self.chat_container)
        layout.addWidget(self.scroll_area)

        # Input
        input_layout = QHBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Escribe tu pregunta aquí...")
        self.input_box.setStyleSheet("""
            background-color: #2a2a2a;
            border: 2px solid white;
            border-radius: 15px;
            padding: 10px;
            color: white;
        """)
        self.input_box.setFixedHeight(60)
        self.input_box.textChanged.connect(self.ajustar_altura_input)
        self.input_box.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        send_btn = QPushButton("➤")
        send_btn.setFixedSize(40, 40)
        send_btn.setStyleSheet("background-color: white; color: black; border-radius: 20px;")
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_box)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)

    def ajustar_altura_input(self):
        doc_height = self.input_box.document().size().height()
        nueva_altura = max(60, min(120, int(doc_height + 20)))  # mínimo 60px, máximo 120px
        self.input_box.setFixedHeight(nueva_altura)

    def add_message(self, sender, text):
        message = QLabel()
        message.setWordWrap(True)
        message.setText(text)
        message.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        if sender == "user":
            message.setStyleSheet("background-color: #3a3a3a; padding: 10px; border-radius: 10px; margin: 10px;")
            message.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, message)
        else:
            message.setStyleSheet("background-color: transparent; padding: 10px; margin: 10px; color: white;")
            icon = QLabel("🤖")
            icon.setStyleSheet("font-size: 24px; margin-right: 6px;")
            row = QHBoxLayout()
            row.addWidget(icon)
            row.addWidget(message)
            row.addStretch()
            container = QWidget()
            container.setLayout(row)
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, container)

        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def send_message(self):
        user_text = self.input_box.toPlainText().strip()
        if not user_text:
            return

        self.add_message("user", user_text)
        self.input_box.clear()
        self.ultima_pregunta = user_text

        try:
            response = requests.post("http://localhost:8000/preguntar", json={"pregunta": user_text})
            response.raise_for_status()
            respuesta_ia = response.json().get("respuesta", "⚠️ Error en la respuesta de la IA.")
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Error de conexión", "❌ No hay conexión con el servidor.")
            return
        except requests.exceptions.HTTPError as e:
            QMessageBox.critical(self, "Error HTTP", f"⚠️ Error al procesar la solicitud:\n{e}")
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", f"⚠️ Ocurrió un error inesperado:\n{str(e)}")
            return

        self.ultima_respuesta = respuesta_ia
        self.add_bot_response_with_button(respuesta_ia)


    def add_bot_response_with_button(self, respuesta):
        # Oculta botones previos
        for i in reversed(range(self.chat_layout.count() - 1)):
            item = self.chat_layout.itemAt(i)
            widget = item.widget()
            if widget:
                for sub in widget.findChildren(QPushButton):
                    if sub.text().startswith("📩"):
                        sub.hide()

        respuesta_label = QLabel(respuesta)
        respuesta_label.setWordWrap(True)
        respuesta_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        respuesta_label.setStyleSheet("background-color: transparent; padding: 10px; margin: 10px; color: white;")

        icon = QLabel("💬")
        icon.setStyleSheet("font-size: 30px; margin-right: 6px;")

        reportar_btn = QPushButton("📩 Reportar respuesta")
        reportar_btn.setStyleSheet("background-color: #ff4d4d; color: white; padding: 4px; border-radius: 6px;")
        reportar_btn.clicked.connect(self.reportar_respuesta)

        col = QVBoxLayout()
        col.addWidget(respuesta_label)
        col.addWidget(reportar_btn, alignment=Qt.AlignmentFlag.AlignLeft)

        row = QHBoxLayout()
        row.addWidget(icon)
        row.addLayout(col)
        row.addStretch()

        container = QWidget()
        container.setLayout(row)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, container)

        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def reportar_respuesta(self):
        if not self.ultima_pregunta or not self.ultima_respuesta:
            return

        try:
            payload = {
                "pregunta": self.ultima_pregunta,
                "respuesta": self.ultima_respuesta
            }
            r = requests.post("http://localhost:8000/reportar-pregunta", json=payload)
            if r.status_code == 200:
                QMessageBox.information(self, "Reporte de pregunta", r.json().get("mensaje", "Reporte exitoso."))
            else:
                QMessageBox.critical(self, "Error", r.json().get("detail", "Error al reportar."))
        except Exception as e:
            QMessageBox.critical(self, "Error de conexión", f"⚠️ No se pudo conectar con el servidor")

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
