"""
Módulo de Extracción y Traducción — Fase 1 de ALDICE

Lee un archivo Netlist exportado desde Proteus en formato Tango,
parsea componentes y nodos de conexión, y genera un archivo de
hechos lógicos `.pl` compatible con Prolog.

Formato Tango de entrada:
  - Bloques de componentes: [...]
    Línea 1: Referencia (C1, R1, V1)
    Línea 2: Tipo (CAP10, RESISTOR, VSOURCE)
    Línea 3: Valor (10uF, 220, 5V)
  - Bloques de nodos: (...)
    Línea 1: Nombre del nodo (N00000, N00001)
    Siguientes: Tuplas componente,pin (V1,1 / R1,1 / D1,K)

Formato de salida Prolog:
  componente(referencia, tipo, 'valor').
  conexion(nodo, componente, pin).
"""

import re
import sys
import os


def _normalizar_id(texto: str) -> str:
    """Convierte un identificador a minúsculas y elimina espacios extremos."""
    return texto.strip().lower()


def _escapar_prolog(texto: str) -> str:
    """Escapa caracteres especiales para que sean válidos en un átomo Prolog."""
    return texto.replace("\\", "\\\\").replace("'", "\\'")


def parse_bloques(texto: str) -> tuple[list[dict], list[dict]]:
    """
    Extrae bloques de componentes [...] y nodos (...) del contenido Tango.

    Retorna:
        (componentes, nodos)
        - componentes: lista de dicts con keys ref, tipo, valor
        - nodos: lista de dicts con key nodo, conexiones (lista de (ref, pin))
    """
    componentes = []
    nodos = []

    # Bloques de componente: contenido entre [ y ]
    for match in re.finditer(r"\[(.*?)\]", texto, re.DOTALL):
        lineas = [l.strip() for l in match.group(1).splitlines() if l.strip()]
        if len(lineas) >= 3:
            componentes.append({
                "ref": _normalizar_id(lineas[0]),
                "tipo": _normalizar_id(lineas[1]),
                "valor": _normalizar_id(lineas[2]),
            })

    # Bloques de nodo/conexión: contenido entre ( y )
    for match in re.finditer(r"\((.*?)\)", texto, re.DOTALL):
        lineas = [l.strip() for l in match.group(1).splitlines() if l.strip()]
        if len(lineas) >= 2:
            nodo_nombre = _normalizar_id(lineas[0])
            conexiones = []
            for linea in lineas[1:]:
                partes = linea.split(",")
                if len(partes) == 2:
                    ref = _normalizar_id(partes[0])
                    pin = _normalizar_id(partes[1])
                    conexiones.append((ref, pin))
            if conexiones:
                nodos.append({"nodo": nodo_nombre, "conexiones": conexiones})

    return componentes, nodos


def generar_prolog(componentes: list[dict], nodos: list[dict]) -> str:
    """
    Genera el contenido del archivo .pl con hechos Prolog.

    Produce dos secciones:
      - componente(ref, tipo, 'valor').
      - conexion(nodo, ref, pin).
    """
    lineas = []

    # --- Hechos de componentes ---
    lineas.append("% ============================================")
    lineas.append("% Hechos de componentes")
    lineas.append("% ============================================")
    for c in componentes:
        ref = _escapar_prolog(c["ref"])
        tipo = _escapar_prolog(c["tipo"])
        valor = _escapar_prolog(c["valor"])
        lineas.append(f"componente({ref}, {tipo}, '{valor}').")

    lineas.append("")

    # --- Hechos de conexiones ---
    lineas.append("% ============================================")
    lineas.append("% Hechos de conexiones")
    lineas.append("% ============================================")
    for nodo in nodos:
        nodo_id = _escapar_prolog(nodo["nodo"])
        for ref, pin in nodo["conexiones"]:
            ref_esc = _escapar_prolog(ref)
            pin_esc = _escapar_prolog(pin)
            lineas.append(f"conexion({nodo_id}, {ref_esc}, {pin_esc}).")

    return "\n".join(lineas) + "\n"


def parse_tango_netlist(file_path: str, output_prolog_path: str) -> str:
    """
    Función principal: lee un netlist Tango, lo parsea y genera un archivo .pl.

    Args:
        file_path: Ruta al archivo .NET en formato Tango.
        output_prolog_path: Ruta de salida para el archivo .pl.

    Returns:
        Contenido generado del archivo .pl.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No se encontró el archivo: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        contenido = f.read()

    componentes, nodos = parse_bloques(contenido)
    salida = generar_prolog(componentes, nodos)

    with open(output_prolog_path, "w", encoding="utf-8") as f:
        f.write(salida)

    return salida


# ============================================================
# Bloque de ejemplo de uso
# ============================================================
if __name__ == "__main__":
    # Rutas de ejemplo (ajustar según entorno)
    dir_base = os.path.join(os.path.dirname(__file__), "..", "..", "Example")
    dir_netlists = os.path.join(dir_base, "Netlists")
    dir_prolog = os.path.join(dir_base, "Prolog")

    ejemplos = [
        ("Circuito_Basico.NET", "circuito_bueno.pl"),
        ("Circuito_Basico_Malo.NET", "circuito_malo.pl"),
        ("Divisor_Tension.NET", "divisor_tension.pl"),
    ]

    for entrada, salida in ejemplos:
        ruta_entrada = os.path.join(dir_netlists, entrada)
        ruta_salida = os.path.join(dir_prolog, salida)

        if not os.path.isfile(ruta_entrada):
            print(f"[AVISO] Saltando {entrada} — archivo no encontrado")
            continue

        print(f"Parseando: {entrada}")
        resultado = parse_tango_netlist(ruta_entrada, ruta_salida)
        print(resultado)
        print(f" -> Generado: {ruta_salida}\n")
