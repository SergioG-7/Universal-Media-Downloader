# YouTube & Spotify Multi-Format Downloader & Zipper

[![CI Pipeline](https://github.com/SergioG-7/Youtube-Media-Downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/SergioG-7/Youtube-Media-Downloader/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Herramienta modular de línea de comandos (CLI) de alto rendimiento para la descarga, transcodificación y empaquetado de contenido multimedia desde YouTube y Spotify (canciones individuales, álbumes o listas de reproducción). Diseñada con arquitectura modular (*src-layout*), procesamiento concurrente multihilo, normalización de audio profesional, transferencia inalámbrica local vía código QR y exportación automática de listas `.m3u`.

## Características

* **Soporte Multi-Plataforma & Formato:**
  * **YouTube:** Descarga de videos individuales y playlists completas.
  * **Spotify:** Resolución automática de pistas/álbumes/playlists públicas sin requerir API Keys, extrayendo metadatos oficiales y descargando el audio equivalente en YouTube.
  * **Audio (MP3):** Bitrates configurables (128k, 192k, 320k) con inyección automática de etiquetas ID3 (Título, Artista, Álbum, Año) y portada incrustada en alta resolución.
  * **Video (MP4):** Multiplexado y transcodificación inteligente hasta 1080p vía FFmpeg.
* **Descarga Concurrente Multihilo:** Utiliza `ThreadPoolExecutor` para procesar múltiples pistas en paralelo, optimizando significativamente los tiempos de descarga.
* **Normalización de Audio (EBU R128):** Filtro `loudnorm` integrado para nivelar el volumen percibido entre diferentes fuentes de audio.
* **Transferencia Móvil vía QR (Zero-Disk Footprint):** Levanta un micro-servidor HTTP local efímero y proyecta un código QR en consola para descargar archivos directamente al smartphone desde la misma red Wi-Fi sin dejar residuos en el PC.
* **Control de Duplicados & Historial:** Registro automático en `history.json` para evitar descargar archivos previamente procesados.
* **Exportador de Playlists (.m3u):** Generación automática de listas de reproducción universales compatibles con reproductores de Android y PC.
* **Auto-actualización de Motor:** Comando integrado `--update` para actualizar `yt-dlp` a su versión más reciente ante cambios en YouTube.
* **Interfaz de Terminal Avanzada:** Monitorización en tiempo real con barras de progreso individuales por hilo, spinners y tablas de resumen mediante `Rich`.

## Requisitos

* Python 3.10 o superior
* Conexión a internet

## Instalación

```bash
git clone [https://github.com/SergioG-7/Youtube-Media-Downloader.git](https://github.com/SergioG-7/Youtube-Media-Downloader.git)
cd Youtube-Media-Downloader
python -m venv .venv

# En Windows:
.venv\Scripts\activate
# En Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

## Guía de Uso

### Modo Interactivo (Asistente en Terminal)
Ejecuta el programa directamente sin parámetros para acceder al menú interactivo:
```bash
python main.py
```

### Modo CLI (Parámetros por Línea de Comandos)

```bash
# Descargar playlist de YouTube en MP3 (320 kbps) con normalización y 6 hilos
python main.py -u "[https://www.youtube.com/playlist?list=ID](https://www.youtube.com/playlist?list=ID)" -f mp3 -q 320k -w 6 --normalize

# Descargar cancion o album de Spotify a MP3 y transferir directo al movil vía QR
python main.py -u "[https://open.spotify.com/track/ID](https://open.spotify.com/track/ID)" -f mp3 --qr

# Descargar video en MP4 (1080p) y guardar en carpeta local sin comprimir en ZIP
python main.py -u "[https://www.youtube.com/watch?v=ID](https://www.youtube.com/watch?v=ID)" -f mp4 -q 1080p --no-zip

# Actualizar el motor yt-dlp a la versión más reciente
python main.py --update
```

## Estructura del Proyecto

```text
├── .github/workflows/
│   └── ci.yml               # Pipeline de Integración Continua (GitHub Actions)
├── src/
│   ├── __init__.py
│   ├── client.py            # Parser CLI (argparse) y asistente interactivo con Rich
│   ├── config.py            # Dataclass de configuración de ejecución
│   ├── downloader.py        # Orquestador concurrente multihilo y llamadas a yt-dlp
│   ├── file_dir.py          # Gestión de archivos, compresión ZIP UTF-8 y listas .m3u
│   ├── history.py           # Sistema de deduplicación y persistencia de historial
│   ├── postprocessor.py     # Inyección de metadatos ID3 y carátulas con Mutagen
│   ├── server.py            # Servidor HTTP local y renderizado de QR ASCII
│   └── spotify_resolver.py  # Extracción de metadatos de Spotify y matching en YouTube
├── tests/
│   └── test_core.py         # Suite de pruebas unitarias con Pytest
├── .gitignore
├── main.py                  # Entrypoint de la aplicación
├── requirements.txt
└── README.md
```

## Pruebas Unitarias

Para ejecutar localmente las pruebas del sistema:
```bash
python -m pytest -v
```

## Licencia

Distribuido bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.