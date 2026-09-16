import pytest

from semver import InvalidVersion, compare, latest, parse, satisfies


def test_parses_basic_version():
    v = parse("1.2.3")
    assert (v.major, v.minor, v.patch) == (1, 2, 3)


def test_parses_leading_v():
    assert parse("v2.0.1").minor == 0


def test_parses_prerelease():
    assert parse("1.0.0-alpha.1").prerelease == "alpha.1"


def test_parses_build_metadata():
    assert parse("1.0.0+build.5").build == "build.5"


def test_rejects_garbage():
    with pytest.raises(InvalidVersion):
        parse("not-a-version")


def test_rejects_two_part_version():
    with pytest.raises(InvalidVersion):
        parse("1.2")


def test_rejects_leading_zero():
    with pytest.raises(InvalidVersion):
        parse("01.2.3")


def test_str_roundtrips():
    assert str(parse("1.2.3-beta+exp")) == "1.2.3-beta+exp"


def test_is_prerelease_flag():
    assert parse("1.0.0-rc1").is_prerelease
    assert not parse("1.0.0").is_prerelease


def test_numeric_ordering_beats_string_ordering():
    assert compare("1.10.0", "1.9.0") == 1


def test_equal_versions():
    assert compare("1.2.3", "1.2.3") == 0


def test_patch_ordering():
    assert compare("1.2.3", "1.2.4") == -1


def test_minor_outranks_patch():
    assert compare("1.3.0", "1.2.99") == 1


def test_major_outranks_minor():
    assert compare("2.0.0", "1.99.99") == 1


def test_prerelease_sorts_below_its_release():
    assert compare("1.0.0-alpha", "1.0.0") == -1


def test_numeric_prerelease_sorts_below_alphanumeric():
    assert compare("1.0.0-1", "1.0.0-alpha") == -1


def test_prerelease_numeric_parts_compare_numerically():
    assert compare("1.0.0-alpha.2", "1.0.0-alpha.10") == -1


def test_build_metadata_is_ignored_in_ordering():
    assert compare("1.0.0+a", "1.0.0+b") == 0


def test_satisfies_is_true_for_equal():
    assert satisfies("1.2.3", "1.2.3")


def test_satisfies_is_false_for_lower():
    assert not satisfies("1.2.2", "1.2.3")


def test_latest_picks_highest():
    assert latest(["1.0.0", "1.10.0", "1.9.9"]) == "1.10.0"


def test_latest_prefers_release_over_prerelease():
    assert latest(["1.0.0", "1.0.0-rc1"]) == "1.0.0"


def test_latest_rejects_empty_list():
    with pytest.raises(ValueError):
        latest([])


def test_bump_patch():
    assert str(parse("1.2.3").bump("patch")) == "1.2.4"


def test_bump_minor_resets_patch():
    assert str(parse("1.2.3").bump("minor")) == "1.3.0"


def test_bump_major_resets_minor_and_patch():
    assert str(parse("1.2.3").bump("major")) == "2.0.0"


def test_bump_drops_prerelease():
    assert str(parse("1.2.3-rc1").bump("patch")) == "1.2.4"


def test_bump_rejects_unknown_part():
    with pytest.raises(ValueError):
        parse("1.2.3").bump("epoch")
