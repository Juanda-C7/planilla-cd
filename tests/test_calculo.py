import pytest

from planilla.calculo import (
    Planilla,
    bonificacion_incentivo,
    descuento_igss,
    descuento_isr,
    descuento_prestamo,
    isr_anual,
    liquidar,
    pago_horas_extra,
    resumen,
    salario_ordinario,
    valor_hora,
)


# ============================================================
# valor_hora
# ============================================================

@pytest.mark.parametrize(
    "salario_base",
    [-1, 0],
)
def test_valor_hora_salario_no_valido_bva(salario_base):
    with pytest.raises(ValueError):
        valor_hora(salario_base)


def test_valor_hora_unidad_minima_valida_bva():
    assert valor_hora(1) == pytest.approx(1 / 240)


def test_valor_hora_salario_representativo_ep():
    assert valor_hora(4000) == pytest.approx(4000 / 240)


# ============================================================
# pago_horas_extra
# ============================================================

@pytest.mark.parametrize(
    "horas_extra",
    [-1, 49],
)
def test_pago_horas_extra_fuera_de_rango_bva(horas_extra):
    with pytest.raises(ValueError):
        pago_horas_extra(4000, horas_extra)


@pytest.mark.parametrize(
    "horas_extra, esperado",
    [
        (0, 0),
        (1, 25),
        (47, 1175),
        (48, 1200),
    ],
)
def test_pago_horas_extra_fronteras_bva(horas_extra, esperado):
    assert pago_horas_extra(4000, horas_extra) == pytest.approx(esperado)


def test_pago_horas_extra_caso_representativo_ep():
    assert pago_horas_extra(4000, 24) == pytest.approx(600)


# ============================================================
# salario_ordinario
# ============================================================

def test_salario_ordinario_sin_horas_extra_ep():
    assert salario_ordinario(4000, 0) == pytest.approx(4000)


def test_salario_ordinario_con_horas_extra_ep():
    assert salario_ordinario(4000, 8) == pytest.approx(4200)


def test_salario_ordinario_maximo_horas_extra_bva():
    assert salario_ordinario(4000, 48) == pytest.approx(5200)


# ============================================================
# bonificacion_incentivo
# ============================================================

@pytest.mark.parametrize(
    "dias_trabajados",
    [-1, 31],
)
def test_bonificacion_dias_fuera_de_rango_bva(dias_trabajados):
    with pytest.raises(ValueError):
        bonificacion_incentivo(dias_trabajados)


@pytest.mark.parametrize(
    "dias_trabajados, esperado",
    [
        (0, 0),
        (1, 250 / 30),
        (29, 250 * 29 / 30),
        (30, 250),
    ],
)
def test_bonificacion_fronteras_bva(dias_trabajados, esperado):
    assert bonificacion_incentivo(dias_trabajados) == pytest.approx(esperado)


def test_bonificacion_mes_parcial_ep():
    assert bonificacion_incentivo(15) == pytest.approx(125)


# ============================================================
# descuento_igss
# Tabla de decisión:
# None  -> no descuento
# False -> no descuento
# True  -> 4.83%
# ============================================================

@pytest.mark.parametrize(
    "afiliado, esperado",
    [
        (None, 0),
        (False, 0),
        (True, 4000 * 0.0483),
    ],
)
def test_descuento_igss_tabla_decision(afiliado, esperado):
    assert descuento_igss(4000, afiliado) == pytest.approx(esperado)


# ============================================================
# isr_anual
# ============================================================

@pytest.mark.parametrize(
    "renta_bruta_anual",
    [0, 47999],
)
def test_isr_sin_impuesto_bva(renta_bruta_anual):
    assert isr_anual(renta_bruta_anual) == pytest.approx(0)


def test_isr_frontera_deduccion_bva():
    assert isr_anual(48000) == pytest.approx(0)


def test_isr_justo_sobre_deduccion_bva():
    assert isr_anual(48001) == pytest.approx(0.05)


def test_isr_tramo_1_ep():
    assert isr_anual(200000) == pytest.approx(7600)


def test_isr_frontera_tramo_1_bva():
    assert isr_anual(348000) == pytest.approx(15000)


def test_isr_inicio_tramo_2_bva():
    assert isr_anual(348001) == pytest.approx(15000.07)


