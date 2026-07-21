# Sistema de Diagnóstico y Planificación de Fallos en Prototipos Electrónicos

## 📋 Descripción del Proyecto
La aplicación implementa una arquitectura de **Inteligencia Artificial híbrida**. Combina el análisis de casos mediante memoria local, inferencia lógica a través de un motor en **PROLOG**, y generación de planes de acción mediante el estándar **PDDL**. El sistema extrae la topología del circuito desde archivos de texto Netlist (formatos SDF o SPICE) exportados desde el entorno de simulación **Proteus**.

## 🚀 Características Principales
* **Parsing Automatizado:** Extracción y traducción de la topología de circuitos desde Netlists.
* **IA Híbrida:** 
    * **Razonamiento Analógico:** Gestión de historial de fallos a través de archivos **JSON**.
    * **Razonamiento Deductivo:** Motor de inferencia en **PROLOG** que utiliza búsqueda en profundidad y *backtracking* para aislar causas raíz.
* **Planificación Automática:** Generación de planes de acción deterministas mediante **PDDL** (modelo STRIPS) para guiar la resolución de fallos.
* **Interfaz Gráfica:** GUI construida con librerías nativas de Python (PyQt/CustomTkinter).

## 🛠️ Tecnologías Utilizadas
* **Backend:** Python.
* **Lógica de Diagnóstico:** PROLOG (integrado mediante librerías bidireccionales).
* **Planificación:** PDDL (estándar STRIPS).
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
├── Example/
│   ├── Circuito_Basico.NET          # Netlist ejemplo (circuito correcto)
│   ├── Circuito_Basico.PNG
│   ├── Circuito_Basico_Malo.NET     # Netlist ejemplo (circuito con fallo)
│   └── Circuito_Basico_Malo.PNG
└── modulos/
    ├── __init__.py
    └── modulo1/                     # Módulo de Extracción y Traducción
        ├── __init__.py
        └── netlist_parser.py        # Parser de Netlists Tango → hechos Prolog
```

## License

MIT License. See [LICENSE](LICENSE) for details.
