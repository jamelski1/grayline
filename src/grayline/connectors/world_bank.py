"""World Bank indicators connector.

Fetches development indicators that can serve as economic context
for strategic analysis (GDP growth, trade volumes, etc.).
"""

import logging

import numpy as np
import pandas as pd
import requests

from grayline.connectors.base import BaseConnector
from grayline.utils.dates import generate_week_starts

logger = logging.getLogger(__name__)

WB_API_URL = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"


class WorldBankConnector(BaseConnector):
    name = "world_bank"

    def fetch(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch World Bank indicator data for Iran."""
        start_year = start_date[:4]
        end_year = end_date[:4]

        indicator = "NY.GDP.MKTP.KD.ZG"  # GDP growth
        url = WB_API_URL.format(country="IRN", indicator=indicator)
        params = {
            "date": f"{start_year}:{end_year}",
            "format": "json",
            "per_page": 100,
        }
        resp = requests.get(url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if len(data) < 2:
            return pd.DataFrame()
        return pd.DataFrame(data[1])

    def normalize(self, raw: pd.DataFrame) -> pd.DataFrame:
        """Convert annual World Bank data to a lookup table."""
        if raw.empty:
            return raw
        raw = raw[["date", "value"]].dropna()
        raw.columns = ["year", "gdp_growth"]
        return raw

    def load_sample(self) -> pd.DataFrame:
        """Generate sample World Bank-style economic context.

        Since World Bank data is annual, we interpolate to weekly for the panel.
        Returns a maritime_incident_count proxy derived from economic stress.
        """
        weeks = generate_week_starts("2023-01-02", periods=110)
        rng = np.random.default_rng(45)

        # Maritime incidents in the Gulf — baseline + spikes
        incidents = rng.poisson(lam=2, size=len(weeks)).astype(float)
        # Houthi escalation period
        incidents[55:80] += rng.integers(2, 8, size=25)

        return pd.DataFrame({
            "week_start": weeks,
            "maritime_incident_count": incidents,
        })
