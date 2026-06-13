"""
predict.py — Unified ECG Prediction + Explanation Pipeline
===========================================================
Phase 6 : Single-sample prediction
Phase 7 : Real-time IoT simulation (N patients, 1-second cadence)
Phase 8 : Inline explanation via explain.py (LLM or rule-based fallback)

Pipeline per patient:
    raw row → scale → predict → assess_risk → explain → print + save

Run:
    python predict.py
"""

import os
import sys
import time
import joblib
import numpy as np
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    return os.path.abspath(os.path.join(SCRIPT_DIR, "..", filename))

# ── explain.py must be in the same directory ──────────────────────────────────
try:
    from src.explain import explain_prediction, ollama_status
except ImportError as e:
    if e.name in ('explain', 'src.explain'):
        print("[ERROR] explain.py not found in current directory.")
    else:
        print(f"[ERROR] Dependency import error inside explain.py: {e}")
        import traceback
        traceback.print_exc()
    raise SystemExit(1)

# ── ANSI colours ──────────────────────────────────────────────────────────────
R  = "\033[91m"; Y = "\033[93m"; G = "\033[92m"
C  = "\033[96m"; B = "\033[1m";  RS = "\033[0m"

# ── Constants ─────────────────────────────────────────────────────────────────
LABEL_NAMES = {0: "Normal", 1: "Arrhythmia", 2: "Other / Unknown"}

FEATURES = [
    "mean", "std", "max", "min",
    "peak_count", "heart_rate", "energy", "zero_crossings",
    "hrv", "rr_mean", "skewness", "kurtosis",
    "age", "sex"
]

N_PATIENTS = 10
DELAY_SEC  = 1.0

# ══════════════════════════════════════════════════════════════════════════════
# ISSUE 3 FIX — Data-driven risk threshold (not label-only)
# ══════════════════════════════════════════════════════════════════════════════
def assess_risk(cls: int, confidence: float, hr: float, hrv: float) -> tuple[str, str]:
    """
    Returns (risk_level, ansi_colour) based on class AND confidence AND vitals.

    Rules (clinically motivated):
      Arrhythmia + confidence ≥ 0.85                  → HIGH
      Arrhythmia + confidence < 0.85                   → MEDIUM
      Other/Unknown + confidence ≥ 0.80                → MEDIUM
      Normal   + confidence ≥ 0.80                     → LOW
      Any class + confidence < 0.60                    → MEDIUM  (model uncertain)
      Tachycardia (HR > 120) or bradycardia (HR < 40)  → bump up one level
    """
    risk = "LOW"

    if cls == 1:                                # Arrhythmia
        risk = "HIGH" if confidence >= 0.85 else "MEDIUM"
    elif cls == 2:                              # Other / Unknown
        risk = "MEDIUM" if confidence >= 0.80 else "LOW"
    else:                                       # Normal
        risk = "LOW"

    # Confidence too low → never call it LOW outright
    if confidence < 0.60 and risk == "LOW":
        risk = "MEDIUM"

    # Vital sign override: extreme HR bumps risk
    if hr > 120 or hr < 40:
        if risk == "LOW":
            risk = "MEDIUM"
        elif risk == "MEDIUM":
            risk = "HIGH"

    colour = {
        "HIGH":   R,
        "MEDIUM": Y,
        "LOW":    G
    }.get(risk, RS)

    return risk, colour


# ── Predict one sample — ISSUE 2 FIX: always uses predict_proba ──────────────
def predict_sample(row: pd.Series) -> dict:
    """
    Scale → predict → proba → risk → return result dict.
    confidence is always from predict_proba (required for risk threshold logic).
    """
    # Column-order fix: reindex to FEATURES before transform so the
    # order is guaranteed identical to training, preventing silent bugs.
    row    = row[FEATURES]
    scaled = scaler.transform(row.values.reshape(1, -1))

    cls = int(model.predict(scaled)[0])

    if hasattr(model, "predict_proba"):
        proba      = model.predict_proba(scaled)[0]   # e.g. [0.05, 0.91, 0.04]
        confidence = float(proba[cls])                # winning-class prob 0-1
    else:
        proba      = None
        confidence = 1.0
        print(f"{Y}[WARN]{RS} Model has no predict_proba — confidence set to 1.0")

    # Full per-class probability breakdown for transparency / viva / debugging
    if proba is not None:
        proba_breakdown = {
            LABEL_NAMES.get(i, str(i)): round(float(p) * 100, 1)
            for i, p in enumerate(proba)
        }
    else:
        proba_breakdown = {}

    label           = LABEL_NAMES.get(cls, str(cls))
    hr              = float(row.get("heart_rate", 0.0))
    hrv             = float(row.get("hrv", 0.0))
    risk, risk_col  = assess_risk(cls, confidence, hr, hrv)

    return {
        "cls":             cls,
        "label":           label,
        "confidence":      confidence,        # 0.0-1.0 (used by assess_risk/explain)
        "conf_pct":        confidence * 100,  # display-friendly %
        "proba_breakdown": proba_breakdown,   # full class-probability dict
        "hr":              hr,
        "hrv":             hrv,
        "age":             int(row.get("age", -1)),
        "sex_code":        int(row.get("sex", -1)),
        "risk":            risk,
        "risk_col":        risk_col,
    }


