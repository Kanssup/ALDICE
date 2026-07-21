# AGENTS.md

## Project

ALDICE — Fault Diagnosis and Planning System for Electronic Prototypes.
Hybrid AI: case-based memory (JSON) + PROLOG inference + PDDL planning (STRIPS).
GUI: PyQt or CustomTkinter. Language: Python.

## Status

Greenfield — no source code, build system, or tests exist yet. Only README, LICENSE, and example data.

## Planned architecture

1. **Netlist parser** — reads Proteus `.NET` files, builds circuit topology graph
2. **Case memory** — stores past diagnoses as JSON, analogical matching
3. **PROLOG engine** — depth-first + backtracking for fault isolation (likely `pyswip`)
4. **PDDL planner** — STRIPS-based action plan generation (external planner)
5. **GUI** — load netlists, display diagnosis, present plans

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

- No established conventions yet — keep code clean and well-structured from the start
- Python project: follow PEP 8, use type hints
- No package manager or dependency files exist yet — set up `pyproject.toml` or `requirements.txt` as needed
