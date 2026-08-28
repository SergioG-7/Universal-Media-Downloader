import argparse
import sys
from pathlib import Path
from typing import Tuple

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from src.config import DownloadConfig

console = Console()


def solicitar_datos_interactivos() -> Tuple[str, str, str, str, bool, int]:
    console.print(
        Panel.fit(
            "[bold cyan]Media Downloader Pro (YouTube & Spotify)[/bold cyan]\n"
            "[dim]Audio/Video concurrente con metadatos oficiales y QR local[/dim]",
            border_style="cyan",
        )
    )

    url = Prompt.ask("[bold yellow]Ingresa el enlace (YouTube o Spotify)[/bold yellow]").strip()
    if not url:
        console.print("[red]Error: El enlace no puede estar vacio.[/red]")
        sys.exit(1)

    console.print("\n[bold]Formato de salida:[/bold]")
    console.print("  [cyan]1)[/cyan] Audio MP3")
    console.print("  [cyan]2)[/cyan] Video MP4")
    opc_formato = Prompt.ask("Selecciona formato", choices=["1", "2"], default="1")

    normalizar = False
    if opc_formato == "2":
        formato = "mp4"
        console.print("\n[bold]Resolucion de video:[/bold]")
        console.print("  [cyan]1)[/cyan] Mejor disponible (best)\n  [cyan]2)[/cyan] 1080p\n  [cyan]3)[/cyan] 720p\n  [cyan]4)[/cyan] 480p")
        opc_cal = Prompt.ask("Selecciona calidad", choices=["1", "2", "3", "4"], default="1")
        calidades = {"1": "best", "2": "1080p", "3": "720p", "4": "480p"}
        calidad = calidades.get(opc_cal, "best")
    else:
        formato = "mp3"
        console.print("\n[bold]Bitrate de audio:[/bold]")
        console.print("  [cyan]1)[/cyan] 320 kbps (Alta fidelidad)\n  [cyan]2)[/cyan] 192 kbps (Estandar)\n  [cyan]3)[/cyan] 128 kbps (Ligero)")
        opc_cal = Prompt.ask("Selecciona calidad", choices=["1", "2", "3"], default="2")
        calidades = {"1": "320k", "2": "192k", "3": "128k"}
        calidad = calidades.get(opc_cal, "192k")

        opc_norm = Prompt.ask("\nDeseas normalizar el volumen del audio (EBU R128)?", choices=["s", "n"], default="s")
        normalizar = opc_norm.lower() == "s"

    console.print("\n[bold]Destino de los archivos:[/bold]")
    console.print("  [cyan]1)[/cyan] Guardar en PC (archivo ZIP)")
    console.print("  [cyan]2)[/cyan] Guardar en PC (carpeta suelta)")
    console.print("  [cyan]3)[/cyan] Descargar directo al movil via QR (cero residuos en PC)")
    opc_destino = Prompt.ask("Selecciona destino", choices=["1", "2", "3"], default="1")

    mapa_destino = {"1": "zip", "2": "carpeta", "3": "movil"}
    modo_salida = mapa_destino.get(opc_destino, "zip")

    return url, formato, calidad, modo_salida, normalizar, 4


def obtener_configuracion(temp_dir: Path) -> DownloadConfig:
    parser = argparse.ArgumentParser(
        description="Downloader concurrente de YouTube y Spotify con interfaz Rich, normalizacion y QR."
    )
    parser.add_argument("-u", "--url", type=str, help="URL de YouTube o Spotify.")
    parser.add_argument("-f", "--format", choices=["mp3", "mp4"], help="Formato de salida.")
    parser.add_argument("-q", "--quality", type=str, help="Calidad de audio o video.")
    parser.add_argument("-o", "--output", type=str, default="descargas", help="Ruta de salida.")
    parser.add_argument("-w", "--workers", type=int, default=4, help="Descargas paralelas.")
    parser.add_argument("--normalize", action="store_true", help="Normaliza volumen de audio EBU R128.")
    parser.add_argument("--qr", action="store_true", help="Modo movil via QR.")
    parser.add_argument("--no-zip", action="store_true", help="Guardar en carpeta sin comprimir.")

    args = parser.parse_args()

    if args.url:
        url = args.url
        formato = args.format or "mp3"
        if formato == "mp3":
            calidad = args.quality if args.quality in ["128k", "192k", "320k"] else "192k"
        else:
            calidad = args.quality if args.quality in ["best", "1080p", "720p", "480p"] else "best"

        if args.qr:
            modo_salida = "movil"
        elif args.no_zip:
            modo_salida = "carpeta"
        else:
            modo_salida = "zip"

        normalizar = args.normalize
        workers = args.workers
        nombre_salida = args.output
    else:
        try:
            url, formato, calidad, modo_salida, normalizar, workers = solicitar_datos_interactivos()
            nombre_salida = "descargas"
        except KeyboardInterrupt:
            console.print("\n[yellow]Operacion cancelada por el usuario.[/yellow]")
            sys.exit(0)

    ruta_destino = None
    if modo_salida == "zip":
        nombre_zip = nombre_salida if nombre_salida.endswith(".zip") else f"{nombre_salida}.zip"
        ruta_destino = Path(nombre_zip).resolve()
    elif modo_salida == "carpeta":
        ruta_destino = Path(nombre_salida).resolve()

    return DownloadConfig(
        url=url,
        formato=formato,
        calidad=calidad,
        directorio_salida=temp_dir,
        modo_salida=modo_salida,
        ruta_destino=ruta_destino,
        normalizar_audio=normalizar,
        max_workers=workers,
    )