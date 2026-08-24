"""
Retroalimentación del usuario dentro de cada caso (C3).

El usuario marca en la interfaz si una mitigación "sirvió" o
"no funcionó". Esa información se persiste dentro del caso
(no como entidad separada) y pondera las búsquedas futuras:
un caso útil sube ligeramente de similitud y uno rechazado baja.
"""

from datetime import date

from .persistencia import cargar_historial, guardar_historial


def _factor(caso: dict) -> float:
    """Factor de ponderación según votos de utilidad del caso."""
    fb = caso.get("feedback", {})
    votos_util = int(fb.get("votos_util", 0))
    votos_no_util = int(fb.get("votos_no_util", 0))
    neto = votos_util - votos_no_util
    factor = 1.0 + 0.05 * neto
    return max(0.7, min(1.15, factor))


def ponderar_similitud(similitud: float, caso: dict) -> float:
    """Ajusta la similitud base según el feedback histórico del caso."""
    return min(1.0, similitud * _factor(caso))


def registrar_feedback(
    caso_id: str,
    util: bool,
    comentario: str | None = None,
    ruta: str | None = None,
) -> dict:
    """
    Registra un voto de utilidad dentro del caso indicado.

    Args:
        caso_id: identificador del caso (ej. "caso_001").
        util: True si la mitigación sirvió, False en caso contrario.
        comentario: nota opcional del técnico.
        ruta: ruta alternativa al archivo JSON.

    Returns:
        El bloque feedback actualizado del caso.

    Raises:
        KeyError: si no existe el caso con ese id.
    """
    historial = cargar_historial(ruta)

    for caso in historial.get("casos", []):
        if caso["id"] != caso_id:
            continue

        fb = caso.setdefault(
            "feedback", {"votos_util": 0, "votos_no_util": 0, "comentarios": []}
        )
        if util:
            fb["votos_util"] += 1
        else:
            fb["votos_no_util"] += 1
        if comentario:
            fb["comentarios"].append({"texto": comentario, "fecha": date.today().isoformat()})

        guardar_historial(historial, ruta)
        return fb

    raise KeyError(f"No existe el caso: {caso_id}")