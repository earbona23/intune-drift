from drift.demo import demo_data
from drift.diff import comparar
from drift.weakening import CatalogoDebilitamiento

CAT = CatalogoDebilitamiento()


def test_detecta_agregada_eliminada_y_modificada():
    d = comparar(demo_data.antes(), demo_data.despues(), CAT)
    r = d["resumen"]
    assert r["agregadas"] == 1     # Android
    assert r["eliminadas"] == 1    # Windows
    assert r["modificadas"] >= 1


def test_cuenta_los_settings_que_debilitan():
    d = comparar(demo_data.antes(), demo_data.despues(), CAT)
    # c1: passwordMinimumLength 6->4, encryption true->false, inactividad 5->15 = 3 debilitan
    assert d["resumen"]["settings_que_debilitan"] == 3


def test_la_politica_que_mas_debilita_va_primera():
    d = comparar(demo_data.antes(), demo_data.despues(), CAT)
    assert d["politicas_modificadas"][0]["debilita"] >= 1


def test_reordenar_no_es_un_cambio():
    a = demo_data.antes()
    d = comparar(a, list(reversed(a)), CAT)
    assert d["resumen"]["modificadas"] == 0
    assert d["resumen"]["settings_que_debilitan"] == 0
