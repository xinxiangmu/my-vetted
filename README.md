# my-vetted

[![verify](https://github.com/xinxiangmu/my-vetted/actions/workflows/verify.yml/badge.svg)](https://github.com/xinxiangmu/my-vetted/actions/workflows/verify.yml)

A library of code that has been **used, tested, and approved** — built for
[`vetted`](https://github.com/xinxiangmu/vetted), so a coding agent can pull a unit
instead of writing one.

Every unit here passed the gate: its tests exist, contain real assertions, pass, and
**detect breakage** — break one line of `src/` and the tests go red. That is what
lets an agent use a unit without you reviewing it afterwards.

## Use it

```bash
pip install git+https://github.com/xinxiangmu/vetted
git clone https://github.com/xinxiangmu/my-vetted ~/my-vetted
export VETTED_LIB=~/my-vetted

vetted search ratelimit
vetted pull token_bucket
```

Then point your agent at [`skills/vetted-use/SKILL.md`](https://github.com/xinxiangmu/vetted/blob/main/skills/vetted-use/SKILL.md).

## Layout

```
manifest.json          every unit, in one fetch
units/<id>/
  meta.json            I/O contract, deps, effects, version
  src/                 the code
  tests/               the original tests
  README.md            API, kill rate, usage lifted from the tests
```

`manifest.json` is the only file an agent needs to read first. It carries each
unit's public API signatures and its `effects` — whether the unit touches the
network, the filesystem, the environment, the clock, randomness, or nothing at all.

## What is in here

All sixteen are stdlib-only with zero third-party dependencies. Clocks, sleeps, and
environments are injected, which is why they can be tested deterministically.

### For agent work

| Unit | Kill rate | What it does |
|------|:---------:|--------------|
| `json_repair` | 92% | Recover JSON from LLM output: code fences, surrounding prose, trailing commas, responses cut off mid-string |
| `conversation_memory` | 92% | Chat history under a token budget; system prompt and pinned turns survive, oldest ordinary turns go first |
| `context_assembler` | 75% | Build a prompt from prioritised sections under a budget, and report what was dropped instead of truncating silently |
| `tool_registry` | 100% | Expose Python callables as tool declarations read off their signatures, then dispatch calls back with validation |
| `sse_parser` | 100% | Incremental SSE parsing for streaming responses; a token split across two network reads is not lost |
| `jsonl_log` | 83% | Append-only event log; a crashed run still leaves every prior event readable |
| `text_chunker` | 75% | Split long text into overlapping chunks on sentence boundaries, including CJK |

### General

| Unit | Kill rate | What it does |
|------|:---------:|--------------|
| `retry` | 100% | Exponential backoff with injectable sleep, so retry policy is testable without waiting |
| `secret_mask` | 100% | Redact credentials in logs, dicts, and prompts, by key name and by pattern |
| `env_config` | 83% | Typed environment reading that fails loudly at startup, not at 3am on a `None` |
| `semver` | 83% | Semantic version parsing and ordering, including pre-release rules |
| `batch_iter` | 83% | Lazy batching, sliding windows, dedupe, and grouping over iterables |
| `ttl_cache` | 83% | LRU cache with per-entry expiry and an injectable clock |
| `json_store` | 80% | Atomic JSON file writes — a crash mid-write leaves the previous version intact |
| `token_bucket` | 83% | Token bucket rate limiter with an injectable clock |
| `safe_path` | 67% | Confine user-supplied paths to a base directory; rejects traversal and absolute components |

Kill rate is the share of injected defects the unit's own tests caught. 60% is the
admission floor.

## Contributions

Not open yet. The value of this library is that one person has actually used and
vetted every unit in it; accepting units vetted by strangers removes that, and a
part-time maintainer cannot review code by description.

**Fork it and keep your own.** That is the intended shape — your library should hold
the implementations *you* approve, not mine. `vetted add ./your/code` is one command.

## Licence

MIT.
