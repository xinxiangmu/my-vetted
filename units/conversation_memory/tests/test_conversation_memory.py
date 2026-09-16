import pytest

from conversation_memory import ConversationMemory, Message, estimate_tokens


def words(n):
    return "word " * n


def test_estimate_is_zero_for_empty():
    assert estimate_tokens("") == 0


def test_estimate_is_at_least_one_for_short_text():
    assert estimate_tokens("ab") == 1


def test_estimate_scales_with_length():
    assert estimate_tokens("x" * 400) == 100


def test_message_rejects_unknown_role():
    with pytest.raises(ValueError):
        Message("wizard", "hi")


def test_message_is_a_plain_dict():
    assert dict(Message("user", "hi")) == {"role": "user", "content": "hi"}


def test_message_keeps_extra_fields():
    assert Message("tool", "out", tool_call_id="c1")["tool_call_id"] == "c1"


def test_add_appends():
    m = ConversationMemory()
    m.add("user", "hello")
    assert len(m) == 1


def test_extend_adds_all():
    m = ConversationMemory()
    m.extend([{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}])
    assert len(m) == 2


def test_tokens_sums_content():
    m = ConversationMemory(counter=len)
    m.add("user", "abcd")
    m.add("assistant", "ef")
    assert m.tokens() == 6


def test_no_trim_when_within_budget():
    m = ConversationMemory(budget=1000, counter=len)
    m.add("user", "short")
    assert m.trim() == 0


def test_trim_drops_oldest_first():
    m = ConversationMemory(budget=20, counter=len, keep_recent=0)
    m.add("user", "a" * 10)
    m.add("user", "b" * 10)
    m.add("user", "c" * 10)
    m.trim()
    contents = [x["content"] for x in m.render()]
    assert contents[0].startswith("b")


def test_trim_brings_total_within_budget():
    m = ConversationMemory(budget=20, counter=len, keep_recent=0)
    for _ in range(5):
        m.add("user", "x" * 10)
    m.trim()
    assert m.tokens() <= 20


def test_system_message_survives_trim():
    m = ConversationMemory(budget=10, counter=len, keep_recent=0)
    m.add("system", "s" * 10)
    for _ in range(5):
        m.add("user", "x" * 10)
    m.trim()
    assert any(x["role"] == "system" for x in m.render())


def test_pinned_message_survives_trim():
    m = ConversationMemory(budget=10, counter=len, keep_recent=0)
    m.add("user", "keep me", pinned=True)
    for _ in range(5):
        m.add("user", "x" * 10)
    m.trim()
    assert any(x["content"] == "keep me" for x in m.render())


def test_recent_messages_are_protected():
    m = ConversationMemory(budget=5, counter=len, keep_recent=2)
    m.add("user", "a" * 10)
    m.add("user", "b" * 10)
    m.add("user", "c" * 10)
    m.trim()
    contents = [x["content"][0] for x in m.render()]
    assert contents == ["b", "c"]


def test_dropped_counter_accumulates():
    m = ConversationMemory(budget=10, counter=len, keep_recent=0)
    for _ in range(4):
        m.add("user", "x" * 10)
    m.trim()
    assert m.dropped == 3


def test_render_returns_plain_dicts():
    m = ConversationMemory(counter=len)
    m.add("user", "hi")
    assert type(m.render()[0]) is dict


def test_clear_keeps_system_by_default():
    m = ConversationMemory()
    m.add("system", "s")
    m.add("user", "u")
    m.clear()
    assert [x["role"] for x in m.render()] == ["system"]


def test_clear_can_drop_everything():
    m = ConversationMemory()
    m.add("system", "s")
    m.clear(keep_system=False)
    assert len(m) == 0


def test_rejects_bad_budget():
    with pytest.raises(ValueError):
        ConversationMemory(budget=0)


def test_rejects_negative_keep_recent():
    with pytest.raises(ValueError):
        ConversationMemory(keep_recent=-1)
