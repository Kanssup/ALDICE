"""
ALDICE — Interfaz Web con Streamlit

Carga un archivo Netlist (.NET) de Proteus, lo guarda en uploads/
y ejecuta el pipeline completo de diagnóstico (parseo → Prolog → memoria).

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

        resultados = pipeline["resultados_diagnostico"]
        tiene_fallos = pipeline["tiene_fallos"]
        st.divider()

        if not tiene_fallos:
            st.success("✅ No se detectaron fallos en el circuito.")
        else:
            st.error("⚠️ Se detectaron fallos en el circuito")

            # ---------- 1. FALLOS ----------
            st.markdown("### 🔍 Fallos detectados")

            # Fuentes en cortocircuito
            if resultados["fuentes_cortocircuito"]:
                with st.expander("🔴 Fuente en cortocircuito", expanded=True):
                    for alerta in resultados["fuentes_cortocircuito"]:
                        st.write(
                            f"- Nodo **{alerta['nodo']}**: fuente "
                            f"**{alerta['componente']}** unida en ambos terminales"
                        )

            # Cortocircuitos (ya sin duplicados de fuentes)
            if resultados["cortocircuitos"]:
                with st.expander("🔴 Cortocircuito", expanded=True):
                    for alerta in resultados["cortocircuitos"]:
                        st.write(
                            f"- Nodo **{alerta['nodo']}**: **{alerta['componente']}** "
                            f"pin {alerta['pin1']} ↔ pin {alerta['pin2']}"
                        )

            # Caminos abiertos
            if resultados["caminos_abiertos"]:
                with st.expander("🟡 Camino abierto", expanded=True):
                    for alerta in resultados["caminos_abiertos"]:
                        st.write(
                            f"- **{alerta['componente']}** pin **{alerta['pin']}** "
                            f"sin conexión de retorno"
                        )

            # Nodos sobrecargados
            if resultados["nodos_sobrecargados"]:
                with st.expander("🔵 Nodo sobrecargado", expanded=True):
                    for alerta in resultados["nodos_sobrecargados"]:
                        st.write(
                            f"- Nodo **{alerta['nodo']}**: "
                            f"{alerta['conexiones']} conexiones"
                        )

            # ---------- 2. SOLUCIONES ----------
            st.divider()
            st.markdown("### 💡 Soluciones")

            if pipeline["similares"]:
                st.caption(
                    "Soluciones recuperadas de la memoria de casos similares"
                )
                for s in pipeline["similares"][:3]:
                    caso = s["caso"]
                    with st.container(border=True):
                        st.markdown(
                            f"**{caso['mitigacion']['accion']}** "
                            f"— similitud {s['similitud']}"
                        )
                        st.write(f"Prioridad: `{caso['mitigacion']['prioridad']}`")
                        st.write("Pasos:")
                        for i, paso in enumerate(caso["mitigacion"]["pasos"], 1):
                            st.write(f"{i}. {paso}")
            else:
                st.warning(
                    "No se encontraron soluciones previas conocidas."
                )
                if pipeline["caso_guardado"]:
                    st.info(
                        f"📝 El fallo es nuevo. Se guardó el caso "
                        f"**{pipeline['caso_guardado']}** en la memoria "
                        f"para futuros diagnósticos."
                    )
else:
    st.info("Sube un archivo .NET de Proteus para comenzar.")