"""Tests for the README's generated sections and the FedRAMP IDs it cites."""

import re

import pytest

from fedramp_ksi import load_catalog
from fedramp_ksi.measures import load_measures
from fedramp_ksi.readme import NB_HYPHEN, README, ReadmeError, main, sections, update


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


@pytest.fixture(scope="module")
def generated(catalog):
    return sections(catalog, load_measures(catalog))


def test_readme_is_current(generated):
    text = README.read_text()
    assert update(text, generated) == text, "run: uv run python -m fedramp_ksi.readme"


def test_every_fedramp_id_in_the_readme_exists(catalog):
    text = README.read_text().replace(NB_HYPHEN, "-")
    known = catalog.rule_ids | {i.id for i in catalog.indicators}
    cited = set(re.findall(r"\b[A-Z]{3}-[A-Z]{3}-[A-Z]{3}\b", text))
    assert cited, "expected the README to cite FedRAMP IDs"
    assert cited <= known, f"not in the pinned rules: {sorted(cited - known)}"


def test_update_replaces_only_marked_sections():
    text = "before\n<!-- BEGIN GENERATED: x -->\nold\n<!-- END GENERATED: x -->\nafter\n"
    assert update(text, {"x": "new\n"}) == (
        "before\n<!-- BEGIN GENERATED: x -->\nnew\n<!-- END GENERATED: x -->\nafter\n"
    )


def test_missing_markers_are_an_error():
    with pytest.raises(ReadmeError, match="no markers for the x section"):
        update("no markers here\n", {"x": "new\n"})


def test_class_a_lists_its_seven_ksis(generated):
    rows = [line for line in generated["class-a"].splitlines() if line.startswith("| KSI")]
    assert len(rows) == 1 + 7  # header plus one row per KSI


def test_class_b_marks_optional_ksis(generated):
    assert "Enforcing Intended State (EIS), optional at Class B" in generated["class-b"]
    assert "optional at Class C" not in generated["class-c"]


@pytest.mark.parametrize("path", [README, README.parent / "measures" / "README.md"])
def test_theme_and_indicator_names_carry_their_abbreviation(catalog, path):
    text = path.read_text()
    names = [(t.name, t.key) for t in catalog.themes]
    names += [(i.name, i.id.split("-")[2]) for i in catalog.indicators]
    # A theme name inside a longer name, such as Incident Response inside Reviewing
    # Incident Response Procedures, is checked as part of the longer name instead.
    spans = [(m.start(), m.end(), n) for n, _ in names for m in re.finditer(re.escape(n), text)]
    missing = [
        f"{name} ({key})"
        for name, key in names
        for m in re.finditer(re.escape(name), text)
        if not text.startswith(f" ({key})", m.end())
        and not any(o != name and s <= m.start() and m.end() <= e for s, e, o in spans)
    ]
    assert not missing, f"{path.name}: write these with their abbreviation: {sorted(set(missing))}"


def test_class_tables_list_every_ksi(catalog, generated):
    for name in ("class-b", "class-c"):
        assert all(i.id.replace("-", NB_HYPHEN) in generated[name] for i in catalog.indicators)


def test_unknown_argument_prints_usage(capsys):
    assert main(["--bogus"]) == 2
    assert "usage" in capsys.readouterr().err
