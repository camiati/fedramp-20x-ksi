"""Check whether FedRAMP/rules has changed the files pinned in data/.

Compares the SHA-256 of each pinned file in data/upstream.json with the same file at
the latest upstream commit. Only the pinned files are compared, so upstream changes to
other files (README, tooling) don't count as drift.

Run as a module to check the latest commit and write an issue body when files differ:

    python -m fedramp_ksi.upstream issue.md
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from fedramp_ksi.catalog import DATA_DIR

RAW_URL = "https://raw.githubusercontent.com/FedRAMP/rules/{commit}/{path}"


@dataclass(frozen=True)
class Change:
    file: str
    upstream_path: str
    pinned_sha256: str
    latest_sha256: str


@dataclass(frozen=True)
class Drift:
    pinned_commit: str
    latest_commit: str
    changes: tuple[Change, ...]


def check(
    latest_commit: str,
    fetch: Callable[[str], bytes] | None = None,
    data_dir: Path = DATA_DIR,
) -> Drift:
    """Compare each pinned file with its copy at latest_commit."""
    fetch = fetch or _fetch
    upstream = json.loads((data_dir / "upstream.json").read_text())
    changes = []
    for name, meta in upstream["files"].items():
        url = RAW_URL.format(commit=latest_commit, path=meta["upstream_path"])
        latest = hashlib.sha256(fetch(url)).hexdigest()
        if latest != meta["sha256"]:
            changes.append(Change(name, meta["upstream_path"], meta["sha256"], latest))
    return Drift(upstream["commit"], latest_commit, tuple(changes))


def latest_commit(repository: str = "https://github.com/FedRAMP/rules") -> str:
    out = subprocess.run(
        ["git", "ls-remote", repository, "HEAD"],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    ).stdout
    return parse_ls_remote(out)


def parse_ls_remote(output: str) -> str:
    sha, _, ref = output.strip().partition("\t")
    if ref != "HEAD" or len(sha) != 40:
        raise ValueError(f"unexpected git ls-remote output: {output!r}")
    return sha


def issue_body(drift: Drift) -> str:
    repo = "https://github.com/FedRAMP/rules"
    rows = "\n".join(
        f"| `{c.upstream_path}` | `{c.pinned_sha256[:12]}` | `{c.latest_sha256[:12]}` |"
        for c in drift.changes
    )
    return f"""FedRAMP/rules has changed files pinned in `data/`.

- Pinned: [`{drift.pinned_commit[:7]}`]({repo}/commit/{drift.pinned_commit})
- Latest: [`{drift.latest_commit[:7]}`]({repo}/commit/{drift.latest_commit})
- Diff: {repo}/compare/{drift.pinned_commit}...{drift.latest_commit}

| File | Pinned SHA-256 | Latest SHA-256 |
|---|---|---|
{rows}

To update, follow "Upstream data is pinned and unchanged" in CLAUDE.md: copy the new files, \
update `data/upstream.json`, and update the expectations in `tests/test_catalog.py` in the \
same pull request.
"""


def _fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print("usage: python -m fedramp_ksi.upstream ISSUE_BODY_PATH", file=sys.stderr)
        return 2
    drift = check(latest_commit())
    if not drift.changes:
        print(f"Pinned files match FedRAMP/rules at {drift.latest_commit[:7]}.")
        return 0
    Path(argv[0]).write_text(issue_body(drift))
    changed = ", ".join(c.upstream_path for c in drift.changes)
    print(f"FedRAMP/rules {drift.latest_commit[:7]} changed: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
