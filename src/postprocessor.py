from pathlib import Path
from typing import Any, Dict
from urllib.request import urlopen

import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3


def incrustar_metadatos_mp3(
    archivo_mp3: Path,
    info_yt: Dict[str, Any],
    ruta_miniatura: Path | None = None,
    meta_spotify: Dict[str, Any] | None = None,
) -> None:
    # Si existen metadatos de Spotify se usan de forma prioritaria
    if meta_spotify:
        titulo = meta_spotify.get("title")
        artista = meta_spotify.get("artist")
        album = meta_spotify.get("album")
        fecha = meta_spotify.get("release_date")
    else:
        titulo = info_yt.get("title")
        artista = info_yt.get("uploader") or info_yt.get("channel")
        album = None
        fecha = info_yt.get("upload_date")

    try:
        audio = EasyID3(str(archivo_mp3))
    except mutagen.id3.ID3NoHeaderError:
        audio = mutagen.File(str(archivo_mp3), easy=True)
        audio.add_tags()

    if titulo:
        audio["title"] = str(titulo)
    if artista:
        audio["artist"] = str(artista)
    if album:
        audio["album"] = str(album)
    if fecha and len(str(fecha)) >= 4:
        audio["date"] = str(fecha)[:4]

    audio.save()

    # Inyeccion de caratula (desde URL HD de Spotify o archivo local)
    data_imagen = None
    if meta_spotify and meta_spotify.get("cover_url"):
        try:
            with urlopen(meta_spotify["cover_url"]) as resp:
                data_imagen = resp.read()
        except Exception:
            pass

    if not data_imagen and ruta_miniatura and ruta_miniatura.exists():
        try:
            with open(ruta_miniatura, "rb") as f:
                data_imagen = f.read()
        except Exception:
            pass

    if data_imagen:
        try:
            audio_raw = ID3(str(archivo_mp3))
            audio_raw.add(
                APIC(
                    encoding=3,
                    mime="image/jpeg",
                    type=3,
                    desc="Cover",
                    data=data_imagen,
                )
            )
            audio_raw.save()
        except Exception:
            pass