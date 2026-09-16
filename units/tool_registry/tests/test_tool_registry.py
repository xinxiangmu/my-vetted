import pytest

from tool_registry import ToolError, ToolRegistry, build_schema


def add(a: int, b: int = 2) -> int:
    """Add two numbers."""
    return a + b


def greet(name: str):
    """Say hello."""
    return f"hello {name}"


def test_schema_uses_function_name():
    assert build_schema(add)["name"] == "add"


def test_schema_uses_first_docstring_line():
    assert build_schema(add)["description"] == "Add two numbers."


def test_schema_maps_type_hints():
    props = build_schema(add)["input_schema"]["properties"]
    assert props["a"]["type"] == "integer"


def test_schema_defaults_unhinted_to_string():
    def f(x):
        """No hints."""

    assert build_schema(f)["input_schema"]["properties"]["x"]["type"] == "string"


def test_schema_marks_only_params_without_defaults_required():
    assert build_schema(add)["input_schema"]["required"] == ["a"]


def test_schema_skips_varargs():
    def f(a: int, *args, **kwargs):
        """V."""

    assert list(build_schema(f)["input_schema"]["properties"]) == ["a"]


def test_register_and_contains():
    r = ToolRegistry()
    r.register(add)
    assert "add" in r
    assert len(r) == 1


def test_register_under_custom_name():
    r = ToolRegistry()
    r.register(add, name="sum_two")
    assert "sum_two" in r
    assert "add" not in r


def test_register_returns_the_function_for_decorator_use():
    r = ToolRegistry()
    assert r.register(add) is add


def test_duplicate_registration_rejected():
    r = ToolRegistry()
    r.register(add)
    with pytest.raises(ToolError):
        r.register(add)


def test_unregister_reports_whether_present():
    r = ToolRegistry()
    r.register(add)
    assert r.unregister("add") is True
    assert r.unregister("add") is False


def test_schemas_lists_every_tool():
    r = ToolRegistry()
    r.register(add)
    r.register(greet)
    assert {s["name"] for s in r.schemas()} == {"add", "greet"}


def test_call_dispatches():
    r = ToolRegistry()
    r.register(add)
    assert r.call("add", {"a": 1, "b": 3}) == 4


def test_call_applies_defaults():
    r = ToolRegistry()
    r.register(add)
    assert r.call("add", {"a": 1}) == 3


def test_call_with_no_arguments_at_all():
    r = ToolRegistry()
    r.register(lambda: "ok", name="ping")
    assert r.call("ping") == "ok"


def test_unknown_tool_raises_and_lists_known_ones():
    r = ToolRegistry()
    r.register(add)
    with pytest.raises(ToolError) as exc:
        r.call("nope")
    assert "add" in str(exc.value)


def test_missing_required_argument_raises():
    r = ToolRegistry()
    r.register(add)
    with pytest.raises(ToolError) as exc:
        r.call("add", {"b": 1})
    assert "missing" in str(exc.value)


def test_unexpected_argument_raises():
    r = ToolRegistry()
    r.register(greet)
    with pytest.raises(ToolError) as exc:
        r.call("greet", {"name": "amy", "extra": 1})
    assert "unexpected" in str(exc.value)


def test_empty_registry_reports_none_registered():
    r = ToolRegistry()
    with pytest.raises(ToolError) as exc:
        r.call("anything")
    assert "none" in str(exc.value)
