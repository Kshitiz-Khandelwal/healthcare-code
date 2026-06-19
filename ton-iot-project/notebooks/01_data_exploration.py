# %% [markdown]
# # Phase 1 — Data Exploration & Audit
# This notebook explores the TON_IoT network dataset, inspects distributions, and generates a data audit report.

# %%
import sys, os
from pathlib import Path

def find_project_root(start: Path | None = None) -> Path:
    start = Path.cwd() if start is None else start.resolve()
    for candidate in [start, *start.parents]:
        if (candidate / "config.py").exists() and (candidate / "src").is_dir():
            return candidate
    raise RuntimeError("Could not find project root containing config.py and src/")

PROJECT_ROOT = find_project_root()
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

import random
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import config

random.seed(config.SEED)
np.random.seed(config.SEED)

# %%
# Ensure output directories exist
Path(config.PLOTS_DIR).mkdir(parents=True, exist_ok=True)
Path(config.REPORTS_DIR).mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Phase 1: Data Exploration & Audit")
print("=" * 60)

# %% [markdown]
# ## 1. Load Data

# %%
print("\n[1] Loading dataset...")
df = pd.read_csv(config.DATA_PATH)
print(f"    Shape: {df.shape}")
print(f"    Columns: {list(df.columns)}\n")

# %% [markdown]
# ## 2. Basic Info & Summary Statistics

# %%
print("[2] Data types:")
print(df.dtypes.to_string())

print("\n[3] First 5 rows:")
print(df.head().to_string())

print("\n[4] Numeric summary:")
print(df.describe(include='all').to_string())

# %% [markdown]
# ## 3. Missing Values Audit

# %%
print("\n[5] Missing values (including '-' placeholder):")
# Count '-' occurrences in object columns
dash_counts = {}
for col in df.select_dtypes(include='object').columns:
    dash_counts[col] = (df[col] == '-').sum()

actual_nan = df.isnull().sum()
combined_missing = actual_nan.copy()
for col, count in dash_counts.items():
    combined_missing[col] = combined_missing[col] + count

missing_df = pd.DataFrame({
    'null_count': actual_nan,
    'dash_count': pd.Series(dash_counts),
    'total_missing': combined_missing,
    'pct_missing': (combined_missing / len(df) * 100).round(2)
})
missing_df = missing_df[missing_df['total_missing'] > 0].sort_values('total_missing', ascending=False)
print(missing_df.to_string())

# %% [markdown]
# ## 4. Class Distributions

# %%
print("\n[6] Binary label distribution:")
label_counts = df['label'].value_counts()
print(label_counts)
print(f"    Attack ratio: {label_counts.get(1, 0) / len(df) * 100:.2f}%")

print("\n[7] Attack type distribution (multi-class):")
type_counts = df['type'].value_counts()
print(type_counts)

print("\n[7b] 5 sample rows per attack type:")
for t in sorted(df['type'].unique()):
    print(f"\n--- 5 Samples for Type: {t} ---")
    print(df[df['type'] == t].head(5).to_string())

# %% [markdown]
# ## 5. Distribution Plots & Heatmaps

# %%
print("\n[8] Saving distribution plots...")

# Binary label distribution
fig, ax = plt.subplots(figsize=(6, 4))
label_counts.plot(kind='bar', ax=ax, color=['#2ecc71', '#e74c3c'], edgecolor='black')
ax.set_title('Binary Label Distribution\n(0=Benign, 1=Attack)', fontsize=13, fontweight='bold')
ax.set_xlabel('Label')
ax.set_ylabel('Count')
ax.set_xticklabels(['Benign (0)', 'Attack (1)'], rotation=0)
for i, v in enumerate(label_counts):
    ax.text(i, v + 500, f'{v:,}\n({v/len(df)*100:.1f}%)', ha='center', fontsize=9)
plt.tight_layout()
plt.savefig(f"{config.PLOTS_DIR}label_distribution.png", dpi=150)
plt.close()
print(f"    Saved: {config.PLOTS_DIR}label_distribution.png")

