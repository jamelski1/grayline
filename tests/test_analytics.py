"""Tests for the analytics module."""

import pandas as pd
import pytest

from grayline.analytics.composite_score import compute_composite_score, min_max_normalize
from grayline.analytics.lag_features import add_lag_features
from grayline.analytics.moving_averages import add_moving_averages


@pytest.fixture
def sample_panel():
    return pd.DataFrame({
        "week_start": pd.date_range("2024-01-01", periods=12, freq="W-MON"),
        "ofac_total_new": [5, 8, 3, 12, 7, 6, 9, 4, 11, 8, 5, 7],
        "acled_proxy_attack_count": [3, 5, 2, 8, 6, 4, 7, 3, 9, 5, 4, 6],
        "acled_iran_protest_count": [10, 12, 8, 15, 11, 9, 14, 7, 16, 12, 10, 13],
        "oil_revenue_proxy": [80, 82, 79, 85, 81, 78, 83, 77, 86, 82, 80, 84],
        "regional_escalation_index": [35, 40, 32, 48, 38, 33, 42, 30, 50, 39, 35, 41],
    })


class TestMovingAverages:
    def test_basic(self, sample_panel):
        result = add_moving_averages(sample_panel, ["ofac_total_new"], window=4)
        assert "ofac_total_new_4w_avg" in result.columns
        assert len(result) == 12

    def test_missing_column_ignored(self, sample_panel):
        result = add_moving_averages(sample_panel, ["nonexistent"], window=4)
        assert "nonexistent_4w_avg" not in result.columns


class TestLagFeatures:
    def test_basic(self, sample_panel):
        result = add_lag_features(sample_panel, ["ofac_total_new"], lags=[1, 4])
        assert "ofac_total_new_lag_1w" in result.columns
        assert "ofac_total_new_lag_4w" in result.columns
        # First row lag-1 should be NaN
        assert pd.isna(result["ofac_total_new_lag_1w"].iloc[0])


class TestCompositeScore:
    def test_normalize(self):
        s = pd.Series([0, 5, 10])
        normed = min_max_normalize(s)
        assert normed.iloc[0] == 0.0
        assert normed.iloc[-1] == 1.0

    def test_score_range(self, sample_panel):
        score = compute_composite_score(sample_panel)
        assert score.min() >= 0
        assert score.max() <= 100
