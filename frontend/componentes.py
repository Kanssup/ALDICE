"""
Componentes dinámicos de visualización de ALDICE.

Funciones reutilizables que renderizan en Streamlit los diagnósticos
lógicos generados por Prolog (reglas_diagnostico.pl) y los pasos de
mitigación recuperados de la memoria de casos (historial.json).

Cada componente es agnóstico de la fuente de datos (consola o web)
y sigue el mismo esquema de datos que devuelve el pipeline.
"""

import streamlit as st

# Mapa de colores para prioridades de mitigación
_PRIORIDAD_COLOR = {
    "critica": ":red",
    "alta": ":orange",
    "media": ":yellow",
    "baja": ":green",
}


# ============================================
# Alertas individuales (un fallo = un componente)
# ============================================

def alerta_fuente_cortocircuito(alerta: dict) -> None:
    """Renderiza una fuente de voltaje en cortocircuito."""
    with st.expander("🔴 Fuente en cortocircuito", expanded=True):
        st.write(
            f"Nodo **{alerta['nodo']}**: la fuente **{alerta['componente']}** "
            f"tiene ambos terminales unidos."
        )
        st.caption("Regla: `alerta_fuente_cortocircuito/2` — vsource con pines 1 y 2 en el mismo nodo.")


def alerta_cortocircuito(alerta: dict) -> None:
    """Renderiza un cortocircuito entre pines del mismo componente."""
    with st.expander("🔴 Cortocircuito", expanded=True):
        st.write(
            f"Nodo **{alerta['nodo']}**: **{alerta['componente']}** "
            f"pin {alerta['pin1']} ↔ pin {alerta['pin2']}."
        )
        st.caption("Regla: `alerta_cortocircuito/4` — pines del mismo componente en un nodo.")


def alerta_camino_abierto(alerta: dict) -> None:
    """Renderiza un pin sin conexión de retorno."""
    with st.expander("🟡 Camino abierto", expanded=True):
        st.write(
            f"**{alerta['componente']}** — pin **{alerta['pin']}** "
            f"sin conexión de retorno."
        )
        st.caption("Regla: `alerta_camino_abierto/2` — pin conectado a un nodo aislado.")


def alerta_nodo_sobrecargado(alerta: dict) -> None:
    """Renderiza un nodo con exceso de conexiones."""
    with st.expander("🔵 Nodo sobrecargado", expanded=True):
        st.write(
            f"Nodo **{alerta['nodo']}** con **{alerta['conexiones']}** conexiones."
        )
        st.caption("Regla: `alerta_nodo_sobrecargado/2` — más de 4 conexiones.")


# ============================================
# Secciones agregadas
# ============================================

def render_resumen(pipeline: dict) -> None:
    """Muestra métricas resumidas del diagnóstico."""
    resultados = pipeline["resultados_diagnostico"]
    total_fallos = sum(len(v) for v in resultados.values())

    c1, c2, c3 = st.columns(3)
    c1.metric("Fallos detectados", total_fallos)
    c2.metric("Casos similares", len(pipeline["similares"]))
    c3.metric("Componentes", len(pipeline["componentes"]))


def render_fallos(resultados: dict) -> None:
    """Renderiza todos los fallos detectados por Prolog."""
    st.markdown("### 🔍 Fallos detectados")

    alguna_alerta = any(len(v) > 0 for v in resultados.values())

    if not alguna_alerta:
        st.success("✅ No se detectaron fallos en el circuito.")
        return

    for alerta in resultados["fuentes_cortocircuito"]:
        alerta_fuente_cortocircuito(alerta)

    for alerta in resultados["cortocircuitos"]:
        alerta_cortocircuito(alerta)

    for alerta in resultados["caminos_abiertos"]:
        alerta_camino_abierto(alerta)

    for alerta in resultados["nodos_sobrecargados"]:
        alerta_nodo_sobrecargado(alerta)


def render_solucion(caso: dict, similitud: float) -> None:
    """
    Renderiza una solución (caso de memoria) con pasos de mitigación.

    Compatible con el esquema de historial.json, aunque en el futuro la
    mitigación pudiera provenir de un plan PDDL con la misma estructura.
    """
    mitigacion = caso["mitigacion"]
    prioridad = mitigacion.get("prioridad", "media")
    color = _PRIORIDAD_COLOR.get(prioridad, "gray")

    with st.container(border=True):
        st.markdown(f"**{mitigacion['accion']}**")
        st.markdown(
            f"Similitud: **{similitud}** · Prioridad: {color} **{prioridad}**"
        )
        st.divider()
        st.caption("Pasos de mitigación:")
        for i, paso in enumerate(mitigacion.get("pasos", []), 1):
            st.write(f"{i}. {paso}")
        if caso.get("etiquetas"):
            etiquetas = ", ".join(f"`{e}`" for e in caso["etiquetas"])
            st.caption(f"Etiquetas: {etiquetas}")


def render_soluciones(pipeline: dict) -> None:
    """Renderiza la sección de soluciones recuperadas de memoria."""
    st.divider()
    st.markdown("### 💡 Soluciones")

    if not pipeline["tiene_fallos"]:
        st.caption("Circuito sin fallos: no se requieren soluciones.")
        return

    if pipeline["similares"]:
        st.caption("Soluciones recuperadas de la memoria de casos similares.")
        for s in pipeline["similares"][:3]:
            render_solucion(s["caso"], s["similitud"])
    else:
        st.warning("No se encontraron soluciones previas conocidas.")
        if pipeline["caso_guardado"]:
            st.info(
                f"📝 El fallo es nuevo. Se guardó el caso **{pipeline['caso_guardado']}** "
                f"en la memoria para futuros diagnósticos."
            )