from decimal import Decimal

from space_radio import (
    C,
    EARTH_RADIUS_M,
    HYDROGEN_LINE_HZ,
    INTRO,
    circular_period_s,
    doppler,
    hydrogen,
    lookup_bands,
    main,
    max_range_rate_ms,
    parse_freq,
    pass_duration_s,
)


def test_intro_names_the_project_and_sponsor():
    assert "spin-space-radio" in INTRO
    assert "Joshua Almeida" in INTRO
    assert "https://github.com/sponsors/fitzyracing1" in INTRO


def test_help_is_zero():
    assert main([]) == 0
    assert main(["--help"]) == 0


def test_parse_freq_units():
    assert parse_freq("145MHz") == Decimal("145000000")
    assert parse_freq("1420.405751 MHz") == HYDROGEN_LINE_HZ
    assert parse_freq("2.4GHz") == Decimal("2400000000")
    assert parse_freq("145000000") == Decimal("145000000")


def test_hydrogen_rest_frequency():
    result = hydrogen(0)
    assert result["rest_hz"] == Decimal("1420405751")
    assert result["observed_hz"] == result["rest_hz"]
    assert result["shift_hz"] == Decimal("0")


def test_doppler_receding_lowers_frequency():
    # Classical: Δf = -f v / c
    rest = Decimal("145000000")
    radial = Decimal("7215")
    observed = doppler(rest, radial)
    expected = rest * (C - radial) / C
    assert observed == expected
    assert observed < rest


def test_iss_like_period_is_about_92_minutes():
    period = circular_period_s("400")
    minutes = period / Decimal("60")
    assert Decimal("92") < minutes < Decimal("93")


def test_iss_like_horizon_pass_is_about_ten_minutes():
    duration = pass_duration_s("400", 0)
    minutes = duration / Decimal("60")
    assert Decimal("9") < minutes < Decimal("12")


def test_iss_like_horizon_range_rate():
    # v * R / a at 400 km is a bit over 7 km/s * 6371/6771
    vr = max_range_rate_ms("400")
    assert Decimal("7000") < vr < Decimal("7400")


def test_hydrogen_line_is_itu_uhf_and_ieee_l():
    names = lookup_bands(HYDROGEN_LINE_HZ)
    assert "ITU UHF" in names
    assert "IEEE L" in names


def test_two_metre_amateur_is_vhf():
    names = lookup_bands(parse_freq("145MHz"))
    assert "ITU VHF" in names
    assert "IEEE VHF" in names


def test_cli_hydrogen(capsys):
    assert main(["hydrogen"]) == 0
    out = capsys.readouterr().out
    assert "1420.405751" in out


def test_cli_band(capsys):
    assert main(["band", "1420.405751MHz"]) == 0
    out = capsys.readouterr().out
    assert "IEEE L" in out
    assert "ITU UHF" in out


def test_cli_pass(capsys):
    assert main(["pass", "400", "--freq", "145MHz"]) == 0
    out = capsys.readouterr().out
    assert "pass time" in out
    assert "Doppler" in out


def test_rejects_faster_than_light():
    assert main(["doppler", "145MHz", "--radial-ms", "300000000"]) == 2
