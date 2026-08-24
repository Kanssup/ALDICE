#!/usr/bin/env python3
"""
Validación sintética del razonamiento analógico (C4).

Genera netlists sintéticos con fallos conocidos y verifica, sobre una
memoria temporal (nunca toca `data/historial.json`), los criterios:

  C1 — Huella estructural invariante a renombrado de referencias/nodos.
  C2 — Mitigación inteligente por tipo de fallo + componente.
  C3 — Feedback intra-caso que pondera búsquedas futuras.
  Delegación — memoria-primero: Prolog solo para fallos inéditos.

Uso:
    python tests/sintetico.py
Salida: 0 en éxito, 1 si alguna aserción falla.
"""

import os
import sys
import tempfile

_DIR_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _DIR_RAIZ)

from aldice import ejecutar_pipeline  # noqa: E402
from modulos.modulo3 import memoria_casos as memoria  # noqa: E402


# ============================================
# Generadores sintéticos
# ============================================

class CircuitoSintetico:
    """Circuito fuente (V + R) con fallo opcional inyectado."""

    def __init__(self, pref: str, fallo: str | None):
        self.pref = pref
        self.fallo = fallo
        self.componentes = self._componentes()
        self.conexiones = self._conexiones()

    def _componentes(self):
        p = self.pref
        return [
            {"ref": f"v{p}", "tipo": "vsource", "valor": "5v"},
            {"ref": f"r{p}", "tipo": "resistor", "valor": "220"},
            {"ref": f"c{p}", "tipo": "cap10", "valor": "10uf"},
        ]

    def _conexiones(self):
        p = self.pref
        if self.fallo == "fuente_cortocircuito":
            # V1 y V2 unidos en el mismo nodo (fallo típico de la fuente)
            return [
                {"nodo": f"n{p}0", "conexiones": [(f"v{p}", "1"), (f"r{p}", "1"), (f"v{p}", "2"), (f"c{p}", "1")]},
                {"nodo": f"n{p}1", "conexiones": [(f"r{p}", "2"), (f"c{p}", "2")]},
            ]
        if self.fallo == "camino_abierto":
            # Pin aislado en nodo de un solo componente
            return [
                {"nodo": f"n{p}0", "conexiones": [(f"v{p}", "1"), (f"r{p}", "1"), (f"c{p}", "1")]},
                {"nodo": f"n{p}1", "conexiones": [(f"v{p}", "2"), (f"r{p}", "2")]},
                {"nodo": f"n{p}2", "conexiones": [(f"c{p}", "2")]},
            ]
        # Circuito sano (sin fallo): malla cerrada en dos nodos
        return [
            {"nodo": f"n{p}0", "conexiones": [(f"v{p}", "1"), (f"r{p}", "1"), (f"c{p}", "1")]},
            {"nodo": f"n{p}1", "conexiones": [(f"v{p}", "2"), (f"r{p}", "2"), (f"c{p}", "2")]},
        ]

    def a_netlist(self) -> str:
        """Serializa el circuito al formato Tango de Proteus."""
        bloques = []
        for c in self.componentes:
            bloques.append(
                f"[\n{c['ref']}\n{c['tipo'].upper()}\n{c['valor']}\n\n\n\n]"
            )
        for nodo in self.conexiones:
            lineas = [nodo["nodo"]]
            lineas += [f"{ref},{pin}" for ref, pin in nodo["conexiones"]]
            bloques.append(f"({chr(10).join(lineas)})")
        return "\n".join(bloques)


def escribir(directorio: str, nombre: str, circuito: CircuitoSintetico) -> str:
    ruta = os.path.join(directorio, f"{nombre}.NET")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(circuito.a_netlist())
    return ruta


# ============================================
# Aserciones de criterios
# ============================================

def check(condicion: bool, mensaje: str) -> None:
    estado = "[OK]" if condicion else "[FALLO]"
    print(f"  {estado} {mensaje}")
    if not condicion:
        raise AssertionError(mensaje)


