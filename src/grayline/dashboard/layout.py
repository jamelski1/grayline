"""Shared layout components for the Streamlit dashboard."""

import streamlit as st


def apply_global_style() -> None:
    """Apply the analyst-workstation CSS theme."""
    st.markdown("""
    <style>
        /* Global font and background */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Metric cards */
        [data-testid="stMetric"] {
            background: white;
            border: 1px solid #E8ECF0;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.8rem;
            color: #5D6D7E;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.6rem;
            font-weight: 600;
            color: #2C3E50;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: #F8F9FA;
            border-right: 1px solid #E8ECF0;
        }

        /* Section headers */
        h1, h2, h3 {
            color: #2C3E50;
            font-weight: 600;
        }

        /* Divider */
        hr {
            border-color: #E8ECF0;
        }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    """Render a consistent page header."""
    st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.divider()


def metric_row(metrics: list[dict]) -> None:
    """Render a row of metric cards.

    Each metric dict should have: label, value, delta (optional), delta_color (optional).
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            st.metric(
                label=m["label"],
                value=m["value"],
                delta=m.get("delta"),
                delta_color=m.get("delta_color", "normal"),
            )
