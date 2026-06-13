from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import numpy as np
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
from ecg_io import discover_records, load_ecg_mat
from hybrid_predictor import HybridECGPredictor, load_hybrid_artifacts


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


@st.cache_resource(show_spinner="Initializing hybrid predictor...")
def load_predictor(model_name: str) -> HybridECGPredictor:
    return HybridECGPredictor(CONFIG, model_name=model_name)


@st.cache_data(show_spinner="Loading raw ECG signal...")
def load_raw_signal(record_id: str) -> tuple[np.ndarray, int]:
    records = discover_records(CONFIG.raw_dataset_dir, limit=5000)
    record = next(r for r in records if r.record_id == record_id)
    ecg = load_ecg_mat(record.mat_path)
    return ecg, record.sampling_frequency


def plot_ecg_signals(ecg: np.ndarray, fs: int) -> go.Figure:
    from preprocessing import preprocess_lead
    # Preprocess the three leads: I (0), II (1), V5 (10)
    leads = [0, 1, 10]
    lead_names = ["Lead I", "Lead II", "Lead V5"]
    fig = go.Figure()
    
    # Plot first 5 seconds (2500 samples if fs=500)
    limit = min(ecg.shape[1], int(5 * fs))
    time_axis = np.arange(limit) / fs
    
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    for i, lead_idx in enumerate(leads):
        if lead_idx < ecg.shape[0]:
            clean_signal = preprocess_lead(ecg[lead_idx], fs=fs)[:limit]
            fig.add_trace(
                go.Scatter(
                    x=time_axis,
                    y=clean_signal,
                    mode="lines",
                    name=lead_names[i],
                    line=dict(color=colors[i], width=1.5),
                )
            )
    fig.update_layout(
        title="Preprocessed ECG Time-Series (Leads I, II, V5)",
        xaxis_title="Time (seconds)",
        yaxis_title="Normalized Amplitude (z-score)",
        hovermode="x unified",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


@st.cache_data(show_spinner=False)
def get_original_feature_importance(model_name: str, limit: int = 10) -> pd.DataFrame:
    resources = load_model_resources(model_name)
    classifier = resources.classifier
    pca = resources.pca
    feature_names = resources.features
    
    if not hasattr(classifier, "feature_importances_"):
        return pd.DataFrame(columns=["feature", "importance"])
        
    if pca is None:
        frame = pd.DataFrame({
            "feature": feature_names[:len(classifier.feature_importances_)],
            "importance": classifier.feature_importances_
        }).sort_values("importance", ascending=False)
        return frame.head(limit).reset_index(drop=True)
        
    # Project PCA component importance back to original feature space
    W = np.abs(pca.components_)  # shape (n_components, n_features)
    pca_importances = classifier.feature_importances_  # shape (n_components,)
    
    # Calculate importances in original space
    orig_importances = np.dot(pca_importances, W)
    if orig_importances.sum() > 0:
        orig_importances = orig_importances / orig_importances.sum()
        
    frame = pd.DataFrame({
        "feature": feature_names,
        "importance": orig_importances
    }).sort_values("importance", ascending=False)
    
    return frame.head(limit).reset_index(drop=True)


@st.cache_data(show_spinner="Running live hybrid inference...")
def run_live_inference(record_id: str, model_name: str) -> dict:
    predictor = load_predictor(model_name)
    record = next(
        record
        for record in discover_records(CONFIG.raw_dataset_dir, limit=5000)
        if record.record_id == record_id
    )
    return predictor.predict_record(record)


def metric_value(row: pd.Series, name: str, default: float = 0.0) -> float:
    value = row.get(name, default)
    return default if pd.isna(value) else float(value)


def get_hrv_delta(name: str, value: float) -> tuple[str, str]:
    """
    Returns (delta_text, delta_color) based on clinical reference ranges:
      - SDNN: Normal (>=50ms), Borderline (30-50ms), Abnormal (<30ms)
      - RMSSD: Normal (>=25ms), Borderline (15-25ms), Abnormal (<15ms)
      - pNN50: Normal (>=3%), Borderline (1-3%), Abnormal (<1%)
    Uses Streamlit's delta coloring: green for +Normal, red for -Abnormal, gray for Borderline.
    """
    if name == "sdnn":
        if value >= 50.0:
            return "+ Normal (>=50ms)", "normal"
        elif value >= 30.0:
            return "Borderline (30-50ms)", "off"
        else:
            return "- Abnormal (<30ms)", "normal"
    elif name == "rmssd":
        if value >= 25.0:
            return "+ Normal (>=25ms)", "normal"
        elif value >= 15.0:
            return "Borderline (15-25ms)", "off"
        else:
            return "- Abnormal (<15ms)", "normal"
    elif name == "pnn50":
        val_pct = value * 100.0 if value <= 1.0 else value
        if val_pct >= 3.0:
            return f"+ Normal (>=3.0%)", "normal"
        elif val_pct >= 1.0:
            return f"Borderline (1.0-3.0%)", "off"
        else:
            return f"- Abnormal (<1.0%)", "normal"
    return "", "off"


st.title("ECG Hybrid Monitoring System")
st.caption("EfficientNet scalogram features + clinical ECG features + LightGBM")
st.warning(
    "⚠️ Research and decision-support prototype only. This system is not a standalone "
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

st.subheader("Session Overview")
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

st.markdown("**Session Temporal HRV Averages**")
session_hrv_metrics = st.columns(3)
avg_sdnn = float(frame["sdnn"].dropna().mean()) if "sdnn" in frame.columns and frame["sdnn"].notna().any() else 0.0
avg_rmssd = float(frame["rmssd"].dropna().mean()) if "rmssd" in frame.columns and frame["rmssd"].notna().any() else 0.0
avg_pnn50 = float(frame["pnn50"].dropna().mean()) if "pnn50" in frame.columns and frame["pnn50"].notna().any() else 0.0

delta_sdnn, col_sdnn = get_hrv_delta("sdnn", avg_sdnn)
delta_rmssd, col_rmssd = get_hrv_delta("rmssd", avg_rmssd)
delta_pnn50, col_pnn50 = get_hrv_delta("pnn50", avg_pnn50)

session_hrv_metrics[0].metric("Avg SDNN", f"{avg_sdnn:.1f} ms", delta=delta_sdnn, delta_color=col_sdnn)
session_hrv_metrics[1].metric("Avg RMSSD", f"{avg_rmssd:.1f} ms", delta=delta_rmssd, delta_color=col_rmssd)
session_hrv_metrics[2].metric("Avg pNN50", f"{avg_pnn50 * 100:.1f}%" if avg_pnn50 <= 1.0 else f"{avg_pnn50:.1f}%", delta=delta_pnn50, delta_color=col_pnn50)

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

    rec_delta_sdnn, rec_col_sdnn = get_hrv_delta("sdnn", sdnn)
    rec_delta_rmssd, rec_col_rmssd = get_hrv_delta("rmssd", rmssd)
    rec_delta_pnn50, rec_col_pnn50 = get_hrv_delta("pnn50", pnn50)

    clinical_metrics[0].metric("Heart rate", f"{heart_rate:.1f} BPM")
    clinical_metrics[1].metric("HRV", f"{hrv:.1f} ms")
    clinical_metrics[2].metric("SDNN", f"{sdnn:.1f} ms", delta=rec_delta_sdnn, delta_color=rec_col_sdnn)
    clinical_metrics[3].metric("RMSSD", f"{rmssd:.1f} ms", delta=rec_delta_rmssd, delta_color=rec_col_rmssd)
    clinical_metrics[4].metric("pNN50", f"{pnn50 * 100:.1f}%" if pnn50 <= 1.0 else f"{pnn50:.1f}%", delta=rec_delta_pnn50, delta_color=rec_col_pnn50)
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
    if st.button("Run live inference on selected record", use_container_width=True):
        with st.status(
            f"Running EfficientNet-B4 + LightGBM hybrid model pipeline on {selected_id}...",
            expanded=True,
        ) as status:
            def update_status_step(msg):
                st.write(msg)
            
            try:
                predictor = load_predictor(model_name)
                # Find matching record
                records = discover_records(CONFIG.raw_dataset_dir, limit=5000)
                record = next(r for r in records if r.record_id == selected_id)
                
                live_result = predictor.predict_record(record, status_callback=update_status_step)
                
                if live_result["status"] == "ok":
                    status.update(
                        label=(
                            f"Live inference complete: {live_result['prediction']} "
                            f"({live_result['confidence']:.1f}%)"
                        ),
                        state="complete",
                    )
                    st.session_state["live_result"] = live_result
                    st.rerun()
                else:
                    status.update(label="Live inference failed", state="error")
                    st.error(live_result.get("error", "Unknown error"))
            except Exception as exc:
                status.update(label=f"Inference error: {type(exc).__name__}", state="error")
                st.error(f"Failed to run inference: {exc}")

    live_result = st.session_state.get("live_result")
    if live_result and live_result.get("record_id") == selected_id:
        st.caption(
            "Latest live run: "
            f"preprocess/scalogram {live_result.get('preprocessing_scalogram_seconds', 0):.3f}s, "
            f"embedding {live_result.get('embedding_seconds', 0):.3f}s, "
            f"classifier {live_result.get('classifier_seconds', 0):.3f}s, "
            f"total {live_result.get('total_seconds', 0):.3f}s"
        )

st.subheader("ECG Signal & Scalogram Analysis")
analysis_left, analysis_right = st.columns([3, 2])
with analysis_left:
    try:
        raw_ecg, raw_fs = load_raw_signal(selected_id)
        ecg_fig = plot_ecg_signals(raw_ecg, raw_fs)
        st.plotly_chart(ecg_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not load raw ECG time-series: {e}")

with analysis_right:
    scalogram_path = Path(str(selected.get("scalogram_path", "")))
    if scalogram_path.exists() and scalogram_path.is_file():
        st.image(
            Image.open(scalogram_path),
            caption=f"Three-channel CWT scalogram for {selected_id}",
            use_container_width=True,
        )
    else:
        st.info("ℹ️ CWT scalogram image file not found. Click 'Run live inference' to generate it.")

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

if resources is not None:
    importance = get_original_feature_importance(model_name)
    if not importance.empty:
        with st.expander("Top clinical & deep feature contributors (Projected from PCA)"):
            st.bar_chart(importance, x="feature", y="importance", use_container_width=True)
            
            # Show a small table of the top clinical/handcrafted feature values for this patient
            clinical_features_in_top = [f for f in importance["feature"].tolist() if not f.startswith("eff_")]
            if clinical_features_in_top:
                st.markdown("**Patient values for top clinical contributors:**")
                vals = {f: [selected.get(f, "N/A")] for f in clinical_features_in_top}
                st.dataframe(pd.DataFrame(vals), hide_index=True)

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

