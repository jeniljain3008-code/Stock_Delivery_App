import pytest

sqlalchemy_exc = pytest.importorskip("sqlalchemy.exc")

from backend.app.core.errors import database_unavailable_detail


def test_database_unavailable_detail_mentions_supabase_pooler():
    exc = sqlalchemy_exc.OperationalError("select 1", {}, Exception("Network is unreachable"))

    detail = database_unavailable_detail(exc)

    assert detail["error"] == "database_unavailable"
    assert "Session Pooler" in detail["hint"]
    assert "Direct Connection" in detail["hint"]
    assert "Network is unreachable" in detail["details"]
