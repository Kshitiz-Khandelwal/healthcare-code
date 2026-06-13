#!/usr/bin/env python
"""
Test script to verify dashboard dependencies and data
"""
import sys
import traceback

def test_imports():
    """Test all required imports"""
    print("=" * 60)
    print("Testing imports...")
    print("=" * 60)
    
    imports = [
        "time",
        "pandas",
        "streamlit",
        "plotly.graph_objects",
        "plotly.express",
        "pathlib"
    ]
    
    for imp in imports:
        try:
            __import__(imp)
            print(f"✓ {imp}")
        except ImportError as e:
            print(f"✗ {imp}: {e}")
            return False
    return True

def test_data():
    """Test data loading"""
    print("\n" + "=" * 60)
    print("Testing data loading...")
    print("=" * 60)
    
    try:
        import pandas as pd
        from pathlib import Path
        
        CSV_PATH = Path(__file__).resolve().parent / "predictions.csv"
        p = Path(CSV_PATH)
        
        if not p.exists():
            print(f"✗ File not found: {CSV_PATH}")
            return False
        
        df = pd.read_csv(p)
        print(f"✓ File exists: {CSV_PATH}")
        print(f"✓ Loaded {len(df)} records")
        print(f"✓ Columns: {df.columns.tolist()}")
        
        # Check for required columns
        required_cols = ['patient', 'prediction', 'confidence', 'risk', 'heart_rate', 'hrv', 'explanation']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            print(f"✗ Missing columns: {missing}")
            return False
        print(f"✓ All required columns present")
        
        # Check for nulls
        nulls = df.isnull().sum()
        if nulls.any():
            print(f"⚠ Found null values:\n{nulls[nulls > 0]}")
        else:
            print(f"✓ No null values")
        
        # Check data types
        print(f"✓ Data types check:")
        for col in df.columns:
            print(f"  {col}: {df[col].dtype}")
        
        return True
        
    except Exception as e:
        print(f"✗ Data loading failed: {e}")
        traceback.print_exc()
        return False

def test_dashboard_logic():
    """Test dashboard calculation logic"""
    print("\n" + "=" * 60)
    print("Testing dashboard logic...")
    print("=" * 60)
    
    try:
        import pandas as pd
        from pathlib import Path
        
        CSV_PATH = Path(__file__).resolve().parent / "predictions.csv"
        df = pd.read_csv(CSV_PATH)
        
        # Test metrics
        total = len(df)
        high_n = (df["risk"] == "HIGH").sum()
        medium_n = (df["risk"] == "MEDIUM").sum()
        low_n = (df["risk"] == "LOW").sum()
        arr_pct = round(100 * (df["prediction"] == "Arrhythmia").sum() / total, 1)
        avg_hr = round(df["heart_rate"].mean(), 1)
        avg_hrv = round(df["hrv"].mean(), 2)
        avg_conf = round(df["confidence"].mean(), 1)
        
        print(f"✓ Metrics calculation:")
        print(f"  Total: {total}")
        print(f"  Risk breakdown: HIGH={high_n}, MEDIUM={medium_n}, LOW={low_n}")
        print(f"  Arrhythmia %: {arr_pct}%")
        print(f"  Avg HR: {avg_hr} BPM")
        print(f"  Avg HRV: {avg_hrv} ms")
        print(f"  Avg Confidence: {avg_conf}%")
        
        # Test charts
        pred_vc = df["prediction"].value_counts()
        print(f"✓ Prediction distribution: {pred_vc.to_dict()}")
        
        risk_vc = df["risk"].value_counts().reindex(["HIGH", "MEDIUM", "LOW"], fill_value=0)
        print(f"✓ Risk distribution: {risk_vc.to_dict()}")
        
        # Test explanations
        explained = df[df["explanation"] != "Low risk -- no detailed explanation required."]
        print(f"✓ Detailed explanations: {len(explained)} records")
        
        return True
        
    except Exception as e:
        print(f"✗ Dashboard logic failed: {e}")
        traceback.print_exc()
        return False

def test_plotly():
    """Test plotly charts"""
    print("\n" + "=" * 60)
    print("Testing Plotly charts...")
    print("=" * 60)
    try:
        import pandas as pd
        import plotly.graph_objects as go
        import plotly.express as px
        from pathlib import Path
        
        CSV_PATH = Path(__file__).resolve().parent / "predictions.csv"
        df = pd.read_csv(CSV_PATH)
        
        # Test donut chart
        pred_vc = df["prediction"].value_counts()
        fig_donut = go.Figure(go.Pie(
            labels=pred_vc.index.tolist(),
            values=pred_vc.values.tolist(),
            hole=0.65
        ))
        print(f"✓ Donut chart creation")
        
        # Test scatter
        fig_scatter = px.scatter(
            df, x="heart_rate", y="hrv",
            color="risk"
        )
        print(f"✓ Scatter chart creation")
        
        # Test bar
        risk_vc = df["risk"].value_counts().reindex(["HIGH", "MEDIUM", "LOW"], fill_value=0)
        fig_risk = go.Figure(go.Bar(
            x=risk_vc.index.tolist(),
            y=risk_vc.values.tolist()
        ))
        print(f"✓ Bar chart creation")
        
        return True
        
    except Exception as e:
        print(f"✗ Plotly charts failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    all_pass = True
    
    all_pass &= test_imports()
    all_pass &= test_data()
    all_pass &= test_dashboard_logic()
    all_pass &= test_plotly()
    
    print("\n" + "=" * 60)
    if all_pass:
        print("✓ ALL TESTS PASSED - Dashboard should work!")
    else:
        print("✗ SOME TESTS FAILED - See above for details")
    print("=" * 60)
    
    sys.exit(0 if all_pass else 1)
