import serial
import time
import numpy as np
try:
    import soundcard as sc
except ImportError:
    print("No se encuentra la librería 'soundcard'. Asegúrate de instalarla con 'pip install soundcard'.")

# Configuración del puerto serial (Cuando conecto el arduino me sale ese puerto)
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

    # Configuración de captura de audio  (captura lo que suena en la PC)
    # Obtenemos el micrófono/altavoz predeterminado para loopback
    try:
        mic = sc.default_speaker()
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
                    data = np.mean(data, axis=1) # Convertierte el audio a mono(con el estereo no se podia hacer la FFT)

                # Aplica la Transformación Rápida de Fourier (FFT)
                fft_data = np.abs(np.fft.rfft(data))
                
                # Hace la segmentacion en: Graves, Medios, Agudos
                largo = len(fft_data)
                graves = np.mean(fft_data[:largo//8])
                medios = np.mean(fft_data[largo//8:largo//2])
                agudos = np.mean(fft_data[largo//2:])

                # Ajusta los valores para enviarlos al Arduino ( de escala 0-255 pero creo que se pueda aumentar para que los leds 
                # se vean mas brillantes, pero no se si el arduino los pueda manejar)
                val_graves = min(int(graves * 5), 255)
                val_medios = min(int(medios * 5), 255)
                val_agudos = min(int(agudos * 5), 255)

                # Formato de envío para el arduino ("G:150,M:100,A:50\n")
                mensaje = f"G:{val_graves},M:{val_medios},A:{val_agudos}\n"
                arduino.write(mensaje.encode('utf-8'))

                # Revisar si hay datos desde el Arduino (botones o perilla de volumen)
                if arduino.in_waiting > 0:
                    dato_arduino = arduino.readline().decode('utf-8').strip()
                    if dato_arduino:
                        print(f"Recibido del Arduino: {dato_arduino}")
                        #TODO: Investigar cómo controlar Spotify desde Python y agregar la lógica aquí para que
                        #  el Arduino pueda enviar comandos a Spotify.


            except KeyboardInterrupt:
                print("\nFinalizando script...")
                break

    arduino.close()

if __name__ == '__main__':
    main()