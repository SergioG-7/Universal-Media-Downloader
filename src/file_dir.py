import zipfile
from pathlib import Path
from typing import List, Optional


def generar_playlist_m3u(archivos: List[Path], directorio_destino: Path, nombre_lista: str = "playlist.m3u") -> Path:
    # Genera un archivo de lista de reproduccion m3u compatible con Android y reproductores de PC
    ruta_m3u = directorio_destino / nombre_lista
    lineas = ["#EXTM3U\n"]
    for archivo in archivos:
        lineas.append(f"{archivo.name}\n")

    with open(ruta_m3u, "w", encoding="utf-8") as f:
        f.writelines(lineas)

    return ruta_m3u


def empaquetar_en_zip(archivos: List[Path], ruta_zip_salida: Path, archivo_m3u: Path | None = None) -> Optional[Path]:
    if not archivos:
        return None

    todos_los_archivos = list(archivos)
    if archivo_m3u and archivo_m3u.exists():
        todos_los_archivos.append(archivo_m3u)

    print(f"\n[*] Empaquetando {len(todos_los_archivos)} archivo(s) en '{ruta_zip_salida.name}'...")
    with zipfile.ZipFile(ruta_zip_salida, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for archivo in todos_los_archivos:
            if archivo.exists():
                zip_info = zipfile.ZipInfo(archivo.name)
                zip_info.compress_type = zipfile.ZIP_DEFLATED
                zip_info.flag_bits |= 0x800
                with open(archivo, "rb") as f_in:
                    zipf.writestr(zip_info, f_in.read())

    return ruta_zip_salida


def mover_archivos_a_destino(archivos: List[Path], destino: Path, archivo_m3u: Path | None = None) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    todos_los_archivos = list(archivos)
    if archivo_m3u and archivo_m3u.exists():
        todos_los_archivos.append(archivo_m3u)

    print(f"\n[*] Moviendo {len(todos_los_archivos)} archivo(s) al directorio final: {destino}")
    for archivo in todos_los_archivos:
        if archivo.exists():
            destino_final = destino / archivo.name
            if destino_final.exists():
                destino_final.unlink()
            archivo.rename(destino_final)