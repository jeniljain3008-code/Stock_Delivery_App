#!/usr/bin/env python3
"""Verify the local Smart Delivery Analytics API contract.

The script intentionally uses only the Python standard library so it can be run
before installing project dependencies. Start the FastAPI server first.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
from pathlib import Path
from urllib import request
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parents[1]
SAMPLE_FILE = ROOT / "sample_data" / "nse_delivery_sample.csv"

JSON_ENDPOINTS = [
    ("GET", "/health", None),
    ("GET", "/api/v1/dashboard/summary", None),
    ("GET", "/api/v1/stocks", None),
    ("GET", "/api/v1/stocks/BEL/analytics", None),
    ("GET", "/api/v1/scanners/gold-stocks", None),
    ("GET", "/api/v1/sectors/rotation", None),
    (
        "POST",
        "/api/v1/backtests/run",
        {
            "strategy": "delivery",
            "start_date": "2025-10-01",
            "end_date": "2026-01-31",
            "min_accumulation_score": 60,
        },
    ),
    ("POST", "/api/v1/ai/ask", {"question": "Which stocks show institutional accumulation?"}),
    ("POST", "/api/v1/jobs/daily-refresh", None),
]


def _json_request(base_url: str, method: str, path: str, payload: dict | None) -> tuple[int, bytes]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = request.Request(f"{base_url}{path}", data=body, headers=headers, method=method)
    with request.urlopen(req, timeout=15) as response:  # noqa: S310 - local developer verification helper
        return response.status, response.read()


def _multipart_upload(base_url: str) -> tuple[int, bytes]:
    boundary = "----smart-delivery-boundary"
    content_type = mimetypes.guess_type(SAMPLE_FILE.name)[0] or "text/csv"
    file_bytes = SAMPLE_FILE.read_bytes()
    body = b"\r\n".join(
        [
            f"--{boundary}".encode(),
            f'Content-Disposition: form-data; name="file"; filename="{SAMPLE_FILE.name}"'.encode(),
            f"Content-Type: {content_type}".encode(),
            b"",
            file_bytes,
            f"--{boundary}--".encode(),
            b"",
        ]
    )
    req = request.Request(
        f"{base_url}/api/v1/uploads/delivery-data",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with request.urlopen(req, timeout=30) as response:  # noqa: S310 - local developer verification helper
        return response.status, response.read()


def _report_request(base_url: str) -> tuple[int, bytes]:
    req = request.Request(f"{base_url}/api/v1/reports/gold-stocks.xlsx", method="GET")
    with request.urlopen(req, timeout=15) as response:  # noqa: S310 - local developer verification helper
        return response.status, response.read(128)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify local API endpoints")
    parser.add_argument("--base-url", default="http://localhost:8000", help="FastAPI base URL")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    failures: list[str] = []
    for method, path, payload in JSON_ENDPOINTS:
        try:
            status, body = _json_request(base_url, method, path, payload)
            json.loads(body.decode("utf-8"))
            print(f"PASS {method} {path} -> {status}")
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            failures.append(f"FAIL {method} {path}: {exc}")

    for name, check in [
        ("GET /api/v1/reports/gold-stocks.xlsx", _report_request),
        ("POST /api/v1/uploads/delivery-data", _multipart_upload),
    ]:
        try:
            status, _ = check(base_url)
            print(f"PASS {name} -> {status}")
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            failures.append(f"FAIL {name}: {exc}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("All API endpoints verified successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
