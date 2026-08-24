# Registro de Issues y Decisiones

Este documento registra los issues del proyecto, su estado y las decisiones
de arquitectura tomadas, como referencia para futuras sesiones de desarrollo.

## Issues

| Fecha | Nº | Título | Estado | Notas / resolución |
|-------|----|--------|--------|---------------------|
| — | #4 | Implementación del Sistema de Razonamiento Analógico (Memoria JSON) | `completado` | Memoria de casos con similitud de firma y persistencia en `data/historial.json`. Rama `feat/memory_json`. |
| — | #6 | Integración y Orquestación de la Arquitectura de IA Híbrida | `superado` | Ver decisión D01. El valor restante se absorbe en el issue de mejoras de memoria. |
| 2026-08-10 | #11 | Mejora del razonamiento analógico — similitud estructural + retroalimentación | `completado` | Rama `feat/memoria-analogica`. Criterios C1–C4 en la sección siguiente. Verificado con `tests/sintetico.py`. |
| 2026-08-10 | — | Mejora del razonamiento analógico (C1–C4) | `superado` | Absorbido por el issue #11. Rama `feat/memoria-analogica`. Criterios C1–C4 verificados con `tests/sintetico.py`. |

## Decisión de arquitectura

### D01 — PDDL descartado como proveedor de soluciones

**Contexto:** El issue 6 exigía vincular el diagnóstico con un planificador PDDL
(modelo STRIPS) para generar planes de acción deterministas.

**Decisión:** El proyecto descarta los motores de planificación externos. La
**memoria de casos (JSON)** es la proveedora de soluciones y mitigaciones.

**Motivo:** El alcance es determinista y de dominio cerrado; la memoria basada en
casos cubre la generación de soluciones sin dependencias externas, y es
coherente con el enfoque de IA híbrida definido en el README.

**Consecuencia sobre issue 6:**
- Tarea 1 (parser → memoria): ya implementada.
- Tarea 2 (delegación: Prolog solo para fallos inéditos/ambiguos): se implementa
  con el patrón "memoria-primero" y la huella estructural (C1).
- Tarea 3 (PDDL/STRIPS): **obsoleta** por D01.
- Tarea 4 (pipeline secuencial reactivo en Streamlit): casi completa; se cierra
  con el disparo automático al subir el netlist.
- **Estado final:** `superado`.

## Issue #11 — Criterios de aceptación

- [x] **C1 — Similitud topológica invariante a referencias:** dos netlists con
      igual topología pero referencias renombradas (`v1/r1` vs `vcc/r4`) obtienen
      similitud ≥ umbral usando huella estructural de nodos/pines
      (`modulos/modulo3/{firma,similitud}.py`).
- [x] **C2 — Mitigación por defecto inteligente:** casos nuevos reciben
      recomendación según `tipo_fallo` + `componente`; la "validación manual"
      queda como último recurso (`mitigaciones.py`).
- [x] **C3 — Retroalimentación del usuario:** en la UI se marca "sirvió /
      no funcionó"; se persiste dentro del caso (`feedback`) y pondera búsquedas
      (`feedback.py`, `frontend/componentes.py`).
- [x] **C4 — Validación con datos sintéticos:** `tests/sintetico.py` genera
      variaciones conmutadas sin tocar `data/` real.