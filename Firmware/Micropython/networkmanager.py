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

        self.ap.active(False)
        self.sta.active(False)
        
        self.lock = _thread.allocate_lock()
        self.is_monitoring = False
        
        # Status-Variablen
        self.current_status = 0
        self.current_mode = "DISCONNECTED"

    """#####################################################################
    #! @fn           _load_config(self)
    #  @ brief       lade die konfiguration
    #  @ param       none
    #  @ exception   none
    #  @ return      none
    #####################################################################"""
    def _load_config(self):
        self.config = utilities.load_config("WIFI")

    """#####################################################################
    #! @fn           _load_config(self)
    #  @ brief       lade die konfiguration
    #  @ param       credentials: Schlüssel in der config.json für die WLAN-Zugangsdaten
    #  @ param       timeout: Zeit in Sekunden, die auf eine Verbindung gewartet
    #  @ exception   none
    #  @ return      none
    #####################################################################"""
    def _connect_to_sta(self, credentials, timeout=15):
        network.WLAN(network.AP_IF).active(False)
        self.sta  = network.WLAN(network.STA_IF)
        ssid = self.config[credentials]["ssid"]
        pw = self.config[credentials]["password"]
        log.info(f"ssid: {ssid} and password: {pw}")
        
        if not ssid:
            log.warning("STA-Verbindung übersprungen: Keine SSID angegeben.")
            return False
            
        # log.info für normale, wichtige Systemereignisse
        log.info(f"Versuche Verbindung mit: {ssid}")
        self.sta = network.WLAN(network.STA_IF)
        self.sta.active(True)
        self.sta.disconnect()
        time.sleep(2)
        self.sta.connect(ssid, pw)
        
        for i in range(timeout):
            if self.sta.isconnected():
                log.info(f"Erfolgreich verbunden! IP: {self.sta.ifconfig()[0]}")
                return True
                
            # log.debug für detaillierte Infos, die man im Alltag oft ausblenden will
            log.debug(f"Warte auf Verbindung... ({i+1}/{timeout}s),")
            time.sleep(1)
            
        return False

    """#####################################################################
    #! @fn           start_ap_mode(self)
    #  @ brief       starte den AP-Modus
    #  @ param       none
    #  @ exception   none
    #  @ return      none
    #####################################################################"""
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

    """#####################################################################
    #! @fn           manage_connection(self)
    #  @ brief       manage the network connection
    #  @ param       none
    #  @ exception   none
    #  @ return      none
    #####################################################################"""
    def manage_connection(self):
        with self.lock:
            status = self.sta.isconnected()
            self.current_status = status
            
            if self.sta.isconnected():
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

    """#####################################################################
    #! @fn           _monitor_loop(self)
    #  @ brief       Hintergrund-Thread, der die WLAN-Verbindung überwacht 
    #                und bei Problemen automatisch reagiert
    #  @ param       none
    #  @ exception   none
    #  @ return      none
    #####################################################################"""
    def _monitor_loop(self):
        log.info("Hintergrund-Thread für WLAN-Überwachung erfolgreich gestartet.")
        while self.is_monitoring:
            with self.lock:
                self.current_status = self.sta.status()
                if self.ap.active():
                    self.current_mode = "AP"
                elif self.sta.isconnected():
                    self.current_mode = "STA"
                else:
                    self.current_mode = "DISCONNECTED"
            
            if self.current_mode == "AP":
                time.sleep(30)
                log.debug("Prüfe im Hintergrund, ob Router wieder erreichbar ist...")
                self.manage_connection()
            else:
                if not self.sta.isconnected():
                    log.warning("Verbindungsproblem im Thread erkannt!")
                    self.manage_connection()
                time.sleep(10)
    
    """#####################################################################
    #! @fn           get_status
    #  @ brief       Gibt den aktuellen Verbindungsstatus zurück, 
    #                inklusive Modus (STA/AP), Statuscode und IP-Adresse 
    #                (falls verbunden).
    #  @ param       none
    #  @ exception   none
    #  @ return      none
    #####################################################################"""
    def get_status(self):
        with self.lock:
            return {
                "mode": self.current_mode,
                "status": self.current_status,
                "ip": self.sta.ifconfig()[0] if self.sta.isconnected() else None
            }   

    """#####################################################################
    #! @fn           start(self)
    #  @ brief       Starte die WLAN-Verwaltung. Verbindungsstatus wird 
    #                geprüft und bei Bedarf automatisch repariert.
    #  @ param       none
    #  @ exception   none
    #  @ return      none
    #####################################################################"""
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
    #net_mgr_test = NetworkManager()
    #net_mgr_test.start(use_thread=False)
    print("networkmanager")
