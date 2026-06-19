"""
src/data_loader.py
Loads the TON_IoT CSV dataset with optional row-count sampling.
"""
import random
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import config


def load_raw_data(data_path: str = None, max_rows: int | None = None) -> pd.DataFrame:
    """
    Load the TON_IoT CSV dataset.

    Parameters
    ----------
    data_path : str, optional
        Path to train_test_network.csv. Defaults to config.DATA_PATH.
    max_rows : int or None, optional
        If not None, returns a stratified sample of this many rows.
        Stratified on the 'type' column. Defaults to config.MAX_ROWS.

    Returns
    -------
    pd.DataFrame
        Raw loaded dataset.
    """
    if data_path is None:
        data_path = config.DATA_PATH
    if max_rows is None:
        max_rows = config.MAX_ROWS

    print(f"[data_loader] Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"[data_loader] Loaded shape: {df.shape}")

    if max_rows is not None and len(df) > max_rows:
        print(f"[data_loader] Sampling to MAX_ROWS={max_rows} (stratified on 'type')")
        # Stratified sample on type to preserve class ratios
        from sklearn.model_selection import train_test_split
        _, df = train_test_split(
            df,
            test_size=max_rows / len(df),
            stratify=df['type'],
            random_state=config.SEED
        )
        df = df.reset_index(drop=True)
        print(f"[data_loader] Sampled shape: {df.shape}")

    return df
