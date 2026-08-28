import argparse
import sys
from pathlib import Path
from typing import Tuple

from src.config import DownloadConfig


def solicitar_datos_interactivos() -> Tuple[str, str, str, str, int]:
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

    print("\nDestino de los archivos:")
    print("1) Guardar en PC (archivo ZIP)")
    print("2) Guardar en PC (carpeta suelta)")
    print("3) Descargar directo al movil via QR (no guarda nada en PC)")
    opc_destino = input("Opcion [1/2/3] (Default: 1): ").strip()

    mapa_destino = {"1": "zip", "2": "carpeta", "3": "movil"}
    modo_salida = mapa_destino.get(opc_destino, "zip")

    return url, formato, calidad, modo_salida, 4


def obtener_configuracion(temp_dir: Path) -> DownloadConfig:
    parser = argparse.ArgumentParser(
        description="Downloader concurrente de YouTube a MP3/MP4 con streaming QR al movil."
    )
    parser.add_argument("-u", "--url", type=str, help="URL del video o playlist.")
    parser.add_argument("-f", "--format", choices=["mp3", "mp4"], help="Formato de salida.")
    parser.add_argument("-q", "--quality", type=str, help="Calidad (Audio: 128k, 192k, 320k | Video: best, 1080p, 720p, 480p).")
    parser.add_argument("-o", "--output", type=str, default="descargas", help="Ruta/nombre base de salida.")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Numero de descargas paralelas (Default: 4).")
    parser.add_argument("--qr", action="store_true", help="Modo movil: Sirve por QR y no guarda en PC.")
    parser.add_argument("--no-zip", action="store_true", help="Guardar en carpeta sin comprimir.")

    args = parser.parse_args()

    if args.url:
        url = args.url
        formato = args.format or "mp3"
        if formato == "mp3":
            calidad = args.quality if args.quality in ["128k", "192k", "320k"] else "192k"
        else:
            calidad = args.quality if args.quality in ["best", "1080p", "720p", "480p"] else "best"

        if args.qr:
            modo_salida = "movil"
        elif args.no_zip:
            modo_salida = "carpeta"
        else:
            modo_salida = "zip"

        workers = args.workers
        nombre_salida = args.output
    else:
        try:
            url, formato, calidad, modo_salida, workers = solicitar_datos_interactivos()
            nombre_salida = "descargas"
        except KeyboardInterrupt:
            print("\nOperacion cancelada por el usuario.")
            sys.exit(0)

    ruta_destino = None
    if modo_salida == "zip":
        nombre_zip = nombre_salida if nombre_salida.endswith(".zip") else f"{nombre_salida}.zip"
        ruta_destino = Path(nombre_zip).resolve()
    elif modo_salida == "carpeta":
        ruta_destino = Path(nombre_salida).resolve()

    return DownloadConfig(
        url=url,
        formato=formato,
        calidad=calidad,
        directorio_salida=temp_dir,
        modo_salida=modo_salida,
        ruta_destino=ruta_destino,
        max_workers=workers,
    )