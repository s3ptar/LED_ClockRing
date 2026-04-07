import json
import logging
from microdot import Microdot, send_file
import os

# 1. Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('webserver')

# Maximale Größe der Log-Datei in Bytes (z.B. 10 KB)
MAX_LOG_SIZE = 10240 
LOG_FILE = "log/app.log"

def setup_logging():
    # 1. Datei-Check (Rotation)
    try:
        if os.stat(LOG_FILE)[6] > MAX_LOG_SIZE:
            os.remove(LOG_FILE)
    except OSError:
        pass

    # 2. Logger Instanz
    logger = logging.getLogger('webserver')
    logger.setLevel(logging.INFO)

    # 3. Formatter definieren (Das ist der entscheidende Teil!)
    # MicroPython logging erwartet ein Objekt mit einer format() Methode
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

    # 4. Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter) # Formatter zuweisen
    logger.addHandler(console_handler)

    # 5. Custom File Handler
    class FileHandler(logging.Handler):
        def emit(self, record):
            # Wir nutzen den Formatter des Handlers
            log_entry = self.format(record) 
            try:
                with open(LOG_FILE, "a") as f:
                    f.write(log_entry + "\n")
            except Exception:
                pass

    file_handler = FileHandler()
    file_handler.setFormatter(formatter) # Formatter auch hier zuweisen
    logger.addHandler(file_handler)
    
    return logger

# 2. Konfiguration laden
def load_config():
    try:
        with open('config/config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error("Fehler beim Laden der config.json: %s", e)
        return None

config = load_config()
logger = setup_logging()
app = Microdot()

# 3. Routen definieren
@app.route('/')
async def index(request):
    logger.info("Anfrage auf Index-Seite erhalten")
    return send_file('index.html')

@app.route('/api/status')
async def status(request):
    logger.info("API Status-Abruf")
    return {'status': 'online', 'hardware': 'ESP32'}, 200

# 4. Server starten
#if config:
#    logger.info("Starte Webserver auf Port %s...", config['server_port'])
#    try:
#        app.run(port=config['server_port'])
#    except Exception as e:
#        logger.critical("Server-Fehler: %s", e)