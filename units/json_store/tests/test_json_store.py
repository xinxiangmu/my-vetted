import json

import pytest

from json_store import StoreError, append, read, update, write


def test_read_missing_returns_default(tmp_path):
    assert read(tmp_path / "nope.json", default={"a": 1}) == {"a": 1}


def test_write_then_read_roundtrip(tmp_path):
    p = tmp_path / "data.json"
    write(p, {"name": "vetted", "n": 3})
    assert read(p) == {"name": "vetted", "n": 3}


def test_write_creates_parent_directories(tmp_path):
    p = tmp_path / "deep" / "nested" / "data.json"
    write(p, [1, 2])
    assert p.exists()


def test_write_leaves_no_temp_files(tmp_path):
    write(tmp_path / "data.json", {"a": 1})
    assert [f.name for f in tmp_path.iterdir()] == ["data.json"]


def test_write_replaces_previous_content(tmp_path):
    p = tmp_path / "data.json"
    write(p, {"v": 1})
    write(p, {"v": 2})
    assert read(p) == {"v": 2}


def test_read_rejects_corrupt_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not json", encoding="utf-8")
    with pytest.raises(StoreError):
        read(p)


def test_empty_file_returns_default(tmp_path):
    p = tmp_path / "empty.json"
    p.write_text("   ", encoding="utf-8")
    assert read(p, default=[]) == []


def test_update_merges_keys(tmp_path):
    p = tmp_path / "d.json"
    write(p, {"a": 1, "b": 2})
    assert update(p, {"b": 20, "c": 3}) == {"a": 1, "b": 20, "c": 3}
    assert read(p) == {"a": 1, "b": 20, "c": 3}


def test_update_on_missing_file_creates_it(tmp_path):
    p = tmp_path / "new.json"
    assert update(p, {"a": 1}) == {"a": 1}


def test_update_rejects_non_object(tmp_path):
    p = tmp_path / "list.json"
    write(p, [1, 2])
    with pytest.raises(StoreError):
        update(p, {"a": 1})


def test_append_grows_list(tmp_path):
    p = tmp_path / "log.json"
    append(p, "one")
    assert append(p, "two") == ["one", "two"]


def test_append_rejects_non_list(tmp_path):
    p = tmp_path / "obj.json"
    write(p, {"a": 1})
    with pytest.raises(StoreError):
        append(p, "x")


def test_written_file_is_utf8_and_readable_by_stdlib(tmp_path):
    p = tmp_path / "cn.json"
    write(p, {"名称": "模块"})
    assert json.loads(p.read_text(encoding="utf-8")) == {"名称": "模块"}


def test_write_returns_the_path(tmp_path):
    p = tmp_path / "d.json"
    assert write(p, {"a": 1}) == p


def test_indent_is_applied(tmp_path):
    p = tmp_path / "d.json"
    write(p, {"a": 1}, indent=4)
    assert '\n    "a"' in p.read_text(encoding="utf-8")


def test_indent_zero_is_compact(tmp_path):
    p = tmp_path / "d.json"
    write(p, {"a": 1}, indent=0)
    assert '"a"' in p.read_text(encoding="utf-8")


def test_write_to_existing_directory_does_not_fail(tmp_path):
    (tmp_path / "sub").mkdir()
    write(tmp_path / "sub" / "d.json", {"a": 1})
    assert read(tmp_path / "sub" / "d.json") == {"a": 1}
