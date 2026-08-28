import sys
import tempfile
from pathlib import Path

from core.downloader import MediaDownloader
from utils.cli import obtener_configuracion
from utils.file_ops import empaquetar_en_zip, mover_archivos_a_destino


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = obtener_configuracion(temp_path)

        downloader = MediaDownloader(config)

        print("\n[*] Obteniendo metadatos...")
        entries, error = downloader.extraer_info()
        if error:
            print(f"[-] Error: {error}")
            sys.exit(1)

        descargados, fallidos = downloader.ejecutar_pool(entries)

        print("\n" + "=" * 50)
        print("RESUMEN DE LA OPERACION")
        print("=" * 50)

        if descargados:
            print(f"[+] Completados: {len(descargados)} archivo(s).")
            if config.empaquetar_zip and config.ruta_zip:
                zip_path = empaquetar_en_zip(descargados, config.ruta_zip)
                if zip_path:
                    print(f"[+] Archivo ZIP generado en: {zip_path}")
            else:
                destino = Path("descargas").resolve()
                mover_archivos_a_destino(descargados, destino)
                print(f"[+] Archivos guardados en: {destino}")
        else:
            print("[-] No se pudo procesar ningun archivo.")

        if fallidos:
            print(f"\n[!] Fallos ({len(fallidos)}):")
            for f in fallidos:
                print(f"  - {f['titulo']}: {f['razon']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nEjecucion interrumpida por el usuario.")
        sys.exit(0)