"""Plotly chart builders for the Grayline dashboard."""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Neutral analyst-workstation color palette
COLORS = {
    "primary": "#2C3E50",
    "secondary": "#5D6D7E",
    "accent": "#2980B9",
    "positive": "#27AE60",
    "negative": "#C0392B",
    "warning": "#F39C12",
    "bg": "#FAFBFC",
    "grid": "#E8ECF0",
    "text": "#2C3E50",
}

SERIES_COLORS = [
    "#2980B9", "#27AE60", "#C0392B", "#8E44AD",
    "#F39C12", "#1ABC9C", "#E74C3C", "#3498DB",
]

LAYOUT_DEFAULTS = dict(
    font=dict(family="Inter, -apple-system, sans-serif", color=COLORS["text"]),
    paper_bgcolor=COLORS["bg"],
    plot_bgcolor="white",
    margin=dict(l=60, r=30, t=50, b=40),
    xaxis=dict(gridcolor=COLORS["grid"], showgrid=True),
    yaxis=dict(gridcolor=COLORS["grid"], showgrid=True),
    hovermode="x unified",
)


def _apply_defaults(fig: go.Figure) -> go.Figure:
    fig.update_layout(**LAYOUT_DEFAULTS)
    return fig


def time_series(
    df: pd.DataFrame,
    columns: list[str],
    labels: dict[str, str] | None = None,
    title: str = "",
) -> go.Figure:
    """Multi-line time series chart."""
    if labels is None:
        labels = {}
    fig = go.Figure()
    for i, col in enumerate(columns):
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df["week_start"],
                y=df[col],
                name=labels.get(col, col),
                line=dict(color=SERIES_COLORS[i % len(SERIES_COLORS)], width=2),
                mode="lines",
            ))
    fig.update_layout(title=title, legend=dict(orientation="h", y=-0.15))
    return _apply_defaults(fig)


def dual_axis(
    df: pd.DataFrame,
    col_left: str,
    col_right: str,
    label_left: str = "",
    label_right: str = "",
    title: str = "",
) -> go.Figure:
    """Dual-axis chart for comparing two series with different scales."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=df["week_start"], y=df[col_left],
            name=label_left or col_left,
            line=dict(color=SERIES_COLORS[0], width=2),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df["week_start"], y=df[col_right],
            name=label_right or col_right,
            line=dict(color=SERIES_COLORS[2], width=2, dash="dash"),
        ),
        secondary_y=True,
    )
    fig.update_layout(title=title, legend=dict(orientation="h", y=-0.15))
    fig.update_yaxes(title_text=label_left or col_left, secondary_y=False)
    fig.update_yaxes(title_text=label_right or col_right, secondary_y=True)
    return _apply_defaults(fig)


def bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "",
    color: str | None = None,
) -> go.Figure:
    """Simple bar chart."""
    fig = px.bar(df, x=x_col, y=y_col, title=title)
    fig.update_traces(marker_color=color or COLORS["accent"])
    return _apply_defaults(fig)


def heatmap(corr_matrix: pd.DataFrame, title: str = "Correlation Matrix") -> go.Figure:
    """Correlation heatmap."""
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale="RdBu_r",
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate="%{text}",
        textfont=dict(size=11),
    ))
    fig.update_layout(title=title, width=700, height=600)
    return _apply_defaults(fig)


def composite_score_gauge(score: float) -> go.Figure:
    """Gauge chart for composite effectiveness score."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        title={"text": "Composite Effectiveness Score"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": COLORS["accent"]},
            "steps": [
                {"range": [0, 33], "color": "#FADBD8"},
                {"range": [33, 66], "color": "#FCF3CF"},
                {"range": [66, 100], "color": "#D5F5E3"},
            ],
            "threshold": {
                "line": {"color": COLORS["primary"], "width": 3},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    fig.update_layout(height=300)
    return _apply_defaults(fig)
