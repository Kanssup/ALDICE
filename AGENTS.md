# AGENTS.md

## Project

ALDICE — Fault Diagnosis and Planning System for Electronic Prototypes.
Hybrid AI: case-based memory (JSON) + PROLOG inference.
GUI: Streamlit. Language: Python.

## Status

Working prototype. Pipeline memoria-primero in `aldice.py`; case memory
in `modulos/modulo3/` (split in firma/similitud/mitigaciones/feedback);
Prolog diagnostics in `modulos/modulo2/`; web UI in `frontend/`.
Synthetic validation: `tests/sintetico.py`.

## Architecture

1. **Netlist parser** — reads Proteus `.NET` files, builds circuit topology graph
2. **Case memory** — stores past diagnoses as JSON, analogical matching via
   structural fingerprint (C1), smart mitigations (C2), user feedback (C3)
3. **PROLOG engine** — depth-first + backtracking for fault isolation (`pyswip`),
   only for fault cases not recovered from memory (memoria-primero)
4. **GUI** — Streamlit, reactive on file upload

**PDDL planner is discarded** (decision D01, see ISSUES.md).

## Netlist format (`.NET`)

Two bracket styles:

- **Components** (`[...]`): ReferenceDesignator, Type, Value, footprint fields
- **Nets** (`(...)`): NetName, then RefDes.Pin pairs

Example — `Example/Circuito_Basico.NET`:
```
[
R1
R
220
Axial
]
(
N00001
R1,2
D1,1
)
```

Example netlist pairs (good vs faulty) are in `Example/` but currently untracked.

## Constraints

- Scope: resistive circuits, Arduino Uno/Mega/ESP32, I2C, relay modules, basic sensors
- Assumptions: total observability, static deterministic environment
- Proteus netlist input (SDF/SPICE `.NET` format)

## When adding code

- Python project: follow PEP 8, use type hints
- Dependencies: `pyswip`, `streamlit`; venv in `venv/`
- Test: `python tests/sintetico.py` (C1–C4, uses temp memory, never touches data/)
- Header script is `aldice.py`; the public memory API is the facade in
  `modulos/modulo3/memoria_casos.py` (firma / similitud / mitigaciones /
  feedback are internal submodules)
- `data/`, `uploads/`, `venv/`, `Example/Prolog/` are gitignored
