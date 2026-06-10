"""
dashboard.py — ECG Live Monitoring Dashboard
=============================================
Run:
    streamlit run dashboard.py

Keep predict.py running in a separate terminal to feed live data.
Dashboard auto-refreshes every 3 seconds.
"""

import time
from typing import Optional
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ECG Monitor",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Theme / CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    background-color: #070b14;
    color: #c8d8e8;
}
.stApp { background-color: #070b14; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Metric cards */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1929 0%, #0a1520 100%);
    border: 1px solid #1a3050;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 0 20px rgba(0,180,255,0.05);
}
[data-testid="metric-container"] label {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.7rem !important;
    color: #4a7a9b !important;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 1.8rem !important;
    color: #00d4ff !important;
}

/* Alert box */
.alert-high {
    background: linear-gradient(135deg, #1a0a0a, #2a0f0f);
    border: 1px solid #ff3333;
    border-left: 4px solid #ff3333;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 4px 0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: #ff8888;
    box-shadow: 0 0 15px rgba(255,50,50,0.1);
}
.alert-medium {
    background: linear-gradient(135deg, #1a1200, #2a1e00);
    border: 1px solid #ffaa00;
    border-left: 4px solid #ffaa00;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 4px 0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: #ffcc66;
    box-shadow: 0 0 15px rgba(255,170,0,0.1);
}
.alert-low {
    background: linear-gradient(135deg, #091a0e, #0d2415);
    border: 1px solid #00cc66;
    border-left: 4px solid #00cc66;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 4px 0;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.85rem;
    color: #66ffaa;
    box-shadow: 0 0 15px rgba(0,200,100,0.1);
}

/* Section headers */
.section-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #2a5a7a;
    border-bottom: 1px solid #1a3050;
    padding-bottom: 6px;
    margin-bottom: 16px;
}

/* Explanation panel */
.explain-box {
    background: #0a1520;
    border: 1px solid #1a3050;
    border-radius: 6px;
    padding: 14px 18px;
    font-size: 0.9rem;
    line-height: 1.6;
    color: #a0c0d8;
    font-family: 'Rajdhani', sans-serif;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #1a3050;
    border-radius: 8px;
}

/* Title */
.main-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.6rem;
    color: #00d4ff;
    letter-spacing: 0.1em;
    margin: 0;
}
.sub-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: #2a6a8a;
    letter-spacing: 0.2em;
    margin-top: 2px;
}
.status-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #00ff88;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 6px #00ff88; }
    50%       { opacity: 0.4; box-shadow: none; }
}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
CSV_PATH    = "predictions.csv"
REFRESH_SEC = 3

RISK_COLOURS = {
    "HIGH":   "#ff3333",
    "MEDIUM": "#ffaa00",
    "LOW":    "#00cc66"
}
PRED_COLOURS = {
    "Arrhythmia":      "#ff4466",
    "Normal":          "#00cc66",
    "Other / Unknown": "#4488ff"
}

# ── Data loader ───────────────────────────────────────────────────────────────
def load_data() -> Optional[pd.DataFrame]:
    p = Path(CSV_PATH)
    if not p.exists():
        return None
    try:
        df = pd.read_csv(p)
        # Guard: must have the expected columns (not the old validation format)
        required_cols = {"patient", "prediction", "confidence", "risk", "heart_rate", "hrv"}
        if df.empty or not required_cols.issubset(df.columns):
            return None
        # Ensure correct dtypes
        df["patient"]     = pd.to_numeric(df["patient"],     errors="coerce")
        df["confidence"]  = pd.to_numeric(df["confidence"],  errors="coerce")
        df["heart_rate"]  = pd.to_numeric(df["heart_rate"],  errors="coerce")
        df["hrv"]         = pd.to_numeric(df["hrv"],         errors="coerce")
        df = df.dropna(subset=["patient", "risk", "prediction"])
        return df if not df.empty else None
    except Exception:
        return None

# ── Plotly theme helper ────────────────────────────────────────────────────────
CHART_BG = "#070b14"
GRID_COL = "#1a3050"

