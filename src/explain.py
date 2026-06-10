"""
explain.py — Explanation Utility Module
========================================
Import this; do NOT run directly.

Usage:
    from explain import explain_prediction, ollama_status

    text = explain_prediction(
        cls=1, confidence=0.91, hr=112.3, hrv=18.5, age=67, sex_code=1, risk="HIGH"
    )
"""

import time
import requests

# ── Config ────────────────────────────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma:7b"       # swap: "mistral", "gemma:2b", "llama3", etc.
LLM_TIMEOUT  = 30               # seconds per request
MAX_RETRIES  = 2                # retries if LLM times out
RETRY_DELAY  = 1                # seconds between retries

# ── Clinical label mapping ────────────────────────────────────────────────────
LABEL_NAMES = {
    0: "Normal Sinus Rhythm",
    1: "Arrhythmia",
    2: "Other / Unclassified"
}

# ── HRV clinical thresholds (ms) ─────────────────────────────────────────────
#   < 20  → critically low  (severe autonomic dysfunction / acute illness)
#   20-50 → low-borderline  (elevated cardiac risk, monitor closely)
#   50-100→ acceptable      (mildly reduced, non-alarming)
#   > 100 → healthy         (good autonomic regulation)
def _hrv_interpretation(hrv: float) -> tuple[str, str]:
    """Returns (clinical description, severity tag)."""
    if hrv < 20:
        return ("critically reduced (< 20 ms), indicating severe autonomic stress "
                "or acute cardiac dysfunction — immediate review advised", "CRITICAL")
    elif hrv < 50:
        return ("low (< 50 ms), which is associated with elevated cardiac risk "
                "and reduced autonomic flexibility", "LOW")
    elif hrv < 100:
        return ("within an acceptable range (50–100 ms), suggesting moderate "
                "autonomic regulation", "NORMAL")
    else:
        return ("healthy (> 100 ms), indicating good autonomic nervous system activity", "GOOD")


# ── HR clinical thresholds ────────────────────────────────────────────────────
def _hr_interpretation(hr: float) -> tuple[str, str]:
    """Returns (clinical description, severity tag)."""
    if hr < 40:
        return (f"severely bradycardic at {hr:.0f} BPM (< 40 BPM) — "
                "dangerously low heart rate requiring urgent evaluation", "CRITICAL")
    elif hr < 60:
        return (f"bradycardic at {hr:.0f} BPM (60–40 BPM) — below normal, "
                "may indicate conduction block or medication effect", "LOW")
    elif hr <= 100:
        return (f"normal at {hr:.0f} BPM (60–100 BPM)", "NORMAL")
    elif hr <= 120:
        return (f"mildly elevated (tachycardic) at {hr:.0f} BPM — "
                "above the resting normal range of 60–100 BPM", "ELEVATED")
    else:
        return (f"significantly elevated (tachycardic) at {hr:.0f} BPM — "
                "substantially above normal, may indicate stress, fever, or arrhythmia", "HIGH")


# ── Age context helper ────────────────────────────────────────────────────────
def _age_context(age: int) -> str:
    if age <= 0:
        return ""
    elif age < 18:
        return "As a paediatric patient, ECG norms differ from adults; specialist review is advised. "
    elif age < 40:
        return "In a young adult, arrhythmia findings are less expected and warrant thorough investigation. "
    elif age < 65:
        return "In a middle-aged patient, cardiac risk factors such as hypertension and lifestyle should be assessed. "
    else:
        return ("As an older patient (65+), the risk of cardiac events is statistically higher "
                "and findings should be reviewed promptly. ")


# ── Confidence qualifier ──────────────────────────────────────────────────────
def _confidence_note(confidence_pct: float) -> str:
    if confidence_pct >= 90:
        return f"The model is highly confident ({confidence_pct:.0f}%) in this classification. "
    elif confidence_pct >= 75:
        return f"The model is reasonably confident ({confidence_pct:.0f}%) in this result. "
    elif confidence_pct >= 60:
        return (f"The model's confidence is moderate ({confidence_pct:.0f}%), "
                "meaning the ECG pattern has some ambiguity — clinical review is recommended. ")
    else:
        return (f"The model's confidence is low ({confidence_pct:.0f}%), "
                "indicating the signal features are borderline. "
                "Independent clinical assessment is strongly recommended. ")


