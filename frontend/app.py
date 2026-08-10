"""
ALDICE — Interfaz Web con Streamlit

Carga un archivo Netlist (.NET) de Proteus, lo guarda en uploads/
y ejecuta automáticamente el pipeline completo de diagnóstico
(parseo → memoria → Prolog según necesidad), mostrando los resultados
con componentes de visualización reutilizables.

El diagnóstico se dispara de forma reactiva en cuanto se sube el
archivo (no requiere botón). Los resultados se cachean por ruta para
evitar re-ejecutar el motor solo por re-renders de Streamlit.

Ejecución:
    streamlit run frontend/app.py
"""

import os
import sys

import streamlit as st

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _DIR_RAIZ)
_DIR_UPLOADS = os.path.join(_DIR_RAIZ, "uploads")
os.makedirs(_DIR_UPLOADS, exist_ok=True)

from aldice import ejecutar_pipeline
from frontend.componentes import render_resumen, render_fallos, render_soluciones

st.set_page_config(
    page_title="ALDICE — Diagnóstico de Circuitos",
    page_icon="⚡",
    layout="centered",
)


@st.cache_data
def _diagnosticar(ruta: str) -> dict:
    """Ejecuta el pipeline una sola vez por archivo subido."""
    return ejecutar_pipeline(ruta)


st.title("⚡ ALDICE")
st.subheader("Asistente Lógico de Diagnóstico para Circuitos Electrónicos")
st.divider()

uploaded = st.file_uploader(
    "Cargar Netlist de Proteus (formato .NET)",
    type=["net"],
    help="Archivo exportado desde Proteus en formato Tango",
)

if uploaded:
    ruta_destino = os.path.join(_DIR_UPLOADS, uploaded.name)
    with open(ruta_destino, "wb") as f:
        f.write(uploaded.getvalue())
    st.caption(f"Archivo guardado en: `uploads/{uploaded.name}`")

    # ============================================
    # Diagnóstico reactivo: se ejecuta al subir
    # ============================================
    with st.spinner("Ejecutando diagnóstico (parseo → memoria → Prolog)..."):
        pipeline = _diagnosticar(ruta_destino)

    st.divider()
    render_resumen(pipeline)

    fuente = pipeline["resultados_diagnostico"].get("fuente", "prolog")
    if fuente == "memoria":
        st.info("🧠 Fallo recuperado de la memoria de casos (Prolog no ejecutado).")
    render_fallos(pipeline["resultados_diagnostico"])
    render_soluciones(pipeline)
else:
    st.info("Sube un archivo .NET de Proteus para comenzar.")