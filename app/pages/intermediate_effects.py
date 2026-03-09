"""Intermediate Effects dashboard page."""

import pandas as pd
import streamlit as st

from grayline.dashboard.charts import dual_axis, time_series
from grayline.dashboard.layout import metric_row, page_header


def render(panel: pd.DataFrame) -> None:
    page_header(
        "Intermediate Effects",
        "Leading indicators that signal whether policy inputs are generating expected effects",
    )

    if panel.empty:
        st.warning("No data available.")
        return

    latest = panel.iloc[-1]
    prev_4w = panel.tail(5).iloc[0] if len(panel) >= 5 else latest

    metric_row([
        {
            "label": "Oil Revenue Proxy ($/bbl)",
            "value": f"${latest.get('oil_revenue_proxy', 0):.1f}",
            "delta": f"${latest.get('oil_revenue_proxy', 0) - prev_4w.get('oil_revenue_proxy', 0):+.1f} vs 4w ago",
        },
        {
            "label": "Iran Protests (latest)",
            "value": f"{latest.get('acled_iran_protest_count', 0):.0f}",
            "delta": f"{latest.get('acled_iran_protest_count', 0) - prev_4w.get('acled_iran_protest_count', 0):+.0f} vs 4w ago",
        },
        {
            "label": "Maritime Incidents (latest)",
            "value": f"{latest.get('maritime_incident_count', 0):.0f}",
            "delta": f"{latest.get('maritime_incident_count', 0) - prev_4w.get('maritime_incident_count', 0):+.0f} vs 4w ago",
            "delta_color": "inverse",
        },
    ])

    st.markdown("")

    st.plotly_chart(
        time_series(
            panel,
            ["oil_revenue_proxy"],
            labels={"oil_revenue_proxy": "Brent Crude ($/bbl)"},
            title="Oil Revenue Proxy — Brent Crude Weekly Average",
        ),
        use_container_width=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            time_series(
                panel,
                ["acled_iran_protest_count", "four_week_protest_avg"],
                labels={
                    "acled_iran_protest_count": "Weekly Protests",
                    "four_week_protest_avg": "4-Week Average",
                },
                title="Iran Domestic Protest Activity",
            ),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            time_series(
                panel,
                ["maritime_incident_count"],
                labels={"maritime_incident_count": "Maritime Incidents"},
                title="Gulf Maritime Incidents",
            ),
            use_container_width=True,
        )

    st.subheader("Input → Intermediate Relationship")
    st.plotly_chart(
        dual_axis(
            panel,
            col_left="ofac_total_new",
            col_right="oil_revenue_proxy",
            label_left="OFAC Designations",
            label_right="Oil Price ($/bbl)",
            title="Sanctions Pressure vs. Oil Revenue Proxy",
        ),
        use_container_width=True,
    )
