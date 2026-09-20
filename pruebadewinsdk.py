import importlib
import time

# Importación segura de winsdk
try:
    media_control_module = importlib.import_module("winsdk.windows.media.control")
    MediaManager = getattr(media_control_module, "GlobalSystemMediaTransportControlsSessionManager")
    WINSDK_DISPONIBLE = True
except (ImportError, AttributeError):
    WINSDK_DISPONIBLE = False
    print("Error: No se pudo cargar 'winsdk'.")

def obtener_media_info():
    """Función para consultar los metadatos de forma síncrona"""
    if not WINSDK_DISPONIBLE:
        return None, None
    
    try:
        # En Windows, algunas llamadas requieren un loop de eventos temporal si se llaman sincrónicamente
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _run():
            sessions = await MediaManager.request_async()
            if sessions:
                current_session = sessions.get_current_session()
                if current_session:
                    info = await current_session.try_get_media_properties_async()
                    if info:
                        return info.title, info.artist
            return None, None

        return loop.run_until_complete(_run())
    except Exception:
        return None, None

def main():
    print("Monitoreando música en Windows")
    ultima_cancion = ""

    while True:
        titulo, artista = obtener_media_info()
        
        if titulo and artista:
            texto_actual = f"{artista} - {titulo}"
            if texto_actual != ultima_cancion:
                print(f" Reproduciendo: {texto_actual}")
                ultima_cancion = texto_actual
        else:
            if ultima_cancion != "Pausado":
                print("⏸ No hay reproducción activa o está pausado.")
                ultima_cancion = "Pausado"

        time.sleep(3)  # Revisa cada 3 segundos

if __name__ == "__main__":
    main()