# ── Rule-based fallback (no LLM required) ────────────────────────────────────
def _rule_based(label: str, hr: float, hrv: float,
                confidence_pct: float, risk: str,
                age: int = -1, sex: str = "Unknown") -> str:
    """
    Fully structured clinical explanation without any LLM.
    Uses clinical thresholds for HR, HRV, age, and confidence.
    """
    hr_desc,  _  = _hr_interpretation(hr)
    hrv_desc, _  = _hrv_interpretation(hrv)
    conf_note    = _confidence_note(confidence_pct)
    age_ctx      = _age_context(age)

    # --- Classification-specific base sentence ---
    if "Arrhythmia" in label:
        base = (
            f"The LightGBM model detected {label} and assigned a {risk} risk level. "
            f"Arrhythmias represent irregular electrical conduction patterns in the heart "
            f"that may range from benign to life-threatening depending on the type. "
        )
        next_step = (
            "A 12-lead ECG and cardiology referral are recommended for formal classification "
            "of the arrhythmia subtype. " if risk == "HIGH"
            else "Routine cardiac monitoring and a follow-up ECG are suggested. "
        )
    elif "Normal" in label:
        base = (
            f"The LightGBM model classified this ECG as {label} with a {risk} risk level. "
            f"The electrical conduction pattern appears regular, with no detected arrhythmia signature. "
        )
        next_step = (
            "Despite the normal classification, the elevated confidence uncertainty warrants a repeat ECG. "
            if confidence_pct < 70
            else "Routine screening is sufficient; no immediate action required. "
        )
    else:
        base = (
            f"The model returned an {label} result at {risk} risk. "
            f"This indicates the ECG pattern did not clearly match known Normal or Arrhythmia signatures. "
        )
        next_step = "Manual review by a cardiologist is strongly recommended for an unclassified result. "

    # --- Compose full explanation ---
    explanation = (
        conf_note
        + base
        + f"Heart rate is {hr_desc}. "
        + f"HRV is {hrv_desc}. "
        + age_ctx
        + next_step
    )
    return explanation.strip()


# ── LLM prompt builder ────────────────────────────────────────────────────────
def _build_prompt(label: str, hr: float, hrv: float,
                  confidence_pct: float, age, sex: str, risk: str) -> str:
    hr_desc,  hr_tag  = _hr_interpretation(hr)
    hrv_desc, hrv_tag = _hrv_interpretation(hrv)

    clinical_flags = []
    if hr_tag in ("CRITICAL", "HIGH"):
        clinical_flags.append(f"⚠ Heart rate is {hr_desc}")
    if hrv_tag in ("CRITICAL", "LOW"):
        clinical_flags.append(f"⚠ HRV is {hrv_desc}")
    if confidence_pct < 70:
        clinical_flags.append(f"⚠ Low model confidence ({confidence_pct:.0f}%) — result is borderline")

    flags_text = "\n".join(clinical_flags) if clinical_flags else "No critical flags."

    return f"""You are a clinical decision support assistant helping doctors interpret ECG machine learning results.

=== MODEL OUTPUT ===
Classification : {label}
Confidence     : {confidence_pct:.1f}%
Risk Level     : {risk}

=== PATIENT PROFILE ===
Age            : {age} years
Sex            : {sex}
Heart Rate     : {hr:.1f} BPM  [{hr_tag}]
HRV            : {hrv:.2f} ms  [{hrv_tag}]

=== CLINICAL FLAGS ===
{flags_text}

=== TASK ===
Write a clear, 3–4 sentence clinical interpretation for a non-specialist reader.
Cover:
1. What the classification means for this patient's cardiac health.
2. Whether the heart rate and HRV values are clinically concerning given the risk level.
3. One concrete next clinical step (e.g., referral, repeat ECG, 24-hour Holter monitor).

Rules: Plain English only. No bullet points. No markdown. No lists. No hedging phrases like "I think" or "possibly"."""


# ── LLM call with retry ───────────────────────────────────────────────────────
def _llm_call(prompt: str) -> str | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
                timeout=LLM_TIMEOUT
            )
            if resp.status_code == 200:
                text = resp.json().get("response", "").strip()
                # Basic sanity: must be at least 30 chars to be a real response
                if len(text) >= 30:
                    return text
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.JSONDecodeError):
            pass
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)
    return None


# ── Ollama availability check (called fresh each time, not once at import) ───
def _is_ollama_up() -> bool:
    try:
        return requests.get("http://localhost:11434", timeout=2).status_code == 200
    except Exception:
        return False


# ── Public API ────────────────────────────────────────────────────────────────
def explain_prediction(cls: int, confidence: float,
                       hr: float, hrv: float,
                       age: int = -1, sex_code: int = -1,
                       risk: str = "UNKNOWN") -> str:
    """
    Generate a plain-English clinical explanation for a single ECG prediction.

    Parameters
    ----------
    cls        : predicted class id  (0=Normal, 1=Arrhythmia, 2=Other)
    confidence : winning class probability from predict_proba()  (0.0–1.0)
    hr         : heart rate in BPM
    hrv        : HRV in milliseconds
    age        : patient age in years  (-1 = unknown)
    sex_code   : 1=Male, 0=Female, -1=Unknown
    risk       : risk string from assess_risk()  ("HIGH"/"MEDIUM"/"LOW")

    Returns
    -------
    Plain-English explanation string (from LLM if available, else rule-based).
    """
    label          = LABEL_NAMES.get(cls, str(cls))
    sex            = "Male" if sex_code == 1 else ("Female" if sex_code == 0 else "Unknown")
    age_display    = age if age > 0 else "Unknown"
    confidence_pct = confidence * 100

    # Try LLM first (checks Ollama availability live each call)
    if _is_ollama_up():
        prompt = _build_prompt(label, hr, hrv, confidence_pct, age_display, sex, risk)
        result = _llm_call(prompt)
        if result:
            return result
        # LLM reachable but returned empty/garbage → fallback

    # Rule-based fallback (always works, no network needed)
    return _rule_based(label, hr, hrv, confidence_pct, risk, age=age, sex=sex)


def ollama_status() -> str:
    """Return a human-readable Ollama status string."""
    up = _is_ollama_up()
    return f"{'online' if up else 'offline (rule-based fallback active)'} ({OLLAMA_MODEL})"
