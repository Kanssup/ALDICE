#!/usr/bin/env python3
"""
ALDICE — Script principal de diagnóstico

Integra los tres módulos del sistema:
  1. Extracción y Traducción (netlist_parser)
  2. Motor de Inferencia (motor_diagnostico)
  3. Memoria Analógica (memoria_casos)

El flujo es "memoria-primero": se construye la huella estructural,
se busca en memoria; Prolog solo se invoca cuando no hay un caso
suficientemente similar (fallo inédito o ambiguo).

Usa `ejecutar_pipeline()` en modo consola o importándolo desde el frontend.

Uso:
    python aldice.py <archivo.NET>

Ejemplo:
    python aldice.py Example/Netlists/Circuito_Basico_Malo.NET
"""

import os
import sys
import tempfile

# Agregar raíz del proyecto al path
_DIR_RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR_RAIZ)

from modulos.modulo1.netlist_parser import parse_bloques, generar_prolog
from modulos.modulo2.motor_diagnostico import diagnosticar, imprimir_resultados
from modulos.modulo3.memoria_casos import (
    extraer_firma,
    buscar_casos_similares,
    guardar_caso,
    generar_mitigacion,
)


def filtrar_cortocircuitos(resultados: dict) -> list[dict]:
    """
    Elimina cortocircuitos genéricos que ya reporta fuentes_cortocircuito.

    Cuando una fuente está en cortocircuito (sus pines 1 y 2 en el mismo
    nodo), la regla alerta_cortocircuito también la detecta de forma
    redundante (pin1→pin2 y pin2→pin1). Aquí descartamos esos duplicados,
    siempre que sea el mismo nodo y el mismo componente.

    Args:
        resultados: dict de diagnóstico con keys cortocircuitos y
                    fuentes_cortocircuito.

    Returns:
        Lista de cortocircuitos sin los cubiertos por fuentes_cortocircuito.
    """
    fuentes = {
        (a["nodo"], a["componente"])
        for a in resultados.get("fuentes_cortocircuito", [])
    }
    return [
        a
        for a in resultados.get("cortocircuitos", [])
        if (a["nodo"], a["componente"]) not in fuentes
    ]


def _ejecutar_prolog(ruta_hechos: str) -> dict:
    """Corre el motor Prolog y limpia cortocircuitos redundantes."""
    try:
        resultados = diagnosticar(ruta_hechos)
    finally:
        os.unlink(ruta_hechos)
    resultados["cortocircuitos"] = filtrar_cortocircuitos(resultados)
    return resultados


