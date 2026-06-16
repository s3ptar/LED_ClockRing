"""#####################################################################
#! @ file:                   webservices.py
#  @ projekt:                LED_ClockRing
#  @ created on:             2026-06-01
#  @ author:                 R. Gräber
#  @ version:                0
#  @ history:                -
#  @ brief:                  Webservices für die LED_ClockRing, erstellt mit Hilfe von Gemini,
#                             einem KI-Tool von OpenAI, um die Entwicklung zu beschleunigen.
#####################################################################"""


"""#####################################################################
# Includes
#####################################################################"""
import logging
import gc
import time
from microdot import Microdot, Response
#from utemplate import compiled
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
#! @fn           class TelemetryServer
#  @ brief       Ein einfacher Webserver, der Webservices für die 
#                LED_ClockRing bereitstellt.
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""
class WebServer:
    def __init__(self, host='0.0.0.0', port=80, debug=False):
        self.host = host
        self.port = port
        self.debug = debug
        
        # Logger für diese spezifische Klasse erstellen
        self.log = logging.getLogger("TelemetryServer")
        
        self.app = Microdot()
        Response.default_content_type = 'text/html'
        self._register_routes()

    """#####################################################################
    #! @fn           _get_telemetry
    #  @ brief       Liest die aktuellen Telemetriedaten der LED_ClockRing aus, wie z.B.
    #                die Betriebszeit und den freien RAM. Diese Daten werden dann an die Webservices
    #  @ param       none
    #  @ exception   none
    #  @ return      none
    #####################################################################"""
    def _get_telemetry(self):
        # DEBUG-Level: Perfekt für Dinge, die oft passieren, aber im Alltag nicht interessieren
        self.log.debug("Lese Telemetriedaten aus...")
        return {
            'uptime': time.ticks_ms() // 1000,
            'free_ram': gc.mem_free()
        }

    """#####################################################################
    #! @fn           _register_routes
    #  @ brief       Registriert die Webservice-Routen für den Server. 
    #                Hier können weitere Routen hinzugefügt werden, um z.B. 
    #                Einstellungen zu ändern oder historische Daten anzuzeigen.
    #  @ param       none
    #  @ exception   none
    #  @ return      none
    #####################################################################"""
    def _register_routes(self):
        @self.app.route('/')
        def index(request):
            data = self._get_telemetry()
            #render = compiled.render('templates/index.html', **data)
            #return ''.join(render)

    """#####################################################################
    #! @fn           start
    #  @ brief       Startet den Webserver und stellt sicher, dass er auch 
    #                bei Netzwerkproblemen weiterläuft
    #  @ param       none
    #  @ exception   none
    #  @ return      none
    #####################################################################"""
    def start(self):
        # INFO-Level: Wichtige Statusänderungen im Lebenszyklus der App
        self.log.info(f"Server wird gestartet auf http://{self.host}:{self.port}...")
        
        while True:
            try:
                self.app.run(host=self.host, port=self.port, debug=self.debug)
            except OSError as e:
                # ERROR-Level: Hier ist etwas schiefgelaufen, der Server läuft aber weiter
                self.log.error(f"Netzwerk-Socket-Fehler abgefangen: {e}")
                self.log.info("Warte auf Netzwerk-Recovery...")
                time.sleep(2)

"""#####################################################################
#! @fn           int main(){
#  @ brief       start up function
#  @ param       none
#  @ exception   none
#  @ return      none
#####################################################################"""
if __name__ == "__main__":
    print("test")
    #server = TelemetryServer(debug=False)
    #server.start()
