Requeridos:
Instalar Python (en el PATCH)

python main.py

UBUNTU
-Para boorrar el ambiente virtual anterior:
rm -rf chat-env
-Para crear el ambiente virtual:
python3 -m venv chat-env
-Para usar el ambiente virtual: 
source chat-env/bin/activate
-Para desactivar el ambiente virtual:
deactivate
-Instalar dependencias:
pip install -r requirements.txt
-Arrancar la interfaz:
python3 interfaz_chat.py
-Generar portable del chat:
pyinstaller --onefile --windowed --name BoxIA-Chat interfaz_chat.py


