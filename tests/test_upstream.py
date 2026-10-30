"""Tests for the upstream check. Downloads are faked; nothing contacts the network."""

import json

import pytest

from fedramp_ksi.catalog import DATA_DIR
from fedramp_ksi.upstream import check, issue_body, parse_ls_remote

PINNED = json.loads((DATA_DIR / "upstream.json").read_text())
LATEST = "b" * 40


def fake_fetch(overrides=None):
    """Serve the pinned local files by upstream path, with optional replacements."""
    by_path = {meta["upstream_path"]: name for name, meta in PINNED["files"].items()}
    overrides = overrides or {}
    requested = []

    def fetch(url):
        requested.append(url)
        path = url.split(f"/{LATEST}/", 1)[1]
        return overrides.get(path, (DATA_DIR / by_path[path]).read_bytes())

    fetch.requested = requested
    return fetch


def test_unchanged_files_are_not_drift():
    drift = check(LATEST, fetch=fake_fetch())
    assert drift.changes == ()
    assert drift.pinned_commit == PINNED["commit"]
    assert drift.latest_commit == LATEST


def test_fetches_each_pinned_file_at_the_latest_commit():
    fetch = fake_fetch()
    check(LATEST, fetch=fetch)
    assert sorted(fetch.requested) == [
        f"https://raw.githubusercontent.com/FedRAMP/rules/{LATEST}/fedramp-consolidated-rules.json",
        f"https://raw.githubusercontent.com/FedRAMP/rules/{LATEST}/schemas/fedramp-consolidated-rules.schema.json",
    ]


def test_changed_file_is_reported():
    drift = check(LATEST, fetch=fake_fetch({"fedramp-consolidated-rules.json": b"{}"}))
    assert [c.upstream_path for c in drift.changes] == ["fedramp-consolidated-rules.json"]
    change = drift.changes[0]
    assert change.pinned_sha256 == PINNED["files"]["fedramp-consolidated-rules.json"]["sha256"]
    assert change.latest_sha256 != change.pinned_sha256


def test_issue_body_names_commits_and_files():
    drift = check(LATEST, fetch=fake_fetch({"fedramp-consolidated-rules.json": b"{}"}))
    body = issue_body(drift)
    assert f"compare/{PINNED['commit']}...{LATEST}" in body
    assert "| `fedramp-consolidated-rules.json` |" in body
    assert "schema.json" not in body


def test_parse_ls_remote():
    assert parse_ls_remote(f"{LATEST}\tHEAD\n") == LATEST


@pytest.mark.parametrize("output", ["", "abc\tHEAD\n", f"{LATEST}\trefs/heads/main\n"])
def test_parse_ls_remote_rejects_unexpected_output(output):
    with pytest.raises(ValueError):
        parse_ls_remote(output)
