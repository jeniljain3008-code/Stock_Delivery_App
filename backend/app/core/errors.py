from sqlalchemy.exc import OperationalError


def database_unavailable_detail(exc: OperationalError | Exception) -> dict[str, str]:
    message = str(exc.__cause__ or exc)
    hint = (
        "Database connection failed. If this is Render + Supabase, use the Supabase "
        "Session Pooler or Transaction Pooler connection string instead of the Direct "
        "Connection string, because the direct host can resolve to IPv6 on platforms "
        "without outbound IPv6 connectivity."
    )
    return {
        "error": "database_unavailable",
        "message": "The API could not connect to PostgreSQL.",
        "hint": hint,
        "details": message,
    }
