"""
Módulo de Memoria Analógica — Fase 3 de ALDICE

Gestiona la base de conocimiento local en formato JSON.
Almacena casos históricos de fallos, sus firmas topológicas
y las acciones de mitigación sugeridas. Permite buscar casos
similares y registrar nuevos diagnósticos.

Estructura del JSON (historial.json):
{
    "version": "1.0",
    "casos": [
        {
            "id": "caso_001",
            "descripcion": "Cortocircuito en fuente de alimentación",
            "firma": {
                "tipo_fallo": "cortocircuito",
                "componentes_involucrados": ["vsource"],
                "num_nodos_afectados": 1
            },
            "topologia": {
                "componentes": [...],
                "conexiones": [...]
            },
            "mitigacion": {
                "accion": "Verificar conexiones de la fuente",
                "pasos": ["Paso 1", "Paso 2"],
                "prioridad": "critica"
            },
            "fecha": "2026-07-27",
            "etiquetas": ["fuente", "cortocircuito", "critico"]
        }
    ]
}
"""

import json
import os
from datetime import date


def _ruta_relativa(*partes: str) -> str:
    """Resuelve una ruta relativa al directorio raíz del proyecto."""
    dir_raiz = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(dir_raiz, *partes)


def _ruta_datos() -> str:
    """Retorna la ruta al archivo historial.json."""
    return _ruta_relativa("data", "historial.json")


def _cargar_historial(ruta: str | None = None) -> dict:
    """
    Carga el archivo JSON del historial de casos.

    Si el archivo no existe, retorna una estructura vacía válida.
    """
    ruta = ruta or _ruta_datos()

    if not os.path.isfile(ruta):
        return {"version": "1.0", "casos": []}

    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def _guardar_historial(historial: dict, ruta: str | None = None) -> None:
    """Persiste el historial en disco."""
    ruta = ruta or _ruta_datos()
    os.makedirs(os.path.dirname(ruta), exist_ok=True)

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=2, ensure_ascii=False)


# ============================================
# Construcción de firmas topológicas
# ============================================

def extraer_firma(resultados_diagnostico: dict, componentes: list[dict]) -> dict:
    """
    Construye una firma topológica a partir de los resultados del diagnóstico.

    La firma resume las características clave del fallo para permitir
    comparación con casos históricos.

    Args:
        resultados_diagnostico: dict devuelto por motor_diagnostico.diagnosticar().
        componentes: lista de dicts con keys ref, tipo, valor (del parser).

    Returns:
        dict con la firma normalizada del fallo.
    """
    tipos_componentes = set()
    for c in componentes:
        tipos_componentes.add(c["tipo"])

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

    # Componentes involucrados en el fallo
    involucrados = set()
    for alerta in resultados_diagnostico.get("cortocircuitos", []):
        involucrados.add(alerta["componente"])
    for alerta in resultados_diagnostico.get("fuentes_cortocircuito", []):
        involucrados.add(alerta["componente"])
    for alerta in resultados_diagnostico.get("caminos_abiertos", []):
        involucrados.add(alerta["componente"])

    return {
        "tipo_fallo": sorted(tipos_fallo) if tipos_fallo else ["sin_fallo"],
        "componentes_involucrados": sorted(involucrados),
        "tipos_en_circuito": sorted(tipos_componentes),
        "num_alertas": sum(len(v) for v in resultados_diagnostico.values()),
    }


# ============================================
# Búsqueda de casos similares
# ============================================

def calcular_similitud(firma_a: dict, firma_b: dict) -> float:
    """
    Calcula un puntaje de similitud entre dos firmas (0.0 a 1.0).

    Compara:
      - Tipos de fallo coincidentes (peso: 0.5)
      - Componentes involucrados coincidentes (peso: 0.3)
      - Tipos de componente en circuito (peso: 0.2)
    """
    # Similitud de tipos de fallo
    fallos_a = set(firma_a.get("tipo_fallo", []))
    fallos_b = set(firma_b.get("tipo_fallo", []))
    if fallos_a or fallos_b:
        sim_fallos = len(fallos_a & fallos_b) / len(fallos_a | fallos_b)
    else:
        sim_fallos = 1.0

    # Similitud de componentes involucrados
    comp_a = set(firma_a.get("componentes_involucrados", []))
    comp_b = set(firma_b.get("componentes_involucrados", []))
    if comp_a or comp_b:
        sim_comp = len(comp_a & comp_b) / len(comp_a | comp_b)
    else:
        sim_comp = 1.0

    # Similitud de tipos de componente en circuito
    tipos_a = set(firma_a.get("tipos_en_circuito", []))
    tipos_b = set(firma_b.get("tipos_en_circuito", []))
    if tipos_a or tipos_b:
        sim_tipos = len(tipos_a & tipos_b) / len(tipos_a | tipos_b)
    else:
        sim_tipos = 1.0

    return 0.5 * sim_fallos + 0.3 * sim_comp + 0.2 * sim_tipos


