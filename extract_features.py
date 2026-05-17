import subprocess
import json
import os
import re
import pandas as pd

SOLC_PATH  = r"C:\Users\manav\Desktop\smc\solc_bins\solc-0.8.0.exe"
CONTRACTS  = "contracts"
OUTPUT_CSV = "data/features.csv"

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

# ── Rewrite any pragma to 0.8.0 before analysis ───────────────
def normalize_pragma(source):
    return re.sub(
        r"pragma\s+solidity\s+[^;]+;",
        "pragma solidity ^0.8.0;",
        source
    )

# ── Run Slither and return parsed JSON ────────────────────────
def run_slither(contract_path):
    out_json = contract_path + ".json"

    # Read and rewrite pragma to 0.8.0
    try:
        with open(contract_path, "r", encoding="utf-8", errors="ignore") as f:
            original = f.read()
        fixed = normalize_pragma(original)
        with open(contract_path, "w", encoding="utf-8") as f:
            f.write(fixed)
    except Exception as e:
        print(f"    Could not rewrite pragma: {e}")

    try:
        result = subprocess.run(
            [
                "slither", contract_path,
                "--json", out_json,
                "--solc", SOLC_PATH,
                "--disable-color",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if os.path.exists(out_json):
            with open(out_json, "r", encoding="utf-8") as f:
                content = f.read().strip()
            os.remove(out_json)
            if content:
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    pass

        # Fallback: find JSON in stdout
        stdout = result.stdout.strip()
        start  = stdout.find("{")
        if start != -1:
            try:
                return json.loads(stdout[start:])
            except:
                pass

    except subprocess.TimeoutExpired:
        print(f"    TIMEOUT")
    except Exception as e:
        print(f"    ERROR: {e}")

    return None

# ── Extract flat features from Slither output ─────────────────
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

# ── Build full dataset ────────────────────────────────────────
def build_dataset():
    rows  = []
    stats = {"ok": 0, "empty": 0, "failed": 0}

    for label_name, label_val in [("vulnerable", 1), ("secure", 0)]:
        folder = os.path.join(CONTRACTS, label_name)
        if not os.path.exists(folder):
            print(f"Folder missing: {folder}")
            continue

        files = [f for f in os.listdir(folder) if f.endswith(".sol")]
        print(f"\n{'='*55}")
        print(f"Processing {len(files)} {label_name} contracts")
        print(f"{'='*55}")

        for fname in files:
            fpath = os.path.join(folder, fname)
            print(f"\n  {fname}")

            output   = run_slither(fpath)
            features = extract_features(output)

            if output is None:
                stats["failed"] += 1
                print(f"    status : FAILED")
            elif features["total_detectors"] == 0:
                stats["empty"] += 1
                print(f"    status : empty (0 detectors)")
            else:
                stats["ok"] += 1
                print(f"    status : OK  ({features['total_detectors']} detectors | "
                      f"high={features['high_sev_count']} "
                      f"re={features['reentrancy_flag']} "
                      f"ext={features['external_calls']})")

            features["label"]    = label_val
            features["filename"] = fname
            rows.append(features)

    return pd.DataFrame(rows), stats

# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Smart Contract Feature Extractor")
    print(f"Using solc : {SOLC_PATH}")
    print(f"Exists     : {os.path.exists(SOLC_PATH)}\n")

    if not os.path.exists(SOLC_PATH):
        print("ERROR: solc-0.8.0.exe not found.")
        print("Run: venv\\Scripts\\python.exe download_solc.py")
        exit(1)

    df, stats = build_dataset()
    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)

    print(f"\n{'='*55}")
    print(f"SUMMARY")
    print(f"{'='*55}")
    print(f"Total contracts    : {len(df)}")
    print(f"With findings      : {stats['ok']}")
    print(f"Empty (no findings): {stats['empty']}")
    print(f"Failed             : {stats['failed']}")
    print(f"\nLabel distribution:")
    print(df["label"].value_counts().to_string())
    print(f"\nFeature sums:")
    print(df[FEATURES].sum().to_string())
    print(f"\nSaved: {OUTPUT_CSV}")