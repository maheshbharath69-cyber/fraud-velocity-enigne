# 🛡️ Real-Time Transaction Fraud & Velocity Engine

A lightweight, low-latency data engineering Proof of Concept (PoC) designed to simulate high-frequency payment event streaming, in-memory sliding window feature extraction, and hybrid fraud detection (Deterministic Rules + Unsupervised Machine Learning).

Built specifically to solve common fintech data pipeline bottlenecks: **database latency spikes** during historical event lookups and **high false-positive rates** caused by rigid static thresholds.

---

## 🏗️ Architecture & Core Problem Solved

In high-volume payment infrastructure (UPI, Neo-banking, Cards), traditional transaction monitoring architectures face two major challenges:
1. **DB Latency Bottlenecks:** Executing heavy SQL window/group-by queries on relational databases to check user transaction history adds **150ms–300ms** of latency to payment APIs.
2. **False Positive Fatigue:** Blocking legitimate high-value customers purely on static thresholds (e.g., *"flag everything over ₹25,000"*) causes friction and customer churn.

### **Our Solution Design**
* **In-Memory Rolling State Cache (`VelocityFeatureEngine`):** Maintains a fast sliding window state per user to compute velocity metrics in **under 15ms** without hitting relational database tables for every API call.
* **Hybrid Risk Engine (`FraudRiskEvaluator`):** Combines hard deterministic business rules (`HIGH_VELOCITY_BURST`, `GEOLOCATION_JUMP`) with an unsupervised anomaly detection model (`IsolationForest`) to provide both explainability and context.

---

## 📂 Project Structure

```text
fraud-velocity-engine/
│
├── engine.py                # Core data pipeline, stream simulator, rolling cache & ML risk model
├── app.py                   # Interactive Streamlit dashboard UI for live evaluation
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation & architecture overview