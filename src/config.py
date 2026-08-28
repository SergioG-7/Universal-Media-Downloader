from dataclasses import dataclass
from pathlib import Path

@dataclass
class DownloadConfig:
    url: str
    formato: str
    calidad: str
    directorio_salida: Path
    modo_salida: str  # "zip", "carpeta", "movil"
    ruta_destino: Path | None
    max_workers: int = 4