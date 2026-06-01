from pathlib import Path

ROUTES_FILE = Path("backend/app/api/v1/routes.py")


def test_all_public_api_endpoints_are_declared():
    source = ROUTES_FILE.read_text()
    expected_paths = [
        '"/uploads/delivery-data"',
        '"/dashboard/summary"',
        '"/stocks"',
        '"/stocks/{symbol}/analytics"',
        '"/scanners/gold-stocks"',
        '"/sectors/rotation"',
        '"/backtests/run"',
        '"/ai/ask"',
        '"/reports/gold-stocks.xlsx"',
        '"/jobs/daily-refresh"',
    ]
    for path in expected_paths:
        assert path in source


def test_local_api_verification_script_documents_every_endpoint():
    script = Path("scripts/verify_api_endpoints.py").read_text()
    expected_paths = [
        "/health",
        "/api/v1/dashboard/summary",
        "/api/v1/stocks",
        "/api/v1/stocks/BEL/analytics",
        "/api/v1/scanners/gold-stocks",
        "/api/v1/sectors/rotation",
        "/api/v1/backtests/run",
        "/api/v1/ai/ask",
        "/api/v1/jobs/daily-refresh",
        "/api/v1/reports/gold-stocks.xlsx",
        "/api/v1/uploads/delivery-data",
    ]
    for path in expected_paths:
        assert path in script