def buscar_casos_similares(
    firma: dict,
    umbral: float = 0.5,
    ruta: str | None = None,
) -> list[dict]:
    """
    Busca casos en el historial cuya firma sea similar a la dada.

    Args:
        firma: firma topológica (de extraer_firma()).
        umbral: similitud mínima para considerar un caso (0.0–1.0).
        ruta: ruta alternativa al archivo JSON.

    Returns:
        Lista de dicts con el caso y su puntaje de similitud,
        ordenados de mayor a menor similitud.
    """
    historial = _cargar_historial(ruta)
    resultados = []

    for caso in historial.get("casos", []):
        similitud = calcular_similitud(firma, caso.get("firma", {}))
        if similitud >= umbral:
            resultados.append({"caso": caso, "similitud": round(similitud, 3)})

    resultados.sort(key=lambda x: x["similitud"], reverse=True)
    return resultados


# ============================================
# Escritura de nuevos casos
# ============================================

def _generar_id(historial: dict) -> str:
    """Genera un ID incremental para un nuevo caso."""
    existentes = [c["id"] for c in historial.get("casos", [])]
    if not existentes:
        return "caso_001"
    ultimo_num = max(int(e.split("_")[1]) for e in existentes)
    return f"caso_{ultimo_num + 1:03d}"


def guardar_caso(
    descripcion: str,
    firma: dict,
    mitigacion: dict,
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
        componentes: topología de componentes (opcional).
        conexiones: topología de conexiones (opcional).
        etiquetas: etiquetas para indexación (opcional).
        ruta: ruta alternativa al archivo JSON.

    Returns:
        ID del caso creado.
    """
    historial = _cargar_historial(ruta)
    nuevo_id = _generar_id(historial)

    caso = {
        "id": nuevo_id,
        "descripcion": descripcion,
        "firma": firma,
        "topologia": {
            "componentes": componentes or [],
            "conexiones": conexiones or [],
        },
        "mitigacion": mitigacion,
        "fecha": date.today().isoformat(),
        "etiquetas": etiquetas or [],
    }

    historial["casos"].append(caso)
    _guardar_historial(historial, ruta)
    return nuevo_id


# ============================================
# Bloque de ejemplo de uso
# ============================================
if __name__ == "__main__":
    from modulo1.netlist_parser import parse_bloques
    from modulo2.motor_diagnostico import diagnosticar

    # Analizar circuito con fallo
    ruta_netlist = _ruta_relativa("Example", "Netlists", "Circuito_Basico_Malo.NET")
    with open(ruta_netlist, "r", encoding="utf-8") as f:
        contenido = f.read()
    componentes, conexiones_raw = parse_bloques(contenido)

    ruta_hechos = _ruta_relativa("Example", "Prolog", "circuito_malo.pl")
    resultados = diagnosticar(ruta_hechos)

    print("Firma del fallo:")
    firma = extraer_firma(resultados, componentes)
    print(json.dumps(firma, indent=2))

    print("\nBuscando casos similares...")
    similares = buscar_casos_similares(firma, umbral=0.3)
    if similares:
        for s in similares:
            print(f"  Caso {s['caso']['id']}: similitud={s['similitud']}")
    else:
        print("  No se encontraron casos similares.")

    print("\nGuardando caso nuevo...")
    nuevo_id = guardar_caso(
        descripcion="Cortocircuito en fuente V1 - terminales unidos en n00000",
        firma=firma,
        mitigacion={
            "accion": "Verificar soldaduras de V1 y reconectar terminales",
            "pasos": [
                "Inspeccionar visualmente las conexiones de V1",
                "Verificar continuidad entre terminales de V1",
                "Resoldar conexiones si es necesario",
            ],
            "prioridad": "critica",
        },
        componentes=[{"ref": c["ref"], "tipo": c["tipo"], "valor": c["valor"]} for c in componentes],
        etiquetas=["fuente", "cortocircuito", "critico"],
    )
    print(f"  Caso guardado: {nuevo_id}")
