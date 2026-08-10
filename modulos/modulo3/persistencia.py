"""
Acceso a la base de conocimiento local (historial.json).

Helpers compartidos por los submódulos de la memoria de casos:
carga, guardado y generación de identificadores. La ruta por
defecto es `data/historial.json` relativa a la raíz del proyecto.
"""

import json
import os
from datetime import date


def ruta_relativa(*partes: str) -> str:
    """Resuelve una ruta relativa al directorio raíz del proyecto."""
    dir_raiz = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(dir_raiz, *partes)


def ruta_datos() -> str:
    """Retorna la ruta al archivo historial.json."""
    return ruta_relativa("data", "historial.json")


def cargar_historial(ruta: str | None = None) -> dict:
    """
    Carga el archivo JSON del historial de casos.

    Si el archivo no existe, retorna una estructura vacía válida.
    """
    ruta = ruta or ruta_datos()

    if not os.path.isfile(ruta):
        return {"version": "1.0", "casos": []}

    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_historial(historial: dict, ruta: str | None = None) -> None:
    """Persiste el historial en disco."""
    ruta = ruta or ruta_datos()
    os.makedirs(os.path.dirname(ruta), exist_ok=True)

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=2, ensure_ascii=False)


def generar_id(historial: dict) -> str:
    """Genera un ID incremental para un nuevo caso."""
    existentes = [c["id"] for c in historial.get("casos", [])]
    if not existentes:
        return "caso_001"
    ultimo_num = max(int(e.split("_")[1]) for e in existentes)
    return f"caso_{ultimo_num + 1:03d}"