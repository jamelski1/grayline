"""GDELT media and event signals connector.

Fetches data from the GDELT Project to track media tone,
event counts, and escalation signals related to Iran and regional activity.
"""

import logging

import numpy as np
import pandas as pd
import requests

from grayline.connectors.base import BaseConnector
from grayline.utils.dates import generate_week_starts

logger = logging.getLogger(__name__)

GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"


class GDELTConnector(BaseConnector):
    name = "gdelt"

    def fetch(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch GDELT document counts for Iran-related themes."""
        params = {
            "query": "Iran IRGC proxy",
            "mode": "timelinevol",
            "startdatetime": start_date.replace("-", "") + "000000",
            "enddatetime": end_date.replace("-", "") + "000000",
            "format": "json",
        }
        resp = requests.get(GDELT_DOC_API, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if "timeline" not in data:
            return pd.DataFrame()
        series = data["timeline"][0].get("data", [])
        return pd.DataFrame(series)

    def normalize(self, raw: pd.DataFrame) -> pd.DataFrame:
        """Convert GDELT timeline data to weekly escalation index."""
        if raw.empty:
            return raw
        raw["date"] = pd.to_datetime(raw["date"])
        raw["week_start"] = raw["date"].dt.to_period("W-MON").dt.start_time
        weekly = raw.groupby("week_start")["value"].mean().reset_index()
        weekly.columns = ["week_start", "regional_escalation_index"]
        return weekly

    def load_sample(self) -> pd.DataFrame:
        """Generate realistic weekly escalation index values."""
        weeks = generate_week_starts("2023-01-02", periods=110)
        rng = np.random.default_rng(46)

        # Base escalation index 0-100 scale
        base = 35.0
        values = []
        for i in range(len(weeks)):
            noise = rng.normal(0, 5)
            mean_revert = 0.1 * (35 - base)
            base += noise + mean_revert
            base = np.clip(base, 5, 95)
            values.append(round(base, 1))

        values = np.array(values)
        # Escalation spikes aligned with proxy attack periods
        values[60:75] += rng.uniform(10, 25, size=15)
        values[90:100] += rng.uniform(5, 15, size=10)
        values = np.clip(values, 0, 100).round(1)

        return pd.DataFrame({
            "week_start": weeks,
            "regional_escalation_index": values,
        })
