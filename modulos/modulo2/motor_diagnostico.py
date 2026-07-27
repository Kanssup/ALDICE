"""
Módulo de Motor de Inferencia — Fase 2 de ALDICE

Conecta con SWI-Prolog mediante pyswip para cargar hechos y reglas
de diagnóstico, ejecutar consultas y presentar resultados.

Requisitos de instalación (Ubuntu/Debian):
    sudo apt-get update
    sudo apt-get install -y swi-prolog
    pip install pyswip

Uso:
    python motor_diagnostico.py [archivo_hechos.pl]

Si no se especifica archivo, usa el circuito_bueno.pl de ejemplo.
"""

import os
import sys

from pyswip import Prolog


def _ruta_relativa(*partes: str) -> str:
    """Resuelve una ruta relativa al directorio raíz del proyecto."""
    dir_raiz = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(dir_raiz, *partes)


def diagnosticar(ruta_hechos: str) -> dict:
    """
    Ejecuta el diagnóstico completo sobre un archivo de hechos Prolog.

    Args:
        ruta_hechos: Ruta al archivo .pl con hechos (componente/3, conexion/3).

    Returns:
        dict con las listas de alertas encontradas.
    """
    if not os.path.isfile(ruta_hechos):
        raise FileNotFoundError(f"Archivo de hechos no encontrado: {ruta_hechos}")

    prolog = Prolog()

    # Cargar hechos del circuito
    prolog.consult(ruta_hechos)

    # Cargar reglas de diagnóstico
    ruta_reglas = _ruta_relativa("modulos", "modulo2", "reglas_diagnostico.pl")
    if not os.path.isfile(ruta_reglas):
        raise FileNotFoundError(f"Archivo de reglas no encontrado: {ruta_reglas}")
    prolog.consult(ruta_reglas)

    resultados = {
        "cortocircuitos": [],
        "caminos_abiertos": [],
        "fuentes_cortocircuito": [],
        "nodos_sobrecargados": [],
    }

    # --- Consulta 1: Cortocircuitos críticos ---
    for sol in prolog.query("alerta_cortocircuito(Nodo, Ref, Pin1, Pin2)."):
        resultados["cortocircuitos"].append({
            "nodo": sol["Nodo"],
            "componente": sol["Ref"],
            "pin1": sol["Pin1"],
            "pin2": sol["Pin2"],
        })

    # --- Consulta 2: Caminos abiertos ---
    for sol in prolog.query("alerta_camino_abierto(Ref, Pin)."):
        resultados["caminos_abiertos"].append({
            "componente": sol["Ref"],
            "pin": sol["Pin"],
        })

    # --- Consulta 3: Fuentes en cortocircuito ---
    for sol in prolog.query("alerta_fuente_cortocircuito(Nodo, Ref)."):
        resultados["fuentes_cortocircuito"].append({
            "nodo": sol["Nodo"],
            "componente": sol["Ref"],
        })

    # --- Consulta 4: Nodos sobrecargados ---
    for sol in prolog.query("alerta_nodo_sobrecargado(Nodo, Num)."):
        resultados["nodos_sobrecargados"].append({
            "nodo": sol["Nodo"],
            "conexiones": sol["Num"],
        })

    return resultados


def imprimir_resultados(resultados: dict) -> None:
    """Imprime los resultados del diagnóstico en formato legible."""
    total = sum(len(v) for v in resultados.values())

    if total == 0:
        print("\n[OK] No se detectaron fallos en el circuito.\n")
        return

    print(f"\n{'='*50}")
    print(f"  DIAGNÓSTICO — {total} alerta(s) detectada(s)")
    print(f"{'='*50}")

    if resultados["fuentes_cortocircuito"]:
        print("\n[CRITICO] FUENTE EN CORTOCIRCUITO:")
        for alerta in resultados["fuentes_cortocircuito"]:
            print(f"  - Nodo '{alerta['nodo']}': "
                  f"fuente '{alerta['componente']}' unida en ambos terminales")

    if resultados["cortocircuitos"]:
        print("\n[CRITICO] CORTOCIRCUITO DETECTADO:")
        for alerta in resultados["cortocircuitos"]:
            print(f"  - Nodo '{alerta['nodo']}': "
                  f"componente '{alerta['componente']}' "
                  f"pin {alerta['pin1']} ↔ pin {alerta['pin2']}")

    if resultados["caminos_abiertos"]:
        print("\n[ADVERTENCIA] CAMINO ABIERTO:")
        for alerta in resultados["caminos_abiertos"]:
            print(f"  - Componente '{alerta['componente']}' "
                  f"pin '{alerta['pin']}' sin conexión de retorno")

    if resultados["nodos_sobrecargados"]:
        print("\n[INFO] NODO SOBRECARGADO:")
        for alerta in resultados["nodos_sobrecargados"]:
            print(f"  - Nodo '{alerta['nodo']}': "
                  f"{alerta['conexiones']} conexiones")

    print(f"\n{'='*50}\n")


# ============================================================
# Bloque de ejemplo de uso
# ============================================================
if __name__ == "__main__":
    # Determinar archivo de hechos a analizar
    if len(sys.argv) > 1:
        archivo_hechos = sys.argv[1]
    else:
        archivo_hechos = _ruta_relativa("Example", "Prolog", "circuito_bueno.pl")

    print(f"Analizando: {archivo_hechos}")
    resultados = diagnosticar(archivo_hechos)
    imprimir_resultados(resultados)
