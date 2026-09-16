import pytest

from safe_path import UnsafePath, is_inside, safe_join, safe_name


def test_joins_simple_relative_path(tmp_path):
    result = safe_join(tmp_path, "docs", "readme.md")
    assert result == (tmp_path / "docs" / "readme.md").resolve()


def test_rejects_parent_traversal(tmp_path):
    with pytest.raises(UnsafePath):
        safe_join(tmp_path, "..", "secrets.txt")


def test_rejects_deep_traversal(tmp_path):
    with pytest.raises(UnsafePath):
        safe_join(tmp_path, "a", "..", "..", "..", "etc")


def test_rejects_posix_absolute_component(tmp_path):
    with pytest.raises(UnsafePath):
        safe_join(tmp_path, "/etc/passwd")


def test_rejects_windows_absolute_component(tmp_path):
    with pytest.raises(UnsafePath):
        safe_join(tmp_path, "C:\\Windows\\System32")


def test_rejects_empty_component(tmp_path):
    with pytest.raises(UnsafePath):
        safe_join(tmp_path, "")


def test_rejects_null_byte(tmp_path):
    with pytest.raises(UnsafePath):
        safe_join(tmp_path, "a\x00b")


def test_traversal_that_returns_inside_is_allowed(tmp_path):
    result = safe_join(tmp_path, "a", "..", "b")
    assert result == (tmp_path / "b").resolve()


def test_is_inside_true_for_child(tmp_path):
    assert is_inside(tmp_path, tmp_path / "x" / "y")


def test_is_inside_true_for_base_itself(tmp_path):
    assert is_inside(tmp_path, tmp_path)


def test_is_inside_false_for_sibling(tmp_path):
    assert not is_inside(tmp_path / "a", tmp_path / "b")


def test_safe_name_strips_separators():
    assert "/" not in safe_name("a/b/c")
    assert "\\" not in safe_name("a\\b")


def test_safe_name_strips_control_and_reserved_chars():
    assert safe_name('bad<>:"|?*name') == "bad_______name"


def test_safe_name_falls_back_when_everything_is_stripped():
    assert safe_name("...", fallback="anon") == "anon"


def test_safe_name_escapes_windows_reserved_device():
    assert safe_name("CON.txt").startswith("_")


def test_safe_name_truncates_to_255():
    assert len(safe_name("x" * 400)) == 255
