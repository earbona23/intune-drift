"""Clasifica un cambio de setting como debilita / fortalece / neutral, según el
catálogo editable rules/weakening.yaml.

La regla es el conocimiento de seguridad; este módulo solo la aplica. Un setting que
cambió y no está catalogado se marca 'no_clasificado' — cambió algo cuya dirección de
seguridad nadie definió, y eso merece una mirada, no un encogimiento de hombros.
"""
from __future__ import annotations

from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

CATALOGO = Path(__file__).resolve().parent.parent / "rules" / "weakening.yaml"

DEBILITA = "debilita"
FORTALECE = "fortalece"
NEUTRAL = "neutral"
NO_CLASIFICADO = "no_clasificado"


class CatalogoDebilitamiento:
    def __init__(self, ruta: Path | None = None) -> None:
        if yaml is None:
            raise SystemExit("Se necesita PyYAML: pip install -r requirements.txt")
        self._reglas: dict = yaml.safe_load((ruta or CATALOGO).read_text(encoding="utf-8")) or {}

    def clasificar(self, setting: str, antes, despues) -> str:
        regla = self._reglas.get(setting)
        if regla is None:
            return NO_CLASIFICADO

        tipo = regla.get("tipo")
        if tipo == "bool":
            seguro = bool(regla.get("seguro", True))
            # Pasar del valor seguro al inseguro debilita; lo inverso fortalece.
            if bool(antes) == seguro and bool(despues) != seguro:
                return DEBILITA
            if bool(antes) != seguro and bool(despues) == seguro:
                return FORTALECE
            return NEUTRAL

        # min/max solo aplican a números comparables.
        try:
            a, d = float(antes), float(despues)
        except (TypeError, ValueError):
            return NO_CLASIFICADO
        if a == d:
            return NEUTRAL
        if tipo == "min":  # más alto es más seguro
            return DEBILITA if d < a else FORTALECE
        if tipo == "max":  # más bajo es más seguro
            return DEBILITA if d > a else FORTALECE
        return NO_CLASIFICADO
