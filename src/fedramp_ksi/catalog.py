"""Load the FedRAMP 20x Key Security Indicators from a pinned copy of FedRAMP/rules.

The files in data/ are copied unchanged from https://github.com/FedRAMP/rules at the
commit recorded in data/upstream.json. Loading checks each file's SHA-256 against that
record, then validates the rules against FedRAMP's own JSON schema, as FedRAMP's
AGENTS.md asks consumers to do before relying on the data.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RULES_FILE = "fedramp-consolidated-rules.json"
SCHEMA_FILE = "fedramp-consolidated-rules.schema.json"


class CatalogError(Exception):
    """The pinned data is missing, altered, or doesn't match FedRAMP's schema."""


@dataclass(frozen=True)
class Indicator:
    """One KSI, such as KSI-CED-RAT, at JSON path KSI.<theme>.indicators.<id>."""

    id: str
    theme: str
    name: str
    statement: str | None
    class_statements: dict[str, str]
    controls: tuple[str, ...]
    terms: tuple[str, ...]

    @property
    def varies_by_class(self) -> bool:
        return bool(self.class_statements)

    def statement_for(self, service_class: str) -> str | None:
        """Return the statement for a service class (a, b, c, or d).

        Returns None when the indicator varies by class and has no statement for
        this class. Another class's statement is never substituted.
        """
        if self.varies_by_class:
            return self.class_statements.get(service_class)
        return self.statement


@dataclass(frozen=True)
class Theme:
    """A KSI theme, such as KSI-CED (Cybersecurity Education)."""

    id: str
    key: str
    name: str
    status: str
    indicators: tuple[Indicator, ...]


@dataclass(frozen=True)
class Catalog:
    version: str
    last_updated: str
    source_commit: str
    default_artifacts: tuple[str, ...]
    themes: tuple[Theme, ...]

    @property
    def indicators(self) -> tuple[Indicator, ...]:
        return tuple(i for theme in self.themes for i in theme.indicators)

    def indicator(self, indicator_id: str) -> Indicator:
        for i in self.indicators:
            if i.id == indicator_id:
                return i
        raise KeyError(indicator_id)


def load_catalog(data_dir: Path = DATA_DIR) -> Catalog:
    upstream = json.loads((data_dir / "upstream.json").read_text())
    for name, meta in upstream["files"].items():
        _check_sha256(data_dir / name, meta["sha256"])

    rules = json.loads((data_dir / RULES_FILE).read_text())
    schema = json.loads((data_dir / SCHEMA_FILE).read_text())
    errors = sorted(Draft202012Validator(schema).iter_errors(rules), key=str)
    if errors:
        raise CatalogError(f"{RULES_FILE} fails FedRAMP's schema: {errors[0].message}")

    themes = tuple(_theme(key, raw) for key, raw in rules["KSI"].items())
    return Catalog(
        version=rules["info"]["version"],
        last_updated=rules["info"]["last_updated"],
        source_commit=upstream["commit"],
        default_artifacts=tuple(rules["info"]["default_artifacts"]["KSI"]),
        themes=themes,
    )


def _check_sha256(path: Path, expected: str) -> None:
    if not path.is_file():
        raise CatalogError(f"missing pinned file: {path.name}")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise CatalogError(f"{path.name} doesn't match its pinned SHA-256 in upstream.json")


def _theme(key: str, raw: dict) -> Theme:
    return Theme(
        id=raw["id"],
        key=key,
        name=raw["name"],
        status=raw["status"],
        indicators=tuple(_indicator(key, iid, ind) for iid, ind in raw["indicators"].items()),
    )


def _indicator(theme: str, indicator_id: str, raw: dict) -> Indicator:
    by_class = raw.get("varies_by_class", {})
    return Indicator(
        id=indicator_id,
        theme=theme,
        name=raw["name"],
        statement=raw.get("statement"),
        class_statements={c: v["statement"] for c, v in by_class.items()},
        controls=tuple(raw["controls"]),
        terms=tuple(raw.get("terms", ())),
    )
