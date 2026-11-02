"""Tests for the training platform client and check.

Responses are faked or served by a mock server on 127.0.0.1; nothing else is contacted,
and the token is a dummy value.
"""

import json
import threading
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

import pytest

from fedramp_ksi import training
from fedramp_ksi.training import Enrollment, TrainingAPIError, fetch_enrollments, overdue

BASE = "https://training.example.test/api"
TOKEN = "dummy-token"
AS_OF = date(2026, 11, 2)
ROWS = [
    {"email": "ana@example.test", "course": "awareness", "completed_at": "2026-03-04T12:00:00Z"},
    {"email": "ben@example.test", "course": "awareness", "completed_at": None},
    {"email": "cy@example.test", "course": "secure-dev", "completed_at": "2026-10-01T09:30:00Z"},
]


def fake_fetch(pages):
    """Serve pages in order and record each request's URL and headers."""
    requested = []

    def fetch(url, headers):
        requested.append((url, headers))
        page = int(parse_qs(urlsplit(url).query)["page"][0])
        return json.dumps(pages[page - 1] if page <= len(pages) else []).encode()

    fetch.requested = requested
    return fetch


def test_fetches_and_parses_enrollments():
    got = fetch_enrollments(BASE, TOKEN, fake_fetch([ROWS]))
    assert got == (
        Enrollment("ana@example.test", "awareness", date(2026, 3, 4)),
        Enrollment("ben@example.test", "awareness", None),
        Enrollment("cy@example.test", "secure-dev", date(2026, 10, 1)),
    )


def test_sends_the_token_and_pages_until_a_short_page(monkeypatch):
    monkeypatch.setattr(training, "PER_PAGE", 2)
    fetch = fake_fetch([ROWS[:2], ROWS[2:]])
    assert len(fetch_enrollments(BASE + "/", TOKEN, fetch)) == 3
    urls = [url for url, _ in fetch.requested]
    assert urls == [
        f"{BASE}/training/enrollments?page=1&per_page=2",
        f"{BASE}/training/enrollments?page=2&per_page=2",
    ]
    assert all(h["Authorization"] == f"Bearer {TOKEN}" for _, h in fetch.requested)


def test_reads_the_url_and_token_from_the_environment(monkeypatch):
    monkeypatch.setenv("TRAINING_API_URL", BASE)
    monkeypatch.setenv("TRAINING_API_TOKEN", TOKEN)
    fetch = fake_fetch([ROWS])
    fetch_enrollments(fetch=fetch)
    url, headers = fetch.requested[0]
    assert url.startswith(BASE) and headers["Authorization"] == f"Bearer {TOKEN}"


def test_missing_configuration_is_an_error(monkeypatch):
    monkeypatch.delenv("TRAINING_API_URL", raising=False)
    with pytest.raises(TrainingAPIError, match="set TRAINING_API_URL"):
        fetch_enrollments(token=TOKEN, fetch=fake_fetch([]))


@pytest.mark.parametrize("url", ["http://training.example.test", "ftp://127.0.0.1"])
def test_refuses_to_send_the_token_without_https(url):
    with pytest.raises(TrainingAPIError, match="use https"):
        fetch_enrollments(url, TOKEN, fake_fetch([]))


@pytest.mark.parametrize(
    ("page", "error"),
    [
        ({"data": []}, "not a list"),
        ([{"email": "ana@example.test"}], "unexpected enrollment"),
        ([{**ROWS[0], "completed_at": "last week"}], "unexpected completed_at"),
    ],
)
def test_unexpected_responses_are_errors(page, error):
    with pytest.raises(TrainingAPIError, match=error):
        fetch_enrollments(BASE, TOKEN, lambda url, headers: json.dumps(page).encode())


def done(email, course, day):
    return Enrollment(email, course, day)


def test_overdue_finds_missing_and_expired_training():
    enrollments = [
        done("current@example.test", "awareness", date(2026, 1, 1)),
        done("expired@example.test", "awareness", date(2025, 10, 1)),
        done("renewed@example.test", "awareness", date(2025, 1, 1)),
        done("renewed@example.test", "awareness", date(2026, 6, 1)),
        done("other@example.test", "secure-dev", date(2026, 6, 1)),
        done("enrolled@example.test", "awareness", None),
        done("future@example.test", "awareness", date(2026, 12, 1)),
    ]
    required = [
        "current@example.test",
        "expired@example.test",
        "renewed@example.test",
        "other@example.test",
        "enrolled@example.test",
        "future@example.test",
        "never@example.test",
    ]
    assert overdue(required, enrollments, "awareness", AS_OF) == (
        "enrolled@example.test",
        "expired@example.test",
        "future@example.test",
        "never@example.test",
        "other@example.test",
    )


def test_overdue_counts_exactly_365_days_as_current():
    enrollments = [done("ana@example.test", "awareness", date(2025, 11, 2))]
    assert overdue(["ana@example.test"], enrollments, "awareness", AS_OF) == ()
    next_day = date(2026, 11, 3)
    assert overdue(["ana@example.test"], enrollments, "awareness", next_day) == (
        "ana@example.test",
    )


def test_new_staff_have_30_days():
    started = {"new@example.test": date(2026, 10, 10), "late@example.test": date(2026, 9, 1)}
    required = ["new@example.test", "late@example.test"]
    assert overdue(required, [], "awareness", AS_OF, started) == ("late@example.test",)


def test_emails_are_compared_without_case():
    enrollments = [done("Ana@Example.test", "awareness", date(2026, 3, 4))]
    assert overdue(["ana@example.TEST"], enrollments, "awareness", AS_OF) == ()


@pytest.fixture
def mock_server(monkeypatch):
    """A local mock of the reporting API that requires the dummy token."""
    monkeypatch.setattr(training, "PER_PAGE", 2)
    pages = [ROWS[:2], ROWS[2:]]

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlsplit(self.path)
            if self.headers.get("Authorization") != f"Bearer {TOKEN}":
                self.send_response(401)
                self.end_headers()
                return
            if url.path != "/api/training/enrollments":
                self.send_response(404)
                self.end_headers()
                return
            page = int(parse_qs(url.query)["page"][0])
            body = json.dumps(pages[page - 1] if page <= len(pages) else []).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}/api"
    server.shutdown()
    server.server_close()


def test_client_against_a_local_mock_server(mock_server):
    got = fetch_enrollments(mock_server, TOKEN)
    assert [e.email for e in got] == [r["email"] for r in ROWS]


def test_mock_server_rejects_a_wrong_token(mock_server):
    with pytest.raises(OSError, match="401"):
        fetch_enrollments(mock_server, "wrong-token")
