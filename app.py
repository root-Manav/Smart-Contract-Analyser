import streamlit as st
import joblib
import shap
import pandas as pd
import subprocess
import json
import os
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════
SOLC_PATH = r"C:\Users\manav\Desktop\smc\solc_bins\solc-0.8.0.exe"

FEATURES = [
    "high_sev_count",
    "medium_sev_count",
    "low_sev_count",
    "reentrancy_flag",
    "external_calls",
    "access_control",
    "unchecked_calls",
    "total_detectors",
]

FIX_MAP = {
    "reentrancy_flag":  "Use **checks-effects-interactions** pattern. Always update state before external calls. Use OpenZeppelin `ReentrancyGuard`.",
    "external_calls":   "Validate return value of every `.call()`. Use `require(success)` after each call.",
    "access_control":   "Add `onlyOwner` modifier. Use OpenZeppelin `Ownable` to protect sensitive functions.",
    "unchecked_calls":  "Never ignore return values of low-level calls. Use `require(success, 'Failed')`.",
    "high_sev_count":   "HIGH severity issues found — manual review required before any deployment.",
    "medium_sev_count": "MEDIUM severity issues found — review carefully, may be exploitable.",
}

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Smart Contract Analyzer",
    page_icon="🛡️",
    layout="wide",
)

# ══════════════════════════════════════════════════════════════
# LOAD MODELS
# ══════════════════════════════════════════════════════════════
@st.cache_resource
def load_models():
    try:
        rf       = joblib.load("models/random_forest.pkl")
        scaler   = joblib.load("models/scaler.pkl")
        features = joblib.load("models/features.pkl")
        return rf, scaler, features
    except Exception as e:
        st.error(f"Could not load models: {e}")
        st.info("Run `python train_model.py` first.")
        st.stop()

rf, scaler, FEAT_NAMES = load_models()

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def normalize_pragma(source):
    """Rewrite any pragma version to 0.8.0 so solc always works."""
    return re.sub(
        r"pragma\s+solidity\s+[^;]+;",
        "pragma solidity ^0.8.0;",
        source,
    )

