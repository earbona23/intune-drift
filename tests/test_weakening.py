from drift.weakening import (
    DEBILITA,
    FORTALECE,
    NEUTRAL,
    NO_CLASIFICADO,
    CatalogoDebilitamiento,
)

CAT = CatalogoDebilitamiento()


def test_bool_seguro_true_desactivado_debilita():
    assert CAT.clasificar("storageRequireEncryption", True, False) == DEBILITA
    assert CAT.clasificar("storageRequireEncryption", False, True) == FORTALECE


def test_min_bajar_debilita_subir_fortalece():
    assert CAT.clasificar("passwordMinimumLength", 6, 4) == DEBILITA
    assert CAT.clasificar("passwordMinimumLength", 4, 6) == FORTALECE


def test_max_subir_debilita():
    # más minutos hasta bloqueo = menos seguro
    assert CAT.clasificar("passwordMinutesOfInactivityBeforeLock", 5, 15) == DEBILITA


def test_setting_no_catalogado_no_se_asume_inofensivo():
    assert CAT.clasificar("algoInventado", 1, 2) == NO_CLASIFICADO


def test_bool_hacia_el_lado_seguro_no_es_debilita():
    assert CAT.clasificar("pinRequired", True, True) == NEUTRAL
