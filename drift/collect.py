"""Captura de la configuración de Intune vía Graph — SOLO LECTURA.

Normaliza tres familias de políticas a una forma común
{ tipo, id, nombre, settings }, para que el diff no tenga que conocer la forma cruda
de cada endpoint de Graph. `settings` es un dict plano de los campos relevantes.
"""
from __future__ import annotations

from drift.graph import GraphClient

# Campos meta que NO son settings de seguridad (no entran al diff de settings).
_META = {
    "id", "displayName", "description", "createdDateTime", "lastModifiedDateTime",
    "version", "roleScopeTagIds", "@odata.type", "assignments",
}


def _settings(politica: dict) -> dict:
    return {k: v for k, v in politica.items() if k not in _META and not k.startswith("@")}


def _normalizar(politica: dict, tipo: str) -> dict:
    return {
        "tipo": tipo,
        "id": politica.get("id", ""),
        "nombre": politica.get("displayName", politica.get("id", "?")),
        "settings": _settings(politica),
    }


ENDPOINTS = {
    "compliance": "/deviceManagement/deviceCompliancePolicies",
    "configuracion": "/deviceManagement/deviceConfigurations",
    "app_protection": "/deviceManagement/managedAppPolicies",
}


def capturar(g: GraphClient) -> list[dict]:
    """Snapshot completo: lista normalizada de todas las políticas de las 3 familias."""
    snapshot: list[dict] = []
    for tipo, ruta in ENDPOINTS.items():
        for pol in g.get_all(ruta):
            snapshot.append(_normalizar(pol, tipo))
    return snapshot
