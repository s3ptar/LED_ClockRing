"""#####################################################################
#! @ file:                   networmanager.py
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
logger = logging.getLogger(__name__)
"""#####################################################################
# Constant
#####################################################################"""

"""#####################################################################
# Local Funtions
#####################################################################"""

def connect_sta(ssid, password, timeout=15):
    """Versucht, sich als Client (STA) mit einem WLAN zu verbinden."""
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

def start_ap(ssid, password):
    """Aktiviert den Access Point (AP) Modus."""
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
#! @fn           int main(){
#  @ brief       start up function
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""

if __name__ == "__main__":
    start_networkmanager()
