# Sistema de Diagnóstico y Planificación de Fallos en Prototipos Electrónicos

## 📋 Descripción del Proyecto
La aplicación implementa una arquitectura de **Inteligencia Artificial híbrida**. Combina el razonamiento analógico mediante memoria de casos en **JSON**, inferencia lógica a través de un motor en **PROLOG**, y una interfaz web de diagnóstico. El sistema extrae la topología del circuito desde archivos de texto Netlist (formato Tango) exportados desde el entorno de simulación **Proteus**.

> **Decisión de arquitectura (D01):** la generación de planes/acciones se resuelve con la memoria de casos (mitigaciones), descartando motores externos de planificación PDDL/STRIPS. Ver `ISSUES.md`.

## 🚀 Características Principales
* **Parsing Automatizado:** Extracción y traducción de la topología de circuitos desde Netlists.
* **IA Híbrida:**
    * **Razonamiento Analógico:** Memoria de casos en **JSON** con huella estructural invariante a renombrado de referencias (C1), mitigaciones inteligentes (C2) y retroalimentación del usuario que pondera búsquedas (C3).
    * **Razonamiento Deductivo:** Motor de inferencia en **PROLOG** con búsqueda en profundidad y *backtracking* para aislar causas raíz en fallos inéditos.
* **Pipeline memoria-primero:** se consulta la memoria con la huella estructural; Prolog solo se ejecuta para fallos no recuperados (delegación).
* **Interfaz Web:** GUI en **Streamlit** con diagnóstico reactivo al subir el netlist.
* **Validación sintética:** `tests/sintetico.py` verifica C1–C3 con circuitos generados y memoria temporal (C4).

## 🛠️ Tecnologías Utilizadas
* **Backend:** Python (3.10+).
* **Lógica de Diagnóstico:** PROLOG (SWI-Prolog vía `pyswip`).
* **Interfaz:** Streamlit.
* **Simulación:** Proteus (exportación de Netlists).
* **Persistencia:** JSON (aprendizaje analógico).

## 🔧 Alcance Técnico
El sistema está limitado a un ecosistema específico de componentes para garantizar la viabilidad del diagnóstico:
* Circuitos electrónicos resistivos básicos.
* Microcontroladores (familias Arduino Uno, Arduino Mega y ESP32).
* Protocolos de comunicación (conflictos en buses I2C).
* Actuadores de potencia (módulos de relés).
* Sensores analógicos y digitales básicos.

> **Nota:** El proyecto asume observabilidad total y un entorno estático determinista. No abarca la intervención física automatizada sobre el hardware.

## 📁 Estructura del Proyecto

```
ALDICE/
├── README.md
├── LICENSE
├── AGENTS.md
├── ISSUES.md                        # Registro de issues y decisiones (D01)
├── aldice.py                        # Pipeline memoria-primero (consola y web)
├── Example/
│   ├── Netlists/                    # Archivos de entrada desde Proteus
│   │   ├── Circuito_Basico.NET
│   │   ├── Circuito_Basico.PNG
│   │   ├── Circuito_Basico_Malo.NET
│   │   ├── Circuito_Basico_Malo.PNG
│   │   └── Divisor_Tension.NET
│   └── Prolog/                      # Hechos generados (no se sube a Git)
├── frontend/                        # Interfaz web Streamlit
│   ├── __init__.py
│   ├── app.py                       # App reactiva
│   └── componentes.py               # Widgets reutilizables de visualización
├── modulos/
│   ├── __init__.py
│   ├── modulo1/                     # Módulo de Extracción y Traducción
│   │   ├── __init__.py
│   │   └── netlist_parser.py
│   ├── modulo2/                     # Módulo de Motor de Inferencia
│   │   ├── __init__.py
│   │   ├── reglas_diagnostico.pl
│   │   └── motor_diagnostico.py
│   └── modulo3/                     # Módulo de Memoria Analógica
│       ├── __init__.py
│       ├── memoria_casos.py         # Fachada pública (API estable)
│       ├── persistencia.py          # IO del historial JSON
│       ├── firma.py                 # C1: huella estructural
│       ├── similitud.py             # C1: métrica invariante a referencias
│       ├── mitigaciones.py          # C2: recomendaciones por defecto
│       └── feedback.py              # C3: votos de utilidad intra-caso
├── tests/
│   └── sintetico.py                 # C4: validación con circuitos generados
├── data/                            # Datos generados (no se sube a Git)
│   └── historial.json
└── uploads/                         # Netlists subidos por la web (no en Git)
```

## ⚙️ Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/Kanssup/ALDICE.git
cd ALDICE

# 2. Requisito del sistema: SWI-Prolog
sudo apt-get install -y swi-prolog

# 3. Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install pyswip streamlit

# 4. Ejecutar interfaz web (diagnóstico reactivo al subir el archivo)
streamlit run frontend/app.py

# 5. O ejecutar por consola
python aldice.py Example/Netlists/Circuito_Basico_Malo.NET

# 6. Validación sintética del razonamiento analógico (C1–C4)
python tests/sintetico.py
```

## License

MIT License. See [LICENSE](LICENSE) for details.
