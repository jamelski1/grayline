"""Pydantic schemas for indicator data used throughout the Grayline platform."""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class IndicatorCategory(str, Enum):
    INPUT = "input"
    INTERMEDIATE = "intermediate"
    OUTCOME = "outcome"
    DERIVED = "derived"


class SignalDirection(str, Enum):
    """Whether higher values are positive or negative for strategy effectiveness."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class IndicatorMeta(BaseModel):
    """Metadata describing a single indicator tracked by the platform."""

    name: str = Field(..., description="Machine-readable indicator name")
    label: str = Field(..., description="Human-readable display label")
    category: IndicatorCategory
    source: str = Field(..., description="Data source name (e.g. 'ofac', 'acled')")
    direction: SignalDirection = SignalDirection.NEUTRAL
    unit: str = "count"
    description: str = ""


class WeeklyRecord(BaseModel):
    """A single row in the weekly analytic panel."""

    week_start: date

    # Inputs
    ofac_total_new: float = 0.0
    ofac_iran_related: float = 0.0

    # Intermediate indicators
    oil_revenue_proxy: float = 0.0
    acled_iran_protest_count: float = 0.0
    maritime_incident_count: float = 0.0

    # Outcomes
    acled_proxy_attack_count: float = 0.0
    regional_escalation_index: float = 0.0

    # Derived (populated by analytics)
    four_week_attack_avg: float | None = None
    four_week_protest_avg: float | None = None
    sanctions_lag_4w: float | None = None
    composite_effectiveness_score: float | None = None


# Registry of all tracked indicators with metadata
INDICATOR_REGISTRY: list[IndicatorMeta] = [
    IndicatorMeta(
        name="ofac_total_new",
        label="New OFAC Designations",
        category=IndicatorCategory.INPUT,
        source="ofac",
        direction=SignalDirection.POSITIVE,
        unit="count",
        description="Total new OFAC sanctions designations per week",
    ),
    IndicatorMeta(
        name="ofac_iran_related",
        label="Iran-Related OFAC Designations",
        category=IndicatorCategory.INPUT,
        source="ofac",
        direction=SignalDirection.POSITIVE,
        unit="count",
        description="New OFAC designations specifically targeting Iran/IRGC networks",
    ),
    IndicatorMeta(
        name="oil_revenue_proxy",
        label="Oil Revenue Proxy",
        category=IndicatorCategory.INTERMEDIATE,
        source="fred",
        direction=SignalDirection.NEGATIVE,
        unit="USD/barrel",
        description="Brent crude price as a proxy for Iranian oil revenue",
    ),
    IndicatorMeta(
        name="acled_iran_protest_count",
        label="Iran Domestic Protests",
        category=IndicatorCategory.INTERMEDIATE,
        source="acled",
        direction=SignalDirection.POSITIVE,
        unit="events",
        description="Weekly count of protest events inside Iran",
    ),
    IndicatorMeta(
        name="maritime_incident_count",
        label="Maritime Incidents",
        category=IndicatorCategory.INTERMEDIATE,
        source="gdelt",
        direction=SignalDirection.NEGATIVE,
        unit="events",
        description="Maritime security incidents in the Gulf region",
    ),
    IndicatorMeta(
        name="acled_proxy_attack_count",
        label="Proxy Attacks",
        category=IndicatorCategory.OUTCOME,
        source="acled",
        direction=SignalDirection.NEGATIVE,
        unit="events",
        description="Weekly count of attacks by Iran-linked proxy groups",
    ),
    IndicatorMeta(
        name="regional_escalation_index",
        label="Regional Escalation Index",
        category=IndicatorCategory.OUTCOME,
        source="composite",
        direction=SignalDirection.NEGATIVE,
        unit="index",
        description="Composite index of regional escalation signals",
    ),
]
