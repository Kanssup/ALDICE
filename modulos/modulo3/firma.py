"""
Construcción de firmas topológicas y huellas estructurales (C1).

Una firma resume un diagnóstico en rasgos comparables entre casos.
La huella estructural abstrae el grafo del circuito: cada nodo se
codifica por los pares (tipo, pin) que lo conectan, sin nombres de
referencias ni de nodos. Así, circuitos con igual topología pero
referencias renombradas (v1/r1 vs vcc/r4) producen la misma huella.
"""

from collections import Counter


def _normalizar_involucrados(
    resultados_diagnostico: dict, ref_tipo: dict[str, str]
) -> tuple[set[str], set[str]]:
    """Extrae componentes involucrados (refs) y sus tipos normalizados."""
    refs = set()
    for key in ("cortocircuitos", "fuentes_cortocircuito", "caminos_abiertos"):
        for alerta in resultados_diagnostico.get(key, []):
            refs.add(alerta["componente"])

    tipos = {ref_tipo.get(ref, ref) for ref in refs}
    return refs, tipos


def construir_huella(componentes: list[dict], conexiones: list[dict]) -> list[list[str]]:
    """
    Codifica la topología del circuito de forma invariante a nombres.

    Cada nodo se representa por la lista ordenada de pares
    "tipo:pin" de los componentes que lo habitan. La huella es la
    lista de estas codificaciones ordenada globalmente.

    Args:
        componentes: lista de dicts con keys ref, tipo, valor.
        conexiones: lista de dicts con key nodo y conexiones (lista de (ref, pin)).

    Returns:
        Lista ordenada de firmas de nodo (cada una lista de strings).
    """
    ref_tipo = {c["ref"]: c["tipo"] for c in componentes}

    nodos = []
    for nodo in conexiones:
        pares = sorted(
            f"{ref_tipo.get(ref, ref)}:{pin}" for ref, pin in nodo["conexiones"]
        )
        nodos.append(pares)

    nodos.sort(key=lambda p: (len(p), p))
    return nodos


def extraer_firma(
    resultados_diagnostico: dict,
    componentes: list[dict],
    conexiones: list[dict] | None = None,
) -> dict:
    """
    Construye la firma topológica a partir del diagnóstico.

    La firma combina categorías de fallo, componentes involucrados
    (tipos y refs) y la huella estructural para permitir comparación
    robusta con casos históricos.

    Args:
        resultados_diagnostico: dict devuelto por motor_diagnostico.diagnosticar().
        componentes: lista de dicts con keys ref, tipo, valor (del parser).
        conexiones: lista de nodos del parser (opcional; sin ella la
            huella se omite y la comparación degrada a tipos).

    Returns:
        dict con la firma normalizada del fallo.
    """
    ref_tipo = {c["ref"]: c["tipo"] for c in componentes}
    tipos_componentes = set(ref_tipo.values())

    # Determinar tipo de fallo principal
    tipos_fallo = []
    if resultados_diagnostico.get("fuentes_cortocircuito"):
        tipos_fallo.append("cortocircuito_fuente")
    if resultados_diagnostico.get("cortocircuitos"):
        tipos_fallo.append("cortocircuito")
    if resultados_diagnostico.get("caminos_abiertos"):
        tipos_fallo.append("camino_abierto")
    if resultados_diagnostico.get("nodos_sobrecargados"):
        tipos_fallo.append("nodo_sobrecargado")

    refs, tipos = _normalizar_involucrados(resultados_diagnostico, ref_tipo)

    firma: dict = {
        "tipo_fallo": sorted(tipos_fallo) if tipos_fallo else ["sin_fallo"],
        "componentes_involucrados": sorted(refs),
        "tipos_involucrados": sorted(tipos),
        "tipos_en_circuito": sorted(tipos_componentes),
        "num_alertas": sum(len(v) for v in resultados_diagnostico.values()),
    }

    if conexiones:
        firma["huella_estructural"] = construir_huella(componentes, conexiones)

    return firma