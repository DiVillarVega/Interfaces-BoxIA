#manage_reports.py
import sys, os, requests
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QAbstractItemView
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

API_BASE = "http://localhost:8000"

class ReportsUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Preguntas Reportadas")
        self.resize(700, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("📝 Preguntas Reportadas")
        title.setFont(QFont("Arial", 16))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tabla
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Pregunta", "Respuesta", "Fecha", "Acción"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Botones
        btn_layout = QHBoxLayout()
        btn_load = QPushButton("Cargar Lista")
        btn_load.clicked.connect(self.load_reports)
        btn_layout.addWidget(btn_load)


        btn_export = QPushButton("Exportar Excel")
        btn_export.clicked.connect(self.export_excel)
        btn_layout.addWidget(btn_export)

        btn_upload = QPushButton("Subir Respuestas Excel")
        btn_upload.clicked.connect(self.upload_excel)
        btn_layout.addWidget(btn_upload)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_reports(self):
        try:
            r = requests.get(f"{API_BASE}/preguntas-reportadas")
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar: {e}")
            return

        if not data:
            QMessageBox.information(self, "Sin datos", "No hay preguntas reportadas.")
            self.table.setRowCount(0)
            return

        self.table.setRowCount(len(data))
        for i, row in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(row["pregunta"]))
            self.table.setItem(i, 2, QTableWidgetItem(row["respuesta"]))
            dt = datetime.fromisoformat(row["fecha"])
            self.table.setItem(i, 3, QTableWidgetItem(dt.strftime("%Y-%m-%d %H:%M:%S")))
            btn_check = QPushButton("✔️")
            btn_check.setToolTip("Marcar pregunta como revisada")
            btn_check.clicked.connect(lambda _, report_id=row["id"]: self.mark_as_checked(report_id))
            self.table.setCellWidget(i, 4, btn_check)



    def export_excel(self):
        # Verificar si hay filas en la tabla antes de exportar
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Sin datos", "No hay preguntas reportadas.")
            return

        try:
            r = requests.get(f"{API_BASE}/exportar-preguntas", stream=True)
            r.raise_for_status()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar: {e}")
            return

        # Guardar archivo
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Excel", "preguntas_reportadas.xlsx", "Excel Files (*.xlsx)")
        if not path:
            return
        with open(path, "wb") as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)
        QMessageBox.information(self, "Exportado", f"Guardado en:\n{path}")

        
    def upload_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecciona archivo Excel", "", "Excel Files (*.xlsx *.xls)")
        if not path:
            return
        
        try:
            with open(path, "rb") as f:
                files = {"file": (os.path.basename(path), f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
                r = requests.post(f"{API_BASE}/subir-respuestas-excel", files=files)
                r.raise_for_status()
            QMessageBox.information(self, "Éxito", "Archivo subido y procesado correctamente.")
            self.load_reports()  # refrescar tabla tras actualizar
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo subir el archivo:\n{e}")

    def mark_as_checked(self, report_id):
        try:
            r = requests.post(f"{API_BASE}/marcar-revisado", json={"id": report_id})
            r.raise_for_status()
            QMessageBox.information(self, "Actualizado", f"Pregunta con el ID {report_id} marcada como revisada.")
            self.load_reports()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar:\n{e}")




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReportsUI()
    window.show()
    sys.exit(app.exec())
