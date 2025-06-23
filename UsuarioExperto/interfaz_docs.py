import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from manage_reports import ReportsUI  # Importa la ventana de gestión

class UploadUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Carga de Documentos - BOX IA")
        self.setGeometry(100, 100, 500, 300)
        self.selected_file = None
        self.init_ui()
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel#titleLabel {
                color: #00BFFF;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                padding: 10px;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton#uploadButton {
                background-color: #00BFFF;
                color: white;
                padding: 14px;
                font-size: 15px;
                border-radius: 12px;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("📂 Cargar documentos a la IA")
        title.setObjectName("titleLabel")
        title.setFont(QFont("Segoe UI", 16))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.status_label = QLabel("Ningún archivo seleccionado.")
        self.status_label.setFont(QFont("Segoe UI", 11))
        layout.addWidget(self.status_label)

        # Botón para abrir la ventana de gestión de reportes
        btn_manage = QPushButton("🛠️ Gestionar Reportes")
        btn_manage.clicked.connect(self.open_reports_window)
        layout.addWidget(btn_manage)

        # Botón de selección de archivo
        btn_select = QPushButton("🗂️ Seleccionar archivo")
        btn_select.clicked.connect(self.select_file)
        layout.addWidget(btn_select)

        # Botón de subida
        btn_upload = QPushButton("📤 Subir a la IA")
        btn_upload.setObjectName("uploadButton")
        btn_upload.clicked.connect(self.upload_file)
        layout.addWidget(btn_upload)

        self.setLayout(layout)

    def open_reports_window(self):
        self.reports_window = ReportsUI()
        self.reports_window.show()

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo",
            "",
            "Archivos PDF (*.pdf)"
        )
        if file_path:
            self.selected_file = file_path
            self.status_label.setText(f"📁 Archivo seleccionado: {file_path}")
        else:
            self.status_label.setText("❌ No se seleccionó ningún archivo.")

    def upload_file(self):
        if not self.selected_file:
            self.status_label.setText("❗ Primero selecciona un archivo.")
            return

        if not self.selected_file.lower().endswith(".pdf"):
            self.status_label.setText("❌ Solo se permiten archivos PDF.")
            return

        try:
            endpoint = "http://localhost:8000/cargar-documento-pdf"
            with open(self.selected_file, "rb") as f:
                files = {"archivo": f}
                r = requests.post(endpoint, files=files)

            if r.status_code == 200:
                self.status_label.setText("✅ Documento cargado correctamente.")
            else:
                self.status_label.setText("❌ Error al cargar el documento.")
        except Exception as e:
            self.status_label.setText(f"⚠️ Error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UploadUI()
    window.show()
    sys.exit(app.exec())
