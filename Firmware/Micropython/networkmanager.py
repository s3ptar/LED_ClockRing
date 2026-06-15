"""#####################################################################
#! @ file:                   networkmanager.py
#  @ projekt:                LED_ClockRing
#  @ created on:             2026-06-01
#  @ author:                 R. Gräber
#  @ version:                0
#  @ history:                -
#  @ brief:                  Networkmanager für die LED_ClockRing, erstellt mit Hilfe von Gemini,
#                             einem KI-Tool von OpenAI, um die Entwicklung zu beschleunigen.
#####################################################################"""


"""#####################################################################
# Includes
#####################################################################"""
import logging
import time
import utilities
import network
import _thread
"""#####################################################################
# Informations
#####################################################################"""

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
log = logging.getLogger(__name__)
logger = log
"""#####################################################################
# Constant
#####################################################################"""

"""#####################################################################
# Local Funtions
#####################################################################"""

"""#####################################################################
#! @fn           connect_sta(ssid, password, timeout=15):   
#  @ brief       versucht, sich als Client (STA) mit einem WLAN zu verbinden.
#  @ param       ssid: Der Name des WLANs, mit dem verbunden werden soll
#  @ param       password: Das Passwort für den Access Point
#  @ param       timeout: Maximale Zeit (in Sekunden) für den Verbindungsversuch
#  @ exception   none
#  @ return      none
#####################################################################"""
def connect_sta(ssid, password, timeout=15):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    
    if sta.isconnected():
        sta.disconnect()
        
    logger.info(f"Verbinde mit STA: {ssid}")
    sta.connect(ssid, password)
    
    # Warten auf Verbindung mit Timeout
    start_time = time.time()
    while not sta.isconnected():
        if time.time() - start_time > timeout:
            logger.error(f"Timeout bei Verbindung mit {ssid}")
            sta.active(False)
            return False
        time.sleep(0.5)
        
    logger.info("Erfolgreich verbunden! IP: %s", sta.ifconfig()[0])
    return True

"""#####################################################################
#! @fn           start_ap(ssid, password):
#  @ brief       Aktiviert den Access Point (AP) Modus
#  @ param       ssid: Der Name des Access Points
#  @ param       password: Das Passwort für den Access Point
#  @ exception   none
#  @ return      none
#####################################################################"""
def start_ap(ssid, password):
    logger.info(f"Aktiviere Access Point: {ssid}...")
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    
    # Authmode 3 steht für WPA2-PSK Sicherheit
    ap.config(essid=ssid, password=password, authmode=3)
    
    logger.info("AP Modus aktiv. IP-Adresse: %s", ap.ifconfig()[0])

