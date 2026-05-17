import joblib
import shap
import pandas as pd
import subprocess
import json
import sys
import numpy as np

# ── Load saved models ──────────────────────────────────────────
rf       = joblib.load("models/random_forest.pkl")
scaler   = joblib.load("models/scaler.pkl")
FEATURES = joblib.load("models/features.pkl")

def run_slither(path):
    try:
        r = subprocess.run(
            ["slither", path, "--json", "-"],
            capture_output=True, text=True, timeout=60
        )
        if r.stdout:
            return json.loads(r.stdout)
    except:
        pass
    return None

def extract_features(slither_output):
    f = {k: 0 for k in FEATURES}
    if not slither_output or "results" not in slither_output:
        return f
    for d in slither_output["results"].get("detectors", []):
        impact = d.get("impact", "").lower()
        check  = d.get("check",  "").lower()
        if impact == "high":                          f["high_sev_count"]   += 1
        if impact == "medium":                        f["medium_sev_count"] += 1
        if impact in ("low", "informational"):        f["low_sev_count"]    += 1
        if "reentrancy" in check:                     f["reentrancy_flag"]   = 1
        if "external" in check or "call" in check:   f["external_calls"]   += 1
        if "access" in check:                         f["access_control"]   += 1
        if "unchecked" in check:                      f["unchecked_calls"]  += 1
        f["total_detectors"] += 1
    return f

def get_risk_label(score):
    if score < 34: return "LOW RISK"
    if score < 67: return "MEDIUM RISK"
    return "HIGH RISK"

def get_shap_values(explainer, X):
    """Safely extract per-feature SHAP values for class 1 (vulnerable)."""
    raw = explainer.shap_values(X)

    # Case 1: list of arrays — one per class (most common with RandomForest)
    if isinstance(raw, list):
        sv = np.array(raw[1]).flatten()

    # Case 2: single 3D array — shape (n_samples, n_features, n_classes)
    elif isinstance(raw, np.ndarray) and raw.ndim == 3:
        sv = raw[0, :, 1]

    # Case 3: single 2D array — shape (n_samples, n_features)
    elif isinstance(raw, np.ndarray) and raw.ndim == 2:
        sv = raw[0]

    # Case 4: already flat 1D
    else:
        sv = np.array(raw).flatten()

    return sv

def analyse(contract_path):
    print(f"\nAnalysing: {contract_path}")
    print("-" * 50)

    output   = run_slither(contract_path)
    features = extract_features(output)

    X = pd.DataFrame([features])[FEATURES]

    prob  = rf.predict_proba(X)[0][1]
    score = round(prob * 100, 1)
    label = get_risk_label(score)

    print(f"\n  Risk Score : {score} / 100")
    print(f"  Assessment : {label}")
    print(f"\n  Raw features detected:")
    for k, v in features.items():
        if v:
            print(f"    {k:<22} {v}")

    # ── SHAP ──────────────────────────────────────────────────
    try:
        explainer = shap.TreeExplainer(rf)
        sv        = get_shap_values(explainer, X)

        print("\n  Top factors driving this score:")
        # Sort by absolute impact, convert each value to plain float
        impacts = sorted(
            [(feat, float(val)) for feat, val in zip(FEATURES, sv)],
            key=lambda x: -abs(x[1])
        )
        for feat, val in impacts[:5]:
            if abs(val) < 0.001:
                continue
            direction = "increases risk" if val > 0 else "decreases risk"
            bar = ("+" if val > 0 else "-") * min(int(abs(val) * 30), 20)
            print(f"    {feat:<22} {bar:<22} ({val:+.4f})")

    except Exception as e:
        print(f"\n  SHAP explanation unavailable: {e}")
        print("  (Risk score above is still valid)")

    print("\n" + "=" * 50)
    return score, features

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        # Default: try to find any contract automatically
        import os
        for folder in ["contracts/vulnerable", "contracts/secure"]:
            if os.path.exists(folder):
                files = [f for f in os.listdir(folder) if f.endswith(".sol")]
                if files:
                    path = os.path.join(folder, files[0])
                    print(f"No path given — using: {path}")
                    break
        else:
            print("Usage: python predict.py path\\to\\contract.sol")
            sys.exit(1)

    analyse(path)