"""ACLED conflict and protest data connector.

Fetches event data from ACLED to track:
- Iran domestic protest counts (intermediate indicator)
- Proxy group attack counts (outcome indicator)
"""

import logging
import os

import numpy as np
import pandas as pd
import requests

from grayline.connectors.base import BaseConnector
from grayline.utils.dates import generate_week_starts

logger = logging.getLogger(__name__)

ACLED_API_URL = "https://api.acleddata.com/acled/read"


class ACLEDConnector(BaseConnector):
    name = "acled"

    def fetch(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch ACLED events for Iran and proxy conflict regions."""
        api_key = os.getenv("ACLED_API_KEY", "")
        email = os.getenv("ACLED_EMAIL", "")
        if not api_key or not email:
            raise ValueError("ACLED_API_KEY and ACLED_EMAIL required")

        params = {
            "key": api_key,
            "email": email,
            "event_date": f"{start_date}|{end_date}",
            "event_date_where": "BETWEEN",
            "region": "11",  # Middle East
            "limit": 0,  # no limit
        }
        resp = requests.get(ACLED_API_URL, params=params, timeout=120)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        return pd.DataFrame(data)

    def normalize(self, raw: pd.DataFrame) -> pd.DataFrame:
        """Aggregate ACLED events into weekly protest and attack counts."""
        if raw.empty:
            return raw
        raw["event_date"] = pd.to_datetime(raw["event_date"])
        raw["week_start"] = raw["event_date"].dt.to_period("W-MON").dt.start_time

        iran_protests = (
            raw[(raw["country"] == "Iran") & (raw["event_type"] == "Protests")]
            .groupby("week_start")
            .size()
            .reset_index(name="acled_iran_protest_count")
        )

        proxy_countries = ["Iraq", "Syria", "Yemen", "Lebanon"]
        attack_types = ["Battles", "Explosions/Remote violence", "Violence against civilians"]
        proxy_attacks = (
            raw[(raw["country"].isin(proxy_countries)) & (raw["event_type"].isin(attack_types))]
            .groupby("week_start")
            .size()
            .reset_index(name="acled_proxy_attack_count")
        )

        merged = iran_protests.merge(proxy_attacks, on="week_start", how="outer").fillna(0)
        return merged

    def load_sample(self) -> pd.DataFrame:
        """Generate realistic weekly ACLED-derived counts."""
        weeks = generate_week_starts("2023-01-02", periods=110)
        rng = np.random.default_rng(43)

        protests = rng.poisson(lam=12, size=len(weeks)).astype(float)
        attacks = rng.poisson(lam=6, size=len(weeks)).astype(float)

        # Protest surge (e.g., Mahsa Amini anniversary)
        protests[35:45] += rng.integers(10, 30, size=10)
        # Proxy escalation period
        attacks[60:75] += rng.integers(5, 15, size=15)
        # Post-sanctions-surge suppression
        for offset in [16, 44, 79]:
            attacks[offset : offset + 8] = np.maximum(
                attacks[offset : offset + 8] - rng.integers(1, 4, size=8), 0
            )

        return pd.DataFrame({
            "week_start": weeks,
            "acled_iran_protest_count": protests,
            "acled_proxy_attack_count": attacks,
        })
