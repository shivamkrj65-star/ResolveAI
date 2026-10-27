"""Helper UI components, badges, and Plotly charts for ResolveAI."""

from __future__ import annotations

import html
from typing import Any, Dict, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def render_status_badge(status: str) -> str:
    s = (status or "").lower().replace(" ", "_")
    css_class = "status-assigned"
    label = status or "Unknown"

    if "held" in s or "review" in s:
        css_class = "status-held"
        label = "Held for Review"
    elif "resolved" in s or "completed" in s:
        css_class = "status-resolved"
        label = "Resolved"
    elif "rejected" in s:
        css_class = "status-rejected"
        label = "Rejected"
    elif "in_progress" in s:
        css_class = "status-inprogress"
        label = "In Progress"
    elif "assigned" in s:
        css_class = "status-assigned"
        label = "Assigned"

    return f'<span class="status-pill {css_class}">● {html.escape(label)}</span>'


def render_priority_badge(priority: str) -> str:
    p = (priority or "").lower()
    css_class = "priority-medium"
    label = priority or "Medium"

    if "critical" in p:
        css_class = "priority-critical"
        label = "Critical"
    elif "high" in p:
        css_class = "priority-high"
        label = "High"
    elif "medium" in p:
        css_class = "priority-medium"
        label = "Medium"
    elif "low" in p:
        css_class = "priority-low"
        label = "Low"

    return f'<span class="status-pill {css_class}">⚡ {html.escape(label.upper())}</span>'


def build_status_chart(cases: List[Dict[str, Any]]) -> go.Figure:
    if not cases:
        fig = go.Figure()
        fig.update_layout(title="No Cases Available")
        return fig

    status_counts = {}
    for c in cases:
        st_val = c.get("status", "unknown").replace("_", " ").title()
        status_counts[st_val] = status_counts.get(st_val, 0) + 1

    df = pd.DataFrame(list(status_counts.items()), columns=["Status", "Count"])
    colors = {
        "Assigned": "#3b82f6",
        "Held For Review": "#f59e0b",
        "In Progress": "#8b5cf6",
        "Resolved": "#10b981",
        "Rejected": "#ef4444",
    }
    color_map = [colors.get(s, "#64748b") for s in df["Status"]]

    fig = px.pie(
        df,
        values="Count",
        names="Status",
        hole=0.55,
        color_discrete_sequence=color_map,
        title="Complaints by Resolution Status",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )
    return fig


def build_priority_chart(cases: List[Dict[str, Any]]) -> go.Figure:
    if not cases:
        fig = go.Figure()
        fig.update_layout(title="No Cases Available")
        return fig

    priority_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for c in cases:
        p_val = (c.get("priority_level") or "medium").capitalize()
        priority_counts[p_val] = priority_counts.get(p_val, 0) + 1

    df = pd.DataFrame(list(priority_counts.items()), columns=["Priority", "Count"])
    colors = {"Critical": "#ef4444", "High": "#f97316", "Medium": "#3b82f6", "Low": "#10b981"}

    fig = px.bar(
        df,
        x="Priority",
        y="Count",
        color="Priority",
        color_discrete_map=colors,
        title="Authoritative Priority Breakdown",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
    )
    return fig


def build_category_chart(cases: List[Dict[str, Any]]) -> go.Figure:
    if not cases:
        fig = go.Figure()
        fig.update_layout(title="No Cases Available")
        return fig

    category_counts = {}
    for c in cases:
        ext = c.get("extraction", {})
        cat = ext.get("issue_type", "other").replace("_", " ").title()
        category_counts[cat] = category_counts.get(cat, 0) + 1

    df = pd.DataFrame(list(category_counts.items()), columns=["Category", "Count"]).sort_values("Count", ascending=True)

    fig = px.bar(
        df,
        x="Count",
        y="Category",
        orientation="h",
        color="Count",
        color_continuous_scale=["#6366f1", "#a855f7", "#ec4899"],
        title="Complaints by Issue Category",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        coloraxis_showscale=False,
    )
    return fig


def build_location_chart(cases: List[Dict[str, Any]]) -> go.Figure:
    if not cases:
        fig = go.Figure()
        fig.update_layout(title="No Cases Available")
        return fig

    loc_counts = {}
    for c in cases:
        ext = c.get("extraction", {})
        loc = ext.get("building_block", "Unknown Block").strip().title()
        loc_counts[loc] = loc_counts.get(loc, 0) + 1

    df = pd.DataFrame(list(loc_counts.items()), columns=["Building Block", "Reports"]).sort_values("Reports", ascending=False).head(6)

    fig = px.bar(
        df,
        x="Building Block",
        y="Reports",
        color="Reports",
        color_continuous_scale="Viridis",
        title="Top Reported Campus Locations",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=40, b=20),
        coloraxis_showscale=False,
    )
    return fig
