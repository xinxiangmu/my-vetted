"""Semantic version parsing and comparison.

String comparison gets this wrong ("1.10.0" < "1.9.0"), and so does tuple-of-ints
once pre-release tags appear. This follows semver.org ordering, including the rule
that a pre-release sorts before its own release.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

PATTERN = re.compile(
    r"^v?(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>[0-9A-Za-z.\-]+))?"
    r"(?:\+(?P<build>[0-9A-Za-z.\-]+))?$"
)


class InvalidVersion(Exception):
    """The string is not a semantic version."""


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int
    prerelease: str = ""
    build: str = ""

    def __str__(self) -> str:
        out = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            out += f"-{self.prerelease}"
        if self.build:
            out += f"+{self.build}"
        return out

    @property
    def is_prerelease(self) -> bool:
        return bool(self.prerelease)

    def bump(self, part: str = "patch") -> "Version":
        """Next version. Bumping drops any pre-release and build metadata."""
        if part == "major":
            return Version(self.major + 1, 0, 0)
        if part == "minor":
            return Version(self.major, self.minor + 1, 0)
        if part == "patch":
            return Version(self.major, self.minor, self.patch + 1)
        raise ValueError("part must be major, minor or patch")


def parse(text: str) -> Version:
    match = PATTERN.match(text.strip())
    if not match:
        raise InvalidVersion(f"not a semantic version: {text!r}")
    g = match.groupdict()
    return Version(
        int(g["major"]), int(g["minor"]), int(g["patch"]),
        g["prerelease"] or "", g["build"] or "",
    )


def _prerelease_key(prerelease: str) -> list:
    """Dot-separated identifiers; numeric ones sort below alphanumeric ones."""
    key = []
    for part in prerelease.split("."):
        if part.isdigit():
            key.append((0, int(part), ""))
        else:
            key.append((1, 0, part))
    return key


def sort_key(version: Version) -> tuple:
    """Build metadata is excluded from ordering, per the specification."""
    return (
        version.major,
        version.minor,
        version.patch,
        0 if version.prerelease else 1,
        _prerelease_key(version.prerelease) if version.prerelease else [],
    )


def compare(a: str, b: str) -> int:
    """-1 if a < b, 0 if equal, 1 if a > b."""
    ka, kb = sort_key(parse(a)), sort_key(parse(b))
    if ka < kb:
        return -1
    return 1 if ka > kb else 0


def satisfies(version: str, minimum: str) -> bool:
    """Whether `version` is at least `minimum`."""
    return compare(version, minimum) >= 0


def latest(versions: list[str]) -> str:
    if not versions:
        raise ValueError("versions must not be empty")
    return max(versions, key=lambda v: sort_key(parse(v)))
