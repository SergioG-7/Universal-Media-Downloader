import os
import sys
import subprocess
import zipfile

# --- SISTEMA DE AUTO-INSTALACION DE LIBRERIAS ---
try:
    import yt_dlp
    import imageio_ffmpeg
except ImportError:
    print("Faltan librerias necesarias. Instalando dependencias automaticamente, por favor espera...")
    try:
        # Ejecuta el comando pip install para instalar ambas herramientas
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "imageio-ffmpeg"])
        import yt_dlp
        import imageio_ffmpeg
        print("Instalacion completada con exito.\n")
    except Exception as e:
        print(f"Error al intentar instalar las dependencias automaticamente: {e}")
        print("Por favor, abre tu terminal y escribe: pip install yt-dlp imageio-ffmpeg")
        sys.exit(1)
# ------------------------------------------------

def descargar_y_convertir(url):
    os.makedirs('descargas_temporales', exist_ok=True)
    
    # Obtenemos la ruta del FFmpeg que acabamos de instalar automaticamente
    ruta_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    
    opciones_info = {
        'extract_flat': True,
        'ignoreerrors': True,
        'quiet': True
    }
    
    opciones_descarga = {
        'format': 'bestaudio/best',
        'outtmpl': 'descargas_temporales/%(title)s_%(id)s.%(ext)s',
        'ffmpeg_location': ruta_ffmpeg,  # Le indicamos a yt-dlp donde esta FFmpeg
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True
    }

    archivos_descargados = []
    archivos_fallidos = []

    print("Analizando el enlace...")
    try:
        with yt_dlp.YoutubeDL(opciones_info) as ydl:
            info = ydl.extract_info(url, download=False)
            
        if info is None:
            return [], [{"titulo": "Enlace proporcionado", "razon": "No se pudo obtener informacion. Verifica si el video es privado o el enlace es incorrecto."}]

        entries = info.get('entries', [info])

    except Exception as e:
        return [], [{"titulo": url, "razon": f"Error critico al leer el enlace: {str(e)}"}]

    print(f"Se detectaron {len(entries)} elementos. Iniciando descarga...")

    with yt_dlp.YoutubeDL(opciones_descarga) as ydl_descarga:
        for i, entry in enumerate(entries):
            if entry is None:
                archivos_fallidos.append({
                    "titulo": f"Pista #{i+1} (Desconocida)", 
                    "razon": "Video no disponible (posiblemente privado, eliminado o geobloqueado)."
                })
                continue
            
            titulo = entry.get('title', f"Pista #{i+1}")
            
            video_url = entry.get('webpage_url') or entry.get('url')
            if not video_url and entry.get('id'):
                video_url = f"https://www.youtube.com/watch?v={entry.get('id')}"
            elif not video_url:
                video_url = url
            
            print(f"Descargando: {titulo}...")
            
            try:
                info_descarga = ydl_descarga.extract_info(video_url, download=True)
                
                if info_descarga:
                    filename = ydl_descarga.prepare_filename(info_descarga)
                    base, _ = os.path.splitext(filename)
                    mp3_file = base + ".mp3"
                    
                    if os.path.exists(mp3_file):
                        archivos_descargados.append(mp3_file)
                    else:
                        archivos_fallidos.append({"titulo": titulo, "razon": "Se descargo, pero fallo la conversion a formato MP3."})
            except Exception as e:
                error_msg = str(e).split('\n')[0]
                archivos_fallidos.append({"titulo": titulo, "razon": error_msg})

    return archivos_descargados, archivos_fallidos

def crear_zip(archivos, nombre_zip="musica_descargada.zip", borrar_originales=True):
    if not archivos:
        return None
        
    print(f"Empaquetando {len(archivos)} canciones en '{nombre_zip}'...")
    
    with zipfile.ZipFile(nombre_zip, 'w') as zipf:
        for archivo in archivos:
            if os.path.exists(archivo):
                zipf.write(archivo, arcname=os.path.basename(archivo))
                if borrar_originales:
                    os.remove(archivo)
                    
    return nombre_zip

if __name__ == "__main__":
    enlace = input("Ingresa el enlace de YouTube (video o playlist): ")
    
    descargados, fallidos = descargar_y_convertir(enlace)
    
    print("\n" + "="*50 + "\nRESUMEN DE LA OPERACION\n" + "="*50)
    
    if descargados:
        print(f"EXITO: Se descargaron y convirtieron {len(descargados)} canciones.")
        archivo_zip = crear_zip(descargados)
        if archivo_zip:
            print(f"Listo. Tu archivo ZIP esta aqui: {os.path.abspath(archivo_zip)}")
    else:
        print("ADVERTENCIA: No se pudo descargar ninguna cancion.")

    if fallidos:
        print(f"\nERRORES: Hubo {len(fallidos)} pistas que NO se pudieron descargar:")
        for fallo in fallidos:
            print(f"  - {fallo['titulo']}")
            print(f"    -> Razon: {fallo['razon']}\n")
            
    try:
        os.rmdir('descargas_temporales')
    except OSError:
        pass
