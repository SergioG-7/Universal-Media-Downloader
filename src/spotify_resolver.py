import base64
import json
import re
from typing import Any, Dict, List, Tuple
from urllib.request import Request, urlopen
import yt_dlp


def es_url_spotify(url: str) -> bool:
    return "spotify.com" in url.lower()


def extraer_id_y_tipo(url: str) -> Tuple[str | None, str | None]:
    # Extrae el tipo (track, album, playlist) y el identificador de Spotify
    patron = r"spotify\.com/(?:intl-[a-zA-Z]+/)?(track|album|playlist)/([a-zA-Z0-9]+)"
    match = re.search(patron, url)
    if match:
        return match.group(1), match.group(2)
    return None, None


def _obtener_html_embed(tipo: str, id_spotify: str) -> str | None:
    # Consulta la pagina de embed publica que no requiere autenticacion
    url_embed = f"https://open.spotify.com/embed/{tipo}/{id_spotify}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    try:
        req = Request(url_embed, headers=headers)
        with urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return None


def _extraer_payload_json(html: str) -> Dict[str, Any] | None:
    # Intenta extraer la carga util JSON incrustada en la pagina
    match_next = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if match_next:
        try:
            return json.loads(match_next.group(1))
        except Exception:
            pass

    match_init = re.search(r'<script id="initial-state"[^>]*>(.*?)</script>', html, re.DOTALL)
    if match_init:
        raw = match_init.group(1).strip()
        try:
            decoded = base64.b64decode(raw).decode("utf-8")
            return json.loads(decoded)
        except Exception:
            try:
                return json.loads(raw)
            except Exception:
                pass
    return None


def _extraer_oembed_fallback(url: str) -> List[Dict[str, Any]]:
    # Respaldo mediante endpoint oEmbed oficial de Spotify
    try:
        url_limpia = url.split("?")[0]
        oembed_url = f"https://open.spotify.com/oembed?url={url_limpia}"
        req = Request(oembed_url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        titulo_completo = data.get("title", "")
        thumbnail = data.get("thumbnail_url", "")
        autor = data.get("author_name", "")

        if autor and autor.lower() != "spotify":
            artista = autor
            titulo = titulo_completo
        elif " - " in titulo_completo:
            partes = titulo_completo.split(" - ", 1)
            artista = partes[0].strip()
            titulo = partes[1].strip()
        else:
            artista = "Unknown Artist"
            titulo = titulo_completo

        return [
            {
                "title": titulo,
                "artist": artista,
                "album": "Spotify Single",
                "release_date": "",
                "duration_sec": 0,
                "cover_url": thumbnail,
            }
        ]
    except Exception:
        return []


def extraer_tracks_spotify(url: str) -> Tuple[List[Dict[str, Any]], str | None]:
    tipo, id_spotify = extraer_id_y_tipo(url)
    if not tipo or not id_spotify:
        return [], "No se pudo identificar el tipo de enlace de Spotify (track, album o playlist)."

    html = _obtener_html_embed(tipo, id_spotify)
    if not html:
        # Si falla el embed HTML, intenta fallback de oEmbed si es un track
        fallback = _extraer_oembed_fallback(url)
        if fallback:
            return fallback, None
        return [], "No se pudo conectar con el servidor publico de Spotify."

    payload = _extraer_payload_json(html)
    if not payload:
        fallback = _extraer_oembed_fallback(url)
        if fallback:
            return fallback, None
        return [], "No se pudo interpretar la estructura de la pagina de Spotify."

    tracks_data: List[Dict[str, Any]] = []

    try:
        # Navegacion dinamica sobre la estructura de props de Next.js
        props = payload.get("props", {}).get("pageProps", {})
        entity = props.get("state", {}).get("data", {}).get("entity", {}) or props.get("entity", {})

        if tipo == "track":
            titulo = entity.get("name") or entity.get("title")
            artistas = ", ".join([a.get("name", "") for a in entity.get("artists", [])])
            if not artistas and entity.get("artist"):
                artistas = entity.get("artist")

            album_name = entity.get("album", {}).get("name", "Spotify Single")
            cover_url = ""
            images = entity.get("images") or entity.get("album", {}).get("images", [])
            if images and isinstance(images, list):
                cover_url = images[0].get("url", "")

            dur_ms = entity.get("duration", 0) or entity.get("duration_ms", 0)

            if titulo:
                tracks_data.append(
                    {
                        "title": titulo,
                        "artist": artistas or "Unknown Artist",
                        "album": album_name,
                        "release_date": entity.get("releaseDate", {}).get("isoString", "")[:4],
                        "duration_sec": int(dur_ms / 1000) if dur_ms else 0,
                        "cover_url": cover_url,
                    }
                )

        elif tipo in ["album", "playlist"]:
            album_name = entity.get("name") or entity.get("title", "Spotify Collection")
            cover_url = ""
            images = entity.get("images", [])
            if images and isinstance(images, list):
                cover_url = images[0].get("url", "")

            track_list = entity.get("trackList", []) or entity.get("tracks", {}).get("items", [])

            for item in track_list:
                t_nombre = item.get("title") or item.get("name")
                t_artista = item.get("subtitle") or ", ".join([a.get("name", "") for a in item.get("artists", [])])
                t_dur_ms = item.get("duration", 0) or item.get("duration_ms", 0)

                if t_nombre:
                    tracks_data.append(
                        {
                            "title": t_nombre,
                            "artist": t_artista or "Unknown Artist",
                            "album": album_name,
                            "release_date": "",
                            "duration_sec": int(t_dur_ms / 1000) if t_dur_ms else 0,
                            "cover_url": cover_url,
                        }
                    )

        if not tracks_data:
            fallback = _extraer_oembed_fallback(url)
            if fallback:
                return fallback, None
            return [], "No se encontraron pistas legibles en el enlace de Spotify."

        return tracks_data, None

    except Exception as e:
        fallback = _extraer_oembed_fallback(url)
        if fallback:
            return fallback, None
        return [], f"Error procesando metadatos de Spotify: {str(e)}"


def buscar_coincidencia_youtube(track_info: Dict[str, Any]) -> Tuple[str | None, str | None]:
    query = f"ytsearch5:{track_info['artist']} - {track_info['title']} official audio"
    duracion_objetivo = track_info.get("duration_sec", 0)

    opciones = {
        "extract_flat": True,
        "ignoreerrors": True,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            res = ydl.extract_info(query, download=False)
            if not res or not res.get("entries"):
                return None, "No se obtuvieron resultados en YouTube."

            entries = [e for e in res["entries"] if e]
            if not entries:
                return None, "No se encontraron videos disponibles."

            # Prioriza coincidencias dentro del rango de duracion (+/- 15 segs)
            if duracion_objetivo > 0:
                for entry in entries:
                    dur_yt = entry.get("duration")
                    if dur_yt and abs(dur_yt - duracion_objetivo) <= 15:
                        url_match = entry.get("webpage_url") or f"https://www.youtube.com/watch?v={entry.get('id')}"
                        return url_match, None

            # Fallback al primer resultado
            primer_entry = entries[0]
            url_match = primer_entry.get("webpage_url") or f"https://www.youtube.com/watch?v={primer_entry.get('id')}"
            return url_match, None

    except Exception as e:
        return None, f"Error durante la busqueda en YouTube: {str(e)}"