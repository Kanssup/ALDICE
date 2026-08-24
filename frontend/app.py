"""
ALDICE — Interfaz Web con Streamlit

Carga un archivo Netlist (.NET) de Proteus, lo guarda en uploads/
y ejecuta automáticamente el pipeline completo de diagnóstico
(parseo → memoria → Prolog según necesidad).

Layout: sidebar con el circuito cargado y su topología; área
principal con la ruta del pipeline, resumen, fallos y soluciones.
El sistema visual vive en frontend/estilos.py.

Ejecución:
    streamlit run frontend/app.py
"""

import html
import os
import sys

import streamlit as st

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _DIR_RAIZ)
_DIR_UPLOADS = os.path.join(_DIR_RAIZ, "uploads")
os.makedirs(_DIR_UPLOADS, exist_ok=True)

from aldice import ejecutar_pipeline
from frontend import estilos
from frontend.componentes import (
    render_circuito_cargado,
    render_fallos,
    render_resumen,
    render_ruta,
    render_soluciones,
    render_topologia,
)

st.set_page_config(
    page_title="ALDICE — Diagnóstico de Circuitos",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

estilos.inyectar()


@st.cache_data
def _diagnosticar(ruta: str) -> dict:
    """Ejecuta el pipeline una sola vez por archivo subido."""
    return ejecutar_pipeline(ruta)


_MARCA = """
<div style="padding: 6px 2px 14px 2px">
  <div style="font-family: var(--fuente-mono); font-size: 1.35rem; font-weight: 600;
              letter-spacing: 0.24em; color: var(--cobre)">ALDICE</div>
  <div style="font-size: 0.8rem; color: var(--texto-suave); margin-top: 4px">
    Diagnóstico lógico de circuitos electrónicos
  </div>
</div>
"""

_VACIO = """
<div class="aldice-vacio">
  <div class="vacio-marca">ALDICE</div>
  <h3 style="margin-top: 10px">Sube un netlist para comenzar</h3>
  <p class="vacio-linea">
    Carga un archivo <code>.NET</code> exportado desde Proteus en el panel lateral.
    ALDICE lo analiza al instante: busca el fallo en su memoria de casos y,
    si es inédito, lo deduce con su motor lógico Prolog.
  </p>
</div>
"""


def _estado_html(pipeline: dict) -> str:
    """LED de estado del análisis (ok / fallo) para la cabecera."""
    if pipeline["tiene_fallos"]:
        clase = "estado-fallo"
        texto = "FALLO DETECTADO"
        led = '<span class="led"></span>'
    else:
        clase = "estado-ok"
        texto = "SIN FALLOS"
        led = '<span class="led"></span>'
    return (
        f'<span class="aldice-estado {clase}">{led}{texto}</span>'
    )


# ============================================
# Sidebar: marca, carga y estructura del circuito
# ============================================

pipeline = None

with st.sidebar:
    st.markdown(_MARCA, unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Netlist de Proteus (.NET)",
        type=["net"],
        help="Archivo exportado desde Proteus en formato Tango",
        label_visibility="collapsed",
    )

    if uploaded:
        ruta_destino = os.path.join(_DIR_UPLOADS, uploaded.name)
        with open(ruta_destino, "wb") as f:
            f.write(uploaded.getvalue())

        with st.spinner("Analizando netlist..."):
            pipeline = _diagnosticar(ruta_destino)

        render_circuito_cargado(pipeline)
        render_topologia(pipeline)

# ============================================
# Área principal
# ============================================

if pipeline is None:
    st.markdown(_VACIO, unsafe_allow_html=True)
else:
    fuente = pipeline["resultados_diagnostico"].get("fuente", "prolog")

    st.markdown(
        f"""
        <div class="aldice-cabecera">
          <span class="archivo">{html.escape(pipeline['nombre'])}</span>
          {_estado_html(pipeline)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_ruta(pipeline)
    render_resumen(pipeline)
    render_fallos(pipeline)
    render_soluciones(pipeline)
