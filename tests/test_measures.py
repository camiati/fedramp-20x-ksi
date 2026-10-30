"""Tests for measures: they match the catalog and meet the target class."""

import textwrap

import pytest

from fedramp_ksi import load_catalog
from fedramp_ksi.measures import (
    AUTOMATED_MINIMUM,
    TARGET_CLASS,
    MeasureError,
    load_measures,
    readiness,
)

VALID = """
[[measure]]
id = "CED-RAT-01"
ksi = "KSI-CED-RAT"
objective = "o"
check = "c"
metric = "m"
source = "github"
cycle = "daily"
automated = true
evidence_type = "Report"
controls = ["at-2"]
"""
MANUAL = 'automated = false\nmanual_reason = "needs a person"'


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


@pytest.fixture(scope="module")
def measures(catalog):
    return load_measures(catalog)


def test_change_management_measures(measures):
    cmt = [m for m in measures if m.ksi.startswith("KSI-CMT-")]
    assert len(cmt) == 10
    assert sum(not m.automated for m in cmt) == 1


def test_themes_with_measures_meet_the_target_class(catalog, measures):
    themes = {m.ksi.split("-")[1] for m in measures}
    for r in readiness(catalog, measures):
        if r.theme in themes and r.service_class == TARGET_CLASS:
            assert r.short == (), f"{r.theme} is short of Class {TARGET_CLASS.upper()}: {r.short}"


def test_readiness_by_class(catalog, measures):
    cmt = {
        r.service_class: (r.ready, r.total)
        for r in readiness(catalog, measures)
        if r.theme == "CMT"
    }
    assert cmt == {"b": (4, 4), "c": (4, 4), "d": (0, 4)}


def test_themes_without_measures_are_not_ready(catalog, measures):
    ced = [r for r in readiness(catalog, measures) if r.theme == "CED"]
    assert {r.service_class for r in ced} == set(AUTOMATED_MINIMUM)
    assert all(r.ready == 0 and r.short == ("KSI-CED-RAT",) for r in ced)


def test_manual_measures_do_not_count(catalog, write):
    manual = load_measures(catalog, write(VALID.replace("automated = true", MANUAL)))
    ced_b = next(
        r for r in readiness(catalog, manual) if r.theme == "CED" and r.service_class == "b"
    )
    assert ced_b.ready == 0


def test_valid_measure_loads(catalog, write):
    (m,) = load_measures(catalog, write(VALID))
    assert m.id == "CED-RAT-01" and m.controls == ("at-2",)


@pytest.mark.parametrize(
    ("old", "new", "error"),
    [
        ('ksi = "KSI-CED-RAT"', 'ksi = "KSI-CED-XXX"', "unknown KSI"),
        ('id = "CED-RAT-01"', 'id = "CMT-LMC-01"', "should start with CED-RAT-"),
        ('controls = ["at-2"]', 'controls = ["ac-2"]', "not mapped: ac-2"),
        ('controls = ["at-2"]', "controls = []", "non-empty subset"),
        ('source = "github"', 'source = "jira"', "unknown source"),
        ('cycle = "daily"', 'cycle = "hourly"', "unknown cycle"),
        ('evidence_type = "Report"', 'evidence_type = "Email"', "unknown evidence_type"),
        ("automated = true", "automated = false", "needs a manual_reason"),
        ("automated = true", 'automated = "yes"', "true or false"),
        ('metric = "m"\n', "", "missing metric"),
        ('metric = "m"', 'metric = "m"\nowner = "x"', "unknown fields: owner"),
    ],
)
def test_invalid_measures_are_rejected(catalog, write, old, new, error):
    with pytest.raises(MeasureError, match=error):
        load_measures(catalog, write(VALID.replace(old, new)))


def test_duplicate_ids_are_rejected(catalog, write):
    with pytest.raises(MeasureError, match="duplicate"):
        load_measures(catalog, write(VALID + VALID))


@pytest.fixture
def write(tmp_path):
    """Write a measures file to a temporary directory and return the directory."""

    def _write(text):
        (tmp_path / "CED.toml").write_text(textwrap.dedent(text))
        return tmp_path

    return _write
