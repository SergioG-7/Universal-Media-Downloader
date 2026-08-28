from pathlib import Path
from typing import Any, Dict

import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3


def incrustar_metadatos_mp3(archivo_mp3: Path, info: Dict[str, Any], ruta_miniatura: Path | None) -> None:
    # Agrega etiquetas basicas ID3 (titulo, artista, ano)
    try:
        audio = EasyID3(str(archivo_mp3))
    except mutagen.id3.ID3NoHeaderError:
        audio = mutagen.File(str(archivo_mp3), easy=True)
        audio.add_tags()

    if info.get("title"):
        audio["title"] = str(info["title"])
    if info.get("uploader") or info.get("channel"):
        audio["artist"] = str(info.get("uploader") or info.get("channel"))
    if info.get("upload_date") and len(info["upload_date"]) >= 4:
        audio["date"] = info["upload_date"][:4]

    audio.save()

    # Si existe miniatura, se incrusta la portada en el archivo MP3
    if ruta_miniatura and ruta_miniatura.exists():
        try:
            audio_raw = ID3(str(archivo_mp3))
            with open(ruta_miniatura, "rb") as albumart:
                audio_raw.add(
                    APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3,
                        desc="Cover",
                        data=albumart.read(),
                    )
                )
            audio_raw.save()
        except Exception:
            pass