"""
ALDICE — Interfaz Web con Streamlit

Carga un archivo Netlist (.NET) de Proteus, lo guarda en uploads/
y ejecuta el pipeline completo de diagnóstico (parseo → Prolog → memoria),
mostrando los resultados con componentes de visualización reutilizables.

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
    # Ejecutar diagnóstico
    # ============================================
    if st.button("🔍 Diagnosticar circuito", type="primary"):
        with st.spinner("Ejecutando diagnóstico (parseo → Prolog → memoria)..."):
            pipeline = ejecutar_pipeline(ruta_destino)

        st.divider()
        render_resumen(pipeline)
        render_fallos(pipeline["resultados_diagnostico"])
        render_soluciones(pipeline)
else:
    st.info("Sube un archivo .NET de Proteus para comenzar.")