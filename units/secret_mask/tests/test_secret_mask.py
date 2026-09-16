import pytest

from secret_mask import MASK, is_secret_key, mask_data, mask_text, mask_value


def test_recognises_secret_key_names():
    assert is_secret_key("PASSWORD")
    assert is_secret_key("db_password")
    assert is_secret_key("Authorization")


def test_ordinary_key_names_are_not_secrets():
    assert not is_secret_key("username")
    assert not is_secret_key("host")


def test_mask_value_hides_everything_by_default():
    assert mask_value("hunter2") == MASK


def test_mask_value_can_keep_a_suffix():
    assert mask_value("abcdefgh", keep=3) == MASK + "fgh"


def test_mask_value_hides_short_value_entirely():
    assert mask_value("ab", keep=5) == MASK


def test_mask_value_rejects_negative_keep():
    with pytest.raises(ValueError):
        mask_value("abc", keep=-1)


def test_masks_openai_style_key_in_text():
    out = mask_text("use sk-abcdefghijklmnop now")
    assert "sk-abcdefghijklmnop" not in out
    assert MASK in out


def test_masks_github_token_in_text():
    assert "ghp_" not in mask_text("token ghp_ABCDEFGHIJKLMNOPQRST")


def test_masks_bearer_header():
    assert "abcdefghijkl" not in mask_text("Authorization: Bearer abcdefghijkl")


def test_masks_credentials_in_url():
    assert "s3cretpw" not in mask_text("postgres://admin:s3cretpw@db.internal/app")


def test_masks_jwt():
    jwt = "eyJhbGciOiJIUzI1.eyJzdWIiOiIxMjM0.SflKxwRJSMeKKF2QT4"
    assert jwt not in mask_text(f"cookie={jwt}")


def test_leaves_ordinary_text_alone():
    assert mask_text("hello world, port 8080") == "hello world, port 8080"


def test_mask_data_masks_by_key_name():
    out = mask_data({"user": "amy", "password": "hunter2"})
    assert out == {"user": "amy", "password": MASK}


def test_mask_data_recurses_into_nested_structures():
    out = mask_data({"db": {"conf": [{"api_key": "xyz123"}]}})
    assert out["db"]["conf"][0]["api_key"] == MASK


def test_mask_data_also_scrubs_values_in_plain_strings():
    out = mask_data({"note": "key is sk-abcdefghijklmnop"})
    assert "sk-abcdefghijklmnop" not in out["note"]


def test_mask_data_leaves_non_string_scalars_alone():
    assert mask_data({"port": 8080, "on": True}) == {"port": 8080, "on": True}
