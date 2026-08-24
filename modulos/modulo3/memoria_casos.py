"""
Módulo de Memoria Analógica — Fase 3 de ALDICE

Fachada pública de la memoria de casos. La lógica se distribuye en
submódulos especializados y esta fachada mantiene la API estable
que usan el pipeline (aldice.py) y el frontend:

    extraer_firma           → firma.py   (C1: huella estructural)
    construir_huella        → firma.py   (C1)
    calcular_similitud      → similitud.py (C1: invariante a refs)
    buscar_casos_similares  → similitud.py (C3: ponderado por feedback)
    generar_mitigacion      → mitigaciones.py (C2)
    registrar_feedback      → feedback.py (C3)
    guardar_caso            → implementado aquí sobre persistencia

Estructura del JSON (data/historial.json):
{
    "version": "1.0",
    "casos": [
        {
            "id": "caso_001",
            "descripcion": "...",
            "firma": {
                "tipo_fallo": [...],
                "tipos_involucrados": [...],
                "componentes_involucrados": [...],
                "tipos_en_circuito": [...],
                "huella_estructural": [...]
            },
            "topologia": {"componentes": [...], "conexiones": [...]},
            "mitigacion": {"accion": "...", "pasos": [...], "prioridad": "..."},
            "feedback": {"votos_util": 0, "votos_no_util": 0, "comentarios": []},
            "fecha": "...",
            "etiquetas": [...]
        }
    ]
}
"""

from datetime import date

from .mitigaciones import generar_mitigacion
from .firma import construir_huella, extraer_firma
from .persistencia import cargar_historial, generar_id, guardar_historial
from .similitud import buscar_casos_similares, calcular_similitud
from .feedback import registrar_feedback

__all__ = [
    "extraer_firma",
    "construir_huella",
    "calcular_similitud",
    "buscar_casos_similares",
    "generar_mitigacion",
    "registrar_feedback",
    "guardar_caso",
    "cargar_historial",
]


def guardar_caso(
    descripcion: str,
    firma: dict,
    mitigacion: dict | None = None,
    componentes: list[dict] | None = None,
    conexiones: list[dict] | None = None,
    etiquetas: list[str] | None = None,
    ruta: str | None = None,
) -> str:
    """
    Guarda un nuevo caso en el historial.

    Args:
        descripcion: descripción legible del fallo.
        firma: firma topológica (de extraer_firma()).
        mitigacion: dict con keys accion, pasos (lista), prioridad.
            Si se omite, se genera con generar_mitigacion() (C2).
        componentes: topología de componentes (opcional).
        conexiones: topología de conexiones (opcional).
        etiquetas: etiquetas para indexación (opcional).
        ruta: ruta alternativa al archivo JSON.

    Returns:
        ID del caso creado.
    """
    historial = cargar_historial(ruta)
    nuevo_id = generar_id(historial)

    if mitigacion is None:
        mitigacion = generar_mitigacion(
            firma.get("tipo_fallo", []), firma.get("tipos_involucrados", [])
        )

    caso = {
        "id": nuevo_id,
        "descripcion": descripcion,
        "firma": firma,
        "topologia": {
            "componentes": componentes or [],
            "conexiones": conexiones or [],
        },
        "mitigacion": mitigacion,
        "feedback": {"votos_util": 0, "votos_no_util": 0, "comentarios": []},
        "fecha": date.today().isoformat(),
        "etiquetas": etiquetas or [],
    }

    historial["casos"].append(caso)
    guardar_historial(historial, ruta)
    return nuevo_id