def test_isr_tramo_2_ep():
    assert isr_anual(500000) == pytest.approx(25640)


# ============================================================
# descuento_isr
# ============================================================

def test_descuento_isr_salario_sin_impuesto_ep():
    assert descuento_isr(4000) == pytest.approx(0)


def test_descuento_isr_justo_sobre_deduccion_bva():
    assert descuento_isr(4001) == pytest.approx(0.05)


def test_descuento_isr_frontera_tramo_1_bva():
    assert descuento_isr(29000) == pytest.approx(1250)


# ============================================================
# descuento_prestamo
# Tabla de decisión:
# cuota negativa -> error
# margen <= 0     -> descuento 0
# cuota <= margen -> descuento cuota
# cuota > margen  -> descuento solo hasta el margen
# ============================================================

def test_descuento_prestamo_cuota_negativa_bva():
    with pytest.raises(ValueError):
        descuento_prestamo(1000, 4000, -1)


def test_descuento_prestamo_cuota_cero_bva():
    assert descuento_prestamo(1000, 4000, 0) == pytest.approx(0)


def test_descuento_prestamo_sin_margen_tabla_decision():
    assert descuento_prestamo(1200, 4000, 500) == pytest.approx(0)


def test_descuento_prestamo_margen_parcial_bva():
    assert descuento_prestamo(1300, 4000, 500) == pytest.approx(100)


def test_descuento_prestamo_cuota_dentro_del_margen_ep():
    assert descuento_prestamo(2000, 4000, 500) == pytest.approx(500)


def test_descuento_prestamo_cuota_supera_margen_tabla_decision():
    assert descuento_prestamo(2000, 4000, 5000) == pytest.approx(800)


# ============================================================
# liquidar
# ============================================================

def test_liquidar_mes_completo_sin_horas_extra_ep():
    resultado = liquidar(4000)

    assert resultado.salario_ordinario == pytest.approx(4000)
    assert resultado.bonificacion == pytest.approx(250)
    assert resultado.igss == pytest.approx(193.20)
    assert resultado.isr == pytest.approx(0)
    assert resultado.prestamo == pytest.approx(0)
    assert resultado.liquido == pytest.approx(4056.80)


def test_liquidar_con_horas_extra_y_prestamo_ep():
    resultado = liquidar(
        salario_base=4000,
        horas_extra=8,
        dias_trabajados=30,
        afiliado_igss=True,
        cuota_prestamo=500,
    )

    assert resultado.salario_ordinario == pytest.approx(4200)
    assert resultado.bonificacion == pytest.approx(250)
    assert resultado.igss == pytest.approx(202.86)
    assert resultado.isr == pytest.approx(0)
    assert resultado.prestamo == pytest.approx(500)
    assert resultado.liquido == pytest.approx(3747.14)


def test_liquidar_mes_incompleto_sin_igss_ep():
    resultado = liquidar(
        salario_base=4000,
        horas_extra=0,
        dias_trabajados=15,
        afiliado_igss=False,
        cuota_prestamo=0,
    )

    assert resultado.salario_ordinario == pytest.approx(4000)
    assert resultado.bonificacion == pytest.approx(125)
    assert resultado.igss == pytest.approx(0)
    assert resultado.isr == pytest.approx(0)
    assert resultado.prestamo == pytest.approx(0)
    assert resultado.liquido == pytest.approx(4125)


def test_liquidar_maximo_horas_y_limite_prestamo_bva():
    resultado = liquidar(
        salario_base=4000,
        horas_extra=48,
        dias_trabajados=30,
        afiliado_igss=True,
        cuota_prestamo=5000,
    )

    assert resultado.salario_ordinario == pytest.approx(5200)
    assert resultado.bonificacion == pytest.approx(250)
    assert resultado.igss == pytest.approx(251.16)
    assert resultado.prestamo == pytest.approx(3638.84)
    assert resultado.liquido == pytest.approx(1560)


# ============================================================
# resumen
# ============================================================

def test_resumen_formato():
    planilla = Planilla(
        salario_ordinario=4000,
        bonificacion=250,
        igss=193.20,
        isr=0,
        prestamo=500,
        liquido=3556.80,
    )

    assert resumen(planilla) == "Liquido: Q3556.8 | Descuentos: Q693.2"