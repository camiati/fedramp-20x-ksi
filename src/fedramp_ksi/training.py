"""Check training completion against who needs it, for KSI-CED-RAT (measures/CED.toml).

The training platform is a placeholder: a read-only reporting API that lists course
enrollments as JSON, one page at a time. There is no real platform behind it. To connect
one, map its endpoint and field names in fetch_enrollments and _enrollment; overdue, the
check itself, stays the same.

    GET {base_url}/training/enrollments?page=1&per_page=500
    Authorization: Bearer <token>

    [{"email": "a@example.com", "course": "security-awareness",
      "completed_at": "2026-03-04T12:00:00Z"}, ...]

A page shorter than per_page is the last one. The base URL and token come from the
TRAINING_API_URL and TRAINING_API_TOKEN environment variables, never from a file, and the
token is only sent over HTTPS (or plain HTTP to this machine, for local mock servers).
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import date, datetime, timedelta

URL_ENV = "TRAINING_API_URL"
TOKEN_ENV = "TRAINING_API_TOKEN"
PER_PAGE = 500
# CED-RAT-01 to 04: a course is current for 365 days, and new staff have 30 days to finish.
VALID_FOR = timedelta(days=365)
GRACE = timedelta(days=30)
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}

Fetch = Callable[[str, dict[str, str]], bytes]


class TrainingAPIError(Exception):
    """The training platform isn't configured or returned something unexpected."""


@dataclass(frozen=True)
class Enrollment:
    email: str
    course: str
    completed: date | None


def fetch_enrollments(
    base_url: str | None = None,
    token: str | None = None,
    fetch: Fetch | None = None,
) -> tuple[Enrollment, ...]:
    """Every enrollment the platform reports, across all pages."""
    base_url = base_url or _env(URL_ENV)
    token = token or _env(TOKEN_ENV)
    fetch = fetch or _fetch
    _require_https(base_url)
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    enrollments: list[Enrollment] = []
    page = 1
    while True:
        query = urllib.parse.urlencode({"page": page, "per_page": PER_PAGE})
        rows = json.loads(fetch(f"{base_url.rstrip('/')}/training/enrollments?{query}", headers))
        if not isinstance(rows, list):
            raise TrainingAPIError(f"page {page} is not a list of enrollments")
        enrollments.extend(_enrollment(row) for row in rows)
        if len(rows) < PER_PAGE:
            return tuple(enrollments)
        page += 1


def overdue(
    required: Iterable[str],
    enrollments: Iterable[Enrollment],
    course: str,
    as_of: date,
    started: Mapping[str, date] | None = None,
) -> tuple[str, ...]:
    """The people in required with no completion of course in the 365 days before as_of.

    Someone in started who began less than 30 days before as_of isn't overdue yet.
    Emails are compared without case, and the result is sorted.
    """
    latest: dict[str, date] = {}
    for e in enrollments:
        if e.course == course and e.completed and e.completed <= as_of:
            email = e.email.lower()
            latest[email] = max(latest.get(email, e.completed), e.completed)
    started = {email.lower(): day for email, day in (started or {}).items()}
    late = []
    for email in {r.lower() for r in required}:
        done = latest.get(email)
        if done and as_of - done <= VALID_FOR:
            continue
        begun = started.get(email)
        if begun and as_of - begun < GRACE:
            continue
        late.append(email)
    return tuple(sorted(late))


def _enrollment(row: object) -> Enrollment:
    if not isinstance(row, dict) or not {"email", "course", "completed_at"} <= row.keys():
        raise TrainingAPIError(f"unexpected enrollment: {row!r}")
    completed = row["completed_at"]
    try:
        day = datetime.fromisoformat(completed).date() if completed else None
    except (TypeError, ValueError) as err:
        raise TrainingAPIError(f"unexpected completed_at: {completed!r}") from err
    return Enrollment(row["email"], row["course"], day)


def _env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise TrainingAPIError(f"set {name} to connect to the training platform")
    return value


def _require_https(base_url: str) -> None:
    url = urllib.parse.urlsplit(base_url)
    if url.scheme != "https" and not (url.scheme == "http" and url.hostname in LOCAL_HOSTS):
        raise TrainingAPIError(f"refusing to send the token to {base_url}: use https")


def _fetch(url: str, headers: dict[str, str]) -> bytes:
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()
