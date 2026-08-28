from pathlib import Path
import json

from src.config import DownloadConfig
from src.file_dir import empaquetar_en_zip, generar_playlist_m3u
from src.history import cargar_historial, guardar_en_historial
from src.server import obtener_ip_local
from src.spotify_resolver import extraer_id_y_tipo, es_url_spotify


def test_es_url_spotify():
    assert es_url_spotify("https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT") is True
    assert es_url_spotify("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is False


def test_extraer_id_y_tipo_spotify():
    tipo, id_sp = extraer_id_y_tipo("https://open.spotify.com/intl-es/track/4cOdK2wGLETKBW3PvgPWqT?si=abc")
    assert tipo == "track"
    assert id_sp == "4cOdK2wGLETKBW3PvgPWqT"


def test_generar_playlist_m3u(tmp_path: Path):
    archivo1 = tmp_path / "tema1.mp3"
    archivo2 = tmp_path / "tema2.mp3"
    archivo1.write_text("dummy audio 1")
    archivo2.write_text("dummy audio 2")

    ruta_m3u = generar_playlist_m3u([archivo1, archivo2], tmp_path)
    assert ruta_m3u.exists()

    contenido = ruta_m3u.read_text(encoding="utf-8")
    assert "#EXTM3U" in contenido
    assert "tema1.mp3" in contenido
    assert "tema2.mp3" in contenido


def test_empaquetar_en_zip_utf8(tmp_path: Path):
    # Prueba soporte de caracteres internacionales dentro del ZIP
    archivo_japones = tmp_path / "日本語の曲.mp3"
    archivo_japones.write_bytes(b"dummy japanese content")

    ruta_zip = tmp_path / "salida.zip"
    resultado = empaquetar_en_zip([archivo_japones], ruta_zip)

    assert resultado is not None
    assert resultado.exists()
    assert resultado.stat().st_size > 0


def test_obtener_ip_local():
    ip = obtener_ip_local()
    assert isinstance(ip, str)
    assert len(ip.split(".")) == 4