"""#####################################################################
#! @ file:                   main.py
#  @ projekt:                microdot webserver
#  @ created on:             2026 04 06
#  @ author:                 R. Gräber
#  @ version:                0
#  @ history:                -
#  @ brief
#####################################################################"""

"""#####################################################################
# Informations
#####################################################################"""


"""#####################################################################
# Includes
#####################################################################"""
import json
from microdot import Microdot, send_file
import logging
import sys
"""#####################################################################
# Declarations
#####################################################################"""

"""#####################################################################
# Constant
#####################################################################"""

"""#####################################################################
# Global Variable
#####################################################################"""

"""#####################################################################
# local Variable
#####################################################################"""
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('webserver')
app = Microdot()
default_config = {}
"""#####################################################################
# Constant
#####################################################################"""
MAX_LOG_SIZE = 10240 
LOG_FILE = "log/app.log"
date_for_wifi = [
    {"id":"1", "ssid":"WifiZei", "pass":"IstGeheim", "comment":"Home", "mode":"AP"},
    {"id":"2", "ssid":"WifiDrei", "pass":"AuchGeheim", "comment":"Garten", "mode":"STA"}
]

"""#####################################################################
# Local Funtions
#####################################################################"""

"""#####################################################################
#  @ brief       Hauptroute für die HTML-Datei
#####################################################################"""
@app.route('/')
async def index(request):
    return send_file('www/index.html')

"""#####################################################################
#  @ brief       Favicon senden
#####################################################################"""
@app.route('/favicon.ico')
async def favicon(request):
    return send_file('www/favicon.ico')

"""#####################################################################
#  @ brief       Request-Logging (optional, loggt jede Anfrage)
#####################################################################"""
@app.before_request
async def log_request(request):
    logger.info(f"{request.method} {request.path}")

"""#####################################################################
#  @ brief       Daten ans Frontend senden
#####################################################################"""
@app.route('/api/wifidata', methods=['GET'])
async def get_data(request):
    # Beispiel-Datenquelle im Hauptprogramm
     #sensor_daten = {"temperatur": 22.5, "feuchtigkeit": 45}
    logger.info("Daten vom Frontend angefragt")
    # Wir senden das Dictionary als JSON zurück
    return date_for_wifi, 200, {'Content-Type': 'application/json'}

"""#####################################################################
#  @ brief       Daten vom Frontend EMPFANGEN
#####################################################################"""
@app.route('/api/settings', methods=['POST'])
async def post_data(request):
    # Die Daten vom Frontend liegen in request.json
    empfangene_daten = request.json
    logger.info("Daten vom Frontend empfangen: {}".format(empfangene_daten))
    
    # Hier könntest du z.B. eine LED schalten: 
    # if empfangene_daten.get('led') == 'on': led.on()
    
    return {'status': 'erfolgreich gespeichert'}, 200

"""#####################################################################
#  @ brief       Route für statische Dateien (CSS, JS)
#####################################################################"""
@app.route('/<path:path>')
async def static(request, path):
    #return send_file('www/' + path)
    full_path = 'www/' + path
    try:
        return send_file(full_path)
    except Exception as e:
        logger.error(f"Fehler beim Laden von {full_path}: {e}")
        return 'Datei nicht gefunden', 404

"""#####################################################################
#! @fn           read_configuration()
#  @ brief       load config files
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""
def read_configuration():
    # load default konfiguration
    try:
        with open('config/default_config.json','r') as default_config_file:
            config = json.load(default_config_file)
    except Exception as e:
        print("Error read default_config")
        return None

    # load override
    # check if override config exists and load it, then update default config with override values
    try:
        with open('config/override_config.json') as override_config_file:
            config = json.load(override_config_file)
            return config.update(override_config)
    except Exception as e:
        return config


"""#####################################################################
#! @fn           setup_logging()
#  @ brief       init logging and load config files
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""
def setup_logging():
    Load configuration
    global variable
    #global default_config

    ##################### Datei-Check (Rotation) #############################
    try:
        if os.stat(LOG_FILE)[6] > MAX_LOG_SIZE:
            os.remove(LOG_FILE)
    except OSError:
        pass
    ##################### Logger Instanz #####################################
    logger = logging.getLogger('webserver')
    logger.setLevel(logging.INFO)
    
    # Verhindert doppelte Handler, falls setup_logger mehrfach aufgerufen wird
    if logger.hasHandlers():
        logger.handlers.clear()
    #################### Format für Log-Ausgaben ###############################
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    #################### Konsole ##############################################
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Nur INFO und höher in der Konsole
    console_handler.setFormatter(formatter)

    #################### File ##############################################
    #file_handler = RotatingFileHandler(
    #    default_config["logging_params"]["log_name_and_path"], maxBytes=5*1024*1024, backupCount=3, encoding="utf-8"
    #)

    file_handler.setLevel(logging.DEBUG)  # Alles in die Datei
    file_handler.setFormatter(formatter)

    # Handler hinzufügen
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

"""#####################################################################
#! @fn           run_server
#  @ brief       Server Funktion für den Thread
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""
def run_server():
    logger.info("Webserver-Thread wird gestartet...")
    # debug=True kann in Threads manchmal Probleme mit Signal-Handlern machen,
    # daher im Thread oft besser auf False oder vorsichtig nutzen.
    # app.run(host='0.0.0.0', port=5000, debug=False)
    try:
        app.run(debug=True, port=5000)
    except Exception as e:
        log.critical(f"Server abgestürzt: {e}")
        
# --- WLAN Verbindung (Beispiel) ---
def connect_wlan():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        logger.info("Verbinde mit WLAN...")
        wlan.connect('ssid', 'pass')
        while not wlan.isconnected():
            time.sleep(1)
    logger.info("WLAN verbunden! IP: {}".format(wlan.ifconfig()[0]))


"""#####################################################################
#! @fn           int main(){
#  @ brief       start up function
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""
if __name__ == '__main__':
    configuration = read_configuration();
    log = init_app()
    log.info("Starting $__name__")
    # 1. WLAN starten
    connect_wlan()
    log.info("Starte Microdot Server auf Port 5000...")

    # 1. Thread erstellen
    _thread.start_new_thread(run_server, ())

    logger.info("Hauptprogramm läuft weiter...")

    # Hier kannst du nun parallel zum Webserver andere Dinge tun
    try:
        count = 0
        while True:
            count += 1
            # logger.info(f"Haupt-Loop läuft noch... Durchgang {count}")
            time.sleep(30)  # Simuliert Arbeit im Hauptprogramm
    except KeyboardInterrupt:
        logger.info("Programm wird beendet...")

    
