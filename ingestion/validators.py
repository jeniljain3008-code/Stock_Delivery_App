from typing import BinaryIO

import pandas as pd

REQUIRED_COLUMNS = [
    "Date",
    "Symbol",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "DeliveryQty",
    "DeliveryPercent",
]


def parse_delivery_file(file_obj: BinaryIO, suffix: str) -> pd.DataFrame:
    if suffix in {"xlsx", "xls"}:
        df = pd.read_excel(file_obj)
    elif suffix == "csv":
        df = pd.read_csv(
            file_obj,
            thousands=","
        )
    else:
        raise ValueError("Unsupported file type. Upload CSV or Excel.")
    return validate_delivery_frame(df)


def validate_delivery_frame(df: pd.DataFrame) -> pd.DataFrame:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
    clean = df[REQUIRED_COLUMNS].copy()
    clean["Date"] = pd.to_datetime(
        clean["Date"],
        format="%d-%b-%y",
        errors="coerce"
    ).dt.date
    clean["Symbol"] = clean["Symbol"].astype(str).str.upper().str.strip()
    for col in ["Open", "High", "Low", "Close", "DeliveryPercent"]:
        clean[col] = pd.to_numeric(clean[col], errors="coerce")
    for col in ["Volume", "DeliveryQty"]:
        clean[col] = pd.to_numeric(clean[col], errors="coerce").fillna(-1).astype(int)
    if clean.isna().any().any():
        raise ValueError("Upload contains invalid dates, symbols, or numeric values.")
    if (clean[["Open", "High", "Low", "Close", "Volume", "DeliveryQty"]] < 0).any().any():
        raise ValueError("Prices, volume, and delivery quantity must be non-negative.")
    if ((clean["DeliveryPercent"] < 0) | (clean["DeliveryPercent"] > 100)).any():
        raise ValueError("DeliveryPercent must be between 0 and 100.")
    return clean
