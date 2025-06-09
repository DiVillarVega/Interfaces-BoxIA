import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class UploadUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Carga de Documentos - BOX IA")
        self.setGeometry(100, 100, 500, 300)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.selected_file = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("📂 Cargar documentos a la IA")
        title.setFont(QFont("Arial", 16))
        title.setStyleSheet("color: #00BFFF;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.status_label = QLabel("Ningún archivo seleccionado.")
        layout.addWidget(self.status_label)

        btn_select = QPushButton("Seleccionar archivo")
        btn_select.setStyleSheet("background-color: white; color: black; padding: 10px;")
        btn_select.clicked.connect(self.select_file)
        layout.addWidget(btn_select)

        btn_upload = QPushButton("Subir a la IA")
        btn_upload.setStyleSheet("background-color: #00BFFF; color: white; padding: 14px;")
        btn_upload.clicked.connect(self.upload_file)
        layout.addWidget(btn_upload)

        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo", "", "Archivos PDF/TXT (*.pdf *.txt)")
        if file_path:
            self.selected_file = file_path
            self.status_label.setText(f"📁 Archivo seleccionado: {file_path}")
        else:
            self.status_label.setText("❌ No se seleccionó ningún archivo.")

    def upload_file(self):
        if not self.selected_file:
            self.status_label.setText("❗ Primero selecciona un archivo.")
            return

        try:
            ext = self.selected_file.lower()
            endpoint = "http://localhost:8000/cargar-documento-pdf" if ext.endswith(".pdf") else "http://localhost:8000/cargar-documento-txt"
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
