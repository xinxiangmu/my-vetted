import pytest

from env_config import (
    ConfigError,
    get_bool,
    get_float,
    get_int,
    get_list,
    get_str,
    require_all,
)

ENV = {
    "NAME": "vetted",
    "PORT": "8080",
    "RATE": "1.5",
    "DEBUG": "true",
    "OFF": "no",
    "HOSTS": "a, b ,c",
    "EMPTY": "",
}


def test_get_str_returns_value():
    assert get_str("NAME", env=ENV) == "vetted"


def test_get_str_uses_default_when_absent():
    assert get_str("NOPE", default="fallback", env=ENV) == "fallback"


def test_empty_string_counts_as_absent():
    assert get_str("EMPTY", default="fallback", env=ENV) == "fallback"


def test_missing_required_raises():
    with pytest.raises(ConfigError):
        get_str("NOPE", env=ENV)


def test_get_int_parses():
    assert get_int("PORT", env=ENV) == 8080


def test_get_int_rejects_non_numeric():
    with pytest.raises(ConfigError):
        get_int("NAME", env=ENV)


def test_get_int_default():
    assert get_int("NOPE", default=99, env=ENV) == 99


def test_get_float_parses():
    assert get_float("RATE", env=ENV) == 1.5


def test_get_bool_true_and_false_words():
    assert get_bool("DEBUG", env=ENV) is True
    assert get_bool("OFF", env=ENV) is False


def test_get_bool_rejects_other_words():
    with pytest.raises(ConfigError):
        get_bool("NAME", env=ENV)


def test_get_list_strips_and_drops_blanks():
    assert get_list("HOSTS", env=ENV) == ["a", "b", "c"]


def test_require_all_reports_every_missing_name():
    with pytest.raises(ConfigError) as exc:
        require_all(["NAME", "GONE", "ALSO_GONE"], env=ENV)
    assert "GONE" in str(exc.value)
    assert "ALSO_GONE" in str(exc.value)


def test_require_all_passes_when_present():
    require_all(["NAME", "PORT"], env=ENV)
