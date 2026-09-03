import sounddevice as sd
import numpy as np
import serial
import time

# Configuración Serial
# Cambia 'COM3' por el puerto de tu Arduino
try:
    arduino = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2) # Esperar reinicio del Arduino
    print("Conectado al Arduino con éxito.")
except Exception as e:
    print(f"Error al conectar al Arduino: {e}")
    arduino = None

# --- Configuración de Audio ---
CHUNK = 1024               # Bloque de procesamiento
RATE = 44100                # Frecuencia de muestreo estándar

# --- Sube el UMBRAL_MEDIOS hasta encontrar el punto dulce ---
UMBRAL_BAJOS = 80.0   
UMBRAL_MEDIOS = 135.0  # <--- Súbelo de 8.0 a 120.0 (o ve probando con 150.0)
UMBRAL_ALTOS = 30.0   

print("Analizando audio del sistema... Presiona Ctrl+C para salir.")
def audio_callback(indata, frames, time_info, status):
    if status:
        print(status)
    
    # Convertir el canal de audio a un arreglo plano
    data_int = indata[:, 0]
    
    # Aplicar Transformada Rápida de Fourier (FFT)
    fft_data = np.abs(np.fft.rfft(data_int))
    freqs = np.fft.rfftfreq(CHUNK, d=1.0/RATE)
    
    # Filtrar rangos (Bajos: 20-250Hz | Medios: 255-4000Hz | Altos: >4000Hz)
    bajos_indices = np.where((freqs >= 20) & (freqs <= 250))[0]
    medios_indices = np.where((freqs >= 255) & (freqs <= 4000))[0]
    altos_indices = np.where(freqs > 4000)[0]
    
    # CORRECCIÓN: Usamos np.max para capturar el pico real de la frecuencia en vez de promediar con ceros
    vol_bajos = np.max(fft_data[bajos_indices]) * 100 if len(bajos_indices) > 0 else 0
    vol_medios = np.max(fft_data[medios_indices]) * 100 if len(medios_indices) > 0 else 0
    vol_altos = np.max(fft_data[altos_indices]) * 100 if len(altos_indices) > 0 else 0
    
    # Agrega este print temporal para calibrar tus umbrales viendo los valores reales en consola:
    # print(f"Bajos: {vol_bajos:.1f} | Medios: {vol_medios:.1f} | Altos: {vol_altos:.1f}")

    # Enviar comandos al Arduino
    if arduino:
        if vol_bajos > UMBRAL_BAJOS:
            arduino.write(b'B')
        else:
            arduino.write(b'b')

        if vol_medios > UMBRAL_MEDIOS:
            arduino.write(b'M')  # Asegúrate de recibir 'M' en Arduino
        else:
            arduino.write(b'm')  # Asegúrate de recibir 'm' en Arduino

        if vol_altos > UMBRAL_ALTOS:
            arduino.write(b'H')  # Asegúrate de recibir 'H' en Arduino
        else:
            arduino.write(b'h')  # Asegúrate de recibir 'h' en Arduino


# Iniciar la captura de la tarjeta de sonido predeterminada
try:
    with sd.InputStream(samplerate=RATE, channels=1, blocksize=CHUNK, callback=audio_callback):
        while True:
            time.sleep(0.1)
except KeyboardInterrupt:
    print("\nPrograma detenido.")
finally:
    if arduino:
        arduino.close()
