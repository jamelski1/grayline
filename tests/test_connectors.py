"""Tests for data connectors — sample data generation."""

import pandas as pd
import pytest

from grayline.connectors.acled import ACLEDConnector
from grayline.connectors.fred import FREDConnector
from grayline.connectors.gdelt import GDELTConnector
from grayline.connectors.ofac import OFACConnector
from grayline.connectors.world_bank import WorldBankConnector


@pytest.mark.parametrize("ConnectorClass", [
    OFACConnector,
    ACLEDConnector,
    FREDConnector,
    WorldBankConnector,
    GDELTConnector,
])
class TestConnectorSampleData:
    def test_load_sample_returns_dataframe(self, ConnectorClass):
        conn = ConnectorClass()
        df = conn.load_sample()
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_sample_has_week_start(self, ConnectorClass):
        conn = ConnectorClass()
        df = conn.load_sample()
        assert "week_start" in df.columns

    def test_sample_has_reasonable_length(self, ConnectorClass):
        conn = ConnectorClass()
        df = conn.load_sample()
        assert len(df) >= 50
