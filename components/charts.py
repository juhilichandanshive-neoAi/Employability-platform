"""
Chart wrappers around Plotly, one function per chart type in the design
system (gauge, radar, bar, line, pie, heatmap). Every screen should reach
for one of these instead of building a chart inline, so a colour or style
fix only has to happen in one place.

Colour rule (v5, no-orange restyle): student/primary trace = solid purple,
comparison/cohort = grey, target = green dotted line, below-threshold
("needs attention") bars = pink - never orange/amber. See decisions.md.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

import plotly.graph_objects as go
import streamlit as st

PRIMARY = "#7C3AED"
PRIMARY_DARK = "#6D28D9"
GREY = "#D8D4E0"
WARN_PINK = "#EC4899"
TARGET_GREEN = "#16A34A"
TEXT_SECONDARY = "#6B6478"

_LAYOUT_DEFAULTS = dict(
    margin=dict(l=10, r=10, t=20, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Poppins, sans-serif", color="#211C36", size=13),
)


def _is_missing(value) -> bool:
    if value is None:
        return True
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return len(value) == 0
    return False


def as_number(value, default=None):
    """Return a finite number, or ``default``. Empty lists are not numbers."""
    if value is None or isinstance(value, bool):
        return default
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        if len(value) != 1:
            return default
        return as_number(value[0], default)
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return number


def as_target(value) -> float | None:
    """Scalar Plotly hline target, or None. ``[]``, ``None``, and invalid non-scalars omit the line."""
    if _is_missing(value):
        return None
    num = as_number(value)
    if num is None:
        return None
    return float(num)


def as_series(value) -> list[float]:
    if _is_missing(value):
        return []
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        series = [as_number(item, None) for item in value]
        if all(item is None for item in series):
            return []
        return [0.0 if item is None else float(item) for item in series]
    number = as_number(value)
    return [] if number is None else [float(number)]


def _show(fig) -> None:
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def gauge(value: int, max_value: int = 100, height: int = 240):
    numeric = as_number(value, 0)
    ceiling = as_number(max_value, 100) or 100
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=numeric,
        number={"suffix": f"", "font": {"size": 42}},
        gauge={
            "axis": {"range": [0, ceiling], "visible": False},
            "bar": {"color": PRIMARY, "thickness": 0.3},
            "bgcolor": "#F1EFF7",
            "borderwidth": 0,
        },
    ))
    fig.update_layout(height=height, **_LAYOUT_DEFAULTS)
    _show(fig)


def radar(categories, you, compare, compare_label="Role requires", height=340):
    cats = list(categories or [])
    you_series = as_series(you) or []
    compare_series = as_series(compare) or []
    if not cats or not you_series or not compare_series:
        st.caption("Not enough comparable skill values to draw this chart.")
        return
    n = min(len(cats), len(you_series), len(compare_series))
    cats = cats[:n]
    you_series = you_series[:n]
    compare_series = compare_series[:n]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=compare_series + [compare_series[0]], theta=cats + [cats[0]],
        name=compare_label, line=dict(color=GREY, dash="dot"), fill="none",
    ))
    fig.add_trace(go.Scatterpolar(
        r=you_series + [you_series[0]], theta=cats + [cats[0]],
        name="You", line=dict(color=PRIMARY), fillcolor="rgba(124,58,237,0.20)", fill="toself",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, showticklabels=False)),
        showlegend=True,
        legend=dict(orientation="h", y=-0.12),
        height=height, **_LAYOUT_DEFAULTS,
    )
    _show(fig)


def bar(labels, values, warn_below=None, height=280):
    """Bars below `warn_below` read as pink ("needs attention") - this used
    to be the role a leftover orange played; pink is the only accent that
    role uses now, everywhere in the app."""
    series = as_series(values)
    names = list(labels or [])
    if not series or not names:
        st.caption("No values are available for this chart.")
        return
    n = min(len(names), len(series))
    names = names[:n]
    series = series[:n]
    threshold = as_number(warn_below)
    colors = [PRIMARY] * len(series)
    if threshold is not None:
        colors = [WARN_PINK if v < threshold else PRIMARY for v in series]
    fig = go.Figure(go.Bar(
        x=names, y=series, marker_color=colors,
        text=[f"{int(round(v))}%" for v in series], textposition="outside", cliponaxis=False,
        marker_line_width=0, width=[0.72] * len(series),
    ))
    fig.update_traces(marker=dict(cornerradius=4))
    fig.update_yaxes(visible=False, range=[0, 100 * 1.12], fixedrange=True)
    fig.update_xaxes(fixedrange=True, showgrid=False, ticklabelstandoff=8)
    layout = {**_LAYOUT_DEFAULTS, "margin": dict(l=10, r=10, t=30, b=10)}
    fig.update_layout(height=height, bargap=0.28, uniformtext=dict(mode="show", minsize=12), **layout)
    _show(fig)


def build_line_fig(x, student, cohort=None, target=None, height: int = 280) -> go.Figure | None:
    """Construct and return the Plotly Figure for a line chart safely.

    Accepts None, scalars, or lists for cohort and target without raising TypeError.
    """
    labels = list(x or [])
    student_series = as_series(student)
    if not labels or not student_series:
        return None
    n = min(len(labels), len(student_series))
    labels = labels[:n]
    student_series = student_series[:n]
    fig = go.Figure()
    target_value = as_target(target)
    if target_value is not None:
        fig.add_hline(
            y=target_value,
            line_dash="dot",
            line_color=TARGET_GREEN,
            annotation_text=f"job-ready {int(round(target_value))}",
            annotation_position="top left",
        )
    cohort_series = as_series(cohort)
    if cohort_series:
        if len(cohort_series) == 1 and len(labels) > 1:
            cohort_series = cohort_series * len(labels)
        cohort_n = min(len(labels), len(cohort_series))
        fig.add_trace(
            go.Scatter(
                x=labels[:cohort_n],
                y=cohort_series[:cohort_n],
                name="Cohort",
                line=dict(color=GREY, dash="dot"),
            )
        )
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=student_series,
            name="You",
            line=dict(color=PRIMARY, width=3),
            fill="tozeroy",
            fillcolor="rgba(124,58,237,0.12)",
        )
    )
    fig.update_layout(height=height, showlegend=bool(cohort_series), **_LAYOUT_DEFAULTS)
    return fig


def line(x, student, cohort=None, target=None, height=280):
    fig = build_line_fig(x, student, cohort=cohort, target=target, height=height)
    if fig is None:
        st.caption("No results are available for this chart.")
        return
    _show(fig)



def donut(labels, values, colors=(PRIMARY, "#4F46E5", "#06B6D4"), height=280):
    series = as_series(values)
    names = list(labels or [])
    if not series or not names:
        st.caption("No values are available for this chart.")
        return
    n = min(len(names), len(series))
    fig = go.Figure(go.Pie(
        labels=names[:n], values=series[:n], hole=0.6,
        marker=dict(colors=list(colors)),
        textinfo="none",
    ))
    fig.update_layout(height=height, showlegend=True, legend=dict(orientation="h", y=-0.1), **_LAYOUT_DEFAULTS)
    _show(fig)


def score_ring(value: int, max_value: int = 100, height: int = 240, label: str = None):
    """A single-number progress ring - the score sits in the middle of the
    ring itself, done as a two-slice donut with the empty half masked out,
    rather than Plotly's gauge (which only draws a half-circle)."""
    numeric = as_number(value, 0)
    ceiling = as_number(max_value, 100) or 100
    filled = max(0.0, min(float(ceiling), float(numeric)))
    fig = go.Figure(go.Pie(
        values=[filled, max(ceiling - filled, 0)], hole=0.72,
        marker=dict(colors=[PRIMARY, "#F1EFF7"]),
        textinfo="none", sort=False, direction="clockwise", rotation=0,
    ))
    fig.update_layout(
        height=height, showlegend=False,
        annotations=[dict(
            text=f"<b>{int(round(filled))}%</b>" + (f"<br><span style='font-size:13px;color:#6B6478;'>{label}</span>" if label else ""),
            x=0.5, y=0.5, font=dict(size=34, color="#211C36"), showarrow=False,
        )],
        **_LAYOUT_DEFAULTS,
    )
    _show(fig)


def heatmap(rows, cols, matrix, height=240):
    """Stays in the purple scale, per the design rule."""
    if _is_missing(rows) or _is_missing(cols) or _is_missing(matrix):
        st.caption("No values are available for this chart.")
        return
    fig = go.Figure(go.Heatmap(
        z=matrix, x=cols, y=rows,
        colorscale=[[0, "#F5F3FF"], [1, PRIMARY]],
        showscale=False, xgap=4, ygap=4,
    ))
    fig.update_layout(height=height, **_LAYOUT_DEFAULTS)
    _show(fig)
