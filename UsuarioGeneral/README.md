# Interfaz de Usuario – BOX IA (Chat y Carga de Documentos)

Estas interfaces permiten interactuar visualmente con el modelo de IA que se ejecuta localmente (por ejemplo, a través de un servidor Uvicorn con FastAPI). Son independientes del backend y se conectan por red local (localhost) mediante llamadas HTTP.

---

## Requisitos Previos

- Python 3.10 o superior
- Tener un servidor local (API con FastAPI + Uvicorn) corriendo en el equipo principal (por ejemplo: http://127.0.0.1:8000)

---

## 1. Crear y Activar el Entorno Virtual

### En Windows:
```bash
python -m venv boxia-interface-env
boxia-interface-env\Scripts\activate
```

### En Ubuntu/Linux:
```bash
python3 -m venv boxia-interface-env
source boxia-interface-env/bin/activate
```

---

## 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

---

## 3. Ejecutar la Interfaz

Para la interfaz de chat:
```bash
python3 interfaz_chat.py
```

Para la interfaz de carga de documentos:
```bash
python3 interfaz_documentos.py
```

---

## Notas Importantes

- Asegúrate de que el backend de la API esté ejecutándose antes de abrir la interfaz.
- El archivo API debe estar corriendo con:
```bash
uvicorn api:app --reload
```
- Puedes modificar la IP si usas otro equipo en red local (por ejemplo, 192.168.1.10:8000).
