from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import imageio_ffmpeg
import yt_dlp

from src.config import DownloadConfig
from src.history import cargar_historial, guardar_en_historial
from src.postprocessor import incrustar_metadatos_mp3
from src.spotify_resolver import (
    buscar_coincidencia_youtube,
    es_url_spotify,
    extraer_tracks_spotify,
)


class MediaDownloader:

    def __init__(self, config: DownloadConfig):
        self.config = config
        self.ruta_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        self.historial = cargar_historial()

    def _obtener_opciones_ydl(
        self, plantilla_salida: str, hook_progreso: Callable[[Dict[str, Any]], None] | None = None
    ) -> Dict[str, Any]:
        opciones: Dict[str, Any] = {
            "outtmpl": plantilla_salida,
            "ffmpeg_location": self.ruta_ffmpeg,
            "quiet": True,
            "no_warnings": True,
            "writethumbnail": self.config.formato == "mp3",
        }

        if hook_progreso:
            opciones["progress_hooks"] = [hook_progreso]

        if self.config.formato == "mp3":
            calidad_audio = self.config.calidad.replace("k", "")
            postprocessors: List[Dict[str, Any]] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": calidad_audio,
                }
            ]

            postprocessor_args = []
            if self.config.normalizar_audio:
                postprocessor_args.extend(["-af", "loudnorm=I=-16:TP=-1.5:LRA=11"])

            if postprocessor_args:
                opciones["postprocessor_args"] = postprocessor_args

            opciones.update({"format": "bestaudio/best", "postprocessors": postprocessors})
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
        if es_url_spotify(self.config.url):
            tracks_sp, err = extraer_tracks_spotify(self.config.url)
            if err:
                return [], err
            entries = [{"is_spotify": True, "spotify_meta": t} for t in tracks_sp]
            return entries, None

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
                return [], "No se encontro informacion del enlace provisto."
            entries = info.get("entries", [info])
            return [e for e in entries if e is not None], None
        except Exception as e:
            return [], str(e)

    def descargar_item(
        self,
        entry: Dict[str, Any],
        indice: int,
        progress_callback: Callable[[int, float, str], None] | None = None,
    ) -> Tuple[bool, str, Path | None, str]:
        meta_spotify = None

        if entry.get("is_spotify"):
            meta_spotify = entry["spotify_meta"]
            titulo = f"{meta_spotify['artist']} - {meta_spotify['title']}"
            track_id = f"{meta_spotify['artist']}_{meta_spotify['title']}".lower()

            # Verificacion de duplicado en historial
            if track_id in self.historial:
                if progress_callback:
                    progress_callback(indice, 100.0, "Omitido (Duplicado)")
                return False, titulo, None, "Omitido por estar registrado en el historial."

            video_url, err = buscar_coincidencia_youtube(meta_spotify)
            if not video_url or err:
                return False, titulo, None, err or "Sin coincidencia en YouTube."
        else:
            titulo = entry.get("title", f"Pista_{indice}")
            yt_id = entry.get("id") or ""
            track_id = yt_id if yt_id else titulo.lower()

            # Verificacion de duplicado en historial
            if track_id in self.historial:
                if progress_callback:
                    progress_callback(indice, 100.0, "Omitido (Duplicado)")
                return False, titulo, None, "Omitido por estar registrado en el historial."

            video_url = (
                entry.get("webpage_url")
                or entry.get("url")
                or f"https://www.youtube.com/watch?v={yt_id}"
            )

        plantilla = str(self.config.directorio_salida / "%(title)s.%(ext)s")
        ext_esperada = f".{self.config.formato}"

        def hook_ydl(data: Dict[str, Any]):
            if progress_callback and data.get("status") == "downloading":
                total_bytes = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
                descargados = data.get("downloaded_bytes", 0)
                if total_bytes > 0:
                    porcentaje = (descargados / total_bytes) * 100
                    velocidad = data.get("_speed_str", "")
                    progress_callback(indice, porcentaje, velocidad)

        opciones = self._obtener_opciones_ydl(plantilla, hook_ydl)

        try:
            with yt_dlp.YoutubeDL(opciones) as ydl:
                info_descarga = ydl.extract_info(video_url, download=True)
                if not info_descarga:
                    return False, titulo, None, "Fallo en la extraccion del archivo."

                base_name = ydl.prepare_filename(info_descarga)
                archivo_base = Path(base_name)
                archivo_final = archivo_base.with_suffix(ext_esperada)

                posibles_thumbs = [
                    archivo_base.with_suffix(".jpg"),
                    archivo_base.with_suffix(".webp"),
                    archivo_base.with_suffix(".png"),
                ]
                thumb_path = next((t for t in posibles_thumbs if t.exists()), None)

                if self.config.formato == "mp3" and archivo_final.exists():
                    incrustar_metadatos_mp3(
                        archivo_final,
                        info_descarga,
                        thumb_path,
                        meta_spotify=meta_spotify,
                    )

                for t in posibles_thumbs:
                    if t.exists():
                        try:
                            t.unlink()
                        except OSError:
                            pass

                if archivo_final.exists():
                    # Guardar registro en historial para no repetir
                    guardar_en_historial(track_id)
                    if progress_callback:
                        progress_callback(indice, 100.0, "Completado")
                    return True, titulo, archivo_final, ""
                return False, titulo, None, "No se genero el archivo de salida."

        except Exception as e:
            error_msg = str(e).split("\n")[0]
            return False, titulo, None, error_msg

    def ejecutar_pool(
        self,
        entries: List[Dict[str, Any]],
        progress_manager: Any = None,
        tasks_map: Dict[int, Any] | None = None,
    ) -> Tuple[List[Path], List[Dict[str, str]]]:
        descargados: List[Path] = []
        fallidos: List[Dict[str, str]] = []

        def update_progress(idx: int, percent: float, speed: str):
            if progress_manager and tasks_map and idx in tasks_map:
                task_id = tasks_map[idx]
                progress_manager.update(
                    task_id,
                    completed=percent,
                    description=f"[cyan]Item {idx} ({speed})",
                )

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futuros = [
                executor.submit(self.descargar_item, entry, idx, update_progress)
                for idx, entry in enumerate(entries, start=1)
            ]

            for futuro in as_completed(futuros):
                exito, titulo, ruta_archivo, razon = futuro.result()
                if exito and ruta_archivo:
                    descargados.append(ruta_archivo)
                else:
                    fallidos.append({"titulo": titulo, "razon": razon})

        return descargados, fallidos