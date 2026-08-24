"""
Sistema de diseño de ALDICE — dirección "máscara de soldadura".

Tokens y estilos centralizados que visten la interfaz Streamlit:
verde placa profundo, serigrafía en IBM Plex Mono para referencias
y nodos, acento cobre para el elemento activo. La inyección se hace
una sola vez por rerun desde app.py.
"""

import streamlit as st

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
  --fondo: #122A20;
  --superficie: #1B3A2C;
  --superficie-2: #21453A;
  --borde: #2C5240;
  --texto: #EAF2EC;
  --texto-suave: #9DB8AA;
  --cobre: #DE8F5F;
  --cobre-suave: rgba(222, 143, 95, 0.14);
  --critico: #E4572E;
  --advertencia: #F2B84B;
  --ok: #7FB069;
  --fuente-cuerpo: 'IBM Plex Sans', 'Segoe UI', system-ui, sans-serif;
  --fuente-mono: 'IBM Plex Mono', ui-monospace, 'Cascadia Mono', monospace;
}

/* ---------- Base ---------- */
.stApp {
  background: var(--fondo);
  color: var(--texto);
  font-family: var(--fuente-cuerpo);
}
[data-testid="stHeader"] {
  background: transparent;
}
h1, h2, h3, h4 {
  font-family: var(--fuente-cuerpo);
  color: var(--texto);
  letter-spacing: -0.01em;
}
p, li {
  color: var(--texto);
}

/* Ancho legible del contenido principal, centrado.
   !important: el contenedor lo gestiona CSS-in-JS de Streamlit. */
[data-testid="stMain"] [data-testid="stMainBlockContainer"],
[data-testid="stMainBlockContainer"].block-container {
  max-width: min(1060px, 100%) !important;
  margin-left: auto !important;
  margin-right: auto !important;
}

code {
  font-family: var(--fuente-mono);
  background: var(--superficie-2);
  border: 1px solid var(--borde);
  border-radius: 4px;
  padding: 0.05em 0.35em;
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
  background: #0F2119;
  border-right: 1px solid var(--borde);
}
[data-testid="stSidebar"] * {
  color: var(--texto);
}

/* ---------- Uploader ---------- */
[data-testid="stFileUploaderDropzone"] {
  background: var(--superficie);
  border: 1px dashed var(--cobre);
  border-radius: 10px;
  transition: border-color 120ms ease, background-color 120ms ease;
}
[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploaderDropzone"]:focus-within {
  border-color: var(--cobre);
  background: var(--superficie-2);
}
[data-testid="stFileUploaderDropzoneInstructions"] button,
[data-testid="stFileUploaderDropzoneButton"] button {
  font-family: var(--fuente-cuerpo);
}

/* ---------- Métricas tipo lectura de instrumento ---------- */
[data-testid="stMetric"] {
  background: var(--superficie);
  border: 1px solid var(--borde);
  border-radius: 10px;
  padding: 14px 16px;
}
[data-testid="stMetricLabel"] p {
  font-family: var(--fuente-mono);
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--texto-suave);
}
[data-testid="stMetricValue"] {
  font-family: var(--fuente-mono);
  font-weight: 600;
  color: var(--texto);
}

