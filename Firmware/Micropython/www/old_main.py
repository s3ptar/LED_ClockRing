# main.py
# Simple Hello World program for ESP32 with MicroPython

import sys
import time
import machine
import ubinascii
import gc


def main():
    try:
        # Print to serial console
        print("Hello, World from ESP32 with MicroPython!")
        
        # Frequenz in Hz abrufen
        freq_hz = machine.freq()
        freq_mhz = freq_hz / 1_000_000

        print(f"CPU Frequenz: {freq_mhz} MHz")
        print(f"Plattform: {sys.platform}")
        print(f"Version: {sys.version}")
        print(f"Implementierung: {sys.implementation}")
        
        uid = machine.unique_id()
        # In lesbares Hex-Format umwandeln
        hex_uid = ubinascii.hexlify(uid).decode()

        print(f"Eindeutige Device-ID: {hex_uid}")
        
        alloc = gc.mem_alloc()
        free = gc.mem_free()
        total = alloc + free

        print(f"RAM Total: {total} Bytes")
        print(f"RAM Belegt: {alloc} Bytes")
        print(f"RAM Frei: {free} Bytes")

        # Optional: Blink the onboard LED if available
        try:
            from machine import Pin
            led = Pin(2, Pin.OUT)  # GPIO2 is often the onboard LED
            for _ in range(5):
                led.value(1)  # LED ON
                time.sleep(0.5)
                led.value(0)  # LED OFF
                time.sleep(0.5)
        except Exception as e:
            print("LED blink skipped:", e)

    except Exception as e:
        sys.print_exception(e)

# Run the program
if __name__ == "__main__":
    main()

