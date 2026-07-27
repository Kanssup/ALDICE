"""
ALDICE — Interfaz Web con Streamlit

Ejecución:
    streamlit run frontend/app.py
"""

import streamlit as st

st.set_page_config(
    page_title="ALDICE — Diagnóstico de Circuitos",
    page_icon="⚡",
    layout="centered",
)

st.title("⚡ ALDICE")
st.subheader("Asistente Lógico de Diagnóstico para Circuitos Electrónicos")
