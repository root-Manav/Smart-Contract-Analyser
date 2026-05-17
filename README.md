# 🛡️ AI-Driven Smart Contract Vulnerability Detection System

> An automated pre-auditing tool that combines static analysis and machine learning to detect vulnerabilities in Solidity smart contracts — generating an explainable risk score with actionable fix recommendations.

---

## 📌 Project Overview

Smart contracts deployed on blockchain networks are immutable — once live, they cannot be patched. A single vulnerability can lead to catastrophic and irreversible financial loss. This project addresses that problem by providing an automated, intelligent pre-deployment security analysis tool that any developer can use without expert knowledge.

The system analyzes uploaded `.sol` files using **Slither** (static analysis), extracts semantic vulnerability features, feeds them into a **Random Forest classifier**, and generates a **risk score from 0 to 100** with **SHAP-powered explanations** showing exactly what is driving the risk.

---

## 🎯 Key Features

- **Upload any Solidity `.sol` file** and receive an instant security report
- **Risk score (0–100)** with severity label: Low / Medium / High
- **SHAP explainability chart** showing which vulnerability features are driving the score
- **Recommended fixes** per detected vulnerability type
- **Raw Slither findings table** with check name, impact, confidence, and description
- **Fully local** — no data leaves your machine

---

## 🏗️ System Architecture

```
Raw .sol file
      ↓
Pragma normalization (→ ^0.8.0)
      ↓
Slither static analysis
(control flow graph + taint analysis)
      ↓
JSON output parsed
      ↓
8 numerical features extracted
      ↓
Random Forest Classifier (300 trees)
      ↓
Risk Score + SHAP Explanation
      ↓
Streamlit UI Report
```

---

## 🔍 Vulnerability Categories Detected

| Category | Examples |
|---|---|
| Reentrancy | State updated after external `.call()` |
| Access Control | Missing `onlyOwner` or unprotected setters |
| Unchecked Calls | `.call()` return value not verified |
| Mixed | Combinations of the above |

---

## 🤖 ML Model Details

| Property | Detail |
|---|---|
| Primary Model | Random Forest Classifier |
| Baseline Model | Logistic Regression |
| Features | 8 semantic features from Slither output |
| Train/Test Split | 80% / 20% stratified |
| Class Weighting | Balanced (handles class imbalance) |
| Explainability | SHAP (SHapley Additive exPlanations) |
| Risk Score | `predict_proba(vulnerable) × 100` |

---

## 📊 Feature Set

| Feature | Description |
|---|---|
| `high_sev_count` | Number of HIGH impact Slither findings |
| `medium_sev_count` | Number of MEDIUM impact findings |
| `low_sev_count` | Number of LOW / Informational findings |
| `reentrancy_flag` | 1 if any reentrancy pattern detected |
| `external_calls` | Count of external call findings |
| `access_control` | Count of access control findings |
| `unchecked_calls` | Count of unchecked low-level call findings |
| `total_detectors` | Total number of Slither findings |

---

## 🗂️ Project Structure

```
smart_contract_analyzer/
│
├── contracts/
│   ├── vulnerable/          ← Training contracts (label = 1)
│   └── secure/              ← Training contracts (label = 0)
│
├── data/
│   └── features.csv         ← Extracted features dataset
│
├── models/
│   ├── random_forest.pkl    ← Trained RF model
│   ├── logistic_regression.pkl
│   ├── scaler.pkl
│   └── features.pkl
│
├── solc_bins/
│   └── solc-0.8.0.exe       ← Solidity compiler binary
│
├── uploaded_contracts/      ← Temp folder for UI uploads
│
├── make_contracts.py        ← Generates training contracts
├── extract_features.py      ← Runs Slither + builds features.csv
├── train_model.py           ← Trains and evaluates ML models
├── app.py                   ← Streamlit web interface
└── README.md
```

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.10 or higher
- Windows (tested on Windows 10/11)
- VS Code (recommended)

### Step 1 — Clone the repository

```bash
git clone https://github.com/yourusername/smart-contract-analyzer.git
cd smart-contract-analyzer
```

### Step 2 — Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install dependencies

```bash
pip install streamlit scikit-learn pandas numpy matplotlib seaborn slither-analyzer shap joblib
```

### Step 4 — Download Solidity compiler

Download `solc-0.8.0` for Windows from the official release page:

🔗 [https://binaries.soliditylang.org/windows-amd64/](https://binaries.soliditylang.org/windows-amd64/)

Place it at: `solc_bins\solc-0.8.0.exe`

### Step 5 — Generate training contracts

```bash
python make_contracts.py
```

### Step 6 — Extract features

```bash
python extract_features.py
```

### Step 7 — Train the model

```bash
python train_model.py
```

### Step 8 — Launch the app

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 🚀 Usage

1. Launch the app with `streamlit run app.py`
2. Click **Browse files** and upload any `.sol` Solidity contract
3. Wait for Slither to complete analysis (~5–30 seconds)
4. Review your results:
   - Risk Score and severity label
   - Detected features table
   - SHAP chart showing what drove the score
   - Recommended fixes for each vulnerability
   - Raw Slither findings table

---

## 📚 References

1. Wenhua, Z. et al. *Blockchain Technology: Security Issues, Healthcare Applications, Challenges and Future Trends.* Electronics 2023, 12, 546. https://doi.org/10.3390/electronics12030546
2. Feist, J., Grieco, G., & Groce, A. *Slither: A Static Analysis Framework for Smart Contracts.* Trail of Bits, 2019.
3. Ethereum Foundation. *Smart Contract Security Best Practices.* https://ethereum.org/en/developers/docs/smart-contracts/security
4. Lundberg, S. & Lee, S. *A Unified Approach to Interpreting Model Predictions (SHAP).* NeurIPS 2017.
5. SmartBugs: A Framework to Analyse Solidity Smart Contracts. https://github.com/smartbugs/smartbugs

---


## 👨‍💻 Author

**Manav**
3rd Year Cyber Security Student
Design Project — AI-Driven Smart Contract Vulnerability Detection

---


