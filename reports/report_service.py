from io import BytesIO

import pandas as pd
from fastapi.responses import StreamingResponse


def build_gold_stocks_excel(rows: list[dict]) -> StreamingResponse:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        pd.DataFrame(rows).to_excel(writer, sheet_name="Gold Stocks", index=False)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=gold-stocks.xlsx"},
    )
