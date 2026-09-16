from sse_parser import Event, SSEParser, is_done


def test_single_event():
    p = SSEParser()
    events = p.feed("data: hello\n\n")
    assert [e.data for e in events] == ["hello"]


def test_two_events_in_one_chunk():
    p = SSEParser()
    events = p.feed("data: a\n\ndata: b\n\n")
    assert [e.data for e in events] == ["a", "b"]


def test_event_split_across_chunks_is_not_lost():
    p = SSEParser()
    assert p.feed("data: hel") == []
    assert [e.data for e in p.feed("lo\n\n")] == ["hello"]


def test_newline_split_across_chunks():
    p = SSEParser()
    p.feed("data: x\n")
    assert [e.data for e in p.feed("\n")] == ["x"]


def test_incomplete_event_yields_nothing_until_blank_line():
    p = SSEParser()
    assert p.feed("data: partial\n") == []


def test_close_emits_unterminated_event():
    p = SSEParser()
    p.feed("data: tail\n")
    assert [e.data for e in p.close()] == ["tail"]


def test_close_emits_event_without_trailing_newline():
    p = SSEParser()
    p.feed("data: tail")
    assert [e.data for e in p.close()] == ["tail"]


def test_close_on_empty_parser_yields_nothing():
    assert SSEParser().close() == []


def test_multiline_data_is_joined_with_newline():
    p = SSEParser()
    assert p.feed("data: one\ndata: two\n\n")[0].data == "one\ntwo"


def test_event_name_is_read():
    p = SSEParser()
    assert p.feed("event: ping\ndata: x\n\n")[0].event == "ping"


def test_default_event_name_is_message():
    p = SSEParser()
    assert p.feed("data: x\n\n")[0].event == "message"


def test_id_is_read():
    p = SSEParser()
    assert p.feed("id: 42\ndata: x\n\n")[0].id == "42"


def test_retry_is_read_as_int():
    p = SSEParser()
    assert p.feed("retry: 3000\ndata: x\n\n")[0].retry == 3000


def test_non_numeric_retry_is_ignored():
    p = SSEParser()
    assert p.feed("retry: soon\ndata: x\n\n")[0].retry is None


def test_comment_lines_are_skipped():
    p = SSEParser()
    assert p.feed(": keepalive\ndata: x\n\n")[0].data == "x"


def test_only_a_comment_produces_no_event():
    p = SSEParser()
    assert p.feed(": keepalive\n\n") == []


def test_crlf_line_endings():
    p = SSEParser()
    assert [e.data for e in p.feed("data: x\r\n\r\n")] == ["x"]


def test_leading_space_after_colon_is_stripped_once():
    p = SSEParser()
    assert p.feed("data:  spaced\n\n")[0].data == " spaced"


def test_blank_lines_between_events_do_not_emit_empties():
    p = SSEParser()
    assert len(p.feed("\n\ndata: x\n\n\n\n")) == 1


def test_is_done_detects_sentinel():
    assert is_done(Event(data="[DONE]"))


def test_is_done_false_for_payload():
    assert not is_done(Event(data='{"delta": "hi"}'))


def test_is_done_accepts_custom_sentinel():
    assert is_done(Event(data="END"), sentinel="END")
