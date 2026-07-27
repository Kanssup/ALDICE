#!/usr/bin/env python3
"""
ALDICE — Script principal de diagnóstico

Integra los tres módulos del sistema:
  1. Extracción y Traducción (netlist_parser)
  2. Motor de Inferencia (motor_diagnostico)
  3. Memoria Analógica (memoria_casos)

Uso:
    python aldice.py <archivo.NET>

Ejemplo:
    python aldice.py Example/Netlists/Circuito_Basico_Malo.NET
"""

import os
import sys
import json
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


def diagnosticar_circuito(ruta_netlist: str) -> None:
    """
    Ejecuta el pipeline completo de diagnóstico sobre un netlist.

    Flujo:
        Netlist → Parser → Prolog → Diagnóstico → Memoria → Resultado
    """
    nombre = os.path.basename(ruta_netlist)
    print(f"\n{'='*50}")
    print(f"  ALDICE — Analizando: {nombre}")
    print(f"{'='*50}\n")

    # --- Paso 1: Parsear netlist ---
    print("[1/4] Parseando netlist...")
    with open(ruta_netlist, "r", encoding="utf-8") as f:
        contenido = f.read()
    componentes, conexiones = parse_bloques(contenido)
    print(f"      {len(componentes)} componentes, {len(conexiones)} nodos")

    # Generar hechos Prolog en archivo temporal
    hechos_pl = generar_prolog(componentes, conexiones)
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".pl", delete=False, encoding="utf-8"
    )
    tmp.write(hechos_pl)
    tmp.close()
    print(f"      Hechos Prolog escritos en archivo temporal")

    # --- Paso 2: Diagnosticar con motor Prolog ---
    print("\n[2/4] Ejecutando diagnóstico Prolog...")
    try:
        resultados = diagnosticar(tmp.name)
    finally:
        os.unlink(tmp.name)

    imprimir_resultados(resultados)

    # --- Paso 3: Buscar en memoria ---
    print("[3/4] Buscando casos similares en memoria...")
    firma = extraer_firma(resultados, componentes)
    similares = buscar_casos_similares(firma, umbral=0.5)

    if similares:
        print(f"      Se encontraron {len(similares)} caso(s) similar(es):")
        for s in similares[:3]:
            caso = s["caso"]
            print(f"        - {caso['id']} (similitud: {s['similitud']})")
            print(f"          {caso['mitigacion']['accion']}")
    else:
        print("      No se encontraron casos similares.")

    # --- Paso 4: Guardar si hay fallos ---
    tiene_fallos = any(len(v) > 0 for v in resultados.values())

    if tiene_fallos and not similares:
        print("\n[4/4] Guardando caso nuevo en memoria...")
        id_caso = guardar_caso(
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
        print(f"      Caso guardado como: {id_caso}")
    else:
        print("\n[4/4] No se guardó caso (sin fallos nuevos).")

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
    if not os.path.isfile(ruta):
        print(f"Error: archivo no encontrado — {ruta}")
        sys.exit(1)

    diagnosticar_circuito(ruta)
