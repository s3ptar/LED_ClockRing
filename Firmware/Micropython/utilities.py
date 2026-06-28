"""#####################################################################
#! @ file:                   webservices.py
#  @ projekt:                LED_ClockRing
#  @ created on:             2026-06-01
#  @ author:                 R. Gräber
#  @ version:                0
#  @ history:                -
#  @ brief:                  Hilfsfunktionen für die LED_ClockRing, erstellt mit Hilfe von Gemini,
#                             einem KI-Tool von OpenAI, um die Entwicklung zu beschleunigen.
#####################################################################"""


"""#####################################################################
# Includes
#####################################################################"""
import logging
import json
import esp32
import esp
import machine
import os
import gc
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

"""#####################################################################
#! @fn           get_device_telemetry() -> dict
#  @ brief       read device telemetry data
#  @ param       none
#  @ exception   none
#  @ return      dict device data
#####################################################################"""
def get_device_telemetry() -> dict:

    telemetry_dict = {}

    #get filesystem information
    # os.statvfs gibt Informationen über das Dateisystem zurück
    # '/' steht für das Hauptverzeichnis
    fs_info = os.statvfs('/')
    # Blockgröße in Bytes
    block_size = fs_info[0]
    # Gesamtzahl der Blöcke
    total_blocks = fs_info[2]
    # Freie Blöcke
    free_blocks = fs_info[3]
    # Berechnung in Bytes und Kilobytes
    total_flash = block_size * total_blocks
    free_flash = block_size * free_blocks
    used_flash = total_flash - free_flash
    telemetry_dict["Filesystem"] = {"pyh Flash": f"{esp.flash_size() / (1024 * 1000):.0f} MB",
                                    "total_flash":f"{total_flash} kB",
                                    "free_flash": f"{free_flash} kB",
                                    "used_flash": f"{used_flash} kB",
                                    "Auslastung": f"{(used_flash / total_flash) * 100:.1f}%"
                                    }

    logger.debug(f"Physische Flash-Größe: {esp.flash_size() / (1024 * 1000):.0f} MB")
    logger.debug(f"Freier Flash:     {free_flash / 1024:.2f} KB")
    logger.debug(f"Belegter Flash:   {used_flash / 1024:.2f} KB")
    logger.debug(f"Gesamt-Größe:     {total_flash / 1024:.2f} KB")
    logger.debug(f"Auslastung:       {(used_flash / total_flash) * 100:.1f}%")

    # Holt die aktuellen Speicherwerte (in Bytes)
    free_ram = gc.mem_free()
    allocated_ram = gc.mem_alloc()
    total_ram = free_ram + allocated_ram
    logger.debug(f"Freier RAM:     {free_ram / 1024:.2f} KB")
    logger.debug(f"Belegter RAM:   {allocated_ram / 1024:.2f} KB")
    logger.debug(f"Gesamt verfügbar: {total_ram / 1024:.2f} KB")
    logger.debug(f"Auslastung:     {(allocated_ram / total_ram) * 100:.1f}%")
    telemetry_dict["RAM"] = { "free": f"{free_ram / 1024:.2f} KB",
                              "allocated": f"{allocated_ram / 1024:.2f} KB",
                              "total": f"{total_ram / 1024:.2f} KB",
                              "Auslastung": f"{(allocated_ram / total_ram) * 100:.1f}%"
                              }

    if gc.isenabled():
        logger.debug(f"Garbage Collector disable, is now enabled.")
        telemetry_dict["GarbageCollector"] = {"enabled" : True}
    else:
        logger.debug(f"Garbage Collector enable")
        telemetry_dict["GarbageCollector"] = {"enabled": False}

    # Holt die aktuelle CPU-Frequenz in Hertz
    cpu_freq_hz = machine.freq()
    logger.debug(f"CPU-Frequenz: {cpu_freq_hz / 1000000:.0f} MHz")
    telemetry_dict["CPU"] = {"Frequenz": f"{cpu_freq_hz / 1000000:.0f} MHz"}
    telemetry_dict["Device"] = {"Type": "ESP32-Generic"}

    try:
        # Liefert die Temperatur in Fahrenheit oder Celsius (je nach Chip/Firmware)
        # Meistens wird die Temperatur in Grad Celsius zurückgegeben
        temp_c = (esp32.raw_temperature() - 32) * 5 / 9
        # Falls deine Firmware Fahrenheit liefert, umrechnen: (temp_f - 32) * 5/9
        logger.debug(f"Interne Chip-Temperatur: {temp_c:.1f} °C")
        telemetry_dict["Temperatur"] = {"internal": f"{temp_c:.1f}"}
    except AttributeError:
        logger.debug("Der Temperatursensor wird von diesem Chip/Firmware nicht unterstützt.")

    return telemetry_dict

"""#####################################################################
#! @fn           load_config
#  @ brief       read the default config and override it with the override config
#  @ param       none
#  @ exception   none
#  @ return      dict with the merged configuration
#####################################################################"""
def load_config(config_name = None) -> dict:
    """Lädt die Default-Basis und überschreibt sie mit der Override-Config."""
    # Standardkonfiguration
    config = {} 
    # 1. Default-Config laden
    try:
        with open("config/default_config.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Hinweis: default_config.json nicht gefunden. Nutze Hardcoded Defaults. Error {e}")

    # 2. Override-Config laden und Werte überschreiben
    try:
        with open("config/override_config.json", "r") as f:
            override = json.load(f)
            config.update(override)
    except Exception:
        # Falls keine Override-Datei existiert, ist das völlig okay
        pass
    
    if config_name is not None:
        return config[config_name]
    else:
        return config

"""#####################################################################
#! @fn           int main(){
#  @ brief       start up function
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""


if __name__ == "__main__":
    print("Hello World!")
