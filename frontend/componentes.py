"""
Componentes dinámicos de visualización de ALDICE.

Funciones reutilizables que renderizan en Streamlit los diagnósticos
lógicos generados por Prolog (reglas_diagnostico.pl) y los pasos de
mitigación recuperados de la memoria de casos (historial.json).

Cada componente es agnóstico de la fuente de datos (consola o web)
y sigue el mismo esquema de datos que devuelve el pipeline. Las
fichas usan las clases del sistema de diseño (frontend/estilos.py).
"""

import html

import streamlit as st

from modulos.modulo3.memoria_casos import registrar_feedback

_CLAVES_ALERTAS = (
    "cortocircuitos",
    "caminos_abiertos",
    "fuentes_cortocircuito",
    "nodos_sobrecargados",
)

# Severidad por tipo de fallo: (clase ficha, nombre legible)
_FALLO_SEVERIDAD = {
    "cortocircuito_fuente": ("critica", "Fuente en cortocircuito"),
    "cortocircuito": ("critica", "Cortocircuito"),
    "camino_abierto": ("advertencia", "Camino abierto"),
    "nodo_sobrecargado": ("informativa", "Nodo sobrecargado"),
}
_FALLO_DEFECTO = ("critica", "Fallo detectado")

# Color de chip por prioridad de mitigación
_PRIORIDAD_CHIP = {
    "critica": ("chip-critico", "crítica"),
    "alta": ("chip-advertencia", "alta"),
    "media": ("", "media"),
    "baja": ("", "baja"),
}


def _esc(texto) -> str:
    """Escapa texto dinámico para incrustarlo en HTML."""
    return html.escape(str(texto))


def _seccion(titulo: str) -> None:
    """Encabezado de sección estilo serigrafía."""
    st.markdown(
        f'<div class="aldice-seccion">{_esc(titulo)}</div>',
        unsafe_allow_html=True,
    )


