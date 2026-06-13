from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image


PROJECT_DIR = Path(__file__).resolve().parent
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(SRC_DIR))

from config import CONFIG
from hybrid_predictor import load_hybrid_artifacts


PREDICTIONS_PATH = PROJECT_DIR / "predictions.csv"
RISK_COLORS = {"HIGH": "#d94141", "MEDIUM": "#d99520", "LOW": "#228b5a"}
PREDICTION_COLORS = {
    "Arrhythmia": "#d94141",
    "Normal": "#228b5a",
    "Other / Unknown": "#4777c7",
}


st.set_page_config(
    page_title="ECG Hybrid Monitor",
    page_icon="ECG",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp { background: #f5f7fa; color: #17202a; }
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #d8dee7;
        border-radius: 6px;
        padding: 12px;
    }
    h1, h2, h3 { letter-spacing: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=2, show_spinner=False)
def load_predictions(path: Path) -> Optional[pd.DataFrame]:
    if not path.exists():
        return None
    try:
        frame = pd.read_csv(path)
    except Exception:
        return None

    required = {
        "patient",
        "record_id",
        "prediction",
        "confidence",
        "risk",
        "heart_rate",
        "hrv",
        "status",
    }
    if frame.empty or not required.issubset(frame.columns):
        return None

    numeric_columns = [
        "confidence",
        "heart_rate",
        "hrv",
        "sdnn",
        "rmssd",
        "pnn50",
        "total_seconds",
    ]
    for column in numeric_columns:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


@st.cache_resource(show_spinner="Loading model, scaler, PCA, and CNN backbone...")
def load_model_resources(model_name: str):
    return load_hybrid_artifacts(CONFIG, model_name=model_name)


def metric_value(row: pd.Series, name: str, default: float = 0.0) -> float:
    value = row.get(name, default)
    return default if pd.isna(value) else float(value)


def hrv_status(name: str, value: float) -> str:
    # Broad research-display ranges only; duration and acquisition context affect HRV.
    if name == "sdnn":
        return "low" if value < 20 else ("typical" if value <= 100 else "high")
    if name == "rmssd":
        return "low" if value < 15 else ("typical" if value <= 75 else "high")
    if name == "pnn50":
        return "low" if value < 0.03 else ("typical" if value <= 0.30 else "high")
    return ""


st.title("ECG Hybrid Monitoring System")
st.caption("EfficientNet scalogram features + clinical ECG features + LightGBM")
st.warning(
    "Research and decision-support prototype only. This system is not a standalone "
    "diagnostic device; every result requires review by a qualified clinician."
)

frame = load_predictions(PREDICTIONS_PATH)
if frame is None:
    st.info("No compatible prediction log found. Run `python predict.py --limit 5` first.")
    st.stop()

errors = frame[frame["status"] == "error"].copy()
frame = frame[frame["status"] == "ok"].copy()
if frame.empty:
    st.error("The prediction log contains no successful records.")
    if not errors.empty:
        st.dataframe(errors[["record_id", "error"]], use_container_width=True, hide_index=True)
    st.stop()

model_name = (
    str(frame["model_name"].dropna().iloc[-1])
    if "model_name" in frame.columns and frame["model_name"].notna().any()
    else CONFIG.active_model_name
)

try:
    resources = load_model_resources(model_name)
    resource_status = f"{resources.model_name} ready on {resources.device}"
except Exception as exc:
    resources = None
    resource_status = f"Artifact load warning: {exc}"

status_col, refresh_col = st.columns([5, 1])
with status_col:
    st.caption(
        "Pipeline: preprocessing -> CWT scalogram -> EfficientNet embedding -> "
        f"feature schema -> scaler/PCA -> classifier | {resource_status}"
    )
with refresh_col:
    if st.button("Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

total = len(frame)
high_count = int((frame["risk"] == "HIGH").sum())
arrhythmia_percent = 100 * float((frame["prediction"] == "Arrhythmia").mean())
average_confidence = float(frame["confidence"].mean())
average_hr = float(frame["heart_rate"].mean())
average_hrv = float(frame["hrv"].mean())

metrics = st.columns(6)
metrics[0].metric("Records", total)
metrics[1].metric("High risk", high_count)
metrics[2].metric("Arrhythmia", f"{arrhythmia_percent:.1f}%")
metrics[3].metric("Avg confidence", f"{average_confidence:.1f}%")
metrics[4].metric("Avg heart rate", f"{average_hr:.1f} BPM")
metrics[5].metric("Avg HRV", f"{average_hrv:.1f} ms")

st.subheader("Record Review")
record_ids = frame["record_id"].astype(str).tolist()
selected_id = st.selectbox("Record", record_ids, index=len(record_ids) - 1)
selected = frame[frame["record_id"].astype(str) == selected_id].iloc[-1]

detail_left, detail_right = st.columns([3, 2])
with detail_left:
    clinical_metrics = st.columns(6)
    heart_rate = metric_value(selected, "heart_rate")
    hrv = metric_value(selected, "hrv")
    sdnn = metric_value(selected, "sdnn")
    rmssd = metric_value(selected, "rmssd")
    pnn50 = metric_value(selected, "pnn50")
    confidence = metric_value(selected, "confidence")

    clinical_metrics[0].metric("Heart rate", f"{heart_rate:.1f} BPM")
    clinical_metrics[1].metric("HRV", f"{hrv:.1f} ms")
    clinical_metrics[2].metric("SDNN", f"{sdnn:.1f} ms", hrv_status("sdnn", sdnn))
    clinical_metrics[3].metric("RMSSD", f"{rmssd:.1f} ms", hrv_status("rmssd", rmssd))
    clinical_metrics[4].metric("pNN50", f"{pnn50 * 100:.1f}%", hrv_status("pnn50", pnn50))
    clinical_metrics[5].metric("Confidence", f"{confidence:.1f}%")

    st.markdown(
        f"**Prediction:** {selected['prediction']}  \n"
        f"**Risk:** {selected['risk']}  \n"
        f"**Model:** {selected.get('model_name', model_name)}  \n"
        f"**Total inference latency:** {metric_value(selected, 'total_seconds'):.3f} seconds"
    )
    explanation = str(selected.get("explanation", "")).strip()
    if explanation:
        st.info(explanation)

with detail_right:
    scalogram_path = Path(str(selected.get("scalogram_path", "")))
    if scalogram_path.exists():
        st.image(
            Image.open(scalogram_path),
            caption=f"Three-channel CWT scalogram for {selected_id}",
            use_container_width=True,
        )
    else:
        st.info("Scalogram image is unavailable for this record.")

chart_left, chart_right = st.columns(2)
with chart_left:
    prediction_counts = frame["prediction"].value_counts()
    prediction_figure = go.Figure(
        go.Pie(
            labels=prediction_counts.index,
            values=prediction_counts.values,
            hole=0.55,
            marker={
                "colors": [
                    PREDICTION_COLORS.get(label, "#777777")
                    for label in prediction_counts.index
                ]
            },
        )
    )
    prediction_figure.update_layout(title="Prediction Distribution", height=330)
    st.plotly_chart(prediction_figure, use_container_width=True)

with chart_right:
    scatter = px.scatter(
        frame,
        x="heart_rate",
        y="hrv",
        color="risk",
        color_discrete_map=RISK_COLORS,
        hover_data=["record_id", "prediction", "confidence"],
        labels={"heart_rate": "Heart rate (BPM)", "hrv": "HRV (ms)"},
        title="Heart Rate vs HRV",
    )
    scatter.update_layout(height=330)
    st.plotly_chart(scatter, use_container_width=True)

st.subheader("Prediction Log")
display_columns = [
    "record_id",
    "prediction",
    "confidence",
    "risk",
    "heart_rate",
    "hrv",
    "sdnn",
    "rmssd",
    "pnn50",
    "model_name",
    "total_seconds",
]
st.dataframe(
    frame[[column for column in display_columns if column in frame.columns]],
    use_container_width=True,
    hide_index=True,
)

if not errors.empty:
    with st.expander(f"Errors ({len(errors)})"):
        st.dataframe(
            errors[["record_id", "error"]],
            use_container_width=True,
            hide_index=True,
        )

