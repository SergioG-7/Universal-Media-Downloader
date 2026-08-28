# YouTube Multi-Format Downloader & Zipper

Herramienta modular de línea de comandos (CLI) de alto rendimiento para la descarga y transcodificación de contenido multimedia desde YouTube (videos o playlists completas). Diseñada con arquitectura modular, procesamiento concurrente multihilo y post-procesamiento automático de metadatos e imágenes de portada.

## Características

* **Soporte Multi-Formato:** 
  * **Audio (MP3):** Extracción con bitrates configurables (128k, 192k, 320k) e inyección automática de etiquetas ID3 (Título, Artista, Año) y portada del video incrustada.
  * **Video (MP4):** Transcodificación y multiplexado inteligente de video y audio con soporte hasta 1080p.
* **Descarga Concurrente Multihilo:** Utiliza `ThreadPoolExecutor` para descargar múltiples pistas en paralelo, optimizando significativamente el tiempo en listas de reproducción extensas.
* **Gestión Segura de Archivos:** Todo el procesamiento ocurre en un entorno temporal aislado (`tempfile`), evitando archivos residuales o corrompidos ante interrupciones.
* **Opciones de Salida:** Empaquetado automático en `.zip` o guardado directo en directorio estructurado.
* **Doble Modo:** Soporte nativo para flags por terminal y modo interactivo guiado por consola.

## Requisitos

* Python 3.9+
* Conexión a internet

## Instalación

```bash
git clone [https://github.com/SergioG-7/Youtube-Media-Downloader](https://github.com/SergioG-7/Youtube-Media-Downloader)
cd youtube-media-downloader
python -m venv .venv

# En Windows:
.venv\Scripts\activate
# En Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt