import json
from pathlib import Path
from typing import Set

RUTA_HISTORIAL = Path("history.json")


def cargar_historial() -> Set[str]:
    # Carga los identificadores de canciones ya descargadas previamente
    if not RUTA_HISTORIAL.exists():
        return set()
    try:
        with open(RUTA_HISTORIAL, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("descargados", []))
    except Exception:
        return set()


def guardar_en_historial(nuevo_id: str) -> None:
    # Registra un nuevo identificador en el archivo history.json
    historial = cargar_historial()
    historial.add(nuevo_id)
    try:
        with open(RUTA_HISTORIAL, "w", encoding="utf-8") as f:
            json.dump({"descargados": sorted(list(historial))}, f, indent=4, ensure_ascii=False)
    except Exception:
        pass