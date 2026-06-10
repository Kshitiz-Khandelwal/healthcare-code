import os
import numpy as np
import pandas as pd
from scipy.io import loadmat
from scipy.signal import find_peaks
from scipy.stats import skew, kurtosis

# 📁 UPDATE THIS PATH
DATASET_PATH = "Dataset/WFDBRecords"
OUTPUT_CSV = "ecg_dataset.csv"

sampling_freq = 500  # from .hea file

rows = []

# ------------------------
# PHASE 1 — LABEL MAPPING (50 classes → 3 classes)
# ------------------------
NORMAL = ["426783006"]

ARRHYTHMIA = [
    "164889003",  # atrial fibrillation
    "164890007",
    "426177001"
]

def map_label(dx):
    dx = str(dx)
    if any(code in dx for code in NORMAL):
        return 0       # Normal
    elif any(code in dx for code in ARRHYTHMIA):
        return 1       # Arrhythmia
    else:
        return 2       # Other


# ------------------------
# COUNT TOTAL FILES (for progress)
# ------------------------
total_files = sum(
    1 for root, _, files in os.walk(DATASET_PATH)
    for f in files if f.endswith(".mat")
)

count = 0


def extract_features(mat_path, hea_path, filename):
    try:
        # ------------------------
        # LOAD SIGNAL (.mat)
        # ------------------------
        mat = loadmat(mat_path)

        # Robust key extraction
        if "val" in mat:
            data = mat["val"]
        else:
            key = [k for k in mat.keys() if not k.startswith("__")][0]
            data = mat[key]

        # Shape handling: (12, 5000) → (5000, 12)
        if data.shape[0] == 12:
            data = data.T

        # ------------------------
        # CHANNEL REDUCTION
        # ------------------------
        signal = np.mean(data, axis=1)

        # ------------------------
        # RAW FEATURES
        # ------------------------
        mean_val = np.mean(signal)
        std_val  = np.std(signal)
        max_val  = np.max(signal)
        min_val  = np.min(signal)
        energy   = np.sum(signal ** 2)

        # ------------------------
        # ZERO CROSSING RATE
        # ------------------------
        zero_crossings = ((signal[:-1] * signal[1:]) < 0).sum()

        # ------------------------
        # PHASE 2 — STATISTICAL FEATURES (pre-normalization)
        # ------------------------
        skewness = skew(signal)
        kurt     = kurtosis(signal)

        # ------------------------
        # NORMALIZE (for peak detection only)
        # ------------------------
        if np.std(signal) != 0:
            signal = (signal - np.mean(signal)) / np.std(signal)

        # ------------------------
        # PEAK FEATURES
        # ------------------------
        peaks, _ = find_peaks(signal, distance=150, height=0.5)
        peak_count = len(peaks)

        # ------------------------
        # HEART RATE (BPM)
        # ------------------------
        duration   = len(signal) / sampling_freq
        heart_rate = (peak_count / duration) * 60 if duration > 0 else 0

        # ------------------------
        # PHASE 2 — HEART RATE VARIABILITY (HRV)
        # ------------------------
        if len(peaks) > 1:
            rr_intervals = np.diff(peaks)
            hrv          = np.std(rr_intervals)
            rr_mean      = np.mean(rr_intervals)
        else:
            hrv     = 0
            rr_mean = 0

        # ------------------------
        # READ .hea FILE
        # ------------------------
        age   = -1
        sex   = -1
        label = 2  # default: Other

        with open(hea_path, "r") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()

            if line.startswith("#Age:"):
                age_str = line.split(":")[1].strip()
                age = int(age_str) if age_str.isdigit() else -1

            elif line.startswith("#Sex:"):
                sex_str = line.split(":")[1].strip()
                if sex_str == "Male":
                    sex = 1
                elif sex_str == "Female":
                    sex = 0
                else:
                    sex = -1

            elif line.startswith("#Dx:"):
                dx = line.split(":")[1].strip()
                # PHASE 1: map raw dx codes → 3-class label
                label = map_label(dx)

        return {
            "filename":       filename,
            "mean":           mean_val,
            "std":            std_val,
            "max":            max_val,
            "min":            min_val,
            "peak_count":     peak_count,
            "heart_rate":     heart_rate,
            "energy":         energy,
            "zero_crossings": zero_crossings,
            "hrv":            hrv,        # PHASE 2
            "rr_mean":        rr_mean,    # PHASE 2
            "skewness":       skewness,   # PHASE 2
            "kurtosis":       kurt,       # PHASE 2
            "age":            age,
            "sex":            sex,
            "label":          label       # 0=Normal, 1=Arrhythmia, 2=Other
        }

    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")
        return None


# ------------------------
# PROCESS DATASET
# ------------------------
for root, dirs, files in os.walk(DATASET_PATH):
    for file in files:
        if file.endswith(".mat"):
            mat_path = os.path.join(root, file)
            hea_path = mat_path.replace(".mat", ".hea")

            if os.path.exists(hea_path):
                result = extract_features(mat_path, hea_path, file)
                if result:
                    rows.append(result)

            count += 1
            if count % 100 == 0:
                print(f"Processed {count}/{total_files} files...")


# ------------------------
# SAVE DATASET
# ------------------------
df = pd.DataFrame(rows)

# Label mapping reference
mapping = pd.DataFrame({
    "label": ["Normal", "Arrhythmia", "Other"],
    "code":  [0, 1, 2]
})
mapping.to_csv("label_mapping.csv", index=False)

# Save dataset
df.to_csv(OUTPUT_CSV, index=False)

print("\n✅ Dataset created:", OUTPUT_CSV)
print("📊 Total samples:", len(df))
print("\n📊 Class distribution:")
print(df["label"].value_counts().rename({0: "Normal", 1: "Arrhythmia", 2: "Other"}))
print("\n", df.head())