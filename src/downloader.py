from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Tuple

import imageio_ffmpeg
import yt_dlp

from src.config import DownloadConfig
from src.postprocessor import incrustar_metadatos_mp3


class MediaDownloader:

    def __init__(self, config: DownloadConfig):
        self.config = config
        self.ruta_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    def _obtener_opciones_ydl(self, plantilla_salida: str) -> Dict[str, Any]:
        opciones: Dict[str, Any] = {
            "outtmpl": plantilla_salida,
            "ffmpeg_location": self.ruta_ffmpeg,
            "quiet": True,
            "no_warnings": True,
            "writethumbnail": self.config.formato == "mp3",
        }

        if self.config.formato == "mp3":
            calidad_audio = self.config.calidad.replace("k", "")
            opciones.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": calidad_audio,
                        }
                    ],
                }
            )
        else:
            if self.config.calidad == "best":
                regla_formato = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            else:
                altura = self.config.calidad.replace("p", "")
                regla_formato = (
                    f"bestvideo[height<={altura}][ext=mp4]+bestaudio[ext=m4a]/"
                    f"best[height<={altura}][ext=mp4]/best"
                )
            opciones.update(
                {
                    "format": regla_formato,
                    "merge_output_format": "mp4",
                }
            )
        return opciones

    def extraer_info(self) -> Tuple[List[Dict[str, Any]], str | None]:
        opciones_info = {
            "extract_flat": True,
            "ignoreerrors": True,
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with yt_dlp.YoutubeDL(opciones_info) as ydl:
                info = ydl.extract_info(self.config.url, download=False)
            if not info:
                return [], "No se encontro informacion del enlace."
            entries = info.get("entries", [info])
            return [e for e in entries if e is not None], None
        except Exception as e:
            return [], str(e)

    def descargar_item(self, entry: Dict[str, Any], indice: int, total: int) -> Tuple[bool, str, Path | None, str]:
        titulo = entry.get("title", f"Pista_{indice}")
        video_url = (
            entry.get("webpage_url")
            or entry.get("url")
            or f"https://www.youtube.com/watch?v={entry.get('id', '')}"
        )

        plantilla = str(self.config.directorio_salida / "%(title)s.%(ext)s")
        opciones = self._obtener_opciones_ydl(plantilla)
        ext_esperada = f".{self.config.formato}"

        print(f"[*] [{indice}/{total}] Iniciando descarga: {titulo}")

        try:
            with yt_dlp.YoutubeDL(opciones) as ydl:
                info_descarga = ydl.extract_info(video_url, download=True)
                if not info_descarga:
                    return False, titulo, None, "No se pudo descargar el medio."

                base_name = ydl.prepare_filename(info_descarga)
                archivo_base = Path(base_name)
                archivo_final = archivo_base.with_suffix(ext_esperada)

                # Busca miniatura descargada por yt-dlp para postprocesar
                posibles_thumbs = [
                    archivo_base.with_suffix(".jpg"),
                    archivo_base.with_suffix(".webp"),
                    archivo_base.with_suffix(".png"),
                ]
                thumb_path = next((t for t in posibles_thumbs if t.exists()), None)

                if self.config.formato == "mp3" and archivo_final.exists():
                    incrustar_metadatos_mp3(archivo_final, info_descarga, thumb_path)

                # Elimina miniaturas temporales residuales
                for t in posibles_thumbs:
                    if t.exists():
                        try:
                            t.unlink()
                        except OSError:
                            pass

                if archivo_final.exists():
                    print(f"[+] [{indice}/{total}] Completado: {titulo}")
                    return True, titulo, archivo_final, ""
                return False, titulo, None, "No se genero el archivo de salida esperado."

        except Exception as e:
            error_msg = str(e).split("\n")[0]
            print(f"[-] [{indice}/{total}] Error en: {titulo} -> {error_msg}")
            return False, titulo, None, error_msg

    def ejecutar_pool(self, entries: List[Dict[str, Any]]) -> Tuple[List[Path], List[Dict[str, str]]]:
        descargados: List[Path] = []
        fallidos: List[Dict[str, str]] = []
        total = len(entries)

        print(f"[*] Procesando {total} elementos con {self.config.max_workers} hilos concurrentes...\n")

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futuros = [
                executor.submit(self.descargar_item, entry, idx, total)
                for idx, entry in enumerate(entries, start=1)
            ]

            for futuro in as_completed(futuros):
                exito, titulo, ruta_archivo, razon = futuro.result()
                if exito and ruta_archivo:
                    descargados.append(ruta_archivo)
                else:
                    fallidos.append({"titulo": titulo, "razon": razon})

        return descargados, fallidos