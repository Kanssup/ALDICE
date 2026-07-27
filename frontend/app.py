"""
ALDICE — Interfaz Web con Streamlit

Carga un archivo Netlist (.NET) de Proteus y ejecuta el pipeline
completo de diagnóstico: parseo → Prolog → memoria → resultados.

Ejecución:
    streamlit run frontend/app.py
"""

import os
import sys
import tempfile

import streamlit as st

# Agregar raíz del proyecto al path
_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _DIR_RAIZ)

from modulos.modulo1.netlist_parser import parse_bloques, generar_prolog
from modulos.modulo2.motor_diagnostico import diagnosticar
from modulos.modulo3.memoria_casos import (
    extraer_firma,
    buscar_casos_similares,
    guardar_caso,
)


# ============================================
# Configuración de la página
# ============================================
st.set_page_config(
    page_title="ALDICE — Diagnóstico de Circuitos",
    page_icon="⚡",
    layout="centered",
)

st.title("⚡ ALDICE")
st.subheader("Asistente Lógico de Diagnóstico para Circuitos Electrónicos")
st.divider()


# ============================================
# Carga de archivo
# ============================================
uploaded = st.file_uploader(
    "Cargar Netlist de Proteus (formato .NET)",
    type=["net"],
    help="Archivo exportado desde Proteus en formato Tango",
)

if uploaded:
    st.success(f"Archivo cargado: **{uploaded.name}**")

    # Guardar temporalmente
    tmp_net = tempfile.NamedTemporaryFile(
        mode="w", suffix=".net", delete=False, encoding="utf-8"
    )
    tmp_net.write(uploaded.getvalue().decode("utf-8"))
    tmp_net.close()

    # ============================================
    # Botón de diagnóstico
    # ============================================
    if st.button("🔍 Diagnosticar circuito", type="primary"):
        with st.spinner("Parseando netlist..."):
            with open(tmp_net.name, "r", encoding="utf-8") as f:
                contenido = f.read()
            componentes, conexiones = parse_bloques(contenido)

        st.info(f"**{len(componentes)}** componentes, **{len(conexiones)}** nodos")

        # --- Prolog ---
        with st.spinner("Ejecutando diagnóstico Prolog..."):
            hechos_pl = generar_prolog(componentes, conexiones)
            tmp_pl = tempfile.NamedTemporaryFile(
                mode="w", suffix=".pl", delete=False, encoding="utf-8"
            )
            tmp_pl.write(hechos_pl)
            tmp_pl.close()

            try:
                resultados = diagnosticar(tmp_pl.name)
            finally:
                os.unlink(tmp_pl.name)

        # --- Memoria ---
        with st.spinner("Buscando casos similares..."):
            firma = extraer_firma(resultados, componentes)
            similares = buscar_casos_similares(firma, umbral=0.5)

        tiene_fallos = any(len(v) > 0 for v in resultados.values())

        # ============================================
        # Mostrar resultados
        # ============================================
        if not tiene_fallos:
            st.success("✅ No se detectaron fallos en el circuito.")
        else:
            st.error("⚠️ Se detectaron fallos en el circuito")

            # Cortocircuitos
            if resultados.get("fuentes_cortocircuito"):
                st.markdown("### 🔴 Fuente en Cortocircuito")
                for alerta in resultados["fuentes_cortocircuito"]:
                    st.write(
                        f"- Nodo **{alerta['nodo']}**: "
                        f"fuente **{alerta['componente']}** unida en ambos terminales"
                    )

            if resultados.get("cortocircuitos"):
                st.markdown("### 🔴 Cortocircuito")
                for alerta in resultados["cortocircuitos"]:
                    st.write(
                        f"- Nodo **{alerta['nodo']}**: "
                        f"**{alerta['componente']}** pin {alerta['pin1']} ↔ pin {alerta['pin2']}"
                    )

            # Caminos abiertos
            if resultados.get("caminos_abiertos"):
                st.markdown("### 🟡 Camino Abierto")
                for alerta in resultados["caminos_abiertos"]:
                    st.write(
                        f"- **{alerta['componente']}** "
                        f"pin **{alerta['pin']}** sin conexión de retorno"
                    )

            # Nodos sobrecargados
            if resultados.get("nodos_sobrecargados"):
                st.markdown("### 🔵 Nodo Sobrecargado")
                for alerta in resultados["nodos_sobrecargados"]:
                    st.write(
                        f"- Nodo **{alerta['nodo']}**: "
                        f"{alerta['conexiones']} conexiones"
                    )

            # --- Mitigaciones ---
            if similares:
                st.divider()
                st.markdown("### 💡 Soluciones sugeridas")
                for s in similares[:3]:
                    caso = s["caso"]
                    with st.expander(
                        f"{caso['id']} — {caso['mitigacion']['accion']} "
                        f"(similitud: {s['similitud']})"
                    ):
                        st.write(f"**Descripción:** {caso['descripcion']}")
                        st.write(f"**Prioridad:** {caso['mitigacion']['prioridad']}")
                        st.write("**Pasos:**")
                        for i, paso in enumerate(caso["mitigacion"]["pasos"], 1):
                            st.write(f"{i}. {paso}")
            else:
                # Guardar caso nuevo
                id_caso = guardar_caso(
                    descripcion=f"Fallo detectado en {uploaded.name}",
                    firma=firma,
                    mitigacion={
                        "accion": "Requiere revisión manual del técnico",
                        "pasos": [
                            "Inspeccionar visualmente el circuito",
                            "Verificar conexiones con multímetro",
                            "Comparar con esquemático original",
                        ],
                        "prioridad": "alta",
                    },
                    componentes=componentes,
                    etiquetas=firma["tipo_fallo"],
                )
                st.warning(
                    f"📝 Caso nuevo guardado como **{id_caso}** "
                    f"(sin soluciones previas conocidas)"
                )

        os.unlink(tmp_net.name)

else:
    st.info("Sube un archivo .NET de Proteus para comenzar el diagnóstico.")

    with st.expander("ℹ️ ¿Qué hace ALDICE?"):
        st.write("""
        ALDICE analiza circuitos electrónicos detectando:
        - **Cortocircuitos** — pines del mismo componente en un nodo
        - **Caminos abiertos** — pines sin retorno de corriente
        - **Nodos sobrecargados** — exceso de conexiones

        Usa Prolog para el diagnóstico y una memoria JSON para
        recordar soluciones de fallos previos.
        """)
