"""Load the measures that demonstrate each KSI and report readiness by certification class.

A measure is one specific, checkable thing that demonstrates a KSI. Measures live in
measures/<THEME>.toml. Each one supplies FedRAMP's first two default KSI artifacts
(what the measure is and its objective, and its cycle) and states whether it is
automated, which feeds the fourth (SDR-CSX-KSI).

Readiness follows FRC-CSX-VVK: each KSI needs at least 1 automated method for Class B,
2 for Class C, and 4 for Class D. Class A has no minimum.

Run as a module to print readiness for every class:

    python -m fedramp_ksi.measures
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from fedramp_ksi.catalog import Catalog, load_catalog

MEASURES_DIR = Path(__file__).resolve().parents[2] / "measures"

# FRC-CSX-VVK: minimum automated methods per KSI, by certification class.
AUTOMATED_MINIMUM = {"b": 1, "c": 2, "d": 4}
# The class this repo's theoretical service aims for. Every theme with measures must meet it.
TARGET_CLASS = "c"

SOURCES = {
    "aws-cloudtrail",
    "aws-config",
    "aws-security-hub",
    "github",
    "terraform",
    "vanta",
    "attestation",
}
CYCLES = {"per-change", "continuous", "daily", "weekly", "monthly", "quarterly", "annual"}
# The evidenceType values allowed by FedRAMP's Security Decision Record schema.
EVIDENCE_TYPES = {
    "Log",
    "Report",
    "Screenshot",
    "Configuration",
    "Policy",
    "Procedure",
    "Audit Record",
}

REQUIRED = (
    "id",
    "ksi",
    "objective",
    "check",
    "metric",
    "source",
    "cycle",
    "automated",
    "evidence_type",
    "controls",
)
OPTIONAL = ("manual_reason",)


class MeasureError(Exception):
    """A measure file is malformed or doesn't match the KSI catalog."""


@dataclass(frozen=True)
class Measure:
    id: str
    ksi: str
    objective: str
    check: str
    metric: str
    source: str
    cycle: str
    automated: bool
    evidence_type: str
    controls: tuple[str, ...]
    manual_reason: str | None = None


@dataclass(frozen=True)
class Readiness:
    """How many of a theme's KSIs meet a class's automated-measure minimum."""

    theme: str
    service_class: str
    ready: int
    total: int
    short: tuple[str, ...]


def load_measures(catalog: Catalog, measures_dir: Path = MEASURES_DIR) -> tuple[Measure, ...]:
    measures = []
    for path in sorted(measures_dir.glob("*.toml")):
        raw = tomllib.loads(path.read_text())
        for entry in raw.get("measure", []):
            measures.append(_measure(path.name, entry))
    _validate(measures, catalog)
    return tuple(measures)


def readiness(catalog: Catalog, measures: tuple[Measure, ...]) -> tuple[Readiness, ...]:
    automated: dict[str, int] = {}
    for m in measures:
        if m.automated:
            automated[m.ksi] = automated.get(m.ksi, 0) + 1
    results = []
    for theme in catalog.themes:
        for service_class, minimum in AUTOMATED_MINIMUM.items():
            short = tuple(i.id for i in theme.indicators if automated.get(i.id, 0) < minimum)
            total = len(theme.indicators)
            results.append(Readiness(theme.key, service_class, total - len(short), total, short))
    return tuple(results)


def _measure(filename: str, entry: dict) -> Measure:
    where = f"{filename}: {entry.get('id', '<no id>')}"
    missing = [f for f in REQUIRED if f not in entry]
    unknown = sorted(set(entry) - set(REQUIRED) - set(OPTIONAL))
    if missing:
        raise MeasureError(f"{where} is missing {', '.join(missing)}")
    if unknown:
        raise MeasureError(f"{where} has unknown fields: {', '.join(unknown)}")
    return Measure(**{**entry, "controls": tuple(entry["controls"])})


def _validate(measures: list[Measure], catalog: Catalog) -> None:
    indicators = {i.id: i for i in catalog.indicators}
    seen = set()
    for m in measures:
        if m.id in seen:
            raise MeasureError(f"duplicate measure id {m.id}")
        seen.add(m.id)
        if m.ksi not in indicators:
            raise MeasureError(f"{m.id} refers to unknown KSI {m.ksi}")
        if not m.id.startswith(m.ksi.removeprefix("KSI-") + "-"):
            raise MeasureError(f"{m.id} should start with {m.ksi.removeprefix('KSI-')}-")
        for field, value, allowed in (
            ("source", m.source, SOURCES),
            ("cycle", m.cycle, CYCLES),
            ("evidence_type", m.evidence_type, EVIDENCE_TYPES),
        ):
            if value not in allowed:
                raise MeasureError(f"{m.id} has unknown {field} {value!r}")
        if not isinstance(m.automated, bool):
            raise MeasureError(f"{m.id}: automated must be true or false")
        if not m.automated and not m.manual_reason:
            raise MeasureError(f"{m.id} is manual, so it needs a manual_reason")
        extra = set(m.controls) - set(indicators[m.ksi].controls)
        if not m.controls or extra:
            raise MeasureError(
                f"{m.id} controls must be a non-empty subset of {m.ksi}'s controls"
                + (f"; not mapped: {', '.join(sorted(extra))}" if extra else "")
            )


def main() -> int:
    catalog = load_catalog()
    results = readiness(catalog, load_measures(catalog))
    print("Theme  Class B  Class C  Class D")
    for theme in catalog.themes:
        row = {r.service_class: r for r in results if r.theme == theme.key}
        cells = "  ".join(f"{row[c].ready:>2}/{row[c].total:<4}" for c in AUTOMATED_MINIMUM)
        print(f"{theme.key:<5}  {cells}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
