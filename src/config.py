from dataclasses import dataclass
from pathlib import Path


@dataclass
class DownloadConfig:
    url: str
    formato: str
    calidad: str
    directorio_salida: Path
    ruta_zip: Path | None
    empaquetar_zip: bool
    max_workers: int = 4