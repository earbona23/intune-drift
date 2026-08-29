"""Dos snapshots DEMO de Intune: 'antes' y 'despues', con cambios reales entre ellos.

Datos INVENTADOS, deterministas. Están pensados para que el diff muestre el rango
completo: un setting que DEBILITA (cifrado desactivado, PIN más corto), uno que
FORTALECE, una política nueva, una eliminada, y un cambio de un setting no catalogado.
Así cualquiera ve el valor de la herramienta sin un tenant.
"""
from __future__ import annotations


def _pol(tipo, id_, nombre, settings):
    return {"tipo": tipo, "id": id_, "nombre": nombre, "settings": settings}


def antes() -> list[dict]:
    return [
        _pol("compliance", "c1", "iOS — Base corporativa", {
            "passwordRequired": True,
            "passwordMinimumLength": 6,
            "storageRequireEncryption": True,
            "securityBlockJailbrokenDevices": True,
            "passwordMinutesOfInactivityBeforeLock": 5,
        }),
        _pol("compliance", "c2", "Windows — Base corporativa", {
            "bitLockerEnabled": True,
            "firewallEnabled": True,
            "defenderEnabled": True,
            "osMinimumVersion": "10.0.19045",
        }),
        _pol("app_protection", "a1", "Outlook — Protección de datos", {
            "pinRequired": True,
            "minimumPinLength": 6,
            "saveAsBlocked": True,
            "maximumPinRetries": 5,
        }),
    ]


def despues() -> list[dict]:
    return [
        # c1: DEBILITA (cifrado desactivado, PIN más corto, bloqueo más tardío) + uno que fortalece
        _pol("compliance", "c1", "iOS — Base corporativa", {
            "passwordRequired": True,
            "passwordMinimumLength": 4,               # bajó: DEBILITA
            "storageRequireEncryption": False,        # true->false: DEBILITA
            "securityBlockJailbrokenDevices": True,
            "passwordMinutesOfInactivityBeforeLock": 15,  # subió: DEBILITA
            "deviceThreatProtectionEnabled": True,    # setting nuevo activado: FORTALECE
        }),
        # c2 ELIMINADA (ya no está)
        # a1: un cambio no catalogado
        _pol("app_protection", "a1", "Outlook — Protección de datos", {
            "pinRequired": True,
            "minimumPinLength": 6,
            "saveAsBlocked": True,
            "maximumPinRetries": 5,
            "allowedDataStorageLocations": ["oneDriveForBusiness"],  # no catalogado
        }),
        # AGREGADA
        _pol("compliance", "c3", "Android — Base corporativa", {
            "passwordRequired": True,
            "storageRequireEncryption": True,
            "securityBlockJailbrokenDevices": True,
        }),
    ]
