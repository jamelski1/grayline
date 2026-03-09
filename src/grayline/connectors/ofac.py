"""OFAC sanctions data connector.

Fetches the OFAC SDN (Specially Designated Nationals) list and tracks
new designations over time as a measure of sanctions pressure.
"""

import logging
from io import StringIO

import numpy as np
import pandas as pd
import requests

from grayline.connectors.base import BaseConnector
from grayline.utils.dates import generate_week_starts

logger = logging.getLogger(__name__)

OFAC_SDN_CSV_URL = "https://www.treasury.gov/ofac/downloads/sdn.csv"


class OFACConnector(BaseConnector):
    name = "ofac"

    def fetch(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch current OFAC SDN list CSV."""
        resp = requests.get(OFAC_SDN_CSV_URL, timeout=60)
        resp.raise_for_status()
        # SDN CSV has no header row; assign standard columns
        cols = [
            "ent_num", "sdn_name", "sdn_type", "program", "title",
            "call_sign", "vess_type", "tonnage", "grt", "vess_flag",
            "vess_owner", "remarks",
        ]
        df = pd.read_csv(StringIO(resp.text), header=None, names=cols, dtype=str)
        return df

    def normalize(self, raw: pd.DataFrame) -> pd.DataFrame:
        """Convert SDN list into weekly new-designation counts.

        Since the SDN CSV is a point-in-time snapshot without date fields,
        normalization for historical weekly counts requires the sample data path.
        This method returns the raw snapshot for archival purposes.
        """
        return raw

    def load_sample(self) -> pd.DataFrame:
        """Generate realistic weekly OFAC designation counts."""
        weeks = generate_week_starts("2023-01-02", periods=110)
        rng = np.random.default_rng(42)

        total_new = rng.poisson(lam=8, size=len(weeks))
        iran_frac = rng.uniform(0.15, 0.45, size=len(weeks))
        iran_related = np.round(total_new * iran_frac).astype(int)

        # Simulate sanctions surges
        for surge_start in [12, 40, 75]:
            total_new[surge_start : surge_start + 4] += rng.integers(5, 15, size=4)
            iran_related[surge_start : surge_start + 4] += rng.integers(2, 8, size=4)

        return pd.DataFrame({
            "week_start": weeks,
            "ofac_total_new": total_new,
            "ofac_iran_related": iran_related,
        })
