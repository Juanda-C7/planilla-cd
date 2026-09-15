from planilla import cli


def test_parse_args_convierte_valores_numericos():
    datos = cli.parse_args(
        [
            "salario_base=4000",
            "horas_extra=8",
            "dias_trabajados=30",
            "cuota_prestamo=500",
        ]
    )

    assert datos == {
        "salario_base": 4000.0,
        "horas_extra": 8.0,
        "dias_trabajados": 30.0,
        "cuota_prestamo": 500.0,
    }


def test_parse_args_conserva_valores_no_numericos():
    datos = cli.parse_args(
        [
            "salario_base=4000",
            "afiliado_igss=si",
        ]
    )

    assert datos["salario_base"] == 4000.0
    assert datos["afiliado_igss"] == "si"


def test_parse_args_ignora_argumentos_sin_igual():
    datos = cli.parse_args(
        [
            "salario_base=4000",
            "argumento_invalido",
        ]
    )

    assert datos == {"salario_base": 4000.0}


def test_main_sin_salario_muestra_uso(monkeypatch, capsys):
    monkeypatch.setattr(cli.sys, "argv", ["planilla"])

    resultado = cli.main()

    salida = capsys.readouterr()

    assert resultado == 1
    assert cli.USO in salida.out


def test_main_calcula_planilla(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        [
            "planilla",
            "salario_base=4000",
            "horas_extra=8",
            "dias_trabajados=30",
            "cuota_prestamo=500",
            "afiliado_igss=si",
        ],
    )

    resultado = cli.main()

    salida = capsys.readouterr()

    assert resultado == 0
    assert "Liquido: Q9999.99" in salida.out
    assert "Descuentos: Q702.86" in salida.out


def test_main_afiliado_no(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.sys,
        "argv",
        [
            "planilla",
            "salario_base=4000",
            "afiliado_igss=no",
        ],
    )

    resultado = cli.main()

    salida = capsys.readouterr()

    assert resultado == 0
    assert "Liquido: Q4250.0" in salida.out
    assert "Descuentos: Q0.0" in salida.out