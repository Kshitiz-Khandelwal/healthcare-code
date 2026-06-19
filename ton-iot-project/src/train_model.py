"""
src/train_model.py
Model training, cross-validation, evaluation, and artifact saving utilities.
"""
import json
import time
import datetime
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score,
    precision_score, recall_score, classification_report,
    confusion_matrix
)
from sklearn.model_selection import StratifiedKFold, cross_validate
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config


def run_cv_evaluation(model, X_train, y_train, task: str = "binary") -> dict:
    """
    Run stratified k-fold cross-validation.

    Parameters
    ----------
    model : sklearn-compatible estimator
    X_train, y_train : arrays
    task : 'binary' or 'multiclass'

    Returns
    -------
    dict : mean CV scores {'cv_accuracy', 'cv_f1', 'cv_auc'}
    """
    cv = StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=config.SEED)

    if task == "binary":
        scoring = {"accuracy": "accuracy", "f1": "f1", "auc": "roc_auc"}
    else:
        scoring = {"accuracy": "accuracy", "f1_macro": "f1_macro"}

    t0 = time.time()
    cv_results = cross_validate(model, X_train, y_train, cv=cv, scoring=scoring, n_jobs=1)
    runtime = time.time() - t0

    result = {
        "cv_accuracy": cv_results["test_accuracy"].mean(),
        "cv_runtime_seconds": round(runtime, 3),
    }
    if task == "binary":
        result["cv_f1"] = cv_results["test_f1"].mean()
        result["cv_auc"] = cv_results["test_auc"].mean()
    else:
        result["cv_f1_macro"] = cv_results["test_f1_macro"].mean()

    return result


def evaluate_on_test(model, X_test, y_test, task: str = "binary", classes=None) -> dict:
    """
    Evaluate model on the held-out test set.

    Parameters
    ----------
    model : fitted sklearn-compatible estimator
    X_test, y_test : arrays
    task : 'binary' or 'multiclass'
    classes : list, optional — class labels for multi-class

    Returns
    -------
    dict : test metrics
    """
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    result = {
        "test_accuracy": float(accuracy_score(y_test, y_pred)),
        "test_report": classification_report(y_test, y_pred, target_names=classes, output_dict=True),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }

    if task == "binary":
        result["test_f1"] = float(f1_score(y_test, y_pred))
        result["test_precision"] = float(precision_score(y_test, y_pred))
        result["test_recall"] = float(recall_score(y_test, y_pred))
        result["test_auc"] = float(roc_auc_score(y_test, y_proba[:, 1]))
    else:
        result["test_f1_macro"] = float(f1_score(y_test, y_pred, average='macro'))
        result["test_f1_weighted"] = float(f1_score(y_test, y_pred, average='weighted'))
        # Multi-class AUC (one-vs-rest, weighted)
        try:
            result["test_auc"] = float(roc_auc_score(
                y_test, y_proba, multi_class='ovr', average='weighted'
            ))
        except Exception:
            result["test_auc"] = None

    return result


def save_model(model, path: str) -> None:
    """Save a sklearn-compatible model to disk with joblib."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    print(f"[train_model] Model saved: {path}")


def save_metadata(metadata: dict, path: str) -> None:
    """Save a metadata dict as JSON."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    print(f"[train_model] Metadata saved: {path}")


def build_metadata(model_name: str, task: str, dataset_size: int,
                   feature_count: int, feature_hash: str,
                   test_metrics: dict, seed: int = 42) -> dict:
    """Build a standardized metadata dict for a trained model."""
    return {
        "timestamp_utc": datetime.datetime.utcnow().isoformat(),
        "model_name": model_name,
        "task": task,
        "seed": seed,
        "dataset_size": dataset_size,
        "feature_count": feature_count,
        "feature_hash": feature_hash,
        "test_accuracy": test_metrics.get("test_accuracy"),
        "test_f1": test_metrics.get("test_f1") or test_metrics.get("test_f1_macro"),
        "test_auc": test_metrics.get("test_auc"),
        "split_method": "stratified_train_test_split_80_20",
    }
