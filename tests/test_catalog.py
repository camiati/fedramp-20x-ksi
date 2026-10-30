"""Pin the KSI catalog so any upstream change fails the build instead of slipping through.

When FedRAMP/rules changes, update data/ and data/upstream.json, then update these
expectations deliberately in the same pull request.
"""

import hashlib
import json
import shutil

import pytest

from fedramp_ksi import CatalogError, load_catalog
from fedramp_ksi.catalog import DATA_DIR, RULES_FILE

EXPECTED_INDICATORS = {
    "CED": ["RAT"],
    "CMT": ["LMC", "RMV", "RVP", "VTD"],
    "CNA": ["DFP", "EIS", "IBP", "MAT", "OFA", "RNT", "RVP", "ULN"],
    "IAM": ["AAM", "APM", "ELP", "JIT", "SNU", "SUS"],
    "INR": ["AAR", "RIR", "RPI"],
    "MLA": ["ALA", "EVC", "LET", "OSM", "RVL"],
    "PIY": ["GIV", "RES", "RIS", "RSD", "RVD"],
    "RPL": ["ABO", "ARP", "RRO", "TRC"],
    "SCR": ["MIT", "MON"],
    "SVC": ["ACM", "ASM", "EIS", "PRR", "RUD", "SIN", "VCM", "VRI"],
}
CLASS_SPECIFIC = {"KSI-CNA-EIS", "KSI-MLA-ALA", "KSI-SVC-PRR", "KSI-SVC-RUD", "KSI-SVC-VCM"}
# Upstream maps KSI-PIY-RES (Reviewing Executive Support) to no 800-53 controls.
NO_CONTROLS = {"KSI-PIY-RES"}

# Indicator fields the loader reads. The schema also allows artifacts and references;
# if upstream starts using them, this fails so the loader is extended instead of
# silently dropping them.
HANDLED_FIELDS = {"name", "statement", "varies_by_class", "controls", "terms", "updated"}


@pytest.fixture(scope="module")
def catalog():
    return load_catalog()


def test_pinned_version(catalog):
    assert catalog.version == "2026.10.13.01"
    assert catalog.last_updated == "2026-10-13"
    assert catalog.source_commit == "a89d78477ddea98dc57eca24f5007794c2b4eeb6"


def test_ten_themes_all_stable(catalog):
    assert [t.key for t in catalog.themes] == list(EXPECTED_INDICATORS)
    assert all(t.id == f"KSI-{t.key}" for t in catalog.themes)
    assert {t.status for t in catalog.themes} == {"stable"}


def test_forty_six_indicators(catalog):
    assert len(catalog.indicators) == 46
    for theme in catalog.themes:
        expected = [f"KSI-{theme.key}-{k}" for k in EXPECTED_INDICATORS[theme.key]]
        assert [i.id for i in theme.indicators] == expected


def test_every_indicator_has_one_statement_shape(catalog):
    for i in catalog.indicators:
        assert (i.statement is None) == i.varies_by_class, i.id


def test_control_mappings(catalog):
    assert {i.id for i in catalog.indicators if not i.controls} == NO_CONTROLS
    assert sum(len(i.controls) for i in catalog.indicators) == 558


def test_class_specific_statements(catalog):
    assert {i.id for i in catalog.indicators if i.varies_by_class} == CLASS_SPECIFIC
    eis = catalog.indicator("KSI-CNA-EIS")
    assert set(eis.class_statements) == {"b", "c"}
    assert eis.statement_for("b").startswith("**Optional:**")
    assert eis.statement_for("a") is None


def test_common_statement_applies_to_every_class(catalog):
    rat = catalog.indicator("KSI-CED-RAT")
    assert rat.statement_for("a") == rat.statement_for("d") == rat.statement


def test_five_default_artifacts(catalog):
    assert len(catalog.default_artifacts) == 5


def test_loader_reads_every_field_upstream_uses():
    rules = json.loads((DATA_DIR / RULES_FILE).read_text())
    used = {f for theme in rules["KSI"].values() for i in theme["indicators"].values() for f in i}
    assert used <= HANDLED_FIELDS


def test_unknown_indicator_raises(catalog):
    with pytest.raises(KeyError):
        catalog.indicator("KSI-XXX-YYY")


def test_altered_file_is_rejected(tmp_path):
    shutil.copytree(DATA_DIR, tmp_path, dirs_exist_ok=True)
    with (tmp_path / RULES_FILE).open("a") as f:
        f.write("\n")
    with pytest.raises(CatalogError, match="SHA-256"):
        load_catalog(tmp_path)


def test_schema_violation_is_rejected(tmp_path):
    shutil.copytree(DATA_DIR, tmp_path, dirs_exist_ok=True)
    rules = json.loads((tmp_path / RULES_FILE).read_text())
    del rules["KSI"]["CED"]["indicators"]["KSI-CED-RAT"]["controls"]
    (tmp_path / RULES_FILE).write_text(json.dumps(rules))
    upstream = json.loads((tmp_path / "upstream.json").read_text())
    upstream["files"][RULES_FILE]["sha256"] = _sha256(tmp_path / RULES_FILE)
    (tmp_path / "upstream.json").write_text(json.dumps(upstream))
    with pytest.raises(CatalogError, match="schema"):
        load_catalog(tmp_path)


def _sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