def main() -> None:
    print("=" * 60)
    print("  Validación sintética C4 — razonamiento analógico")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as dir_circuitos:
        dir_historial = tempfile.mkdtemp()
        ruta_memoria = os.path.join(dir_historial, "historial.json")

        # Circuitos base
        base_malo = CircuitoSintetico("1", "fuente_cortocircuito")
        base_sano = CircuitoSintetico("2", None)
        base_abierto = CircuitoSintetico("3", "camino_abierto")

        ruta_malo = escribir(dir_circuitos, "fallo_fuente", base_malo)
        ruta_sano = escribir(dir_circuitos, "sano", base_sano)
        ruta_abierto = escribir(dir_circuitos, "camino_abierto_con_fallo", base_abierto)

        # ========================================
        # Delegación memoria-primero
        # ========================================
        print("\n[1/4] Delegación memoria-primero")
        p1 = ejecutar_pipeline(ruta_malo, ruta_historial=ruta_memoria)
        check(p1["resultados_diagnostico"].get("fuente") == "prolog",
              "Fallo inédito: se ejecutó Prolog (fuente='prolog')")
        check(p1["caso_guardado"] == "caso_001",
              f"Caso nuevo guardado ({p1['caso_guardado']})")
        check(p1["tiene_fallos"], "El circuito con fallo reporta fallos")

        p2 = ejecutar_pipeline(ruta_malo, ruta_historial=ruta_memoria)
        check(p2["resultados_diagnostico"].get("fuente") == "memoria",
              "Fallo conocido: se resolvió por memoria (fuente='memoria')")
        check(p2["caso_guardado"] is None,
              "Sin caso duplicado guardado en segunda pasada")

        p_sano = ejecutar_pipeline(ruta_sano, ruta_historial=ruta_memoria)
        check(not p_sano["tiene_fallos"], "Circuito sano no reporta fallos")
        check(p_sano["caso_guardado"] is None, "Circuito sano no se guarda en memoria")

        # ========================================
        # C1 — Invariante a renombrado
        # ========================================
        print("\n[2/4] C1 — Huella invariante a renombrado")
        renombrado = CircuitoSintetico("9", "fuente_cortocircuito")
        ruta_renombrado = escribir(dir_circuitos, "fallo_renombrado", renombrado)
        p_r = ejecutar_pipeline(ruta_renombrado, ruta_historial=ruta_memoria)
        check(p_r["resultados_diagnostico"].get("fuente") == "memoria",
              "Topología idéntica con refs/nodos renombrados se resuelve por memoria")
        check(p_r["similares"] and p_r["similares"][0]["similitud"] >= 0.5,
              f"Similitud {p_r['similares'][0]['similitud'] if p_r['similares'] else 0:.3f} ≥ 0.5")

        # Consultar las firmas directas para validar la métrica
        firma_caso = memoria.buscar_casos_similares(
            p_r["firma"], umbral=0.0, ruta=ruta_memoria
        )
        check(bool(firma_caso), "Firma renombrada matchea el caso almacenado")

        # Circuito distinto no debe matchear con 1.0
        p_otro = ejecutar_pipeline(ruta_abierto, ruta_historial=ruta_memoria)
        sim_abierto = p_otro["similares"][0]["similitud"] if p_otro["similares"] else 0.0
        check(sim_abierto < 1.0,
              f"Fallo de distinto tipo no es idéntico (similitud {sim_abierto:.3f} < 1.0)")

        # ========================================
        # C2 — Mitigación inteligente
        # ========================================
        print("\n[3/4] C2 — Mitigación inteligente")
        casos_c2 = memoria.buscar_casos_similares(p_r["firma"], ruta=ruta_memoria)
        caso = casos_c2[0]["caso"] if casos_c2 else None
        check(caso is not None, "El caso guardado es recuperable")
        mit = caso["mitigacion"] if caso else {}
        check(mit.get("prioridad") == "critica", "Fuente en cortocircuito → prioridad crítica")
        check("fuente" in mit.get("accion", "").lower(),
              f"Mitigación específica de fuente ('{mit.get('accion')}')")

        # === C3 — Feedback dentro del caso ===
        print("\n[4/4] C3 — Feedback intra-caso")
        # Firma de consulta con huella ligeramente distinta (nodo extra)
        # → la misma firma de fallo, similar pero no idéntica (base < 1.0).
        firma_c3 = dict(p_r["firma"])
        firma_c3["huella_estructural"] = p_r["firma"]["huella_estructural"] + [
            ["resistor:x", "vsource:y"],
        ]
        antes = memoria.buscar_casos_similares(firma_c3, ruta=ruta_memoria, umbral=0.0)
        base_b = antes[0]["similitud_base"]
        check(0.5 <= base_b < 1.0,
              f"Firma de consulta con base intermedia ({base_b:.3f})")

        memoria.registrar_feedback("caso_001", util=True,
                                   comentario="Funcionó en banco", ruta=ruta_memoria)
        despues = memoria.buscar_casos_similares(firma_c3, ruta=ruta_memoria, umbral=0.0)
        check(despues[0]["similitud"] > base_b,
              f"Voto válido sube la similitud ({base_b:.3f} → {despues[0]['similitud']:.3f})")

        from modulos.modulo3.persistencia import cargar_historial
        historial = cargar_historial(ruta_memoria)
        fb = [c for c in historial["casos"] if c["id"] == "caso_001"][0]["feedback"]
        check(fb["votos_util"] == 1 and fb["comentarios"][0]["texto"] == "Funcionó en banco",
              "Feedback persistido dentro del caso")

        memoria.registrar_feedback("caso_001", util=False, ruta=ruta_memoria)
        final = memoria.buscar_casos_similares(firma_c3, ruta=ruta_memoria, umbral=0.0)
        check(final[0]["similitud"] <= despues[0]["similitud"],
              "Voto negativo reduce la ponderación")

    print("\n" + "=" * 60)
    print("  Validación C4 completada: todos los criterios OK")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())