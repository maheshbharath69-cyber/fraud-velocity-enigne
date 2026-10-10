import streamlit as st
import pandas as pd
import time
from Engine import TransactionStreamSimulator, VelocityFeatureEngine, FraudRiskEvaluator

st.set_page_config(page_title="Fintech Fraud Engine PoC", layout="wide")

st.title("🛡️ Real-Time Transaction Fraud & Velocity Engine")
st.markdown("Designed for low-latency payment API monitoring & anomaly detection")


# Initialize Engine Components
@st.cache_resource
def load_engine():
    return TransactionStreamSimulator(), VelocityFeatureEngine(), FraudRiskEvaluator()


simulator, feature_engine, risk_evaluator = load_engine()

# Sidebar Controls
st.sidebar.header("Stream Controls")
run_stream = st.sidebar.checkbox("Start Live Stream", value=False)
trigger_fraud = st.sidebar.button("🚨 Simulate Fraud Attack")

# Metrics Overview
col1, col2, col3 = st.columns(3)
metric_total = col1.empty()
metric_blocked = col2.empty()
metric_avg_latency = col3.empty()

# Table Placeholder
table_placeholder = st.empty()

if 'history' not in st.session_state:
    st.session_state.history = []

if run_stream or trigger_fraud:
    event = simulator.generate_event(force_fraud=trigger_fraud)
    features = feature_engine.update_and_extract_features(event)
    result = risk_evaluator.evaluate_risk(event, features)

    st.session_state.history.insert(0, result)
    if len(st.session_state.history) > 20:
        st.session_state.history.pop()

df = pd.DataFrame(st.session_state.history)

if not df.empty:
    total_txns = len(df)
    blocked_txns = len(df[df['decision'] == 'REJECT'])
    avg_latency = round(df['latency_ms'].mean(), 2)

    metric_total.metric("Total Events Analyzed", total_txns)
    metric_blocked.metric("Fraud Attacks Blocked", blocked_txns)
    metric_avg_latency.metric("Pipeline Latency", f"{avg_latency} ms")

    st.subheader("Live Transaction Stream Log")
    st.dataframe(df, use_container_width=True)

if run_stream:
    time.sleep(1)
    st.rerun()
