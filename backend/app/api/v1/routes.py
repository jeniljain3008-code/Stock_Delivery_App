from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from ai_engine.analyst import answer_question
from backend.app.core.security import get_current_user
from backend.app.db.session import get_db
from backend.app.schemas import (
    AIAnswer,
    AIQuestion,
    BacktestRequest,
    DashboardSummary,
    ExplosionBacktestRequest,
)
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.upload_service import UploadService
from reports.report_service import build_gold_stocks_excel
from backend.app.services.nse_service import NSEService
from backend.app.schemas import NSEFetchRequest
from fastapi.responses import StreamingResponse
from io import StringIO

router = APIRouter(prefix="/api/v1", dependencies=[Depends(get_current_user)])
UploadFileDependency = Annotated[UploadFile, File(...)]
DatabaseDependency = Annotated[Session, Depends(get_db)]


@router.post("/nse/fetch")
async def fetch_nse_delivery_data(
    request: NSEFetchRequest,
):

    df = await NSEService().fetch_delivery_data(
        request.trade_date
    )

    return {
        "status": "success",
        "rows": len(df),
        "data": df.head(100).to_dict(
            orient="records"
        ),
    }
@router.get("/nse/download")
async def download_nse_delivery_data(
    trade_date: str,
):

    df = await NSEService().fetch_delivery_data(
        trade_date
    )

    csv_buffer = StringIO()

    df.to_csv(
        csv_buffer,
        index=False,
    )

    csv_buffer.seek(0)

    return StreamingResponse(
        iter([csv_buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename=nse_delivery_{trade_date}.csv"
        },
    )
@router.post("/uploads/delivery-data")
async def upload_delivery_data(file: UploadFileDependency, db: DatabaseDependency):
    return await UploadService(db).ingest(file)


@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary():
    return AnalyticsService().dashboard()


@router.get("/stocks")
def list_stocks():
    return AnalyticsService().stocks()


@router.get("/stocks/{symbol}/analytics")
def stock_analytics(symbol: str):
    return AnalyticsService().stock_analytics(symbol)


@router.get("/scanners/gold-stocks")
def gold_stocks():
    return AnalyticsService().gold_stocks()


@router.get("/sectors/rotation")
def sector_rotation():
    return AnalyticsService().sector_rotation()


@router.post("/backtests/run")
def backtest(request: BacktestRequest):
    return AnalyticsService().backtest(request)
    
@router.post("/backtests/explosion")
def explosion_backtest(
    request: ExplosionBacktestRequest,
):
    return AnalyticsService().explosion_backtest(
        request.days,
    )

@router.get(
    "/backtests/pre-explosion-study"
)
def pre_explosion_study(
    days: int = 365,
):

    return AnalyticsService(
    ).pre_explosion_study(
        days=days
    )

@router.get(
    "/backtests/pre-explosion-winner-study"
)
def pre_explosion_winner_study(
    days: int = 365,
):

    return AnalyticsService(
    ).pre_explosion_winner_study(
        days=days
    )

@router.get(
    "/backtests/winner-vs-loser-study"
)
def winner_vs_loser_study(
    days: int = 365,
):

    return AnalyticsService(
    ).winner_vs_loser_study(
        days=days
    )

@router.get(
    "/backtests/top-decile-study"
)
def top_decile_study(
    days: int = 365,
):

    return AnalyticsService(
    ).top_decile_study(
        days=days
    )
@router.post("/ai/ask", response_model=AIAnswer)
def ask_ai(question: AIQuestion):
    analytics = AnalyticsService()
    return answer_question(
        question.question, question.symbol, analytics.stocks(), analytics.gold_stocks()
    )


@router.get("/reports/gold-stocks.xlsx")
def gold_stock_report():
    return build_gold_stocks_excel(AnalyticsService().gold_stocks())


@router.post("/jobs/daily-refresh")
def daily_refresh():
    return {
        "status": "scheduled",
        "jobs": ["data_refresh", "ranking_refresh", "report_generation", "ai_summary"],
    }