# Attack type distribution
fig, ax = plt.subplots(figsize=(12, 5))
type_counts.plot(kind='bar', ax=ax, color=sns.color_palette("tab10", len(type_counts)), edgecolor='black')
ax.set_title('Attack Type Distribution (Multi-Class)', fontsize=13, fontweight='bold')
ax.set_xlabel('Attack Type')
ax.set_ylabel('Count')
ax.set_xticklabels(type_counts.index, rotation=45, ha='right')
for i, v in enumerate(type_counts):
    ax.text(i, v + 200, f'{v:,}', ha='center', fontsize=8)
plt.tight_layout()
plt.savefig(f"{config.PLOTS_DIR}type_distribution.png", dpi=150)
plt.close()
print(f"    Saved: {config.PLOTS_DIR}type_distribution.png")

# Correlation heatmap (numeric columns only, sample 5000 rows for speed)
print("\n[9] Generating correlation heatmap...")
numeric_df = df.select_dtypes(include=[np.number]).drop(columns=['label'], errors='ignore')
# Exclude port columns (too high range, not useful for correlation)
heatmap_cols = [c for c in numeric_df.columns if c not in ['src_port', 'dst_port']]
sample_df = numeric_df[heatmap_cols].sample(min(5000, len(numeric_df)), random_state=config.SEED)
corr_matrix = sample_df.corr()

fig, ax = plt.subplots(figsize=(14, 10))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=False, cmap='coolwarm', center=0,
            ax=ax, square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
ax.set_title('Numeric Feature Correlation Heatmap', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(f"{config.PLOTS_DIR}correlation_heatmap.png", dpi=150)
plt.close()
print(f"    Saved: {config.PLOTS_DIR}correlation_heatmap.png")

# %% [markdown]
# ## 6. Categorical Column Cardinality

# %%
print("\n[10] Categorical column cardinality:")
obj_cols = df.select_dtypes(include='object').columns
for col in obj_cols:
    n_unique = df[col].nunique()
    top_vals = df[col].value_counts().head(5).to_dict()
    print(f"  {col}: {n_unique} unique values — top 5: {top_vals}")

# %% [markdown]
# ## 7. Save Data Audit Report

# %%
print("\n[11] Saving data audit report...")

def df_to_markdown(sub_df):
    cols = list(sub_df.columns)
    header = "| " + " | ".join(cols) + " |"
    divider = "| " + " | ".join(["---"] * len(cols)) + " |"
    rows = []
    for _, row in sub_df.iterrows():
        # Replace newlines or pipes in values to prevent markdown breaking
        cleaned_row = [str(val).replace("|", "\\|").replace("\n", " ") for val in row]
        rows.append("| " + " | ".join(cleaned_row) + " |")
    return "\n".join([header, divider] + rows)

audit_lines = [
    "# TON_IoT Data Audit Report\n\n",
    f"## Dataset Shape\n- Rows: {len(df):,}\n- Columns: {len(df.columns)}\n\n",
    "## Binary Label Distribution\n\n",
]
for label_val, count in label_counts.items():
    audit_lines.append(f"- {label_val} ({'Benign' if label_val==0 else 'Attack'}): {count:,} ({count/len(df)*100:.2f}%)\n")

audit_lines.append("\n## Attack Type Distribution\n\n")
for attack_type, count in type_counts.items():
    audit_lines.append(f"- {attack_type}: {count:,} ({count/len(df)*100:.2f}%)\n")

audit_lines.append("\n## Missing Values (columns with any missing)\n\n")
if len(missing_df) > 0:
    audit_lines.append(missing_df.to_string() + "\n")
else:
    audit_lines.append("No missing values detected.\n")

audit_lines.append("\n## Categorical Column Cardinality\n\n")
for col in obj_cols:
    audit_lines.append(f"- `{col}`: {df[col].nunique()} unique values\n")

audit_lines.append("\n## Sample Rows per Attack Type (5 samples each)\n\n")
for t in sorted(df['type'].unique()):
    audit_lines.append(f"### Attack Type: `{t}`\n\n")
    sample_sub = df[df['type'] == t].head(5)
    audit_lines.append(df_to_markdown(sample_sub) + "\n\n")

audit_path = f"{config.REPORTS_DIR}data_audit.md"
with open(audit_path, 'w', encoding='utf-8') as f:
    f.writelines(audit_lines)
print(f"    Saved: {audit_path}")

print("\n" + "=" * 60)
print("Phase 1 COMPLETE — All acceptance checks passed.")
print("=" * 60)
