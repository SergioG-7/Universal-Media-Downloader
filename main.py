import sys
import tempfile
from pathlib import Path

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table

from src.client import obtener_configuracion
from src.downloader import MediaDownloader
from src.file_dir import (
    empaquetar_en_zip,
    generar_playlist_m3u,
    mover_archivos_a_destino,
)
from src.server import servir_archivo_y_mostrar_qr

console = Console()


def mostrar_tabla_resumen(descargados: list[Path], fallidos: list[dict], formato: str, calidad: str) -> None:
    tabla = Table(title="Resumen de Descargas", border_style="cyan")
    tabla.add_column("Item", justify="left", style="white")
    tabla.add_column("Formato / Calidad", justify="center", style="cyan")
    tabla.add_column("Estado", justify="center")

    for f in descargados:
        tabla.add_row(f.name, f"{formato.upper()} ({calidad})", "[bold green]EXITO[/bold green]")

    for f in fallidos:
        tabla.add_row(f["titulo"], f"{formato.upper()} ({calidad})", f"[bold yellow]{f['razon']}[/bold yellow]")

    console.print(tabla)


def main() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = obtener_configuracion(temp_path)

        downloader = MediaDownloader(config)

        with console.status("[bold green]Analizando enlace y obteniendo metadatos...", spinner="dots"):
            entries, error = downloader.extraer_info()

        if error:
            console.print(f"[bold red][-] Error:[/bold red] {error}")
            sys.exit(1)

        total = len(entries)
        console.print(f"\n[bold cyan][*] Se detectaron {total} elementos. Descargando con {config.max_workers} hilos...[/bold cyan]\n")

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        )

        tasks_map = {}
        with progress:
            for idx, entry in enumerate(entries, start=1):
                if entry.get("is_spotify"):
                    meta = entry["spotify_meta"]
                    titulo = f"{meta['artist']} - {meta['title']}"
                else:
                    titulo = entry.get("title", f"Pista #{idx}")

                nombre_corto = (titulo[:35] + "..") if len(titulo) > 37 else titulo
                task_id = progress.add_task(f"[dim]Esperando: {nombre_corto}", total=100)
                tasks_map[idx] = task_id

            descargados, fallidos = downloader.ejecutar_pool(entries, progress, tasks_map)

        console.print("")
        mostrar_tabla_resumen(descargados, fallidos, config.formato, config.calidad)

        if not descargados:
            console.print("[yellow][-] No se descargo ningun archivo nuevo (pueden ser duplicados u omitidos).[/yellow]")
            return

        # Generar archivo de playlist m3u si hay mas de un tema
        archivo_m3u = None
        if len(descargados) > 1:
            archivo_m3u = generar_playlist_m3u(descargados, temp_path)

        if config.modo_salida == "movil":
            if len(descargados) > 1:
                zip_temp = temp_path / "descargas_movil.zip"
                archivo_a_servir = empaquetar_en_zip(descargados, zip_temp, archivo_m3u)
            else:
                archivo_a_servir = descargados[0]

            if archivo_a_servir and archivo_a_servir.exists():
                servir_archivo_y_mostrar_qr(archivo_a_servir)
                console.print("[green][*] Archivos temporales eliminados del PC.[/green]")

        elif config.modo_salida == "zip" and config.ruta_destino:
            zip_path = empaquetar_en_zip(descargados, config.ruta_destino, archivo_m3u)
            if zip_path:
                console.print(f"\n[bold green][+] Archivo ZIP guardado en:[/bold green] {zip_path}")

        elif config.modo_salida == "carpeta" and config.ruta_destino:
            mover_archivos_a_destino(descargados, config.ruta_destino, archivo_m3u)
            console.print(f"\n[bold green][+] Archivos guardados en:[/bold green] {config.ruta_destino}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Ejecucion interrumpida por el usuario.[/yellow]")
        sys.exit(0)