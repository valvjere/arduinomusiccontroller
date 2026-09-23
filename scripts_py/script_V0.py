import serial
import time
import numpy as np
import warnings
from soundcard.mediafoundation import SoundcardRuntimeWarning

# Ignorar la advertencia de discontinuidad de audio para limpiar la terminal 
warnings.filterwarnings("ignore", category=SoundcardRuntimeWarning)

# --- Nuevos umbrales ajustados a tus datos reales ---
UMBRAL_BAJOS = 6.5   
UMBRAL_MEDIOS = 0.45  
UMBRAL_ALTOS = 0.12

try:
    import soundcard as sc
except ImportError:
    print("No se encuentra la librería 'soundcard'. Instalarla con 'pip install soundcard' en la terminal.")

# Configuración del puerto serial
PUERTO_SERIAL = 'COM3'
VELOCIDAD = 9600

def main():
    try:
        arduino = serial.Serial(PUERTO_SERIAL, VELOCIDAD, timeout=1)
        time.sleep(2) # Esperar a que la conexión se establezca
        print(f"Conectado al puerto serial {PUERTO_SERIAL}")
    except Exception as e:
        print(f"Error al conectar con el puerto serial: {e}")
        return

    # Configuración de captura de audio (loopback)
    try:
        speaker = sc.default_speaker()
        mic = sc.get_microphone(id=speaker.name, include_loopback=True)
        print(f"Capturando audio de: {mic.name}")
    except Exception as e:
        print(f"No se pudo conectar el dispositivo de audio: {e}")
        return

    # Parámetros para la FFT
    sample_rate = 44100
    block_size = 1024

    print("Iniciando visualizador... Presiona Ctrl+C para detener.")
    
    with mic.recorder(samplerate=sample_rate, channels=1) as recorder:
        while True:
            try:
                # Captura el bloque de audio
                data = recorder.record(numframes=block_size)
                
                if len(data.shape) > 1:
                    data = np.mean(data, axis=1) # Convierte el audio a mono

                # Aplica la Transformación Rápida de Fourier (FFT)
                fft_data = np.abs(np.fft.rfft(data))
                
                # Segmentación en: Graves, Medios, Agudos
                largo = len(fft_data)
                graves = np.mean(fft_data[:largo//8])
                medios = np.mean(fft_data[largo//8:largo//2])
                agudos = np.mean(fft_data[largo//2:])

                # --- PISO MÁS ALTO Y MULTIPLICADOR CONTROLADO ---
                # Ahora exigimos que la música supere un nivel más alto para encender
                val_graves = min(int(max(0, graves - 6.5) * 40), 255)
                val_medios = min(int(max(0, medios - 0.42) * 700), 255)
                val_agudos = min(int(max(0, agudos - 0.12) * 1400), 255)

                # Envío ultrarrápido de 3 bytes puros al Arduino
                if arduino:
                    arduino.write(bytes([val_graves, val_medios, val_agudos]))
            except KeyboardInterrupt:
                print("\nFinalizando script...")
                break

    arduino.close()

if __name__ == '__main__':
    main()