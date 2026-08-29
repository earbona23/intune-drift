"""intune-drift — captura la configuración de Intune y diffea dos snapshots.

  python -m drift.cli --demo                         # diff de dos snapshots demo
  python -m drift.cli snapshot --salida hoy.json     # capturar (demo)
  python -m drift.cli snapshot --live --salida hoy.json
  python -m drift.cli diff ayer.json hoy.json        # comparar dos snapshots
  python -m drift.cli diff ayer.json hoy.json --json informe.json

Código de salida 2 si el diff contiene algún cambio que DEBILITA la postura
(útil como paso de CI que avisa cuando una edición de Intune reduce la seguridad).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from drift.config import cargar
from drift.diff import comparar
from drift.report import console
from drift.weakening import CatalogoDebilitamiento


def _capturar(es_demo: bool, cfg) -> list[dict]:
    if es_demo:
        from drift.demo import demo_data
        return demo_data.despues()
    from drift.collect import capturar
    from drift.graph import GraphClient
    g = GraphClient(cfg.tenant_id, cfg.client_id, cfg.client_secret)
    return capturar(g)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Drift de configuración de Intune (solo lectura)")
    sub = p.add_subparsers(dest="cmd")

    ps = sub.add_parser("snapshot", help="Capturar un snapshot")
    ps.add_argument("--live", action="store_true")
    ps.add_argument("--salida", type=Path, required=True)

    pd = sub.add_parser("diff", help="Comparar dos snapshots")
    pd.add_argument("anterior", type=Path)
    pd.add_argument("actual", type=Path)
    pd.add_argument("--json", type=Path)
    pd.add_argument("--sin-color", action="store_true")

    p.add_argument("--demo", action="store_true", help="Diff de dos snapshots demo")
    p.add_argument("--sin-color", action="store_true")
    args = p.parse_args(argv)

    cat = CatalogoDebilitamiento()

    if args.cmd == "snapshot":
        cfg = cargar(modo="live" if args.live else "demo")
        snap = _capturar(cfg.es_demo, cfg)
        args.salida.write_text(json.dumps(snap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Snapshot escrito: {args.salida} ({len(snap)} políticas)", file=sys.stderr)
        return 0

    if args.cmd == "diff":
        anterior = json.loads(args.anterior.read_text(encoding="utf-8"))
        actual = json.loads(args.actual.read_text(encoding="utf-8"))
        d = comparar(anterior, actual, cat)
        if args.json:
            args.json.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"Informe escrito: {args.json}", file=sys.stderr)
        else:
            print(console.render(d, demo=False, color=not args.sin_color))
        return 2 if d["resumen"]["settings_que_debilitan"] else 0

    # Por defecto: demo (diff de los dos snapshots sintéticos)
    from drift.demo import demo_data
    d = comparar(demo_data.antes(), demo_data.despues(), cat)
    print(console.render(d, demo=True, color=not args.sin_color))
    return 2 if d["resumen"]["settings_que_debilitan"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