def run_slither(file_path, source_code):
    """
    Save contract, normalize pragma, run Slither,
    return parsed JSON or None.
    """
    # Write normalized source
    fixed = normalize_pragma(source_code)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(fixed)

    out_json = file_path + ".result.json"

    try:
        result = subprocess.run(
            [
                "slither", file_path,
                "--json", out_json,
                "--solc", SOLC_PATH,
                "--disable-color",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        stderr = result.stderr.strip()
        stdout = result.stdout.strip()

        # Store for debug panel
        st.session_state["stderr"] = stderr
        st.session_state["stdout"] = stdout

        # Read output file
        if os.path.exists(out_json):
            with open(out_json, "r", encoding="utf-8") as f:
                content = f.read().strip()
            os.remove(out_json)
            if content:
                try:
                    return json.loads(content)
                except:
                    pass

        # Fallback: stdout
        start = stdout.find("{")
        if start != -1:
            try:
                return json.loads(stdout[start:])
            except:
                pass

    except subprocess.TimeoutExpired:
        st.error("Slither timed out (>120s).")
    except FileNotFoundError:
        st.error("Slither not found. Make sure venv is active.")
    except Exception as e:
        st.error(f"Slither error: {e}")

    return None

def extract_features(slither_output):
    f = {k: 0 for k in FEATURES}

    if not slither_output:
        return f

    detectors = []
    if "results" in slither_output:
        detectors = slither_output["results"].get("detectors", [])
    elif "detectors" in slither_output:
        detectors = slither_output["detectors"]

    f["total_detectors"] = len(detectors)

    for d in detectors:
        impact = d.get("impact", "").lower()
        check  = d.get("check",  "").lower()

        if impact == "high":                          f["high_sev_count"]   += 1
        elif impact == "medium":                      f["medium_sev_count"] += 1
        elif impact in ("low", "informational"):      f["low_sev_count"]    += 1

        if "reentrancy" in check:                     f["reentrancy_flag"]   = 1
        if "external" in check or "call" in check:   f["external_calls"]   += 1
        if "access" in check or "owner" in check:    f["access_control"]   += 1
        if "unchecked" in check:                      f["unchecked_calls"]  += 1

    return f

def get_shap_values(explainer, X):
    raw = explainer.shap_values(X)
    if isinstance(raw, list):
        sv = np.array(raw[1]).flatten()
    elif isinstance(raw, np.ndarray):
        if raw.ndim == 3:    sv = raw[0, :, 1]
        elif raw.ndim == 2:  sv = raw[0]
        else:                sv = raw.flatten()
    else:
        sv = np.array(raw).flatten()
    return [float(v) for v in sv]

def risk_label(score):
    if score < 34:  return "🟢 LOW RISK",    "success"
    if score < 67:  return "🟡 MEDIUM RISK", "warning"
    return               "🔴 HIGH RISK",    "error"

# ══════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════
st.title("🛡️ Smart Contract Security Analyzer")
st.caption("Upload a Solidity `.sol` file for an instant AI-powered vulnerability report.")
st.divider()

# Solc check
if not os.path.exists(SOLC_PATH):
    st.error(f"solc not found at `{SOLC_PATH}`")
    st.info("Run `venv\\Scripts\\python.exe download_solc.py` to download it.")
    st.stop()

uploaded = st.file_uploader("Upload your `.sol` file", type=["sol"])

if uploaded:

    # ── Save to project upload folder ─────────────────────────
    upload_dir = os.path.join(os.getcwd(), "uploaded_contracts")
    os.makedirs(upload_dir, exist_ok=True)
    save_path   = os.path.join(upload_dir, uploaded.name)
    source_code = uploaded.getvalue().decode("utf-8", errors="ignore")

    # ── Run analysis ───────────────────────────────────────────
    with st.spinner("Running Slither analysis..."):
        slither_out = run_slither(save_path, source_code)
        features    = extract_features(slither_out)

    # ── Predict ────────────────────────────────────────────────
    X     = pd.DataFrame([features])[FEAT_NAMES]
    prob  = rf.predict_proba(X)[0][1]
    score = round(prob * 100, 1)
    label, level = risk_label(score)

    # ── Score row ──────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("Risk Score", f"{score} / 100")
    with c2:
        if level == "success":   st.success(label)
        elif level == "warning": st.warning(label)
        else:                    st.error(label)
    c3.metric("High severity findings", features["high_sev_count"])

    st.divider()

    # ── Two columns ────────────────────────────────────────────
    left, right = st.columns(2)

    with left:
        st.subheader("Detected features")
        feat_df = pd.DataFrame(
            list(features.items()),
            columns=["Feature", "Value"]
        )
        st.dataframe(feat_df, use_container_width=True)

    with right:
        st.subheader("What is driving the risk?")
        try:
            explainer = shap.TreeExplainer(rf)
            sv        = get_shap_values(explainer, X)

            shap_df = pd.DataFrame({
                "Feature":    FEAT_NAMES,
                "SHAP value": sv,
            })
            shap_df["abs"] = shap_df["SHAP value"].abs()
            shap_df = shap_df.sort_values("abs", ascending=True).drop("abs", axis=1)

            fig, ax = plt.subplots(figsize=(6, 4))
            colors  = ["#ef4444" if v > 0 else "#22c55e"
                       for v in shap_df["SHAP value"]]
            ax.barh(shap_df["Feature"], shap_df["SHAP value"], color=colors)
            ax.axvline(0, color="gray", linewidth=0.8)
            ax.set_xlabel("Impact  (red = raises risk, green = lowers risk)")
            ax.set_facecolor("#0e1117")
            fig.patch.set_facecolor("#0e1117")
            ax.tick_params(colors="white")
            ax.xaxis.label.set_color("white")
            st.pyplot(fig)
            plt.close(fig)

        except Exception as e:
            st.warning(f"SHAP chart unavailable: {e}")

    st.divider()

    # ── Fix recommendations ────────────────────────────────────
    st.subheader("🔧 Recommended fixes")
    triggered = [
        k for k, v in features.items()
        if v and int(v) > 0 and k in FIX_MAP
    ]
    if triggered:
        for k in triggered:
            st.warning(f"**{k}** — {FIX_MAP[k]}")
    else:
        st.success(
            "No vulnerability triggers detected. "
            "Contract appears clean — always do a final manual review before deployment."
        )

    st.divider()

    # ── Raw Slither findings ───────────────────────────────────
    st.subheader("📋 Raw Slither findings")
    detectors = []
    if slither_out:
        if "results" in slither_out:
            detectors = slither_out["results"].get("detectors", [])
        elif "detectors" in slither_out:
            detectors = slither_out["detectors"]

    if detectors:
        rows = []
        for d in detectors:
            rows.append({
                "Check":       d.get("check", ""),
                "Impact":      d.get("impact", ""),
                "Confidence":  d.get("confidence", ""),
                "Description": d.get("description", "")[:200],
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("No Slither findings for this contract.")

    # ── Debug panel ────────────────────────────────────────────
    with st.expander("🔍 Debug info"):
        st.write(f"**solc path:** `{SOLC_PATH}`")
        st.write(f"**solc exists:** `{os.path.exists(SOLC_PATH)}`")
        st.write(f"**saved to:** `{save_path}`")
        stderr = st.session_state.get("stderr", "")
        stdout = st.session_state.get("stdout", "")
        if slither_out:
            st.success("Slither returned valid JSON")
        else:
            st.error("Slither returned no JSON")
        if stderr:
            st.text_area("stderr", stderr, height=150)
        if stdout:
            st.text_area("stdout", stdout, height=100)

    # ── Cleanup ────────────────────────────────────────────────
    try:
        os.remove(save_path)
    except:
        pass