"""
Comparación de firmas y búsqueda de casos similares (C1, C3).

La similitud pondera rasgos invariantes al renombrado de referencias
(tipo de fallo, tipos involucrados y huella estructural) para que dos
netlists con igual topología y referencias distintas queden cerca.
El resultado de cada caso puede ponderarse por la retroalimentación
del usuario (feedback) registrada en el propio caso.
"""

from collections import Counter

from . import feedback
from .persistencia import cargar_historial


def _jaccard(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 1.0
    return len(set_a & set_b) / len(set_a | set_b)


def _es_desconocido(s: set) -> bool:
    """Un lado 'desconocido' (vacío o sin_fallo) no aporta evidencia."""
    return not s or s == {"sin_fallo"}


def _tipos_involucrados(firma: dict) -> set:
    """Preferirá tipos (invariantes); si el caso es antiguo, usa refs."""
    if "tipos_involucrados" in firma and firma["tipos_involucrados"]:
        return set(firma["tipos_involucrados"])
    return set(firma.get("componentes_involucrados", []))


def _huella_como_multiset(huella) -> list[tuple]:
    return [tuple(n) for n in huella]


def _similitud_multiset(lista_a: list, lista_b: list) -> float:
    """Similitud multiset (Counter-Jaccard) entre dos secuencias."""
    ca, cb = Counter(lista_a), Counter(lista_b)
    if not ca and not cb:
        return 1.0
    inter = sum((ca & cb).values())
    union = sum((ca | cb).values())
    return inter / union


def calcular_similitud(firma_a: dict, firma_b: dict) -> float:
    """
    Puntaje de similitud entre dos firmas (0.0 a 1.0).

    Compara, cuando están disponibles en ambos lados:
      - Tipos de fallo (peso base 0.35)
      - Tipos de componentes involucrados (peso base 0.30)
      - Huella estructural de nodos/pines (peso base 0.35)

    Un campo vacío o "sin_fallo" en cualquiera de las dos firmas se
    trata como desconocido: su peso se redistribuye a los demás campos
    para que la búsqueda previa a Prolog dependa de la estructura, no
    de fallos que aún no se han diagnosticado.
    """
    fallos_a = set(firma_a.get("tipo_fallo", []))
    fallos_b = set(firma_b.get("tipo_fallo", []))
    tipos_a = _tipos_involucrados(firma_a)
    tipos_b = _tipos_involucrados(firma_b)

    huella_a = firma_a.get("huella_estructural")
    huella_b = firma_b.get("huella_estructural")

    fallos_ok = not (_es_desconocido(fallos_a) or _es_desconocido(fallos_b))
    tipos_ok = not (_es_desconocido(tipos_a) or _es_desconocido(tipos_b))
    huella_ok = huella_a is not None and huella_b is not None

    if not (fallos_ok or tipos_ok or huella_ok):
        return 0.0

    pesos = {"fallos": 0.35, "tipos": 0.30, "huella": 0.35}
    activos = [k for k in ("fallos", "tipos", "huella") if locals()[k + "_ok"]]

    suma = sum(pesos[k] for k in activos)
    normalizados = {k: pesos[k] / suma for k in activos}

    total = 0.0
    if fallos_ok:
        total += normalizados["fallos"] * _jaccard(fallos_a, fallos_b)
    if tipos_ok:
        total += normalizados["tipos"] * _jaccard(tipos_a, tipos_b)
    if huella_ok:
        total += normalizados["huella"] * _similitud_multiset(
            _huella_como_multiset(huella_a), _huella_como_multiset(huella_b)
        )

    return round(total, 4)


def buscar_casos_similares(
    firma: dict,
    umbral: float = 0.5,
    ruta: str | None = None,
) -> list[dict]:
    """
    Busca casos con firma similar, ponderados por feedback del usuario.

    Args:
        firma: firma topológica (de extraer_firma()).
        umbral: similitud mínima para considerar un caso (0.0–1.0).
        ruta: ruta alternativa al archivo JSON.

    Returns:
        Lista de dicts con el caso, su puntaje base y el puntaje
        ajustado por feedback, ordenados de mayor a menor similitud.
    """
    historial = cargar_historial(ruta)
    resultados = []

    for caso in historial.get("casos", []):
        base = calcular_similitud(firma, caso.get("firma", {}))
        if base >= umbral:
            ajustada = feedback.ponderar_similitud(base, caso)
            resultados.append({
                "caso": caso,
                "similitud": round(ajustada, 3),
                "similitud_base": round(base, 3),
            })

    resultados.sort(key=lambda x: x["similitud"], reverse=True)
    return resultados