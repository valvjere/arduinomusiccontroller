import serial
import time
import numpy as np
import warnings
import pyautogui
import asyncio # permite concurrencia sin bloquear procesos, útil para la consulta de winsdk
import threading #Considere que usar hilos sale mejor que meter la consulta de winsdk en el bucle principal, para no bloquear la captura de audio
from soundcard.mediafoundation import SoundcardRuntimeWarning

# Intenta importar winsdk para la sesión multimedia de Windows
try:
    import importlib

    MediaManager = getattr(
        importlib.import_module("winsdk.windows.media.control"),
        "GlobalSystemMediaTransportControlsSessionManager",
    )
    WINSDK_DISPONIBLE = True
except ImportError:
    WINSDK_DISPONIBLE = False
    print("Aviso: 'winsdk' no se pudo cargar correctamente.")

# Ignorar advertencias de audio
warnings.filterwarnings("ignore", category=SoundcardRuntimeWarning)

try:
    import soundcard as sc
except ImportError:
    print("No se encuentra la librería 'soundcard'. Instalarla con 'pip install soundcard'.")

PUERTO_SERIAL = 'COM3'  # Cambia por tu puerto si es necesario
VELOCIDAD = 9600

# Variables globales para compartir entre hilos
cancion_actual = ""
artista_actual = ""

def obtener_info_multimedia_sync():
    """Función auxiliar para ejecutar la consulta asíncrona de winsdk de forma síncrona"""
    async def _obtener():
        try:
            sessions = await MediaManager.request_async()
            current_session = sessions.get_current_session()
            if current_session:
                info = await current_session.try_get_media_properties_async()
                if info:
                    return info.title, info.artist
        except Exception:
            pass
        return "", ""

    try:
        return asyncio.run(_obtener())
    except Exception:
        return "", ""

def hilo_spotify_y_lcd(arduino):
    """Hilo secundario que revisa la canción cada 3 segundos y la manda al Arduino si cambió"""
    global cancion_actual, artista_actual
    ultima_enviada = ""

    while True:
        if WINSDK_DISPONIBLE:
            titulo, artista = obtener_info_multimedia_sync()
            if titulo:
                nuevo_texto = f"{titulo[:16]}|{artista[:16]}" # Formato para dividir líneas en LCD 16x2
                if nuevo_texto != ultima_enviada:
                    cancion_actual = titulo
                    artista_actual = artista
                    ultima_enviada = nuevo_texto
                    
                    # Enviar texto al Arduino por puerto Serial con un marcador de inicio 'T'
                    if arduino and arduino.is_open:
                        mensaje_serial = f"T:{titulo[:16]},{artista[:16]}\n"
                        arduino.write(mensaje_serial.encode('utf-8'))
                        print(f"-> Reproduciendo: {artista} - {titulo}")
        time.sleep(3)

def main():
    arduino = None
    try:
        arduino = serial.Serial(PUERTO_SERIAL, VELOCIDAD, timeout=1)
        time.sleep(2) 
        print(f"Conectado al puerto serial {PUERTO_SERIAL}")
    except Exception as e:
        print(f"Error al conectar con el puerto serial: {e}")
        return

    # Iniciar el hilo secundario para los metadatos de Windows/Spotify
    hilo_metadatos = threading.Thread(target=hilo_spotify_y_lcd, args=(arduino,), daemon=True)
    hilo_metadatos.start()

    try:
        speaker = sc.default_speaker()
        mic = sc.get_microphone(id=speaker.name, include_loopback=True)
        print(f"Capturando audio de: {mic.name}")
    except Exception as e:
        print(f"No se pudo conectar el dispositivo de audio: {e}")
        if arduino and arduino.is_open:
            arduino.close()
        return

    sample_rate = 44100
    block_size = 1024

    print("Controlador y visualizador activos... Presiona Ctrl+C para detener.")
    
    try:
        with mic.recorder(samplerate=sample_rate, channels=1) as recorder:
            while True:
                # Procesar y enviar datos de audio al Arduino (LEDs por FFT)
                data = recorder.record(numframes=block_size)
                
                if len(data.shape) > 1:
                    data = np.mean(data, axis=1)

                fft_data = np.abs(np.fft.rfft(data))
                
                largo = len(fft_data)
                graves = np.mean(fft_data[:largo//8])
                medios = np.mean(fft_data[largo//8:largo//2])
                agudos = np.mean(fft_data[largo//2:])

                val_graves = min(int(max(0, graves - 6.5) * 40), 255)
                val_medios = min(int(max(0, medios - 0.42) * 700), 255)
                val_agudos = min(int(max(0, agudos - 0.12) * 1400), 255)

                if arduino and arduino.is_open:
                    # Enviamos un byte indicador de audio o directamente los valores si el Arduino los distingue
                    # Envío de 3 bytes para los LEDs
                    arduino.write(bytes([val_graves, val_medios, val_agudos]))

                # 2. Leer si el Arduino envió algún comando de los botones
                if arduino.in_waiting > 0:
                    comando = arduino.readline().decode('utf-8', errors='ignore').strip()
                    
                    if comando == "CMD_PLAY":
                        pyautogui.press('playpause')
                        print("-> Acción: Play / Pausa")
                    elif comando == "CMD_NEXT":
                        pyautogui.press('nexttrack')
                        print("-> Acción: Siguiente canción")
                    elif comando == "CMD_PREV":
                        pyautogui.press('prevtrack')
                        print("-> Acción: Canción anterior")

    except KeyboardInterrupt:
        print("\nFinalizando script y liberando el puerto...")
    finally:
        if arduino and arduino.is_open:
            arduino.close()
            print("Puerto serial cerrado correctamente.")

if __name__ == '__main__':
    main()