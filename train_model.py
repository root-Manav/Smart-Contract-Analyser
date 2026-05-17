import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

CSV_PATH = "data/features.csv"
MODEL_DIR = "models"

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

# ── Load ──────────────────────────────────────────────────────
print("="*55)
print("Smart Contract ML Trainer")
print("="*55)

df = pd.read_csv(CSV_PATH)
print(f"\nLoaded {len(df)} rows from {CSV_PATH}")
print(f"\nLabel distribution:")
print(df["label"].value_counts().to_string())

X = df[FEATURES]
y = df["label"]

counts = y.value_counts()
print(f"\nClass counts: {dict(counts)}")

# ── Guard: need both classes ──────────────────────────────────
if len(counts) < 2:
    print("\nERROR: Only one class in dataset.")
    print("Make sure both contracts/vulnerable/ and contracts/secure/ have .sol files.")
    exit(1)

# ── Train / test split ────────────────────────────────────────
min_count  = counts.min()
stratify   = y if min_count >= 2 else None
test_size  = 0.2 if min_count >= 5 else 0.3

if len(df) < 6:
    print("\nWARNING: Dataset too small. Training on full data.")
    X_train = X_test = X
    y_train = y_test = y
else:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=42,
        stratify=stratify,
    )

print(f"\nTrain samples : {len(X_train)}")
print(f"Test samples  : {len(X_test)}")

# ── Scale ─────────────────────────────────────────────────────
scaler     = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

# ── Random Forest ─────────────────────────────────────────────
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    min_samples_leaf=1,
    random_state=42,
    class_weight="balanced",
)
rf.fit(X_train, y_train)

# ── Logistic Regression ───────────────────────────────────────
lr = LogisticRegression(
    max_iter=1000,
    random_state=42,
    class_weight="balanced",
)
lr.fit(X_train_sc, y_train)

# ── Evaluate ──────────────────────────────────────────────────
print(f"\n{'='*55}")
for name, model, Xt in [
    ("Random Forest",       rf, X_test),
    ("Logistic Regression", lr, X_test_sc),
]:
    preds = model.predict(Xt)
    print(f"\n{name}")
    print("-"*40)
    print(classification_report(
        y_test, preds,
        target_names=["Secure", "Vulnerable"],
        zero_division=0,
    ))
    try:
        proba = model.predict_proba(Xt)[:, 1]
        auc   = roc_auc_score(y_test, proba)
        print(f"ROC-AUC : {auc:.4f}")
    except Exception as e:
        print(f"ROC-AUC : N/A ({e})")

    print(f"\nConfusion Matrix ({name}):")
    cm = confusion_matrix(y_test, preds)
    print(f"  TN={cm[0,0]}  FP={cm[0,1]}")
    print(f"  FN={cm[1,0]}  TP={cm[1,1]}")

# ── Feature importance ────────────────────────────────────────
print(f"\n{'='*55}")
print("Feature Importances (Random Forest)")
print("-"*40)
for feat, imp in sorted(
    zip(FEATURES, rf.feature_importances_),
    key=lambda x: -x[1]
):
    bar = "█" * int(imp * 50)
    print(f"  {feat:<22} {bar} {imp:.4f}")

# ── Save ──────────────────────────────────────────────────────
os.makedirs(MODEL_DIR, exist_ok=True)
joblib.dump(rf,       f"{MODEL_DIR}/random_forest.pkl")
joblib.dump(lr,       f"{MODEL_DIR}/logistic_regression.pkl")
joblib.dump(scaler,   f"{MODEL_DIR}/scaler.pkl")
joblib.dump(FEATURES, f"{MODEL_DIR}/features.pkl")

print(f"\n{'='*55}")
print(f"Models saved to {MODEL_DIR}/")
print("  random_forest.pkl")
print("  logistic_regression.pkl")
print("  scaler.pkl")
print("  features.pkl")
print(f"{'='*55}")
print("\nDone! Run: streamlit run app.py")