def dark_layout(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(family="Share Tech Mono", size=11,
                                         color="#4a7a9b"), x=0.02),
        paper_bgcolor=CHART_BG,
        plot_bgcolor="#0a1520",
        font=dict(family="Rajdhani", color="#c8d8e8"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        xaxis=dict(gridcolor=GRID_COL, zerolinecolor=GRID_COL),
        yaxis=dict(gridcolor=GRID_COL, zerolinecolor=GRID_COL),
    )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════════════════

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_status = st.columns([5, 1])
with col_title:
    st.markdown('<p class="main-title">🫀 ECG MONITORING SYSTEM</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">REAL-TIME CARDIAC RISK ASSESSMENT · LIGHTGBM + GEMMA:7B</p>',
                unsafe_allow_html=True)
with col_status:
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<span class="status-dot"></span><span style="font-family:Share Tech Mono;'
                'font-size:0.7rem;color:#00ff88;letter-spacing:0.1em">LIVE</span>',
                unsafe_allow_html=True)

st.markdown("---")

# ── Load data ─────────────────────────────────────────────────────────────────
df = load_data()

if df is None:
    st.markdown("""
    <div style="text-align:center; padding:80px; font-family:'Share Tech Mono',monospace;
                color:#2a5a7a; font-size:0.9rem; letter-spacing:0.15em;">
        ⏳ WAITING FOR DATA<br><br>
        <span style="font-size:0.7rem; color:#1a3050;">
        Run predict.py to start the pipeline<br>
        predictions.csv will appear here automatically
        </span>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(REFRESH_SEC)
    st.rerun()

# ── KPI metrics row ───────────────────────────────────────────────────────────
st.markdown('<p class="section-header">● SESSION METRICS</p>', unsafe_allow_html=True)

total    = len(df)
high_n   = int((df["risk"] == "HIGH").sum())
medium_n = int((df["risk"] == "MEDIUM").sum())
low_n    = int((df["risk"] == "LOW").sum())
arr_pct  = round(100 * (df["prediction"] == "Arrhythmia").sum() / total, 1)
avg_hr   = round(df["heart_rate"].mean(), 1)
avg_hrv  = round(df["hrv"].mean(), 2)
avg_conf = round(df["confidence"].mean(), 1)

m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
m1.metric("Total Patients",  total)
m2.metric("🔴 HIGH Risk",    high_n)
m3.metric("🟡 MEDIUM Risk",  medium_n)
m4.metric("🟢 LOW Risk",     low_n)
m5.metric("Arrhythmia %",    f"{arr_pct}%")
m6.metric("Avg HR",          f"{avg_hr} BPM")
m7.metric("Avg Confidence",  f"{avg_conf}%")

st.markdown("<br>", unsafe_allow_html=True)

# ── Main content: charts + alerts ─────────────────────────────────────────────
left, right = st.columns([3, 2])

with left:
    # ── Chart 1: Prediction distribution (donut) ──────────────────────────────
    st.markdown('<p class="section-header">● PREDICTION DISTRIBUTION</p>',
                unsafe_allow_html=True)
    pred_vc = df["prediction"].value_counts()
    fig_donut = go.Figure(go.Pie(
        labels=pred_vc.index.tolist(),
        values=pred_vc.values.tolist(),
        hole=0.65,
        marker=dict(
            colors=[PRED_COLOURS.get(l, "#888") for l in pred_vc.index],
            line=dict(color="#070b14", width=3)
        ),
        textfont=dict(family="Rajdhani", size=13),
        hovertemplate="<b>%{label}</b><br>%{value} patients (%{percent})<extra></extra>"
    ))
    fig_donut.add_annotation(
        text=f"<b>{total}</b><br><span style='font-size:10'>patients</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(family="Share Tech Mono", size=18, color="#00d4ff")
    )
    dark_layout(fig_donut)
    fig_donut.update_layout(showlegend=True, height=280,
                            legend=dict(orientation="h", y=-0.05))
    st.plotly_chart(fig_donut, use_container_width=True)

    # ── Chart 2: HR vs HRV scatter ────────────────────────────────────────────
    st.markdown('<p class="section-header">● HEART RATE vs HRV BY RISK</p>',
                unsafe_allow_html=True)
    fig_scatter = px.scatter(
        df, x="heart_rate", y="hrv",
        color="risk",
        color_discrete_map=RISK_COLOURS,
        hover_data={"patient": True, "prediction": True, "confidence": True,
                    "heart_rate": ":.1f", "hrv": ":.2f"},
        labels={"heart_rate": "Heart Rate (BPM)", "hrv": "HRV (ms)"},
    )
    fig_scatter.update_traces(marker=dict(size=11, opacity=0.85,
                                          line=dict(width=1, color="#070b14")))
    dark_layout(fig_scatter)
    fig_scatter.update_layout(height=260)
    st.plotly_chart(fig_scatter, use_container_width=True)

with right:
    # ── Risk bar chart ────────────────────────────────────────────────────────
    st.markdown('<p class="section-header">● RISK DISTRIBUTION</p>',
                unsafe_allow_html=True)
    risk_vc = df["risk"].value_counts().reindex(["HIGH", "MEDIUM", "LOW"], fill_value=0)
    fig_risk = go.Figure(go.Bar(
        x=risk_vc.index.tolist(),
        y=risk_vc.values.tolist(),
        marker=dict(
            color=[RISK_COLOURS[r] for r in risk_vc.index],
            line=dict(color="#070b14", width=2)
        ),
        text=risk_vc.values.tolist(),
        textposition="outside",
        textfont=dict(family="Share Tech Mono", size=14, color="#c8d8e8"),
        hovertemplate="<b>%{x}</b><br>%{y} patients<extra></extra>"
    ))
    dark_layout(fig_risk)
    fig_risk.update_layout(height=220, showlegend=False,
                           yaxis=dict(visible=False))
    st.plotly_chart(fig_risk, use_container_width=True)

    # ── Alert feed ────────────────────────────────────────────────────────────
    st.markdown('<p class="section-header">● PATIENT ALERTS</p>',
                unsafe_allow_html=True)

    # Sort: HIGH first, then MEDIUM, then LOW; within each group newest (highest patient ID) first
    risk_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    df_sorted = df.copy()
    df_sorted["_order"] = df_sorted["risk"].map(risk_order)
    df_sorted = df_sorted.sort_values(["_order", "patient"], ascending=[True, False])

    # Show only latest 15 to avoid scroll overflow
    for _, row in df_sorted.head(15).iterrows():
        risk  = row["risk"]
        cls   = risk.lower()
        icon  = "🔴" if risk == "HIGH" else ("🟡" if risk == "MEDIUM" else "🟢")
        st.markdown(
            f'<div class="alert-{cls}">'
            f'{icon} <b>Patient {int(row["patient"])}</b> &nbsp;|&nbsp; '
            f'{row["prediction"]} &nbsp;|&nbsp; '
            f'HR: {row["heart_rate"]} BPM &nbsp;|&nbsp; '
            f'Conf: {row["confidence"]}% &nbsp;|&nbsp; [{risk}]'
            f'</div>',
            unsafe_allow_html=True
        )

# ── Confidence trend (full width) ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p class="section-header">● CONFIDENCE TREND (LAST 30 PATIENTS)</p>',
            unsafe_allow_html=True)

# Use sequential index for X-axis since patient IDs are large non-sequential numbers
df_trend = df.tail(30).copy().reset_index(drop=True)
df_trend["seq"] = df_trend.index + 1          # 1 … N for clean X-axis
df_trend["label"] = df_trend.apply(
    lambda r: f"P{int(r['patient'])}", axis=1  # shown in hover
)

fig_trend = go.Figure()
for pred, colour in PRED_COLOURS.items():
    subset = df_trend[df_trend["prediction"] == pred]
    if subset.empty:
        continue
    fig_trend.add_trace(go.Scatter(
        x=subset["seq"],
        y=subset["confidence"],
        mode="markers+lines",
        name=pred,
        text=subset["label"],
        line=dict(color=colour, width=2),
        marker=dict(size=9, color=colour,
                    line=dict(color="#070b14", width=1)),
        hovertemplate=(
            f"<b>{pred}</b><br>"
            "Patient: %{text}<br>Confidence: %{y:.1f}%<extra></extra>"
        )
    ))

fig_trend.add_hline(y=85, line=dict(color="rgba(255,51,51,0.4)", dash="dot", width=1),
                    annotation_text="HIGH threshold (85%)",
                    annotation_font=dict(family="Share Tech Mono", size=10, color="#ff5555"))
dark_layout(fig_trend)
fig_trend.update_layout(
    height=240,
    xaxis=dict(title="Prediction sequence (newest = rightmost)",
               tickmode="linear", dtick=max(1, len(df_trend) // 10)),
    yaxis=dict(title="Confidence %", range=[0, 105]),
)
st.plotly_chart(fig_trend, use_container_width=True)

# ── Explanation panel ─────────────────────────────────────────────────────────
st.markdown('<p class="section-header">● AI EXPLANATIONS (GEMMA:7B)</p>',
            unsafe_allow_html=True)

LOW_RISK_TEXT = "Low risk -- no detailed explanation required."
explained = df[
    df["explanation"].notna() &
    (df["explanation"].str.strip() != LOW_RISK_TEXT) &
    (df["explanation"].str.strip() != "")
].copy()

# Sort explained by risk severity then newest first
explained["_order"] = explained["risk"].map(risk_order)
explained = explained.sort_values(["_order", "patient"], ascending=[True, False])

if explained.empty:
    st.markdown('<div class="explain-box" style="color:#2a5a7a;">'
                'No HIGH/MEDIUM risk patients to display.</div>',
                unsafe_allow_html=True)
else:
    tabs = st.tabs([f"Patient {int(r['patient'])} [{r['risk']}]"
                    for _, r in explained.iterrows()])
    for tab, (_, row) in zip(tabs, explained.iterrows()):
        with tab:
            icon   = "🔴" if row["risk"] == "HIGH" else "🟡"
            expl   = str(row["explanation"]).strip()
            # Render explanation with sentence breaks for readability
            expl_html = expl.replace(". ", ".<br>")
            st.markdown(
                f'<div class="explain-box">'
                f'<b style="color:#00d4ff">{icon} {row["prediction"]}</b> &nbsp;·&nbsp; '
                f'Patient <b>{int(row["patient"])}</b> &nbsp;·&nbsp; '
                f'Confidence: <b>{row["confidence"]}%</b> &nbsp;·&nbsp; '
                f'Risk: <b style="color:{RISK_COLOURS.get(row["risk"], "#ccc")}">{row["risk"]}</b>'
                f'<br><br>'
                f'HR: {row["heart_rate"]} BPM &nbsp;|&nbsp; HRV: {row["hrv"]} ms'
                f'<br><br>'
                f'{expl_html}'
                f'</div>',
                unsafe_allow_html=True
            )

# ── Raw data table ────────────────────────────────────────────────────────────
with st.expander("📋 Full prediction log"):
    display_df = df.drop(columns=["explanation"], errors="ignore").copy()
    # Colour-code the risk column manually as a simple display
    def _colour_risk(val: str) -> str:
        return f"color: {RISK_COLOURS.get(val, '#c8d8e8')}; font-weight: bold"

    styled = display_df.style.applymap(_colour_risk, subset=["risk"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

# ── Footer + auto-refresh ─────────────────────────────────────────────────────
st.markdown("---")
col_f1, col_f2 = st.columns([4, 1])
with col_f1:
    st.markdown(
        f'<span style="font-family:Share Tech Mono;font-size:0.65rem;color:#1a3050;">'
        f'AUTO-REFRESH EVERY {REFRESH_SEC}s · '
        f'SOURCE: {CSV_PATH} · '
        f'TOTAL LOGGED: {total} PATIENTS · '
        f'MODEL: LIGHTGBM · EXPLAINABILITY: GEMMA:7B</span>',
        unsafe_allow_html=True
    )
with col_f2:
    if st.button("🔄 Refresh now"):
        st.rerun()

time.sleep(REFRESH_SEC)
st.rerun()