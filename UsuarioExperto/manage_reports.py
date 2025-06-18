import sys, os, requests
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QAbstractItemView, QComboBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

API_BASE = "http://localhost:8000"

class ReportsUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Preguntas Reportadas")
        self.resize(800, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("📝 Preguntas Reportadas")
        title.setFont(QFont("Arial", 16))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Reportada", "Revisada", "Eliminada"])
        self.status_filter.currentIndexChanged.connect(self.load_reports)
        layout.addWidget(self.status_filter)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Pregunta", "Respuesta", "Fecha", "Acción"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

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
        estado = self.status_filter.currentText().lower()
        params = {} if estado == "todas" else {"estado": estado}

        try:
            r = requests.get(f"{API_BASE}/preguntas-reportadas", params=params)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar: {e}")
            return

        if not data:
            self.table.setRowCount(0)
            QMessageBox.information(self, "Sin datos", "No hay preguntas reportadas.")
            return

        mostrar_experto = estado in {"revisada", "eliminada"}
        columnas = ["ID", "Pregunta", "Respuesta", "Fecha"]
        if mostrar_experto:
            columnas.append("Respuesta Experto")
        columnas.append("Acción")

        self.table.setColumnCount(len(columnas))
        self.table.setHorizontalHeaderLabels(columnas)
        self.table.clearContents()  # <-- LIMPIA BIEN TODO
        self.table.setRowCount(len(data))

        for i, row in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(str(row["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(row["pregunta"]))
            self.table.setItem(i, 2, QTableWidgetItem(row["respuesta"]))
            dt = datetime.fromisoformat(row["fecha"])
            self.table.setItem(i, 3, QTableWidgetItem(dt.strftime("%Y-%m-%d %H:%M:%S")))

            col_offset = 4
            if mostrar_experto:
                self.table.setItem(i, col_offset, QTableWidgetItem(row.get("respuesta_experto", "")))
                col_offset += 1

            # Botones de acción
            btns_layout = QHBoxLayout()
            btns_widget = QWidget()

            if estado == "reportada":
                btn = QPushButton("✔️")
                btn.setToolTip("Marcar pregunta como revisada")
                btn.clicked.connect(lambda _, rid=row["id"]: self.mark_as_checked(rid))
                btns_layout.addWidget(btn)

            elif estado == "revisada":
                btn1 = QPushButton("🗑️")
                btn1.setToolTip("Eliminar respuesta de ChromaDB")
                btn1.clicked.connect(lambda _, rid=row["id"]: self.delete_from_chroma(rid))
                btns_layout.addWidget(btn1)

                btn2 = QPushButton("🔄")
                btn2.setToolTip("Reactivar como reportada")
                btn2.clicked.connect(lambda _, rid=row["id"]: self.reactivate_report(rid))
                btns_layout.addWidget(btn2)

            elif estado == "eliminada":
                btn = QPushButton("🔄")
                btn.setToolTip("Reactivar como reportada")
                btn.clicked.connect(lambda _, rid=row["id"]: self.reactivate_report(rid))
                btns_layout.addWidget(btn)

            btns_layout.setContentsMargins(0, 0, 0, 0)
            btns_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            btns_widget.setLayout(btns_layout)
            self.table.setCellWidget(i, col_offset, btns_widget)


    def export_excel(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Sin datos", "No hay preguntas reportadas.")
            return

        estado = self.status_filter.currentText().lower()

        try:
            r = requests.get(f"{API_BASE}/exportar-preguntas", params={"estado": estado}, stream=True)
            r.raise_for_status()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo exportar: {e}")
            return

        sugerido = f"preguntas_{estado}.xlsx"
        path, _ = QFileDialog.getSaveFileName(self, "Guardar Excel", sugerido, "Excel Files (*.xlsx)")
        if not path:
            return

        try:
            with open(path, "wb") as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            QMessageBox.information(self, "Exportado", f"Guardado en:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo:\n{e}")

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
            self.load_reports()
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

    def delete_from_postgres(self, report_id):
        try:
            r = requests.post(f"{API_BASE}/eliminar-pregunta", json={"id": report_id})
            r.raise_for_status()
            QMessageBox.information(self, "Eliminado", f"Pregunta con el ID {report_id} eliminada de PostgreSQL.")
            self.load_reports()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{e}")

    def delete_from_chroma(self, report_id):
        try:
            r = requests.post(f"{API_BASE}/eliminar-de-chroma", json={"id": report_id})
            r.raise_for_status()
            QMessageBox.information(self, "Chroma", f"Respuesta eliminada de Chroma para el ID {report_id}.")
            self.load_reports()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar de Chroma:\n{e}")

    def reactivate_report(self, report_id):
        try:
            r = requests.post(f"{API_BASE}/reactivar-pregunta", json={"id": report_id})
            r.raise_for_status()
            QMessageBox.information(self, "Reactivado", f"Pregunta con el ID {report_id} reactivada como reportada.")
            self.load_reports()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo reactivar:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReportsUI()
    window.show()
    sys.exit(app.exec())
