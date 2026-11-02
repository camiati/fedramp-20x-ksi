"""Tests for measures: they match the catalog and meet the target class."""

import textwrap

import pytest

from fedramp_ksi import load_catalog
from fedramp_ksi.measures import (
    AUTOMATED_MINIMUM,
    TARGET_CLASS,
    MeasureError,
    decisions_report,
    load_measures,
    main,
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
decisions = ["d"]
"""
MANUAL = 'automated = false\nmanual_reason = "needs a person"'


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


@pytest.fixture(scope="module")
def measures(catalog):
    return load_measures(catalog)


@pytest.mark.parametrize(
    ("theme", "total", "manual"),
    [
        ("CED", 5, 1),
        ("CMT", 10, 1),
        ("CNA", 27, 5),
        ("IAM", 18, 2),
        ("INR", 11, 2),
        ("MLA", 14, 3),
        ("SVC", 23, 3),
    ],
)
def test_measure_counts(measures, theme, total, manual):
    ours = [m for m in measures if m.ksi.startswith(f"KSI-{theme}-")]
    assert len(ours) == total
    assert sum(not m.automated for m in ours) == manual


def test_themes_with_measures_meet_the_target_class(catalog, measures):
    themes = {m.ksi.split("-")[1] for m in measures}
    for r in readiness(catalog, measures):
        if r.theme in themes and r.service_class == TARGET_CLASS:
            assert r.short == (), f"{r.theme} is short of Class {TARGET_CLASS.upper()}: {r.short}"


@pytest.mark.parametrize(
    ("theme", "expected"),
    [
        ("CED", {"b": (1, 1), "c": (1, 1), "d": (1, 1)}),
        ("CMT", {"b": (4, 4), "c": (4, 4), "d": (0, 4)}),
        ("CNA", {"b": (8, 8), "c": (8, 8), "d": (0, 8)}),
        ("IAM", {"b": (6, 6), "c": (6, 6), "d": (0, 6)}),
        ("INR", {"b": (3, 3), "c": (3, 3), "d": (0, 3)}),
        ("MLA", {"b": (5, 5), "c": (5, 5), "d": (0, 5)}),
        ("SVC", {"b": (8, 8), "c": (8, 8), "d": (0, 8)}),
    ],
)
def test_readiness_by_class(catalog, measures, theme, expected):
    got = {
        r.service_class: (r.ready, r.total)
        for r in readiness(catalog, measures)
        if r.theme == theme
    }
    assert got == expected


def test_themes_without_measures_are_not_ready(catalog, measures):
    scr = [r for r in readiness(catalog, measures) if r.theme == "SCR"]
    assert {r.service_class for r in scr} == set(AUTOMATED_MINIMUM)
    assert all(r.ready == 0 and r.short == ("KSI-SCR-MIT", "KSI-SCR-MON") for r in scr)


def test_manual_measures_do_not_count(catalog, write):
    manual = load_measures(catalog, write(VALID.replace("automated = true", MANUAL)))
    ced_b = next(
        r for r in readiness(catalog, manual) if r.theme == "CED" and r.service_class == "b"
    )
    assert ced_b.ready == 0


def test_valid_measure_loads(catalog, write):
    (m,) = load_measures(catalog, write(VALID))
    assert m.id == "CED-RAT-01" and m.controls == ("at-2",)
    assert m.decisions == ("d",) and m.rules == ()


def test_rules_name_fedramp_rules(catalog, write):
    (m,) = load_measures(catalog, write(VALID + 'rules = ["FRC-CSX-VVK"]\n'))
    assert m.rules == ("FRC-CSX-VVK",)


def test_decisions_report(catalog, write):
    measures = load_measures(catalog, write(VALID + 'rules = ["FRC-CSX-VVK"]\n'))
    assert decisions_report(measures) == (
        "CED-RAT-01  KSI-CED-RAT\n"
        "  FedRAMP rules: FRC-CSX-VVK\n"
        "  Controls:      at-2\n"
        "  Decisions:\n"
        "    - d\n"
    )


def test_every_measure_states_its_decisions(measures):
    assert all(m.decisions for m in measures)
    assert "none beyond the KSI" in decisions_report(measures)


def test_incident_reporting_implements_the_iec_rules(measures):
    (m,) = [m for m in measures if m.id == "INR-RIR-02"]
    assert m.rules == ("IEC-CSO-EFR", "IEC-CSO-IIR", "IEC-CSO-OIR", "IEC-CSO-FIR")


def test_unknown_option_prints_usage(capsys):
    assert main(["--bogus"]) == 2
    assert "usage" in capsys.readouterr().err


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
        ('decisions = ["d"]\n', "", "missing decisions"),
        ('decisions = ["d"]', "decisions = []", "at least one decision"),
        ('decisions = ["d"]', 'decisions = [" "]', "at least one decision"),
        ('decisions = ["d"]', 'decisions = "d"', "decisions must be a list"),
        ('decisions = ["d"]', 'decisions = ["d"]\nrules = ["XXX-YYY-ZZZ"]', "unknown FedRAMP"),
        ('decisions = ["d"]', 'decisions = ["d"]\nrules = ["KSI-CED-RAT"]', "unknown FedRAMP"),
        ('decisions = ["d"]', 'decisions = ["d"]\nrules = "FRC-CSX-VVK"', "rules must be a list"),
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
