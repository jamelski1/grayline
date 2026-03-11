"""Application settings loaded from environment variables."""

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    """Central settings object for all Grayline configuration."""

    acled_api_key: str = field(default_factory=lambda: os.getenv("ACLED_API_KEY", ""))
    acled_email: str = field(default_factory=lambda: os.getenv("ACLED_EMAIL", ""))
    fred_api_key: str = field(default_factory=lambda: os.getenv("FRED_API_KEY", ""))

    # Data freshness
    max_data_age_days: int = 7

    # Analysis defaults
    default_lag_weeks: list[int] = field(default_factory=lambda: [1, 4, 8, 12])
    moving_average_window: int = 4

    # Panel date range
    panel_start_date: str = "2023-01-01"


settings = Settings()
