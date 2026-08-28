import sys
import tempfile
from pathlib import Path

from src.client import obtener_configuracion
from src.downloader import MediaDownloader
from src.file_dir import empaquetar_en_zip, mover_archivos_a_destino
from src.server import servir_archivo_y_mostrar_qr


def main() -> None:
    # Contexto temporal seguro: se destruye automaticamente al salir
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

        if not descargados:
            print("[-] No se pudo procesar ningun archivo.")
            if fallidos:
                print(f"\n[!] Fallos ({len(fallidos)}):")
                for f in fallidos:
                    print(f"  - {f['titulo']}: {f['razon']}")
            return

        print(f"[+] Completados: {len(descargados)} archivo(s).")

        # Flujo segun la opcion seleccionada
        if config.modo_salida == "movil":
            # Si es mas de un archivo, se empaqueta en zip temporal para pasarlo todo junto
            if len(descargados) > 1:
                zip_temporal = temp_path / "descargas_movil.zip"
                archivo_a_servir = empaquetar_en_zip(descargados, zip_temporal)
            else:
                archivo_a_servir = descargados[0]

            if archivo_a_servir and archivo_a_servir.exists():
                servir_archivo_y_mostrar_qr(archivo_a_servir)
                print("[*] Archivos temporales eliminados del PC correctamente.")

        elif config.modo_salida == "zip" and config.ruta_destino:
            zip_path = empaquetar_en_zip(descargados, config.ruta_destino)
            if zip_path:
                print(f"[+] Archivo ZIP guardado en PC: {zip_path}")

        elif config.modo_salida == "carpeta" and config.ruta_destino:
            mover_archivos_a_destino(descargados, config.ruta_destino)
            print(f"[+] Archivos guardados en carpeta de PC: {config.ruta_destino}")

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