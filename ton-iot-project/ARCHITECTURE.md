# Architecture

## System Layout

```
Raw CSV → Feature Engineering → Binary/Multi-class Training → Prediction → Dashboard
```

## Component Map

| Component | File | Purpose |
|---|---|---|
| Config | `config.py` | All configuration values |
| Data Loader | `src/data_loader.py` | Load CSV, apply MAX_ROWS sampling |
| Feature Engineering | `src/feature_engineering.py` | Drop, impute, encode, transform, derive |
| Preprocessing | `src/preprocessing.py` | StandardScaler fit/transform wrappers |
| Model Training | `src/train_model.py` | Cross-validation, evaluation, model saving |
| Predictor | `src/predictor.py` | Load artifacts, run inference on new data |
| Validation | `scripts/validate_all.py` | Check all artifacts exist and hash integrity |
| Tests | `tests/test_predictor.py` | Integration tests for predictor |

## src/ Module API Signatures

### data_loader.py
```python
def load_raw_data(data_path: str, max_rows: int | None = None) -> pd.DataFrame: ...
```

### feature_engineering.py
```python
def engineer_features(df: pd.DataFrame, fit: bool = True,
                       label_encoders: dict | None = None,
                       scaler=None) -> tuple[pd.DataFrame, dict, scaler]: ...
```

### preprocessing.py
```python
def fit_scaler(X_train: pd.DataFrame) -> StandardScaler: ...
def transform(X: pd.DataFrame, scaler: StandardScaler) -> np.ndarray: ...
```

### train_model.py
```python
def run_cv_evaluation(model, X_train, y_train, cv, scoring: str) -> dict: ...
def evaluate_on_test(model, X_test, y_test, task: str) -> dict: ...
def save_model(model, path: str) -> None: ...
def save_metadata(metadata: dict, path: str) -> None: ...
```

### predictor.py
```python
def load_artifacts(models_dir: str) -> dict: ...
def predict_binary(features: pd.DataFrame, artifacts: dict) -> dict: ...
def predict_multiclass(features: pd.DataFrame, artifacts: dict) -> dict: ...
```

## Artifact Naming Convention

All model artifacts are versioned with model name:
- `best_binary_model.pkl` — final binary RandomForestClassifier
- `binary_model_metadata.json` — binary model provenance + metrics + feature hash
- `best_multiclass_model.pkl` — final multi-class RandomForestClassifier
- `multiclass_model_metadata.json` — multi-class model provenance + metrics + feature hash
- `feature_list.pkl` — exact ordered feature column list
- `label_encoders.pkl` — dict of fitted LabelEncoder objects
- `scaler.pkl` — fitted StandardScaler
- `feature_metadata.json` — feature count, encoding summary, hash
