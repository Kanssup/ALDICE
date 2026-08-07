#!/usr/bin/env python3
"""
ALDICE — Script principal de diagnóstico

Integra los tres módulos del sistema:
  1. Extracción y Traducción (netlist_parser)
  2. Motor de Inferencia (motor_diagnostico)
  3. Memoria Analógica (memoria_casos)

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


def ejecutar_pipeline(ruta_netlist: str) -> dict:
    """
    Ejecuta el pipeline completo de diagnóstico sobre un netlist.

    Flujo:
        Netlist → Parser → Prolog → Memoria → Resultado

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

    # Generar hechos Prolog en archivo temporal
    hechos_pl = generar_prolog(componentes, conexiones)
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".pl", delete=False, encoding="utf-8"
    )
    tmp.write(hechos_pl)
    tmp.close()

    # --- Paso 2: Diagnosticar con motor Prolog ---
    try:
        resultados = diagnosticar(tmp.name)
    finally:
        os.unlink(tmp.name)

    # Evitar duplicados entre cortocircuitos y fuentes en cortocircuito
    resultados["cortocircuitos"] = filtrar_cortocircuitos(resultados)

    # --- Paso 3: Buscar en memoria ---
    firma = extraer_firma(resultados, componentes)
    similares = buscar_casos_similares(firma, umbral=0.5)
    tiene_fallos = any(len(v) > 0 for v in resultados.values())

    # --- Paso 4: Guardar si hay fallos nuevos ---
    caso_guardado = None
    if tiene_fallos and not similares:
        caso_guardado = guardar_caso(
            descripcion=f"Fallo detectado en {nombre}",
            firma=firma,
            mitigacion={
                "accion": "Requiere revisión manual del técnico",
                "pasos": [
                    "Inspeccionar visualmente el circuito",
                    "Verificar conexiones con multímetro",
                    "Comparar con esquemático original",
                ],
                "prioridad": "alta",
            },
            componentes=componentes,
            etiquetas=firma["tipo_fallo"],
        )

    return {
        "nombre": nombre,
        "componentes": componentes,
        "conexiones": conexiones,
        "resultados_diagnostico": resultados,
        "firma": firma,
        "similares": similares,
        "caso_guardado": caso_guardado,
        "tiene_fallos": tiene_fallos,
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

    imprimir_resultados(resultados)

    # --- Resultados de memoria ---
    if pipeline["similares"]:
        print(f"[3/4] Se encontraron {len(pipeline['similares'])} caso(s) similar(es):")
        for s in pipeline["similares"][:3]:
            caso = s["caso"]
            print(f"        - {caso['id']} (similitud: {s['similitud']})")
            print(f"          {caso['mitigacion']['accion']}")
    elif pipeline["tiene_fallos"]:
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