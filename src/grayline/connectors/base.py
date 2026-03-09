"""Base class for all data connectors."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import pandas as pd

from grayline.config import RAW_DIR

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Abstract base class that all data connectors must implement."""

    name: str = "base"

    @abstractmethod
    def fetch(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetch raw data from the source API."""

    @abstractmethod
    def normalize(self, raw: pd.DataFrame) -> pd.DataFrame:
        """Normalize raw data into a standard weekly schema."""

    @abstractmethod
    def load_sample(self) -> pd.DataFrame:
        """Return realistic sample data for offline/demo use."""

    def fetch_or_fallback(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Try to fetch live data; fall back to sample data on failure."""
        try:
            raw = self.fetch(start_date, end_date)
            if raw.empty:
                logger.warning("%s: empty response, using sample data", self.name)
                return self.load_sample()
            self._save_snapshot(raw)
            return self.normalize(raw)
        except Exception as e:
            logger.warning("%s: fetch failed (%s), using sample data", self.name, e)
            return self.load_sample()

    def _save_snapshot(self, df: pd.DataFrame) -> Path:
        """Save a timestamped raw data snapshot."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = RAW_DIR / f"{self.name}_{ts}.csv"
        df.to_csv(path, index=False)
        logger.info("Saved raw snapshot: %s", path)
        return path
