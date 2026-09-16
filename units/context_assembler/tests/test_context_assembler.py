import pytest

from context_assembler import Section, assemble, estimate_tokens, report


def sec(name, size, **kw):
    return Section(name=name, content="x" * size, **kw)


def test_everything_fits():
    r = assemble([sec("a", 10), sec("b", 10)], budget=100, counter=len)
    assert r.used == ["a", "b"]
    assert r.complete


def test_priority_decides_order():
    r = assemble(
        [sec("low", 5, priority=90), sec("high", 5, priority=10)],
        budget=100, counter=len,
    )
    assert r.used == ["high", "low"]


def test_required_sections_come_first():
    r = assemble(
        [sec("normal", 5, priority=1), sec("must", 5, required=True, priority=99)],
        budget=100, counter=len,
    )
    assert r.used[0] == "must"


def test_over_budget_section_is_dropped():
    r = assemble([sec("big", 200)], budget=50, counter=len)
    assert r.dropped == ["big"]
    assert r.used == []


def test_required_section_overflows_rather_than_drops():
    r = assemble([sec("must", 200, required=True)], budget=50, counter=len)
    assert r.used == ["must"]
    assert r.dropped == []


def test_lower_priority_is_dropped_first():
    r = assemble(
        [sec("keep", 40, priority=1), sec("lose", 40, priority=99)],
        budget=50, counter=len,
    )
    assert r.used == ["keep"]
    assert r.dropped == ["lose"]


def test_truncatable_section_is_cut_not_dropped():
    long = Section("notes", "\n".join("line" for _ in range(50)), truncatable=True)
    r = assemble([long], budget=20, counter=len)
    assert r.used == ["notes"]
    assert r.truncated == ["notes"]


def test_truncation_respects_budget():
    long = Section("notes", "\n".join("line" for _ in range(50)), truncatable=True)
    r = assemble([long], budget=20, counter=len)
    assert r.tokens <= 20


def test_truncatable_with_no_room_is_dropped():
    r = assemble(
        [sec("fills", 50, priority=1), Section("notes", "abc", truncatable=True, priority=9)],
        budget=50, counter=len,
    )
    assert r.dropped == ["notes"]


def test_complete_is_false_when_something_was_cut():
    long = Section("notes", "\n".join("line" for _ in range(50)), truncatable=True)
    assert not assemble([long], budget=20, counter=len).complete


def test_sections_are_joined_by_separator():
    r = assemble([sec("a", 3), sec("b", 3)], budget=100, counter=len, separator="|")
    assert r.text == "xxx|xxx"


def test_tokens_reflects_final_text():
    r = assemble([sec("a", 3), sec("b", 3)], budget=100, counter=len, separator="")
    assert r.tokens == 6


def test_report_says_complete():
    r = assemble([sec("a", 3)], budget=100, counter=len)
    assert "complete" in report(r)
    assert "incomplete" not in report(r)


def test_report_names_dropped_sections():
    r = assemble([sec("big", 200)], budget=50, counter=len)
    assert "dropped big" in report(r)


def test_report_names_truncated_sections():
    long = Section("notes", "\n".join("line" for _ in range(50)), truncatable=True)
    assert "truncated notes" in report(assemble([long], budget=20, counter=len))


def test_rejects_zero_budget():
    with pytest.raises(ValueError):
        assemble([], budget=0)


def test_estimate_tokens_is_zero_for_empty():
    assert estimate_tokens("") == 0


def test_estimate_tokens_scales():
    assert estimate_tokens("x" * 40) == 10