/* ---------- Fichas de fallo (serigrafía) ---------- */
.aldice-ficha {
  background: var(--superficie);
  border: 1px solid var(--borde);
  border-left-width: 3px;
  border-radius: 10px;
  padding: 14px 18px;
  margin-bottom: 12px;
}
.aldice-ficha .ficha-titulo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.aldice-ficha .ficha-badge {
  font-family: var(--fuente-mono);
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  padding: 2px 9px;
  border-radius: 5px;
  white-space: nowrap;
}
.aldice-ficha .ficha-nombre {
  font-weight: 600;
}
.aldice-ficha .ficha-cuerpo {
  color: var(--texto);
  line-height: 1.5;
}
.aldice-ficha .ficha-regla {
  font-family: var(--fuente-mono);
  font-size: 0.74rem;
  color: var(--texto-suave);
  margin-top: 8px;
}
.ficha.critica { border-left-color: var(--critico); }
.ficha.critica .ficha-badge { background: rgba(228, 87, 46, 0.18); color: #FFB49E; }
.ficha.advertencia { border-left-color: var(--advertencia); }
.ficha.advertencia .ficha-badge { background: rgba(242, 184, 75, 0.16); color: #FFDCA0; }
.ficha.informativa { border-left-color: var(--cobre); }
.ficha.informativa .ficha-badge { background: var(--cobre-suave); color: var(--cobre); }
.ficha.ok { border-left-color: var(--ok); }
.ficha.ok .ficha-badge { background: rgba(127, 176, 105, 0.16); color: #B5DCa4; }

/* ---------- Chips (serigrafía) ---------- */
.aldice-chip {
  display: inline-block;
  font-family: var(--fuente-mono);
  font-size: 0.76rem;
  padding: 2px 9px;
  border-radius: 999px;
  border: 1px solid var(--borde);
  background: var(--superficie-2);
  color: var(--texto);
  margin: 2px 4px 2px 0;
  white-space: nowrap;
}
.aldice-chip.chip-cobre { border-color: var(--cobre); color: var(--cobre); }
.aldice-chip.chip-critico { border-color: var(--critico); color: #FFB49E; }
.aldice-chip.chip-advertencia { border-color: var(--advertencia); color: #FFDCA0; }

/* ---------- Ruta del pipeline ---------- */
.aldice-ruta {
  display: flex;
  align-items: center;
  gap: 0;
  background: var(--superficie);
  border: 1px solid var(--borde);
  border-radius: 10px;
  padding: 14px 20px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.ruta-paso {
  display: flex;
  align-items: center;
  gap: 9px;
}
.ruta-led {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--borde);
  flex-shrink: 0;
}
.ruta-texto .ruta-nombre {
  font-family: var(--fuente-mono);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.07em;
  color: var(--texto-suave);
}
.ruta-texto .ruta-detalle {
  font-size: 0.74rem;
  color: var(--texto-suave);
  opacity: 0.85;
}
.ruta-paso.hecho .ruta-led { background: var(--ok); }
.ruta-paso.activo .ruta-led {
  background: var(--cobre);
  box-shadow: 0 0 8px rgba(222, 143, 95, 0.7);
  animation: aldice-pulso 1.6s ease-in-out infinite;
}
.ruta-paso.activo .ruta-nombre { color: var(--cobre); }
.ruta-enlace {
  flex: 1 1 26px;
  min-width: 18px;
  height: 1px;
  background: var(--borde);
  margin: 0 12px;
}
@keyframes aldice-pulso {
  0%, 100% { box-shadow: 0 0 4px rgba(222, 143, 95, 0.4); }
  50% { box-shadow: 0 0 11px rgba(222, 143, 95, 0.85); }
}

/* ---------- Topología de nodos ---------- */
.aldice-nodo {
  background: var(--superficie);
  border: 1px solid var(--borde);
  border-radius: 10px;
  padding: 10px 14px;
  height: 100%;
}
.aldice-nodo.en-fallo {
  border-color: var(--critico);
  box-shadow: inset 0 0 0 1px rgba(228, 87, 46, 0.35);
}
.aldice-nodo .nodo-nombre {
  font-family: var(--fuente-mono);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: var(--cobre);
  margin-bottom: 7px;
}
.aldice-nodo.en-fallo .nodo-nombre { color: #FFB49E; }

/* ---------- Encabezados de sección ---------- */
.aldice-seccion {
  font-family: var(--fuente-mono);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--texto-suave);
  border-bottom: 1px solid var(--borde);
  padding-bottom: 6px;
  margin: 22px 0 12px 0;
}

/* ---------- Botones píldora ---------- */
.stButton > button {
  border-radius: 999px;
  border: 1px solid var(--borde);
  background: var(--superficie-2);
  color: var(--texto);
  font-family: var(--fuente-mono);
  font-size: 0.82rem;
  font-weight: 500;
  padding: 6px 18px;
  transition: border-color 120ms ease, background-color 120ms ease;
}
.stButton > button:hover {
  border-color: var(--cobre);
  color: var(--cobre);
  background: var(--cobre-suave);
}
.stButton > button:focus-visible {
  outline: 2px solid var(--cobre);
  outline-offset: 2px;
}
.stButton > button:disabled {
  opacity: 0.45;
  border-color: var(--borde);
  color: var(--texto-suave);
  background: var(--superficie-2);
}

/* ---------- Estado vacío / cabecera ---------- */
.aldice-vacio {
  text-align: center;
  padding: 64px 20px 40px;
  color: var(--texto-suave);
}
.aldice-vacio .vacio-marca {
  font-family: var(--fuente-mono);
  font-size: 2.4rem;
  font-weight: 600;
  letter-spacing: 0.26em;
  color: var(--cobre);
}
.hero-subtitulo {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--texto);
  margin-top: 10px;
  letter-spacing: 0.02em;
}
.hero-descripcion {
  max-width: 560px;
  margin: 18px auto 0;
  line-height: 1.65;
}
.hero-caps {
  display: flex;
  justify-content: center;
  gap: 14px;
  flex-wrap: wrap;
  max-width: 760px;
  margin: 28px auto 0;
}
.hero-cap {
  background: var(--superficie);
  border: 1px solid var(--borde);
  border-radius: 10px;
  padding: 14px 16px;
  width: 220px;
  text-align: left;
}
.hero-cap .cap-titulo {
  font-family: var(--fuente-mono);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  color: var(--cobre);
  margin-bottom: 6px;
}
.hero-cap .cap-texto {
  font-size: 0.84rem;
  line-height: 1.5;
  color: var(--texto-suave);
}
.hero-invitacion {
  font-family: var(--fuente-mono);
  font-size: 0.8rem;
  letter-spacing: 0.05em;
  margin-top: 30px;
}
.aldice-cabecera {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}
.aldice-cabecera .archivo {
  font-family: var(--fuente-mono);
  font-size: 0.86rem;
  color: var(--texto);
}
.aldice-estado {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: var(--fuente-mono);
  font-size: 0.78rem;
  letter-spacing: 0.07em;
  padding: 4px 12px;
  border-radius: 999px;
  border: 1px solid var(--borde);
}
.aldice-estado .led {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
.aldice-estado.estado-ok { color: var(--ok); border-color: rgba(127, 176, 105, 0.5); }
.aldice-estado.estado-ok .led { background: var(--ok); }
.aldice-estado.estado-fallo { color: #FFB49E; border-color: rgba(228, 87, 46, 0.5); }
.aldice-estado.estado-fallo .led { background: var(--critico); }

/* ---------- Accesibilidad ---------- */
@media (prefers-reduced-motion: reduce) {
  .ruta-paso.activo .ruta-led { animation: none; }
  [data-testid="stFileUploaderDropzone"],
  .stButton > button { transition: none; }
}
"""


def inyectar() -> None:
    """Inyecta el sistema de diseño una vez por ejecución del script."""
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)
