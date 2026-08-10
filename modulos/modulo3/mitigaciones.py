"""
Mitigaciones inteligentes por defecto (C2).

Genera la recomendación de reparación a partir del tipo de fallo y
del tipo de componente involucrado, de modo que los casos nuevos no
carguen siempre la plantilla genérica de "revisión manual". La
revisión manual queda como último recurso únicamente para fallos
combinados sin regla conocida.
"""

from typing import Any

_PRIORIDADES = {
    "cortocircuito_fuente": "critica",
    "cortocircuito": "critica",
    "camino_abierto": "media",
    "nodo_sobrecargado": "media",
}

_MITIGACION_MANUAL: dict[str, Any] = {
    "accion": "Requiere revisión manual del técnico",
    "pasos": [
        "Inspeccionar visualmente el circuito",
        "Verificar conexiones con multímetro",
        "Comparar con esquemático original",
    ],
    "prioridad": "alta",
}

# Reglas por tipo de fallo. En cortocircuito se refina según el
# tipo de componente involucrado.
_REGLA_CORTOCIRCUITO: dict[str, dict[str, Any]] = {
    "vsource": {
        "accion": "Verificar la soldadura y polaridad de la fuente de alimentación",
        "pasos": [
            "Medir continuidad entre los pines de la fuente",
            "Revisar si ambos terminales están unidos por un puente de estaño",
            "Verificar la polaridad indicada en el esquemático",
        ],
        "prioridad": "critica",
    },
    "resistor": {
        "accion": "Revisar que los pines de la resistencia no estén puenteados",
        "pasos": [
            "Inspeccionar visualmente los pines de la resistencia",
            "Comprobar separación entre pista y pasta",
            "Medir el valor real de la resistencia con multímetro",
        ],
        "prioridad": "critica",
    },
    "diode": {
        "accion": "Comprobar la orientación y soldadura del diodo",
        "pasos": [
            "Verificar el marcado de ánodo/cátodo",
            "Medir la caída en polarización directa",
            "Revisar posibles puentes de estaño entre pines",
        ],
        "prioridad": "critica",
    },
    "default": {
        "accion": "Verificar que los pines del componente no estén unidos entre sí",
        "pasos": [
            "Inspeccionar visualmente el área del componente",
            "Medir continuidad entre todos los pares de pines",
            "Rehacer la soldadura si se encuentra un puente",
        ],
        "prioridad": "critica",
    },
}

_REGLA_CAMINO_ABIERTO: dict[str, Any] = {
    "accion": "Restaurar la conexión de retorno del pin aislado",
    "pasos": [
        "Identificar el nodo al que debería conectarse el pin",
        "Verificar con multímetro la continuidad del tramo",
        "Añadir la traza o cable que completa el camino",
    ],
    "prioridad": "media",
}

_REGLA_NODO_SOBRECARGADO: dict[str, Any] = {
    "accion": "Redistribuir las conexiones del nodo sobrecargado",
    "pasos": [
        "Revisar el esquemático para reubicar uniones",
        "Añadir puntos de prueba intermedios",
        "Rediseñar el PCB si el fan-out supera el límite",
    ],
    "prioridad": "media",
}


def _refinar_cortocircuito(tipos_involucrados: list[str]) -> dict[str, Any]:
    for tipo in tipos_involucrados:
        if tipo in _REGLA_CORTOCIRCUITO:
            return _REGLA_CORTOCIRCUITO[tipo]
    return _REGLA_CORTOCIRCUITO["default"]


def generar_mitigacion(tipo_fallo: list[str], tipos_involucrados: list[str] | None = None) -> dict[str, Any]:
    """
    Sugiere una mitigación según el tipo de fallo dominante.

    Args:
        tipo_fallo: lista de categorías de fallo (de la firma).
        tipos_involucrados: tipos de componentes involucrados (opcional).

    Returns:
        dict con keys accion, pasos, prioridad.
    """
    tipos_involucrados = tipos_involucrados or []

    if not tipo_fallo or tipo_fallo == ["sin_fallo"]:
        return {
            "accion": "No se requiere intervención",
            "pasos": ["El circuito no presenta fallos detectados"],
            "prioridad": "baja",
        }

    if "cortocircuito_fuente" in tipo_fallo:
        fallo = "cortocircuito_fuente"
        regla = _REGLA_CORTOCIRCUITO["vsource"].copy()
        regla["accion"] = "Verificar la fuente de alimentación (ambos terminales en el mismo nodo)"
    elif "cortocircuito" in tipo_fallo:
        fallo = "cortocircuito"
        regla = _refinar_cortocircuito(tipos_involucrados)
    elif "camino_abierto" in tipo_fallo:
        fallo = "camino_abierto"
        regla = _REGLA_CAMINO_ABIERTO.copy()
    elif "nodo_sobrecargado" in tipo_fallo:
        fallo = "nodo_sobrecargado"
        regla = _REGLA_NODO_SOBRECARGADO.copy()
    else:
        regla = _MITIGACION_MANUAL.copy()
        return regla

    regla["prioridad"] = _PRIORIDADES[fallo]
    return regla