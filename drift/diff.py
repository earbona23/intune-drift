"""Motor de diff de snapshots de Intune, con lente de seguridad.

Compara dos snapshots (cada uno es la lista normalizada de políticas) y reporta:
  - políticas AGREGADAS y ELIMINADAS
  - por política MODIFICADA, cada setting que cambió, clasificado por si DEBILITA,
    fortalece o es neutral respecto de la postura de seguridad.

El diff se identifica por (tipo, id) de política, no por su posición: reordenar la
lista no debe verse como un cambio.
"""
from __future__ import annotations

from drift.weakening import DEBILITA, CatalogoDebilitamiento


def _indexar(snapshot: list[dict]) -> dict[tuple, dict]:
    return {(p.get("tipo"), p.get("id")): p for p in snapshot}


def _diff_settings(antes: dict, despues: dict, cat: CatalogoDebilitamiento) -> list[dict]:
    claves = set(antes.get("settings", {})) | set(despues.get("settings", {}))
    cambios = []
    for k in sorted(claves):
        va = antes.get("settings", {}).get(k, None)
        vd = despues.get("settings", {}).get(k, None)
        if va == vd:
            continue
        cambios.append({
            "setting": k,
            "antes": va,
            "despues": vd,
            "impacto": cat.clasificar(k, va, vd),
        })
    return cambios


def comparar(anterior: list[dict], actual: list[dict], cat: CatalogoDebilitamiento) -> dict:
    antes = _indexar(anterior)
    ahora = _indexar(actual)

    agregadas = [ahora[k] for k in ahora if k not in antes]
    eliminadas = [antes[k] for k in antes if k not in ahora]

    modificadas = []
    for k in ahora:
        if k not in antes:
            continue
        cambios = _diff_settings(antes[k], ahora[k], cat)
        if cambios:
            modificadas.append({
                "tipo": k[0],
                "id": k[1],
                "nombre": ahora[k].get("nombre", k[1]),
                "cambios": cambios,
                "debilita": sum(1 for c in cambios if c["impacto"] == DEBILITA),
            })

    # Lo que debilita, primero: es lo que hay que mirar.
    modificadas.sort(key=lambda m: -m["debilita"])

    total_debilita = sum(m["debilita"] for m in modificadas)
    return {
        "resumen": {
            "agregadas": len(agregadas),
            "eliminadas": len(eliminadas),
            "modificadas": len(modificadas),
            "settings_que_debilitan": total_debilita,
        },
        "politicas_agregadas": [{"tipo": p.get("tipo"), "nombre": p.get("nombre")} for p in agregadas],
        "politicas_eliminadas": [{"tipo": p.get("tipo"), "nombre": p.get("nombre")} for p in eliminadas],
        "politicas_modificadas": modificadas,
    }
