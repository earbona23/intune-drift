"""Reporte de consola del diff, con lo que DEBILITA destacado primero."""
from __future__ import annotations

_COL = {"debilita": "\033[91m", "fortalece": "\033[92m", "neutral": "\033[90m",
        "no_clasificado": "\033[95m"}
_RESET = "\033[0m"
_MARCA = {"debilita": "▼ DEBILITA", "fortalece": "▲ fortalece",
          "neutral": "· neutral", "no_clasificado": "? sin clasificar"}


def render(diff: dict, demo: bool, color: bool = True) -> str:
    def c(imp, txt):
        return f"{_COL.get(imp, '')}{txt}{_RESET}" if color else txt

    r = diff["resumen"]
    out = []
    if demo:
        out.append("  ●  DATOS DEMO — snapshots sintéticos, ningún tenant real  ●\n")
    out.append("DRIFT DE CONFIGURACIÓN DE INTUNE")
    out.append("=" * 56)
    out.append(f"Políticas agregadas    : {r['agregadas']}")
    out.append(f"Políticas eliminadas   : {r['eliminadas']}")
    out.append(f"Políticas modificadas  : {r['modificadas']}")
    out.append(c("debilita", f"Settings que DEBILITAN : {r['settings_que_debilitan']}"))
    out.append("")

    for p in diff["politicas_eliminadas"]:
        out.append(c("debilita", f"[ELIMINADA] {p['tipo']} · {p['nombre']}"))
    for p in diff["politicas_agregadas"]:
        out.append(f"[NUEVA]     {p['tipo']} · {p['nombre']}")
    if diff["politicas_eliminadas"] or diff["politicas_agregadas"]:
        out.append("")

    for m in diff["politicas_modificadas"]:
        etiqueta = f"[MODIFICADA] {m['tipo']} · {m['nombre']}"
        out.append(c("debilita", etiqueta) if m["debilita"] else etiqueta)
        for ch in m["cambios"]:
            marca = c(ch["impacto"], _MARCA.get(ch["impacto"], ch["impacto"]))
            out.append(f"    {marca}  {ch['setting']}: {ch['antes']} → {ch['despues']}")
        out.append("")

    out.append("Herramienta de SOLO LECTURA. No modifica ninguna política.")
    return "\n".join(out)
