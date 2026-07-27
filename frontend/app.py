"""
ALDICE — Interfaz Web con Streamlit

Ejecución:
    streamlit run frontend/app.py
"""

import os

import streamlit as st

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DIR_UPLOADS = os.path.join(_DIR_RAIZ, "uploads")
os.makedirs(_DIR_UPLOADS, exist_ok=True)

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
    st.success(f"Archivo guardado en: `uploads/{uploaded.name}`")
else:
    st.info("Sube un archivo .NET de Proteus para comenzar.")