def _ficha(severidad: str, badge: str, titulo: str, cuerpo: str, regla: str) -> None:
    """
    Ficha de fallo estilo serigrafía.

    Args:
        severidad: critica | advertencia | informativa | ok.
        badge: referencia corta del componente (mono, ej. "V1").
        titulo: nombre del fallo.
        cuerpo: descripción en una o dos líneas.
        regla: procedencia técnica (regla Prolog o caso de memoria).
    """
    bloques = f"""
          <div class="ficha-titulo">
            <span class="ficha-badge">{_esc(badge)}</span>
            <span class="ficha-nombre">{_esc(titulo)}</span>
          </div>
          <div class="ficha-cuerpo">{cuerpo}</div>"""
    if regla:
        bloques += f'\n          <div class="ficha-regla">{regla}</div>'
    st.markdown(
        f"""
        <div class="aldice-ficha ficha {severidad}">{bloques}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _chip(ref: str, pin) -> str:
    """Chip de pin estilo serigrafía: V1·1."""
    return f'<span class="aldice-chip">{_esc(ref)}·{_esc(pin)}</span>'


# ============================================
# Ruta del pipeline (Parseo → Memoria → Prolog)
# ============================================

def render_ruta(pipeline: dict) -> None:
    """
    Indicador de ruta del diagnóstico: ilumina el motor que resolvió
    el caso (codifica la arquitectura memoria-primero).
    """
    fuente = pipeline["resultados_diagnostico"].get("fuente", "prolog")
    similares = pipeline.get("similares", [])
    detalle_memoria = (
        f"coincidencia {similares[0]['similitud']:.2f}" if similares else "sin coincidencias"
    )
    if fuente == "memoria":
        clase_memoria, detalle_prolog = "activo", "no requerido"
    else:
        clase_memoria, detalle_prolog = "hecho", "ejecutado"

    pasos = [
        ("hecho", "PARSEO", "netlist leído"),
        (clase_memoria, "MEMORIA DE CASOS", detalle_memoria),
        ("activo" if fuente != "memoria" else "", "MOTOR PROLOG", detalle_prolog),
    ]
    segmentos = []
    for i, (clase, nombre, detalle) in enumerate(pasos):
        if i > 0:
            segmentos.append('<div class="ruta-enlace"></div>')
        clase_css = f"ruta-paso {clase}" if clase else "ruta-paso"
        segmentos.append(
            f"""
            <div class="{clase_css}">
              <span class="ruta-led"></span>
              <div class="ruta-texto">
                <div class="ruta-nombre">{nombre}</div>
                <div class="ruta-detalle">{detalle}</div>
              </div>
            </div>
            """
        )
    st.markdown(
        f'<div class="aldice-ruta">{"".join(segmentos)}</div>',
        unsafe_allow_html=True,
    )


# ============================================
# Panel lateral: circuito cargado y topología
# ============================================

def render_circuito_cargado(pipeline: dict) -> None:
    """Tarjeta resumen del circuito analizado (sidebar)."""
    tipos = sorted({c["tipo"] for c in pipeline["componentes"]})
    chips_tipos = "".join(
        f'<span class="aldice-chip">{_esc(tipo)}</span>' for tipo in tipos
    )
    st.markdown(
        f"""
        <div class="aldice-ficha ficha informativa" style="margin-top:14px">
          <div class="ficha-titulo">
            <span class="ficha-nombre">Circuito cargado</span>
          </div>
          <div class="ficha-cuerpo">
            {_esc(pipeline['nombre'])}<br/>
            {len(pipeline['componentes'])} componentes · {len(pipeline['conexiones'])} nodos
          </div>
          <div style="margin-top:8px">{chips_tipos}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_topologia(pipeline: dict) -> None:
    """
    Nodos del circuito como buses con sus pines en chips.
    Los nodos involucrados en fallos se marcan en rojo.
    """
    resultados = pipeline["resultados_diagnostico"]
    nodos_fallo = {
        a["nodo"]
        for clave in ("cortocircuitos", "fuentes_cortocircuito", "nodos_sobrecargados")
        for a in resultados.get(clave, [])
    }

    _seccion("Topología del circuito")
    for nodo in pipeline["conexiones"]:
        clase_fallo = "en-fallo" if nodo["nodo"] in nodos_fallo else ""
        chips = "".join(_chip(ref, pin) for ref, pin in nodo["conexiones"])
        st.markdown(
            f"""
            <div class="aldice-nodo {clase_fallo}">
              <div class="nodo-nombre">{_esc(nodo['nodo'])}</div>
              {chips}
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================
# Secciones agregadas del área principal
# ============================================

def render_resumen(pipeline: dict) -> None:
    """Muestra métricas resumidas del diagnóstico."""
    resultados = pipeline["resultados_diagnostico"]
    alertas = [resultados.get(k, []) for k in _CLAVES_ALERTAS]
    if resultados.get("fuente") == "memoria" and pipeline["similares"]:
        alertas_activas = len(pipeline["similares"])
        label = "Casos recuperados"
    else:
        alertas_activas = sum(len(v) for v in alertas)
        label = "Fallos detectados"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(label, alertas_activas)
    c2.metric("Casos similares", len(pipeline["similares"]))
    c3.metric("Componentes", len(pipeline["componentes"]))
    c4.metric("Nodos", len(pipeline["conexiones"]))


def render_fallos(pipeline: dict) -> None:
    """Renderiza todos los fallos detectados (Prolog o memoria de casos)."""
    _seccion("Fallos detectados")

    resultados = pipeline["resultados_diagnostico"]

    # Fallo recuperado de memoria: Prolog no se ejecutó, así que los
    # resultados están vacíos; la información vive en los casos similares.
    if resultados.get("fuente") == "memoria" and pipeline["similares"]:
        for s in pipeline["similares"]:
            _render_fallo_memoria(s)
        return

    if not any(len(resultados.get(k, [])) > 0 for k in _CLAVES_ALERTAS):
        _ficha(
            "ok",
            "OK",
            "Sin fallos",
            "No se detectaron anomalías en el circuito.",
            "",
        )
        return

    for alerta in resultados["fuentes_cortocircuito"]:
        _ficha(
            "critica",
            alerta["componente"],
            "Fuente en cortocircuito",
            f"Nodo <code>{_esc(alerta['nodo'])}</code>: "
            f"ambos terminales de la fuente unidos.",
            "alerta_fuente_cortocircuito/2 · vsource con pines 1–2 en el mismo nodo",
        )

    for alerta in resultados["cortocircuitos"]:
        _ficha(
            "critica",
            alerta["componente"],
            "Cortocircuito",
            f"Nodo <code>{_esc(alerta['nodo'])}</code>: "
            f"pin {_esc(alerta['pin1'])} ↔ pin {_esc(alerta['pin2'])}.",
            "alerta_cortocircuito/4 · pines del mismo componente en un nodo",
        )

    for alerta in resultados["caminos_abiertos"]:
        _ficha(
            "advertencia",
            alerta["componente"],
            "Camino abierto",
            f"Pin {_esc(alerta['pin'])} sin conexión de retorno.",
            "alerta_camino_abierto/2 · pin conectado a un nodo aislado",
        )

    for alerta in resultados["nodos_sobrecargados"]:
        _ficha(
            "informativa",
            alerta["nodo"],
            "Nodo sobrecargado",
            f"{alerta['conexiones']} conexiones sobre el mismo nodo.",
            "alerta_nodo_sobrecargado/2 · más de 4 conexiones",
        )


def _render_fallo_memoria(simil: dict) -> None:
    """Renderiza un fallo recuperado de la memoria de casos."""
    caso = simil["caso"]
    firma = caso.get("firma", {})
    tipos = firma.get("tipo_fallo") or caso.get("etiquetas") or ["otro"]
    componentes = firma.get("componentes_involucrados") or []

    severidad, titulo = _FALLO_SEVERIDAD.get(tipos[0], _FALLO_DEFECTO)
    badge = ", ".join(c.upper() for c in componentes[:2]) or "MEM"

    if componentes:
        cuerpo = "Componente(s): " + ", ".join(
            f"<code>{_esc(c)}</code>" for c in componentes
        )
    else:
        cuerpo = "Componente no identificado en el caso guardado."

    mitigacion = caso.get("mitigacion", {})
    regla = (
        f"{_esc(caso['id'])} · similitud {simil['similitud']:.3f} · memoria de casos"
        + (f" · {mitigacion['accion']}" if mitigacion.get("accion") else "")
    )
    _ficha(severidad, badge, titulo, cuerpo, regla)


# ============================================
# Soluciones y retroalimentación
# ============================================

def _votar(caso_id: str, util: bool) -> None:
    """Callback de los botones de retroalimentación (C3)."""
    fb = registrar_feedback(caso_id, util=util)
    st.session_state[f"feedback_votos_{caso_id}"] = fb
    st.session_state[f"feedback_registrado_{caso_id}"] = True


def render_solucion(caso: dict, similitud: float) -> None:
    """
    Renderiza una solución (caso de memoria) con pasos de mitigación.

    Compatible con el esquema de historial.json, aunque en el futuro la
    mitigación pudiera provenir de un plan PDDL con la misma estructura.

    Los botones de retroalimentación se deshabilitan tras el primer voto
    (por sesión) para evitar clics repetidos sobre el mismo caso.
    """
    mitigacion = caso["mitigacion"]
    prioridad = mitigacion.get("prioridad", "media")
    chip_clase, prioridad_texto = _PRIORIDAD_CHIP.get(prioridad, ("", prioridad))
    caso_id = caso["id"]
    votado = st.session_state.get(f"feedback_registrado_{caso_id}", False)

    with st.container(border=True):
        st.markdown(f"**{mitigacion['accion']}**")
        st.markdown(
            f'<span class="aldice-chip chip-cobre">SIMILITUD {similitud:.2f}</span>'
            f'<span class="aldice-chip {chip_clase}">PRIORIDAD {prioridad_texto.upper()}</span>',
            unsafe_allow_html=True,
        )
        st.divider()
        for i, paso in enumerate(mitigacion.get("pasos", []), 1):
            st.write(f"**{i}.** {paso}")
        if caso.get("etiquetas"):
            etiquetas = "".join(
                f'<span class="aldice-chip">{_esc(e)}</span>'
                for e in caso["etiquetas"]
            )
            st.markdown(etiquetas, unsafe_allow_html=True)

        feedback = st.session_state.get(
            f"feedback_votos_{caso_id}", caso.get("feedback", {})
        )
        votos_util = feedback.get("votos_util", 0)
        votos_no_util = feedback.get("votos_no_util", 0)
        st.caption(f"Retroalimentación — útiles: {votos_util} · fallidos: {votos_no_util}")

        c1, c2 = st.columns(2)
        c1.button(
            "Sirvió",
            key=f"util_{caso_id}",
            disabled=votado,
            on_click=_votar,
            args=(caso_id, True),
        )
        c2.button(
            "No funcionó",
            key=f"no_util_{caso_id}",
            disabled=votado,
            on_click=_votar,
            args=(caso_id, False),
        )
        if votado:
            st.caption("Retroalimentación registrada para este caso.")


def render_soluciones(pipeline: dict) -> None:
    """Renderiza la sección de soluciones recuperadas de memoria."""
    _seccion("Soluciones")

    if not pipeline["tiene_fallos"]:
        st.caption("Circuito sin fallos: no se requieren soluciones.")
        return

    if pipeline["similares"]:
        st.caption("Mitigaciones recuperadas de la memoria de casos.")
        for s in pipeline["similares"][:3]:
            render_solucion(s["caso"], s["similitud"])
    else:
        st.warning("Sin soluciones previas conocidas para este fallo.")
        if pipeline["caso_guardado"]:
            st.info(
                f"Fallo nuevo: se guardó el caso **{pipeline['caso_guardado']}** "
                f"en la memoria para futuros diagnósticos."
            )
