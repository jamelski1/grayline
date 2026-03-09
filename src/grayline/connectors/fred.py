"""FRED economic indicators connector.

Fetches economic time series from the Federal Reserve Economic Data API,
primarily Brent crude oil prices as a proxy for Iranian oil revenue.
"""

import logging
import os

import numpy as np
import pandas as pd
import requests

from grayline.connectors.base import BaseConnector
from grayline.utils.dates import generate_week_starts

logger = logging.getLogger(__name__)

FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"
BRENT_SERIES_ID = "DCOILBRENTEU"


class FREDConnector(BaseConnector):
    name = "fred"

    def fetch(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch Brent crude oil price series from FRED."""
        api_key = os.getenv("FRED_API_KEY", "")
        if not api_key:
            raise ValueError("FRED_API_KEY required")

        params = {
            "series_id": BRENT_SERIES_ID,
            "api_key": api_key,
            "file_type": "json",
            "observation_start": start_date,
            "observation_end": end_date,
            "frequency": "w",
        }
        resp = requests.get(FRED_API_URL, params=params, timeout=60)
        resp.raise_for_status()
        observations = resp.json().get("observations", [])
        return pd.DataFrame(observations)

    def normalize(self, raw: pd.DataFrame) -> pd.DataFrame:
        """Convert FRED observations to weekly oil revenue proxy."""
        if raw.empty:
            return raw
        raw["date"] = pd.to_datetime(raw["date"])
        raw["value"] = pd.to_numeric(raw["value"], errors="coerce")
        raw = raw.dropna(subset=["value"])
        raw["week_start"] = raw["date"].dt.to_period("W-MON").dt.start_time

        weekly = raw.groupby("week_start")["value"].mean().reset_index()
        weekly.columns = ["week_start", "oil_revenue_proxy"]
        return weekly

    def load_sample(self) -> pd.DataFrame:
        """Generate realistic weekly Brent crude prices."""
        weeks = generate_week_starts("2023-01-02", periods=110)
        rng = np.random.default_rng(44)

        # Start around $80, random walk with mean reversion
        price = 80.0
        prices = []
        for _ in weeks:
            price += rng.normal(0, 2.5) + 0.05 * (80 - price)
            prices.append(round(max(price, 50), 2))

        return pd.DataFrame({
            "week_start": weeks,
            "oil_revenue_proxy": prices,
        })