# ── Startup ───────────────────────────────────────────────────────────────────
print(f"\n{B}{'='*60}")
print("  ECG Prediction + Explanation Pipeline")
print(f"{'='*60}{RS}")

print(f"\n{B}Loading artefacts...{RS}")
try:
    model  = joblib.load(get_path("model.pkl"))
    scaler = joblib.load(get_path("scaler.pkl"))
    print(f"{G}[OK]{RS} model.pkl + scaler.pkl loaded")
except FileNotFoundError as e:
    print(f"{R}[ERROR]{RS} {e}")
    print("       Run train_model.py first.")
    raise SystemExit(1)

print(f"{G}[OK]{RS} Explanation engine: {ollama_status()}")

print(f"\n{B}Loading ecg_dataset.csv...{RS}")
df = pd.read_csv(get_path("ecg_dataset.csv"))
for col in FEATURES:
    if col not in df.columns:
        df[col] = 0
        print(f"{Y}[WARN]{RS} Column '{col}' missing — filled with 0")

# Pre-calculate unique patient IDs from filenames to keep consistent IDs across runs
if "filename" in df.columns:
    df["patient_id"] = df["filename"].apply(lambda f: int("".join(filter(str.isdigit, str(f)))))
else:
    df["patient_id"] = df.index + 1

# Define CSV loading helper to handle formatting and backup if conflict with model predictions
def load_predictions_csv(filename="predictions.csv"):
    import os
    if os.path.exists(filename):
        try:
            df_pred = pd.read_csv(filename)
            if not df_pred.empty and "patient" not in df_pred.columns:
                backup_name = get_path("validation_predictions.csv")
                print(f"{Y}[WARN]{RS} Old format {filename} detected (from training evaluation). Backing it up to {backup_name} and starting fresh.")
                df_pred.to_csv(backup_name, index=False)
                return pd.DataFrame(columns=["patient", "prediction", "confidence", "risk", "heart_rate", "hrv", "explanation"])
            return df_pred
        except Exception:
            return pd.DataFrame(columns=["patient", "prediction", "confidence", "risk", "heart_rate", "hrv", "explanation"])
    else:
        return pd.DataFrame(columns=["patient", "prediction", "confidence", "risk", "heart_rate", "hrv", "explanation"])

# Load predictions to filter out already predicted patients
import os
existing_df = load_predictions_csv(get_path("predictions.csv"))
predicted_ids = set(existing_df["patient"].unique()) if not existing_df.empty else set()

# Filter dataset to available patients
available_df = df[~df["patient_id"].isin(predicted_ids)]
if available_df.empty:
    print(f"{Y}[WARN]{RS} All patients from dataset have already been predicted. Resetting tracking pool.")
    available_df = df

print(f"{G}[OK]{RS} {len(df)} records loaded, {len(available_df)} new patients available for simulation\n")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 6 — Single patient: predict → explain immediately   (ISSUE 1 FIX)
# ══════════════════════════════════════════════════════════════════════════════
print(f"{B}{'='*60}")
print("  PHASE 6 — Single Patient Prediction + Explanation")
print(f"{'='*60}{RS}\n")

# Sample 1 new patient
sample_row = available_df.sample(1, random_state=None).iloc[0]
patient_id = int(sample_row["patient_id"])
r = predict_sample(sample_row)

print(f"  Patient ID   : {patient_id}")
print(f"  Heart Rate   : {r['hr']:.1f} BPM")
print(f"  HRV          : {r['hrv']:.2f} ms")
print(f"  Age / Sex    : {r['age']} / {'M' if r['sex_code']==1 else 'F'}")
print(f"\n  {B}Prediction   : {r['label']}{RS}")
print(f"  Confidence   : {r['conf_pct']:.1f}%")
print(f"  Risk         : {r['risk_col']}{B}{r['risk']}{RS}")

# Full probability breakdown
if r["proba_breakdown"]:
    print(f"\n  {C}Class probabilities:{RS}")
    for cls_name, pct in r["proba_breakdown"].items():
        bar    = "#" * int(pct / 5)
        marker = "  <- predicted" if cls_name == r["label"] else ""
        print(f"    {cls_name:<22} {pct:>5.1f}%  {bar}{marker}")
print()

