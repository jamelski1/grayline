"""Executive Summary dashboard page."""

import pandas as pd
import streamlit as st

from grayline.dashboard.charts import (
    composite_score_gauge,
    dual_axis,
    time_series,
)
from grayline.dashboard.layout import metric_row, page_header


def render(panel: pd.DataFrame) -> None:
    page_header(
        "Executive Summary",
        "Strategy effectiveness overview — Iran / IRGC regional activity monitoring",
    )

    if panel.empty:
        st.warning("No data available. Click 'Rebuild Data Panel' in the sidebar.")
        return

    latest = panel.iloc[-1]
    prev = panel.iloc[-2] if len(panel) > 1 else latest

    # Last refresh date
    st.caption(f"Latest data: week of {latest['week_start'].strftime('%B %d, %Y')}")

    # Status cards
    def delta(curr, prev_val):
        d = curr - prev_val
        return f"{d:+.1f}" if d != 0 else "0"

    metric_row([
        {
            "label": "Composite Effectiveness",
            "value": f"{latest.get('composite_effectiveness_score', 0):.1f}",
            "delta": delta(
                latest.get("composite_effectiveness_score", 0),
                prev.get("composite_effectiveness_score", 0),
            ),
        },
        {
            "label": "New OFAC Designations",
            "value": f"{latest.get('ofac_total_new', 0):.0f}",
            "delta": delta(latest.get("ofac_total_new", 0), prev.get("ofac_total_new", 0)),
        },
        {
            "label": "Proxy Attacks (4w avg)",
            "value": f"{latest.get('four_week_attack_avg', 0):.1f}",
            "delta": delta(
                latest.get("four_week_attack_avg", 0),
                prev.get("four_week_attack_avg", 0),
            ),
            "delta_color": "inverse",
        },
        {
            "label": "Escalation Index",
            "value": f"{latest.get('regional_escalation_index', 0):.1f}",
            "delta": delta(
                latest.get("regional_escalation_index", 0),
                prev.get("regional_escalation_index", 0),
            ),
            "delta_color": "inverse",
        },
    ])

    st.markdown("")

    # Composite effectiveness gauge and trend
    col1, col2 = st.columns([1, 2])
    with col1:
        score = latest.get("composite_effectiveness_score", 50)
        st.plotly_chart(composite_score_gauge(score), use_container_width=True)

    with col2:
        st.plotly_chart(
            time_series(
                panel,
                ["composite_effectiveness_score"],
                labels={"composite_effectiveness_score": "Effectiveness Score"},
                title="Composite Effectiveness Trend",
            ),
            use_container_width=True,
        )

    # Key indicator overview
    st.subheader("Signal Chain Overview")
    st.plotly_chart(
        dual_axis(
            panel,
            col_left="ofac_total_new",
            col_right="acled_proxy_attack_count",
            label_left="OFAC Designations (Input)",
            label_right="Proxy Attacks (Outcome)",
            title="Policy Inputs vs. Strategic Outcomes",
        ),
        use_container_width=True,
    )

    st.plotly_chart(
        time_series(
            panel,
            ["acled_iran_protest_count", "oil_revenue_proxy", "maritime_incident_count"],
            labels={
                "acled_iran_protest_count": "Iran Protests",
                "oil_revenue_proxy": "Oil Price ($/bbl)",
                "maritime_incident_count": "Maritime Incidents",
            },
            title="Intermediate Effect Indicators",
        ),
        use_container_width=True,
    )
