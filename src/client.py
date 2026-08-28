import argparse
import sys
from pathlib import Path
from typing import Tuple

from core.config import DownloadConfig


def solicitar_datos_interactivos() -> Tuple[str, str, str, bool, int]:
    url = input("Ingresa el enlace de YouTube (video o playlist): ").strip()
    if not url:
        print("Error: El enlace no puede estar vacio.")
        sys.exit(1)

    print("\nSelecciona el formato:")
    print("1) Audio MP3")
    print("2) Video MP4")
    opc_formato = input("Opcion [1/2] (Default: 1): ").strip()

    if opc_formato == "2":
        formato = "mp4"
        print("\nSelecciona la resolucion:")
        print("1) Mejor disponible (best)")
        print("2) 1080p")
        print("3) 720p")
        print("4) 480p")
        opc_cal = input("Opcion [1-4] (Default: 1): ").strip()
        calidades = {"1": "best", "2": "1080p", "3": "720p", "4": "480p"}
        calidad = calidades.get(opc_cal, "best")
    else:
        formato = "mp3"
        print("\nSelecciona el bitrate:")
        print("1) 320 kbps (Alta calidad)")
        print("2) 192 kbps (Estandar)")
        print("3) 128 kbps (Ligero)")
        opc_cal = input("Opcion [1-3] (Default: 2): ").strip()
        calidades = {"1": "320k", "2": "192k", "3": "128k"}
        calidad = calidades.get(opc_cal, "192k")

    print("\nAlmacenamiento de salida:")
    print("1) Comprimir todo en un ZIP")
    print("2) Guardar en una carpeta")
    opc_zip = input("Opcion [1/2] (Default: 1): ").strip()
    empaquetar_zip = opc_zip != "2"

    return url, formato, calidad, empaquetar_zip, 4


def obtener_configuracion(temp_dir: Path) -> DownloadConfig:
    parser = argparse.ArgumentParser(
        description="Downloader concurrente de YouTube a MP3/MP4 con inyeccion de metadatos."
    )
    parser.add_argument("-u", "--url", type=str, help="URL del video o playlist.")
    parser.add_argument("-f", "--format", choices=["mp3", "mp4"], help="Formato de salida.")
    parser.add_argument("-q", "--quality", type=str, help="Calidad (Audio: 128k, 192k, 320k | Video: best, 1080p, 720p, 480p).")
    parser.add_argument("-o", "--output", type=str, default="descargas", help="Ruta/nombre base de salida.")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Numero de descargas paralelas (Default: 4).")
    parser.add_argument("--no-zip", action="store_true", help="Guardar en carpeta sin comprimir en ZIP.")

    args = parser.parse_args()

    if args.url:
        url = args.url
        formato = args.format or "mp3"
        if formato == "mp3":
            calidad = args.quality if args.quality in ["128k", "192k", "320k"] else "192k"
        else:
            calidad = args.quality if args.quality in ["best", "1080p", "720p", "480p"] else "best"
        empaquetar = not args.no_zip
        workers = args.workers
        nombre_salida = args.output
    else:
        try:
            url, formato, calidad, empaquetar, workers = solicitar_datos_interactivos()
            nombre_salida = "descargas"
        except KeyboardInterrupt:
            print("\nOperacion cancelada por el usuario.")
            sys.exit(0)

    ruta_salida = Path(nombre_salida).resolve()
    ruta_zip = None
    if empaquetar:
        nombre_zip = nombre_salida if nombre_salida.endswith(".zip") else f"{nombre_salida}.zip"
        ruta_zip = Path(nombre_zip).resolve()

    return DownloadConfig(
        url=url,
        formato=formato,
        calidad=calidad,
        directorio_salida=temp_dir,
        ruta_zip=ruta_zip,
        empaquetar_zip=empaquetar,
        max_workers=workers,
    )