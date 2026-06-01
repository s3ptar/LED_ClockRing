"""#####################################################################
#! @ file:                   main.py
#  @ projekt:                LED_ClockRing
#  @ created on:             2026-06-01
#  @ author:                 R. Gräber
#  @ Target:                 esp32
#  @ version:                0
#  @ history:                -
#  @ brief
#####################################################################"""

"""#####################################################################
# Includes
#####################################################################"""
import sys
import json
import logging
import os
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
#! @fn           load_config
#  @ brief       read the default config and override it with the override config
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""
def load_config():
    """Lädt die Default-Basis und überschreibt sie mit der Override-Config."""
    # Standardkonfiguration
    config = {} 

    # 1. Default-Config laden
    try:
        with open("/config/default_config.json", "r") as f:
            config.update(json.load(f))
    except Exception:
        print("Hinweis: default_config.json nicht gefunden. Nutze Hardcoded Defaults.")

    # 2. Override-Config laden und Werte überschreiben
    try:
        with open("/config/override_config.json", "r") as f:
            override = json.load(f)
            config.update(override)
    except Exception:
        # Falls keine Override-Datei existiert, ist das völlig okay
        pass
        
    return config


"""#####################################################################
#! @fn          int main(){
#  @ brief       start up function
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""
if __name__ == "__main__":
    print("Starting LED ClockRing Application")

    print("{:<20} {:<10}".format("Name", "Größe (Bytes)"))
    print("-" * 35)

    for file in os.listdir("/config"):
        name = file[0]
        type_code = file[1]  # 0x4000 für Ordner, 0x8000 für Dateien
        if type_code == 0x4000:
            print("{:<20} {:<10}".format(name, "[Ordner]"))
        else:
            size = os.stat(name)[6]  # Index 6 ist die Dateigröße
            print("{:<20} {:<10}".format(name, size))

    config = load_config()
    if config is not None:
        print("Config loaded successfully:")
        print (json.dumps(config, indent=4))
    else:
        print("Failed to load config.")

