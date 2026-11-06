"""Generate the README's readiness and certification class sections.

Each section sits between <!-- BEGIN GENERATED: name --> and <!-- END GENERATED: name -->
markers in README.md. They're built from the pinned catalog and the measures, and are
never edited by hand; tests fail when they're out of date. To regenerate them:

    python -m fedramp_ksi.readme
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from fedramp_ksi.catalog import Catalog, Indicator, Theme, load_catalog
from fedramp_ksi.measures import AUTOMATED_MINIMUM, Measure, load_measures, readiness

README = Path(__file__).resolve().parents[2] / "README.md"
# A non-breaking hyphen, so IDs like KSI-CED-RAT don't wrap in table cells.
NB_HYPHEN = "&#8209;"


class ReadmeError(Exception):
    """README.md is missing the markers for a generated section."""


def sections(catalog: Catalog, measures: tuple[Measure, ...]) -> dict[str, str]:
    """Every generated section's Markdown, by marker name."""
    return {
        "readiness": _readiness(catalog, measures),
        "class-a": _class_a(catalog, measures),
        "class-b": _class(catalog, measures, "b"),
        "class-c": _class(catalog, measures, "c"),
    }


def update(text: str, generated: dict[str, str]) -> str:
    """Replace each generated section in text, leaving everything else unchanged."""
    for name, body in generated.items():
        pattern = re.compile(
            rf"(<!-- BEGIN GENERATED: {name} -->\n).*?(<!-- END GENERATED: {name} -->)",
            re.DOTALL,
        )
        if not pattern.search(text):
            raise ReadmeError(f"README.md has no markers for the {name} section")
        text = pattern.sub(lambda m, body=body: m.group(1) + body + m.group(2), text, count=1)
    return text


def _readiness(catalog: Catalog, measures: tuple[Measure, ...]) -> str:
    results = readiness(catalog, measures)
    covered = {m.ksi.split("-")[1] for m in measures}
    lines = ["| Theme | Class B | Class C | Class D |", "|---|---|---|---|"]
    others = [t for t in catalog.themes if t.key not in covered]
    for theme in catalog.themes:
        if theme.key in covered:
            row = {r.service_class: r for r in results if r.theme == theme.key}
            cells = " | ".join(f"{row[c].ready}/{row[c].total}" for c in AUTOMATED_MINIMUM)
            lines.append(f"| {_theme(theme)} | {cells} |")
    if others:
        total = sum(len(t.indicators) for t in others)
        names = ", ".join(_theme(t) for t in others)
        cells = " | ".join(f"0/{total}" for _ in AUTOMATED_MINIMUM)
        lines.append(f"| Other {len(others)} themes: {names} | {cells} |")
    return "\n".join(lines) + "\n"


def _class_a(catalog: Catalog, measures: tuple[Measure, ...]) -> str:
    themes = {t.key: _theme(t) for t in catalog.themes}
    required = [catalog.indicator(i) for i in catalog.class_a_indicators]
    rows = []
    for i in required:
        ours = [m for m in measures if m.ksi == i.id]
        automated = sum(m.automated for m in ours)
        rows.append(
            f"| {_id(i.id)} | {themes[i.theme]} | {_indicator(i)} | {len(ours)} | {automated} |"
        )
    missing = [i for i in required if not any(m.ksi == i.id for m in measures)]
    if missing:
        summary = (
            f"**{len(required) - len(missing)} of the {len(required)} KSIs Class A requires** "
            "have at least one measure in [`measures/`](./measures/); the rest have none yet."
        )
    else:
        summary = (
            f"**All {len(required)} KSIs Class A requires** have at least one measure in "
            "[`measures/`](./measures/), so this repo covers each of them."
        )
    return _collapsed(
        summary,
        f"The {len(required)} KSIs Class A requires",
        ["| KSI ID | Theme | Indicator | Measures | Automated |", "|---|---|---|---|---|", *rows],
    )


def _class(catalog: Catalog, measures: tuple[Measure, ...], service_class: str) -> str:
    minimum = AUTOMATED_MINIMUM[service_class]
    short = {
        ksi
        for r in readiness(catalog, measures)
        if r.service_class == service_class
        for ksi in r.short
    }
    themes = {t.key: _theme(t) for t in catalog.themes}
    automated = {i.id: 0 for i in catalog.indicators}
    for m in measures:
        if m.automated:
            automated[m.ksi] += 1
    rows = [
        f"| {_id(i.id)} | {themes[i.theme]} | {_name(i, service_class)} | {automated[i.id]} | "
        f"{'No' if i.id in short else 'Yes'} |"
        for i in catalog.indicators
    ]
    total = len(catalog.indicators)
    word = "measure" if minimum == 1 else "measures"
    return _collapsed(
        f"**{total - len(short)} of {total} KSIs ready**, with at least {minimum} "
        f"automated {word} each.",
        f"All {total} KSIs at Class {service_class.upper()}",
        [
            "| KSI ID | Theme | Indicator | Automated measures | Ready |",
            "|---|---|---|---|---|",
            *rows,
        ],
    )


def _collapsed(summary: str, toggle: str, table: list[str]) -> str:
    """A summary line, then a table hidden behind a toggle that GitHub renders."""
    lines = [summary, "", "<details>", f"<summary>{toggle}</summary>", "", *table, ""]
    return "\n".join([*lines, "</details>"]) + "\n"


def _name(indicator: Indicator, service_class: str) -> str:
    statement = indicator.statement_for(service_class)
    if statement is None:
        return f"{_indicator(indicator)}, no Class {service_class.upper()} statement"
    if statement.startswith("**Optional:**"):
        return f"{_indicator(indicator)}, optional at Class {service_class.upper()}"
    return _indicator(indicator)


def _indicator(indicator: Indicator) -> str:
    """An indicator's name with the end of its ID, e.g. Logging Changes (LMC)."""
    return f"{indicator.name} ({indicator.id.split('-')[2]})"


def _theme(theme: Theme) -> str:
    """A theme's name with its key, e.g. Change Management (CMT), the middle of KSI-CMT-LMC."""
    return f"{theme.name} ({theme.key})"


def _id(identifier: str) -> str:
    return identifier.replace("-", NB_HYPHEN)


def main(argv: list[str]) -> int:
    if argv:
        print("usage: python -m fedramp_ksi.readme", file=sys.stderr)
        return 2
    catalog = load_catalog()
    text = README.read_text()
    new = update(text, sections(catalog, load_measures(catalog)))
    if new == text:
        print("README.md is current")
    else:
        README.write_text(new)
        print("updated README.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
