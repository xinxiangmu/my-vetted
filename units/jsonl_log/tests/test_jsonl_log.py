import json

import pytest

from jsonl_log import JSONLLog


def test_append_then_read(tmp_path):
    log = JSONLLog(tmp_path / "run.jsonl")
    log.append("start", step=1)
    assert log.read() == [{"event": "start", "step": 1}]


def test_append_returns_the_record(tmp_path):
    log = JSONLLog(tmp_path / "run.jsonl")
    assert log.append("start", step=1) == {"event": "start", "step": 1}


def test_records_accumulate(tmp_path):
    log = JSONLLog(tmp_path / "run.jsonl")
    log.append("a")
    log.append("b")
    assert [r["event"] for r in log.read()] == ["a", "b"]


def test_one_object_per_line(tmp_path):
    p = tmp_path / "run.jsonl"
    log = JSONLLog(p)
    log.append("a")
    log.append("b")
    assert len(p.read_text(encoding="utf-8").strip().splitlines()) == 2


def test_creates_parent_directories(tmp_path):
    log = JSONLLog(tmp_path / "deep" / "nested" / "run.jsonl")
    log.append("a")
    assert log.path.exists()


def test_reading_missing_file_yields_nothing(tmp_path):
    assert JSONLLog(tmp_path / "absent.jsonl").read() == []


def test_empty_event_name_rejected(tmp_path):
    with pytest.raises(ValueError):
        JSONLLog(tmp_path / "run.jsonl").append("")


def test_clock_adds_timestamp(tmp_path):
    log = JSONLLog(tmp_path / "run.jsonl", clock=lambda: 123.5)
    assert log.append("a")["ts"] == 123.5


def test_no_timestamp_without_clock(tmp_path):
    log = JSONLLog(tmp_path / "run.jsonl")
    assert "ts" not in log.append("a")


def test_redact_hook_is_applied(tmp_path):
    def scrub(record):
        record.pop("token", None)
        return record

    log = JSONLLog(tmp_path / "run.jsonl", redact=scrub)
    assert "token" not in log.append("call", token="secret")


def test_truncated_final_line_is_skipped(tmp_path):
    p = tmp_path / "run.jsonl"
    log = JSONLLog(p)
    log.append("good")
    with p.open("a", encoding="utf-8") as fh:
        fh.write('{"event": "cut off mid')
    assert [r["event"] for r in log.read()] == ["good"]


def test_broken_line_can_raise_instead(tmp_path):
    p = tmp_path / "run.jsonl"
    log = JSONLLog(p)
    log.append("good")
    with p.open("a", encoding="utf-8") as fh:
        fh.write("{broken")
    with pytest.raises(json.JSONDecodeError):
        log.read(skip_broken=False)


def test_blank_lines_are_ignored(tmp_path):
    p = tmp_path / "run.jsonl"
    log = JSONLLog(p)
    log.append("a")
    with p.open("a", encoding="utf-8") as fh:
        fh.write("\n\n")
    assert len(log.read()) == 1


def test_count_all(tmp_path):
    log = JSONLLog(tmp_path / "run.jsonl")
    log.append("a")
    log.append("b")
    assert log.count() == 2


def test_count_by_event(tmp_path):
    log = JSONLLog(tmp_path / "run.jsonl")
    log.append("a")
    log.append("b")
    log.append("a")
    assert log.count("a") == 2


def test_filter_matches_all_fields(tmp_path):
    log = JSONLLog(tmp_path / "run.jsonl")
    log.append("call", tool="search", ok=True)
    log.append("call", tool="search", ok=False)
    assert len(log.filter(tool="search", ok=True)) == 1


def test_filter_returns_empty_when_nothing_matches(tmp_path):
    log = JSONLLog(tmp_path / "run.jsonl")
    log.append("a")
    assert log.filter(event="zzz") == []


def test_tail_returns_last_n(tmp_path):
    log = JSONLLog(tmp_path / "run.jsonl")
    for i in range(5):
        log.append("e", i=i)
    assert [r["i"] for r in log.tail(2)] == [3, 4]


def test_tail_more_than_available(tmp_path):
    log = JSONLLog(tmp_path / "run.jsonl")
    log.append("a")
    assert len(log.tail(10)) == 1


def test_tail_rejects_zero(tmp_path):
    with pytest.raises(ValueError):
        JSONLLog(tmp_path / "run.jsonl").tail(0)


def test_clear_removes_the_file(tmp_path):
    log = JSONLLog(tmp_path / "run.jsonl")
    log.append("a")
    log.clear()
    assert log.read() == []


def test_clear_on_missing_file_is_safe(tmp_path):
    JSONLLog(tmp_path / "absent.jsonl").clear()


def test_unicode_is_preserved(tmp_path):
    log = JSONLLog(tmp_path / "run.jsonl")
    log.append("事件", 名称="模块")
    assert log.read()[0]["名称"] == "模块"
