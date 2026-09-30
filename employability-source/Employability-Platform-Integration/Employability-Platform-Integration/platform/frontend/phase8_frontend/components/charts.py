"""
Chart wrappers around Plotly, one function per chart type in the design
system (gauge, radar, bar, line, pie, heatmap). Every screen should reach
for one of these instead of building a chart inline, so a colour or style
fix only has to happen in one place.

Colour rule (v5, no-orange restyle): student/primary trace = solid purple,
comparison/cohort = grey, target = green dotted line, below-threshold
("needs attention") bars = pink - never orange/amber. See decisions.md.
"""

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


def gauge(value: int, max_value: int = 100, height: int = 240):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": f"", "font": {"size": 42}},
        gauge={
            "axis": {"range": [0, max_value], "visible": False},
            "bar": {"color": PRIMARY, "thickness": 0.3},
            "bgcolor": "#F1EFF7",
            "borderwidth": 0,
        },
    ))
    fig.update_layout(height=height, **_LAYOUT_DEFAULTS)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def radar(categories, you, compare, compare_label="Role requires", height=340):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=compare + [compare[0]], theta=categories + [categories[0]],
        name=compare_label, line=dict(color=GREY, dash="dot"), fill="none",
    ))
    fig.add_trace(go.Scatterpolar(
        r=you + [you[0]], theta=categories + [categories[0]],
        name="You", line=dict(color=PRIMARY), fillcolor="rgba(124,58,237,0.20)", fill="toself",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, showticklabels=False)),
        showlegend=True,
        legend=dict(orientation="h", y=-0.12),
        height=height, **_LAYOUT_DEFAULTS,
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def bar(labels, values, warn_below=None, height=280):
    """Bars below `warn_below` read as pink ("needs attention") - this used
    to be the role a leftover orange played; pink is the only accent that
    role uses now, everywhere in the app."""
    colors = [PRIMARY] * len(values)
    if warn_below is not None:
        colors = [WARN_PINK if v < warn_below else PRIMARY for v in values]
    fig = go.Figure(go.Bar(
        x=labels, y=values, marker_color=colors,
        text=[f"{v}%" for v in values], textposition="outside", cliponaxis=False,
        marker_line_width=0, width=[0.72] * len(values),
    ))
    fig.update_traces(marker=dict(cornerradius=4))
    # Fixed 0-100 axis: every bar rises from the same baseline and the
    # percentage labels sit just above their own bar, at the same offset.
    fig.update_yaxes(visible=False, range=[0, 100 * 1.12], fixedrange=True)
    fig.update_xaxes(fixedrange=True, showgrid=False, ticklabelstandoff=8)
    layout = {**_LAYOUT_DEFAULTS, "margin": dict(l=10, r=10, t=30, b=10)}
    fig.update_layout(height=height, bargap=0.28, uniformtext=dict(mode="show", minsize=12), **layout)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def line(x, student, cohort=None, target=None, height=280):
    fig = go.Figure()
    if target is not None:
        fig.add_hline(y=target, line_dash="dot", line_color=TARGET_GREEN,
                       annotation_text=f"job-ready {target}", annotation_position="top left")
    if cohort is not None:
        fig.add_trace(go.Scatter(x=x, y=cohort, name="Cohort", line=dict(color=GREY, dash="dot")))
    fig.add_trace(go.Scatter(
        x=x, y=student, name="You", line=dict(color=PRIMARY, width=3),
        fill="tozeroy", fillcolor="rgba(124,58,237,0.12)",
    ))
    fig.update_layout(height=height, showlegend=cohort is not None, **_LAYOUT_DEFAULTS)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def donut(labels, values, colors=(PRIMARY, "#4F46E5", "#06B6D4"), height=280):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.6,
        marker=dict(colors=list(colors)),
        textinfo="none",
    ))
    fig.update_layout(height=height, showlegend=True, legend=dict(orientation="h", y=-0.1), **_LAYOUT_DEFAULTS)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def score_ring(value: int, max_value: int = 100, height: int = 240, label: str = None):
    """A single-number progress ring - the score sits in the middle of the
    ring itself, done as a two-slice donut with the empty half masked out,
    rather than Plotly's gauge (which only draws a half-circle)."""
    fig = go.Figure(go.Pie(
        values=[value, max_value - value], hole=0.72,
        marker=dict(colors=[PRIMARY, "#F1EFF7"]),
        textinfo="none", sort=False, direction="clockwise", rotation=0,
    ))
    fig.update_layout(
        height=height, showlegend=False,
        annotations=[dict(
            text=f"<b>{value}%</b>" + (f"<br><span style='font-size:13px;color:#6B6478;'>{label}</span>" if label else ""),
            x=0.5, y=0.5, font=dict(size=34, color="#211C36"), showarrow=False,
        )],
        **_LAYOUT_DEFAULTS,
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def heatmap(rows, cols, matrix, height=240):
    """Stays in the purple scale, per the design rule."""
    fig = go.Figure(go.Heatmap(
        z=matrix, x=cols, y=rows,
        colorscale=[[0, "#F5F3FF"], [1, PRIMARY]],
        showscale=False, xgap=4, ygap=4,
    ))
    fig.update_layout(height=height, **_LAYOUT_DEFAULTS)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
