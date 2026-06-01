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
