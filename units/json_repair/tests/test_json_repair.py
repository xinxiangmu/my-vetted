import pytest

from json_repair import (
    UnrepairableJSON,
    close_unbalanced,
    find_payload,
    loads,
    repair,
    strip_fences,
)


def test_clean_json_parses():
    assert loads('{"a": 1}') == {"a": 1}


def test_strips_json_fence():
    assert loads('```json\n{"a": 1}\n```') == {"a": 1}


def test_strips_bare_fence():
    assert loads('```\n{"a": 1}\n```') == {"a": 1}


def test_strip_fences_leaves_unfenced_text():
    assert strip_fences('  {"a": 1}  ') == '{"a": 1}'


def test_ignores_surrounding_prose():
    text = 'Sure! Here is the result:\n{"a": 1}\nHope that helps.'
    assert loads(text) == {"a": 1}


def test_finds_array_payload():
    assert loads("output: [1, 2, 3] done") == [1, 2, 3]


def test_removes_trailing_comma_in_object():
    assert loads('{"a": 1, "b": 2,}') == {"a": 1, "b": 2}


def test_removes_trailing_comma_in_array():
    assert loads("[1, 2, 3,]") == [1, 2, 3]


def test_closes_truncated_object():
    assert loads('{"a": 1, "b": {"c": 2') == {"a": 1, "b": {"c": 2}}


def test_closes_truncated_array():
    assert loads('[{"a": 1}, {"b": 2') == [{"a": 1}, {"b": 2}]


def test_closes_unterminated_string():
    """The exact failure that killed the old pipeline: JSONDecodeError on a cut string."""
    assert loads('{"reason": "the model ran out of tok') == {
        "reason": "the model ran out of tok"
    }


def test_close_unbalanced_ignores_brackets_inside_strings():
    assert close_unbalanced('{"a": "not { a brace"') == '{"a": "not { a brace"}'


def test_close_unbalanced_respects_escaped_quote():
    assert loads('{"a": "he said \\"hi\\""') == {"a": 'he said "hi"'}


def test_close_unbalanced_leaves_balanced_text_alone():
    assert close_unbalanced('{"a": 1}') == '{"a": 1}'


def test_find_payload_raises_without_brackets():
    with pytest.raises(UnrepairableJSON):
        find_payload("no json here at all")


def test_loads_raises_when_unrecoverable():
    with pytest.raises(UnrepairableJSON):
        loads("absolutely not json")


def test_loads_returns_default_when_given():
    assert loads("absolutely not json", default={}) == {}


def test_repair_returns_a_string_without_parsing():
    assert repair('{"a": 1,}') == '{"a": 1}'


def test_nested_truncation_closes_every_level():
    assert loads('{"a": [{"b": [1, 2') == {"a": [{"b": [1, 2]}]}