def ejecutar_pipeline(ruta_netlist: str) -> dict:
    """
    Ejecuta el pipeline completo de diagnóstico sobre un netlist.

    Flujo (memoria-primero):
        Netlist → Parser → Firma/Huella → Memoria → (Prolog) → Resultado

    Si la memoria devuelve un caso suficientemente similar, Prolog no
    se ejecuta; de lo contrario se consulta el motor para precisar el
    fallo y, si es un fallo nuevo, se almacena en la memoria.

    Args:
        ruta_netlist: Ruta al archivo .NET.

    Returns:
        dict estructurado con toda la información del diagnóstico
        (componentes, resultados Prolog, firma, casos similares, etc.)
    """
    nombre = os.path.basename(ruta_netlist)

    # --- Paso 1: Parsear netlist ---
    with open(ruta_netlist, "r", encoding="utf-8") as f:
        contenido = f.read()
    componentes, conexiones = parse_bloques(contenido)

    # Generar hechos Prolog en archivo temporal (por si se necesita Prolog)
    hechos_pl = generar_prolog(componentes, conexiones)
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".pl", delete=False, encoding="utf-8"
    )
    tmp.write(hechos_pl)
    tmp.close()

    # Iluminar estructura: nodos y conexiones conocidos sin Prolog
    firma = extraer_firma({}, componentes, conexiones)

    # --- Paso 2: Consultar memoria primero ---
    similares = buscar_casos_similares(firma, umbral=0.5)

    if similares:
        # Fallo conocido: no hace falta el motor; se usan los casos
        resultados = {
            "cortocircuitos": [],
            "caminos_abiertos": [],
            "fuentes_cortocircuito": [],
            "nodos_sobrecargados": [],
            "fuente": "memoria",
        }
        caso_guardado = None
    else:
        # --- Paso 3: Solo para fallos inéditos: ejecutar Prolog ---
        resultados = _ejecutar_prolog(tmp.name)
        resultados["fuente"] = "prolog"

        v_fallos = [
            resultados.get(k, [])
            for k in ("cortocircuitos", "caminos_abiertos", "fuentes_cortocircuito", "nodos_sobrecargados")
        ]
        tiene_fallos = any(len(v) > 0 for v in v_fallos)
        firma = extraer_firma(resultados, componentes, conexiones)

        caso_guardado = None
        if tiene_fallos and not similares:
            caso_guardado = guardar_caso(
                descripcion=f"Fallo detectado en {nombre}",
                firma=firma,
                mitigacion=generar_mitigacion(
                    firma.get("tipo_fallo", []),
                    firma.get("tipos_involucrados", []),
                ),
                componentes=componentes,
                conexiones=conexiones,
                etiquetas=firma["tipo_fallo"],
            )

    dev_alertas = [
        resultados.get(k, [])
        for k in ("cortocircuitos", "caminos_abiertos", "fuentes_cortocircuito", "nodos_sobrecargados")
    ]
    return {
        "nombre": nombre,
        "componentes": componentes,
        "conexiones": conexiones,
        "resultados_diagnostico": resultados,
        "firma": firma,
        "similares": similares,
        "caso_guardado": caso_guardado,
        "tiene_fallos": bool(similares or any(len(v) > 0 for v in dev_alertas)),
    }


def diagnosticar_circuito(ruta_netlist: str) -> None:
    """
    Wrapper de consola: ejecuta el pipeline e imprime resultados legibles.
    """
    nombre = os.path.basename(ruta_netlist)
    print(f"\n{'='*50}")
    print(f"  ALDICE — Analizando: {nombre}")
    print(f"{'='*50}\n")

    if not os.path.isfile(ruta_netlist):
        print(f"Error: archivo no encontrado — {ruta_netlist}")
        return

    pipeline = ejecutar_pipeline(ruta_netlist)
    resultados = pipeline["resultados_diagnostico"]
    fuente = resultados.get("fuente", "prolog")

    if fuente == "memoria":
        # Fallo recuperado de la memoria: no se ejecutó Prolog
        print(f"[FUENTE] Memoria de casos (Prolog no ejecutado)")
        print(f"[2/4] Se encontraron {len(pipeline['similares'])} caso(s) similar(es):")
        for s in pipeline["similares"][:3]:
            caso = s["caso"]
            print(f"        - {caso['id']} (similitud: {s['similitud']})")
            print(f"          {caso['mitigacion']['accion']}")
    else:
        imprimir_resultados(resultados)

        # --- Resultados de memoria (post-Prolog) ---
        if pipeline["similares"]:
            print(f"[3/4] Se encontraron {len(pipeline['similares'])} caso(s) similar(es):")
            for s in pipeline["similares"][:3]:
                caso = s["caso"]
                print(f"        - {caso['id']} (similitud: {s['similitud']})")
                print(f"          {caso['mitigacion']['accion']}")
        elif pipeline["caso_guardado"]:
            print(f"[3/4] No se encontraron casos similares.")
            print(f"[4/4] Caso guardado como: {pipeline['caso_guardado']}")
        else:
            print("[3/4] No se encontraron casos similares (circuito sin fallos).")

    print(f"\n{'='*50}")
    print("  Fin del diagnóstico")
    print(f"{'='*50}\n")


# ============================================================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python aldice.py <archivo.NET>")
        print("Ejemplo: python aldice.py Example/Netlists/Circuito_Basico_Malo.NET")
        sys.exit(1)

    ruta = sys.argv[1]
    diagnosticar_circuito(ruta)