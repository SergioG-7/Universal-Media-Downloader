from dataclasses import dataclass
from pathlib import Path

@dataclass
class DownloadConfig:
    url: str
    formato: str
    calidad: str
    directorio_salida: Path
    modo_salida: str
    ruta_destino: Path | None
    normalizar_audio: bool = False
    max_workers: int = 4