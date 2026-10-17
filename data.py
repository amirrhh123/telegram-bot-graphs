"""Fetch daily currency history when a chart is requested."""

import numpy as np
import pandas as pd
import requests

BASE_URL = "https://raw.githubusercontent.com/iran-market/iran-market.github.io/main/data/history"


def get_history(currency: str, today: pd.Timestamp | None = None) -> pd.DataFrame:
    """Return three calendar months of daily high/low midpoint prices in toman."""
    if currency not in {"USD", "EUR"}:
        raise ValueError("Unsupported currency")
    response = requests.get(f"{BASE_URL}/{currency}_IRR_FREE.json", timeout=20)
    response.raise_for_status()
    payload = response.json()
    if payload["meta"]["unit"] != "toman":
        raise ValueError("Unexpected price unit")
    frame = pd.DataFrame(payload["data"])
    if frame.empty:
        raise ValueError("No price history available")
    frame["timestamp"] = pd.to_datetime(frame["t_tehran"], utc=True).dt.tz_convert(
        "Asia/Tehran"
    )
    end = pd.Timestamp.now(tz="Asia/Tehran") if today is None else pd.Timestamp(today)
    end = end.tz_localize("Asia/Tehran") if end.tzinfo is None else end.tz_convert("Asia/Tehran")
    end = end.normalize()
    start = end - pd.DateOffset(months=3)
    frame = frame.loc[
        (frame["timestamp"] >= start)
        & (frame["timestamp"] < end + pd.DateOffset(days=1))
    ].copy()
    if frame.empty:
        raise ValueError("No prices available in the last three months")
    high = pd.to_numeric(frame["high"], errors="raise")
    low = pd.to_numeric(frame["low"], errors="raise")
    frame["price"] = (high + low) / 2
    if not np.isfinite(frame["price"]).all() or (low <= 0).any() or (high < low).any():
        raise ValueError("Invalid price history")
    return frame.sort_values("timestamp")[["timestamp", "date_jalali", "price"]].reset_index(drop=True)