"""#####################################################################
#! @fn           start_networkmanager
#  @ brief       startet den Networkmanager, der die WLAN-Verbindung verwaltet und bei Bedarf in den AP-Modus wechselt.
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""
def start_networkmanager():
    config = utilities.load_config("WIFI")
    if not config:
        logger.error("Abbruch: Keine gültige Konfigurationsdatei gefunden.")
        return

    # Stell sicher, dass beide Interfaces im definierten Zustand starten
    network.WLAN(network.STA_IF).active(False)
    network.WLAN(network.AP_IF).active(False)

    # Bedingung 1: AP-Modus wird direkt erzwungen
    if config.get("force_ap", False):
        logger.info("AP-Modus via Konfiguration erzwungen.")
        start_ap(config["ap_mode"]["ssid"], config["ap_mode"]["password"])
        return

    # Bedingung 2: Versuche Default-STA
    if connect_sta(config["sta_default"]["ssid"], config["sta_default"]["password"]):
        return

    # Bedingung 3: Versuche Fallback-STA
    if connect_sta(config["sta_fallback"]["ssid"], config["sta_fallback"]["password"]):
        return

    # Bedingung 4: Wenn alles fehlschlägt -> AP-Modus
    logger.info("STA-Verbindungen fehlgeschlagen. Wechsle in AP-Modus...")
    start_ap(config["ap_mode"]["ssid"], config["ap_mode"]["password"])



"""#####################################################################
#! @fn           class NetworkManager
#  @ brief       Diese Klasse verwaltet die WLAN-Verbindung der LED_ClockRing. 
#                Sie versucht, sich mit einem definierten WLAN zu verbinden 
#                und wechselt bei Verbindungsproblemen automatisch
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""
class NetworkManager:
    def __init__(self):
        self.config = utilities.load_config("WIFI")
        
        self.sta = network.WLAN(network.STA_IF)
        self.ap = network.WLAN(network.AP_IF)
        
        self.lock = _thread.allocate_lock()
        self.is_monitoring = False
        
        # Status-Variablen
        self.current_status = 0
        self.current_mode = "DISCONNECTED"

    def _load_config(self):
        self.config = self.utilities.load_config("WIFI")


    def _connect_to_sta(self, credentials, timeout=15):
        ssid = self.config[credentials]["ssid"]
        pw = self.config[credentials]["password"]
        log.info(f"ssid: {ssid} and password: {pw}")
        
        if not ssid:
            log.warning("STA-Verbindung übersprungen: Keine SSID angegeben.")
            return False
            
        # log.info für normale, wichtige Systemereignisse
        log.info(f"Versuche Verbindung mit: {ssid}")
        self.sta.active(True)
        self.sta.disconnect()
        time.sleep(0.5)
        self.sta.connect(ssid, pw)
        
        for i in range(timeout):
            status = self.sta.status()
            if status == 3: 
                log.info(f"Erfolgreich verbunden! IP: {self.sta.ifconfig()[0]}")
                return True
            if status == -1:
                log.error(f"Verbindungsfehler: Falsches Passwort für {ssid}")
                break
                
            # log.debug für detaillierte Infos, die man im Alltag oft ausblenden will
            log.debug(f"Warte auf Verbindung... ({i+1}/{timeout}s)")
            time.sleep(1)
            
        return False

    def start_ap_mode(self):
        log.info("Schalte um in AP-Modus (Hotspot)...")
        self.sta.active(False)

        # Authmode 3 steht für WPA2-PSK Sicherheit
        
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(essid=self.config["credentials"]["ssid"], 
                       password=self.config["ap_mode"]["password"], 
                       authmode=3)
        
        log.info(f"AP Aktiv. SSID: {self.ap.config('essid')} | IP: {self.ap.ifconfig()[0]}")

    def manage_connection(self):
        with self.lock:
            status = self.sta.status()
            self.current_status = status
            
            if status == 3:
                self.current_mode = "STA"
                return True
                
            log.warning("Verbindung verloren oder inaktiv. Starte Verbindungs-Kette...")
            
            if self._connect_to_sta("sta_default"):
                if self.ap.active(): self.ap.active(False)
                self.current_mode = "STA"
                return True
                
            log.warning("Primäres WLAN fehlgeschlagen.")
            
            if self._connect_to_sta("sta_fallback"):
                if self.ap.active(): self.ap.active(False)
                self.current_mode = "STA"
                return True
                
            log.critical("Alle STA-Verbindungen fehlgeschlagen! Eskalation zu AP.")
            
            if not self.ap.active():
                self.start_ap_mode()
            
            self.current_mode = "AP"
            self.current_status = 0
            return False

    def _monitor_loop(self):
        log.info("Hintergrund-Thread für WLAN-Überwachung erfolgreich gestartet.")
        while self.is_monitoring:
            with self.lock:
                self.current_status = self.sta.status()
                if self.ap.active():
                    self.current_mode = "AP"
                elif self.sta.status() == 3:
                    self.current_mode = "STA"
                else:
                    self.current_mode = "DISCONNECTED"
            
            if self.current_mode == "AP":
                time.sleep(30)
                log.debug("Prüfe im Hintergrund, ob Router wieder erreichbar ist...")
                self.manage_connection()
            else:
                if self.current_status != 3:
                    log.warning("Verbindungsproblem im Thread erkannt!")
                    self.manage_connection()
                time.sleep(10)

    def start(self, use_thread=True):
        self.manage_connection()
        if use_thread and not self.is_monitoring:
            self.is_monitoring = True
            _thread.start_new_thread(self._monitor_loop, ())

"""#####################################################################
#! @fn           int main(){
#  @ brief       start up function
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""

if __name__ == "__main__":
    start_networkmanager()
