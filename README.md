# YouTube & Spotify Multi-Format Downloader

[![CI Pipeline](https://github.com/SergioG-7/Youtube-Media-Downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/SergioG-7/Youtube-Media-Downloader/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Herramienta de terminal para descargar canciones, álbumes, listas de reproducción y videos de YouTube y Spotify en MP3 o MP4. Organiza las descargas, añade carátulas e información de las pistas, permite pasar los archivos directamente al móvil con un código QR y crea listas de reproducción `.m3u`.

## Características

* **Descarga de YouTube y Spotify:**
  * **YouTube:** Descarga videos sueltos o listas completas.
  * **Spotify:** Busca automáticamente las canciones en YouTube y guarda la carátula oficial y los datos del tema (artista, álbum, año).
  * **Audio (MP3):** Elige la calidad (128k, 192k, 320k) con carátula y datos de la canción incluidos.
  * **Video (MP4):** Descarga videos en diferentes resoluciones hasta 1080p.
* **Descargas paralelas:** Descarga varias canciones al mismo tiempo para terminar más rápido las listas largas.
* **Volumen nivelado:** Opción para que todas las canciones suenen al mismo nivel y no haya cambios bruscos de sonido.
* **Paso directo al móvil con QR:** Escanea un código QR desde el móvil para descargarlo por Wi-Fi sin ocupar espacio en el PC.
* **Control de canciones repetidas:** Lleva un registro en `history.json` para no volver a descargar temas que ya bajaste.
* **Lista de reproducción (.m3u):** Crea un archivo de lista compatible con reproductores de música de Android y PC.
* **Actualización sencilla:** Comando `--update` para actualizar el motor de descargas si YouTube cambia algo.
* **Interfaz clara en consola:** Barras de progreso por cada descarga y tabla con el resumen final.

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

### Modo Guiado (Menú interactivo)
Ejecuta el programa directamente para que te vaya preguntando qué quieres hacer paso a paso:
```bash
python main.py
```

### Modo Comandos (CLI)

```bash
# Descargar una playlist de YouTube en MP3 (320 kbps) con volumen nivelado y 6 descargas a la vez
python main.py -u "[https://www.youtube.com/playlist?list=ID](https://www.youtube.com/playlist?list=ID)" -f mp3 -q 320k -w 6 --normalize

# Descargar de Spotify a MP3 y pasarlo directo al móvil con QR
python main.py -u "[https://open.spotify.com/track/ID](https://open.spotify.com/track/ID)" -f mp3 --qr

# Descargar video en MP4 (1080p) y guardarlo en una carpeta normal
python main.py -u "[https://www.youtube.com/watch?v=ID](https://www.youtube.com/watch?v=ID)" -f mp4 -q 1080p --no-zip

# Actualizar el motor de descargas
python main.py --update
```

## Estructura del Proyecto

```text
├── .github/workflows/
│   └── ci.yml               # Pruebas automáticas en GitHub
├── src/
│   ├── __init__.py
│   ├── client.py            # Menú interactivo y opciones de terminal
│   ├── config.py            # Configuración de las descargas
│   ├── downloader.py        # Motor de descarga en paralelo
│   ├── file_dir.py          # Manejo de carpetas, archivos ZIP y listas .m3u
│   ├── history.py           # Control de canciones ya descargadas
│   ├── postprocessor.py     # Añade carátulas y datos a las canciones
│   ├── server.py            # Servidor local para enviar al móvil con QR
│   └── spotify_resolver.py  # Busca canciones de Spotify en YouTube
├── tests/
│   └── test_core.py         # Pruebas del funcionamiento
├── .gitignore
├── main.py                  # Archivo principal para ejecutar
├── requirements.txt
└── README.md
```

## Pruebas

Para comprobar que todo funciona bien:
```bash
python -m pytest -v
```

## Licencia

Distribuido bajo Licencia MIT. Consulta el archivo `LICENSE` para más información.
