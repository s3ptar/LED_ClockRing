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
from microdot import Microdot, Response, send_file
import os
import utilities
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
log = logging.getLogger(__name__)
logger = log
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
    def __init__(self, host='0.0.0.0', port=80, www_dir="/www", debug=True):
        self.host = host
        self.port = port
        self.debug = debug
        self.www_dir = www_dir.rstrip("/")
        
        # Logger für diese spezifische Klasse erstellen
        
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
    #def _get_telemetry(self):


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
        # Route für die Startseite
        #@self.app.route('/')
        #async def index(request):
        #    log.info(f"Request received")
        #    return 'Hello World!'
        @self.app.route('/')
        async def index(request):
            return send_file('/www/index.html')

        # Der API-Endpunkt für deine AJAX-Anfrage
        @self.app.route('/api/telemetry')
        def get_data(request):
            # Das Dictionary, das an die Website zurückgegeben wird
            # Microdot erkennt das Dict und sendet es automatisch als JSON mit dem Header 'application/json'
            return json.dumps(utilities.get_device_status())

        # Catch-All Route für alle statischen Dateien (CSS, JS, Bilder)
        @self.app.route('/<path:path>')
        async def static_files(request, path):
            # Verhindert, dass User außerhalb von /www zugreifen können (Sicherheit)
            if '..' in path:
                return 'Nicht erlaubt', 403

            # Liefert die Datei aus dem /www-Ordner, falls sie existiert
            log.debug(f"Static file: {path}")
            return send_file('/www/' + path)







    """#####################################################################
    #! @fn           start
    #  @ brief       Startet den Webserver und stellt sicher, dass er auch 
    #                bei Netzwerkproblemen weiterläuft
    #  @ param       none
    #  @ exception   none
    #  @ return      none
    #####################################################################"""
    async def start(self):
        # INFO-Level: Wichtige Statusänderungen im Lebenszyklus der App
        log.info(f"Server wird gestartet auf http://{self.host}:{self.port}...")
        await self.app.start_server(self.host, self.port, debug=self.debug)


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
