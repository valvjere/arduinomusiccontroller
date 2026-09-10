import serial
import time
import numpy as np
try:
    import soundcard as sc
except ImportError:
    print("No se encuentra la librería 'soundcard'. Instalarla con 'pip install soundcard' en la terminal.")

# Configuración del puerto serial
PUERTO_SERIAL = 'COM6'
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

                # Ajusta los valores (escala 0-255)
                val_graves = min(int(graves * 5), 255)
                val_medios = min(int(medios * 5), 255)
                val_agudos = min(int(agudos * 5), 255)
                print("Se procesa bien")
                # Formato de envío para el arduino
                mensaje = f"G:{val_graves},M:{val_medios},A:{val_agudos}\n"
                print(f"Enviando: {mensaje.strip()}")
                arduino.write(mensaje.encode('utf-8'))

            except KeyboardInterrupt:
                print("\nFinalizando script...")
                break

    arduino.close()

if __name__ == '__main__':
    main()