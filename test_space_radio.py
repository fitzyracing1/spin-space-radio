from space_radio import INTRO, main


def test_intro_names_the_project_and_sponsor():
    assert "spin-space-radio" in INTRO
    assert "Joshua Almeida" in INTRO
    assert "https://github.com/sponsors/fitzyracing1" in INTRO


def test_help_is_zero():
    assert main(["--help"]) == 0


def test_no_args_is_zero():
    assert main([]) == 0
