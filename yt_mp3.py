# -*- coding: utf-8 -*-
import argparse
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import imageio_ffmpeg
import yt_dlp


def configurar_opciones_yt_dlp(
    directorio_salida: Path, ruta_ffmpeg: str
) -> Tuple[Dict, Dict]:
    # Genera los diccionarios de configuracion para extraccion y descarga.
    opciones_info = {
        "extract_flat": True,
        "ignoreerrors": True,
        "quiet": True,
        "no_warnings": True,
    }

    opciones_descarga = {
        "format": "bestaudio/best",
        "outtmpl": str(directorio_salida / "%(title)s_%(id)s.%(ext)s"),
        "ffmpeg_location": ruta_ffmpeg,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
    }

    return opciones_info, opciones_descarga


def descargar_y_convertir(
    url: str, directorio_salida: Path
) -> Tuple[List[Path], List[Dict[str, str]]]:
    # Descarga el audio de una URL/Playlist y lo convierte a MP3.
    ruta_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    opciones_info, opciones_descarga = configurar_opciones_yt_dlp(
        directorio_salida, ruta_ffmpeg
    )

    archivos_descargados: List[Path] = []
    archivos_fallidos: List[Dict[str, str]] = []

    print("[*] Analizando enlace y obteniendo metadatos...")
    try:
        with yt_dlp.YoutubeDL(opciones_info) as ydl:
            info = ydl.extract_info(url, download=False)

        if not info:
            return [], [
                {
                    "titulo": url,
                    "razon": "No se pudo obtener informacion del enlace provisto.",
                }
            ]

        entries = info.get("entries", [info])
    except Exception as e:
        return [], [{"titulo": url, "razon": f"Fallo al procesar el enlace: {str(e)}"}]

    total_elementos = len(entries)
    print(f"[*] Elementos detectados: {total_elementos}. Iniciando descargas...")

    with yt_dlp.YoutubeDL(opciones_descarga) as ydl_descarga:
        for idx, entry in enumerate(entries, start=1):
            if entry is None:
                archivos_fallidos.append(
                    {
                        "titulo": f"Pista #{idx}",
                        "razon": "Video no disponible, eliminado o con restriccion regional.",
                    }
                )
                continue

            titulo = entry.get("title", f"Pista #{idx}")
            video_url = (
                entry.get("webpage_url")
                or entry.get("url")
                or f"https://www.youtube.com/watch?v={entry.get('id', '')}"
            )

            print(f"[{idx}/{total_elementos}] Descargando: {titulo}")

            try:
                info_descarga = ydl_descarga.extract_info(
                    video_url, download=True
                )
                if info_descarga:
                    filename = Path(ydl_descarga.prepare_filename(info_descarga))
                    mp3_path = filename.with_suffix(".mp3")

                    if mp3_path.exists():
                        archivos_descargados.append(mp3_path)
                    else:
                        archivos_fallidos.append(
                            {
                                "titulo": titulo,
                                "razon": "Descarga finalizada pero no se genero el archivo MP3.",
                            }
                        )
            except Exception as e:
                error_sanitizado = str(e).split("\n")[0]
                archivos_fallidos.append(
                    {"titulo": titulo, "razon": error_sanitizado}
                )

    return archivos_descargados, archivos_fallidos


def empaquetar_en_zip(archivos: List[Path], ruta_zip_salida: Path) -> Optional[Path]:
    # Comprime los archivos procesados en el ZIP final.
    if not archivos:
        return None

    print(f"[*] Empaquetando {len(archivos)} canciones en '{ruta_zip_salida.name}'...")
    with zipfile.ZipFile(ruta_zip_salida, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for archivo in archivos:
            if archivo.exists():
                zipf.write(archivo, arcname=archivo.name)

    return ruta_zip_salida


def procesar_pipeline(url: str, salida_zip: str) -> None:
    # Ejecuta el pipeline completo bajo un contexto temporal seguro.
    ruta_zip_final = Path(salida_zip).resolve()

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        descargados, fallidos = descargar_y_convertir(url, temp_path)

        print("\n" + "=" * 50)
        print("RESUMEN DE LA OPERACION")
        print("=" * 50)

        if descargados:
            zip_generado = empaquetar_en_zip(descargados, ruta_zip_final)
            print(f"[+] EXITO: {len(descargados)} pistas procesadas correctamente.")
            if zip_generado:
                print(f"[+] Archivo ZIP guardado en: {zip_generado}")
        else:
            print("[-] AVISO: No se proceso ningun archivo de audio exitosamente.")

        if fallidos:
            print(f"\n[!] ADVERTENCIAS: {len(fallidos)} elemento(s) no descargado(s):")
            for fallo in fallidos:
                print(f"  - {fallo['titulo']}")
                print(f"    Razon: {fallo['razon']}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Descarga y empaqueta audio de YouTube (videos o playlists) a MP3 en un ZIP."
    )
    parser.add_argument(
        "-u", "--url", type=str, help="URL del video o lista de reproduccion."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="musica_descargada.zip",
        help="Nombre/Ruta del archivo ZIP de salida (Default: musica_descargada.zip).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    enlace_objetivo = args.url

    if not enlace_objetivo:
        try:
            enlace_objetivo = input("Ingresa el enlace de YouTube (video o playlist): ").strip()
        except KeyboardInterrupt:
            print("\nOperacion cancelada por el usuario.")
            sys.exit(0)

    if not enlace_objetivo:
        print("Error: No se proporciono ninguna URL.")
        sys.exit(1)

    procesar_pipeline(enlace_objetivo, args.output)