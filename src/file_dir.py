import zipfile
from pathlib import Path
from typing import List, Optional


def empaquetar_en_zip(archivos: List[Path], ruta_zip_salida: Path) -> Optional[Path]:
    if not archivos:
        return None

    print(f"\n[*] Empaquetando {len(archivos)} archivo(s) en '{ruta_zip_salida.name}'...")
    with zipfile.ZipFile(ruta_zip_salida, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for archivo in archivos:
            if archivo.exists():
                zipf.write(archivo, arcname=archivo.name)

    return ruta_zip_salida


def mover_archivos_a_destino(archivos: List[Path], destino: Path) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    print(f"\n[*] Moviendo {len(archivos)} archivo(s) al directorio final: {destino}")
    for archivo in archivos:
        if archivo.exists():
            destino_final = destino / archivo.name
            if destino_final.exists():
                destino_final.unlink()
            archivo.rename(destino_final)