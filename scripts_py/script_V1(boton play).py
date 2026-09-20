import serial
import time
import numpy as np
import warnings
import pyautogui
from soundcard.mediafoundation import SoundcardRuntimeWarning

# Ignorar advertencias de audio
warnings.filterwarnings("ignore", category=SoundcardRuntimeWarning)

# Umbrales
UMBRAL_BAJOS = 6.5   
UMBRAL_MEDIOS = 0.45  
UMBRAL_ALTOS = 0.12

try:
    import soundcard as sc
except ImportError:
    print("No se encuentra la librería 'soundcard'. Instalarla con 'pip install soundcard'.")

PUERTO_SERIAL = 'COM3'
VELOCIDAD = 9600

def main():
    arduino = None
    try:
        arduino = serial.Serial(PUERTO_SERIAL, VELOCIDAD, timeout=1)
        time.sleep(2) 
        print(f"Conectado al puerto serial {PUERTO_SERIAL}")
    except Exception as e:
        print(f"Error al conectar con el puerto serial: {e}")
        return

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
                # 1. Procesar y enviar datos de audio al Arduino (LEDs)
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
                    arduino.write(bytes([val_graves, val_medios, val_agudos]))

                # 2. Leer si el Arduino envió algún comando de los botones
                if arduino.in_waiting > 0:
                    comando = arduino.readline().decode('utf-8').strip()
                    
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