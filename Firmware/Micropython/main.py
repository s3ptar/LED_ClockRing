"""#####################################################################
#! @ file:                   main.py
#  @ projekt:                LED_ClockRing
#  @ created on:             2026-06-01
#  @ author:                 R. Gräber
#  @ Target:                 esp32
#  @ version:                0
#  @ history:                -
#  @ brief                  : erstellt mit Hilfe von Gemini, 
#                             einem KI-Tool von OpenAI, um die
                              Entwicklung zu beschleunigen.
#####################################################################"""

"""#####################################################################
# Includes
#####################################################################"""
import sys
import machine
import logging
import os
import time
import utilities
from networkmanager import NetworkManager
import gc
import webrepl
import esp32
import esp
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
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.ERROR)
net_mgr = NetworkManager()
"""#####################################################################
# local Variable
#####################################################################"""

"""#####################################################################
# Constant
#####################################################################"""

"""#####################################################################
# Local Funtions
#####################################################################"""


class RotatingFileHandler(logging.Handler):
    def __init__(self, filename, max_bytes=1024, backup_count=3):
        super().__init__()
        self.filename = filename
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self._stream = open(filename, "a")

    def emit(self, record):
        try:
            # Format the message
            msg = self.format(record) + "\n"

            # Check if we need to rollover before writing
            if self._stream.tell() + len(msg) >= self.max_bytes:
                self.do_rollover()

            self._stream.write(msg)
            self._stream.flush()
        except Exception:
            # Fail silently or use print() if debugging on hardware
            pass

    def do_rollover(self):
        self._stream.close()

        # Delete the oldest backup if it exists
        oldest_file = f"{self.filename}.{self.backup_count}"
        try:
            os.remove(oldest_file)
        except OSError:
            pass

        # Shift middle backups down: log.1 -> log.2, etc.
        for i in range(self.backup_count - 1, 0, -1):
            sfn = f"{self.filename}.{i}"
            dfn = f"{self.filename}.{i + 1}"
            try:
                os.rename(sfn, dfn)
            except OSError:
                pass

        # Rename current log to log.1
        try:
            os.rename(self.filename, f"{self.filename}.1")
        except OSError:
            pass

        # Open a fresh log file
        self._stream = open(self.filename, "w")

    def close(self):
        self._stream.close()
        super().close()



    
"""#####################################################################
#! @fn           get_log_level
#  @ brief       Konvertiert den String-Level in die logging-Konstante
#  @ param       level_str - String wie "DEBUG", "INFO", etc.
#  @ exception   none
#  @ return      none
#####################################################################"""    
def get_log_level(level_str):
    levels = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG
    }
    return levels.get(level_str.upper(), logging.INFO)
"""#####################################################################
#! @fn           setup_logger
#  @ brief       read the default config and override it with the override config
#  @ param       name=__name__ - Name des Loggers, standardmäßig der Modulname
#  @ exception   none
#  @ return      none
#####################################################################"""
def setup_logger(name=__name__):
    config = utilities.load_config("Logging")
    
    # Root Logger anpassen
    logger = logging.getLogger()
    logger.setLevel(get_log_level(config["loglevel_console"]))
    
    # Bestehende Handler löschen (wichtig bei Soft-Resets in MicroPython)
    logger.handlers = []
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # --- KONSOLEN-AUSGABE ---
    if config["console_output"]:
        # MicroPython nutzt standardmäßig einen StreamHandler für die Konsole
        ch = logging.StreamHandler()
        logger.setLevel(get_log_level(config["loglevel_console"]))
        ch.setFormatter(formatter)
        logger.addHandler(ch)


    # --- FILE-AUSGABE ---
    if config["file_output"]:
        # Standard Python nutzt den professionellen RotatingFileHandler
        
        fh = RotatingFileHandler(config["filepath"], max_bytes=config["max_bytes"], backup_count=config["backup_count"])
        fh.setLevel(get_log_level(config["loglevel_file"]))
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logging.getLogger(__name__) # Gibt den Logger für main zurück


"""#####################################################################
#! @fn           int main(){
#  @ brief       start up function
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""
if __name__ == "__main__":
    print("Starting LED ClockRing Application")
    
    logger = setup_logger()
    logger.info("Logger erfolgreich eingerichtet.")
    net_mgr.start(use_thread=True)
    #webrepl.start()

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

    logger.info(f"Freier Flash:     {free_flash / 1024:.2f} KB")
    logger.info(f"Belegter Flash:   {used_flash / 1024:.2f} KB")
    logger.info(f"Gesamt-Größe:     {total_flash / 1024:.2f} KB")
    logger.info(f"Auslastung:       {(used_flash / total_flash) * 100:.1f}%")

    # Holt die aktuellen Speicherwerte (in Bytes)
    free_ram = gc.mem_free()
    allocated_ram = gc.mem_alloc()
    total_ram = free_ram + allocated_ram

    if gc.isenabled():
        logger.info(f"Garbage Collector disable, is now enabled.")
        gc.enable()
        gc.collect()
    else:
        logger.info(f"Garbage Collector enable")
    logger.info(f"Freier RAM:     {free_ram / 1024:.2f} KB")
    logger.info(f"Belegter RAM:   {allocated_ram / 1024:.2f} KB")
    logger.info(f"Gesamt verfügbar: {total_ram / 1024:.2f} KB")
    logger.info(f"Auslastung:     {(allocated_ram / total_ram) * 100:.1f}%")


    # Holt die aktuelle CPU-Frequenz in Hertz
    cpu_freq_hz = machine.freq()
    logger.info(f"CPU-Frequenz: {cpu_freq_hz / 1000000:.0f} MHz")

    try:
        # Liefert die Temperatur in Fahrenheit oder Celsius (je nach Chip/Firmware)
        # Meistens wird die Temperatur in Grad Celsius zurückgegeben
        temp_c = (esp32.raw_temperature() - 32) * 5/9
        # Falls deine Firmware Fahrenheit liefert, umrechnen: (temp_f - 32) * 5/9
        logger.info(f"Interne Chip-Temperatur: {temp_c:.1f} °C")
    except AttributeError:
        logger.info("Der Temperatursensor wird von diesem Chip/Firmware nicht unterstützt.")

    logger.info(f"Physische Flash-Größe: {esp.flash_size() / (1024 * 1000):.0f} MB")

    
    while True:

        time.sleep(10)
        net_mgr_status = net_mgr.get_status()
        logger.debug("nur console")
        #web_server.start()


    