# Explanation
print(f"  {C}Explanation:{RS}")
explanation = explain_prediction(
    cls=r['cls'], confidence=r['confidence'],
    hr=r['hr'], hrv=r['hrv'],
    age=r['age'], sex_code=r['sex_code'],
    risk=r['risk']
)
for line in explanation.split(". "):
    if line.strip():
        print(f"  {line.strip()}.")

print()

# Log Phase 6 prediction to predictions.csv immediately so it reflects on the dashboard
phase6_record = pd.DataFrame([{
    "patient":     patient_id,
    "prediction":  r['label'],
    "confidence":  round(r['conf_pct'], 1),
    "risk":        r['risk'],
    "heart_rate":  round(r['hr'], 1),
    "hrv":         round(r['hrv'], 2),
    "explanation": explanation
}])
existing_df = pd.concat([existing_df, phase6_record], ignore_index=True)
existing_df.to_csv(get_path("predictions.csv"), index=False)
print(f"  {G}[OK]{RS} Phase 6 prediction saved -> predictions.csv")
print()

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 7 + 8 — Real-time simulation: predict → explain per patient
# ══════════════════════════════════════════════════════════════════════════════
print(f"{B}{'='*60}")
print(f"  PHASE 7+8 — Live Monitor: {N_PATIENTS} patients")
print(f"{'='*60}{RS}\n")

# Refresh existing records and filter pool again to exclude the patient predicted in Phase 6
existing_df = load_predictions_csv(get_path("predictions.csv"))
predicted_ids = set(existing_df["patient"].unique()) if not existing_df.empty else set()
available_df = df[~df["patient_id"].isin(predicted_ids)]
if available_df.empty or len(available_df) < N_PATIENTS:
    available_df = df

records = []
sample_pool = available_df.sample(n=min(N_PATIENTS, len(available_df)), random_state=None)

for i, (_, row) in enumerate(sample_pool.iterrows()):
    p_id = int(row["patient_id"])
    r = predict_sample(row)
    
    # ── Header line ──────────────────────────────────────────────────────────
    print(f"{B}Patient {p_id:>5}{RS}  "
          f"HR: {r['hr']:>6.1f} BPM  "
          f"HRV: {r['hrv']:>6.2f}  "
          f"|  {B}{r['label']:<20}{RS}"
          f"Conf: {r['conf_pct']:>5.1f}%  "
          f"|  {r['risk_col']}{B}[{r['risk']}]{RS}")

    # ── Probability breakdown ────────────────────────────────────────────────
    if r["proba_breakdown"]:
        parts = "  ".join(
            f"{name}: {pct:.1f}%" for name, pct in r["proba_breakdown"].items()
        )
        print(f"  {C}Probs ->{RS}  {parts}")

    # Explanation call
    if r['risk'] in ('HIGH', 'MEDIUM'):
        explanation = explain_prediction(
            cls=r['cls'], confidence=r['confidence'],
            hr=r['hr'], hrv=r['hrv'],
            age=r['age'], sex_code=r['sex_code'],
            risk=r['risk']
        )
        tag = f"{R}[GEMMA !]{RS}" if r['risk'] == 'HIGH' else f"{Y}[GEMMA]{RS}"
        print(f"  {tag} {explanation}\n")
    else:
        explanation = 'Low risk -- no detailed explanation required.'
        print(f"  {G}[OK] {explanation}{RS}\n")
        
    records.append({
        "patient":     p_id,
        "prediction":  r['label'],
        "confidence":  round(r['conf_pct'], 1),
        "risk":        r['risk'],
        "heart_rate":  round(r['hr'], 1),
        "hrv":         round(r['hrv'], 2),
        "explanation": explanation
    })

    time.sleep(DELAY_SEC)

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"{B}{'-'*60}")
print("  SESSION SUMMARY")
print(f"{'-'*60}{RS}")

summary_df = pd.DataFrame(records)

for lbl, cnt in summary_df["prediction"].value_counts().items():
    pct = 100 * cnt / len(summary_df)
    print(f"  {lbl:<22} {cnt:>2} patients  {'#'*int(20*pct/100)}  ({pct:.0f}%)")

high_risk = summary_df[summary_df["risk"] == "HIGH"]
if not high_risk.empty:
    ids = [int(p) for p in high_risk["patient"].values]
    print(f"\n  {R}{B}!  HIGH-RISK PATIENTS: {ids}{RS}")
else:
    print(f"\n  {G}[OK]  No high-risk patients in this session{RS}")

# Save to predictions.csv
combined_df = pd.concat([existing_df, summary_df], ignore_index=True)
combined_df.to_csv(get_path("predictions.csv"), index=False)
print(f"\n  {G}[OK]{RS} Full results saved -> predictions.csv")
print(f"{B}{'='*60}{RS}\n")