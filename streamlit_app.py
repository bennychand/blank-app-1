# exposure_app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json, os
from datetime import datetime

st.set_page_config(page_title="Exposure Analyzer", layout="wide")

# --- Session File ---
SESSIONS_FILE = "chemical_sessions.json"

def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_session(session_id, data):
    sessions = load_sessions()
    sessions[session_id] = data
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f, indent=2)

def delete_session(session_id):
    sessions = load_sessions()
    if session_id in sessions:
        del sessions[session_id]
        with open(SESSIONS_FILE, "w") as f:
            json.dump(sessions, f, indent=2)

# --- Sidebar Navigation ---
st.sidebar.title("🧭 Navigation")
section = st.sidebar.radio("Go to", ["Home", "Chemical Exposure"])

# --- Sidebar Session Controls ---
if section == "Chemical Exposure":
    st.sidebar.header("📂 Saved Sessions")
    sessions = load_sessions()
    session_ids = list(sessions.keys())

    if session_ids:
        selected = st.sidebar.selectbox("Load session", session_ids)
        if st.sidebar.button("Load"):
            data = sessions[selected]
            st.session_state.update({
                "organization": data["organization"],
                "location": data["location"],
                "process": data["process"],
                "exposure_type": data["exposure_type"],
                "limit": data["limit"],
                "df": pd.DataFrame(data["data"]),
                "run_analysis": True
            })
            st.rerun()

        with st.sidebar.expander("🗑️ Delete session"):
            to_delete = st.selectbox("Select session", session_ids, key="delete_select")
            confirm = st.checkbox("Yes, delete this session", key="confirm_delete")
            if st.button("Delete", key="delete_button") and confirm:
                delete_session(to_delete)
                st.success(f"Deleted session: {to_delete}")
                st.rerun()
    else:
        st.sidebar.info("No saved sessions yet.")

# --- Home Page ---
if section == "Home":
    st.title("🧪 Workplace Exposure Analyzer")
    st.markdown("Welcome! Use the sidebar to begin a chemical exposure assessment.")
if section == "Chemical Exposure":
    st.title("🧪 Chemical Exposure Assessment")

    st.subheader("📥 Enter Exposure Data")
    input_method = st.radio("Input method", ["Manual Entry", "Upload CSV"])
    df = pd.DataFrame()

    if input_method == "Manual Entry":
        chem_name = st.text_input("Chemical Name", value="Chemical A")
        values = st.text_area("Exposure Values (comma-separated)", "12, 45, 60, 5, 80")
        try:
            exposure_values = [float(v.strip()) for v in values.split(",") if v.strip()]
            df = pd.DataFrame({"Chemical": [chem_name] * len(exposure_values), "Exposure": exposure_values})
        except:
            st.warning("Please enter valid numeric values.")
    else:
        file = st.file_uploader("Upload CSV", type=["csv"])
        if file:
            df = pd.read_csv(file)
            if "Chemical" not in df.columns or "Exposure" not in df.columns:
                st.error("CSV must contain 'Chemical' and 'Exposure' columns.")

    st.subheader("📝 Assessment Metadata")
    org = st.text_input("Organization", value="Acme Chemicals Ltd.")
    loc = st.text_input("Location", value="Norwich, UK")
    proc = st.text_input("Process", value="Batch Reactor Cleaning")
    etype = st.selectbox("Exposure Type", ["Full-shift", "Short-term", "Instantaneous"])
    limit = st.number_input("Exposure Limit (ppm)", min_value=0.0, value=50.0)

    if not df.empty:
        st.subheader("📊 Preview Data")
        st.dataframe(df, use_container_width=True)

        if st.button("▶️ Run Analysis"):
            session_id = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_session(session_id, {
                "organization": org,
                "location": loc,
                "process": proc,
                "exposure_type": etype,
                "limit": limit,
                "data": df.to_dict(orient="records")
            })
            st.session_state.update({
                "run_analysis": True,
                "df": df,
                "organization": org,
                "location": loc,
                "process": proc,
                "exposure_type": etype,
                "limit": limit
            })
            st.rerun()
    else:
        st.info("Please enter or upload exposure data to continue.")
    # --- Analysis Section ---
    if st.session_state.get("run_analysis") and "df" in st.session_state:
        df = st.session_state["df"]
        limit = st.session_state["limit"]

        st.subheader("📈 Exposure Analysis")

        exposures = df["Exposure"].dropna().astype(float)
        n = len(exposures)
        mean = np.mean(exposures)
        std = np.std(exposures, ddof=1)
        ci_low = mean - 1.96 * std / np.sqrt(n)
        ci_high = mean + 1.96 * std / np.sqrt(n)

        st.markdown(f"""
        - **Number of Samples**: {n}
        - **Mean Exposure**: {mean:.2f} ppm
        - **Standard Deviation**: {std:.2f}
        - **95% Confidence Interval**: ({ci_low:.2f}, {ci_high:.2f}) ppm
        """)

        # --- Exposure Category ---
        if ci_high < limit:
            category = "Acceptable"
            color = "green"
        elif ci_low > limit:
            category = "Unacceptable"
            color = "red"
        else:
            category = "Borderline"
            color = "orange"

        st.markdown(f"<h4 style='color:{color};'>Exposure Category: {category}</h4>", unsafe_allow_html=True)

        # --- Bayesian Decision Analysis ---
        st.subheader("🧠 Bayesian Decision Analysis")

        # Prior probabilities
        prior_acceptable = 0.5
        prior_unacceptable = 0.5

        # Likelihoods based on observed mean
        likelihood_acceptable = 1.0 if mean < limit else 0.3
        likelihood_unacceptable = 1.0 if mean > limit else 0.3

        # Posterior probabilities
        numerator_acc = likelihood_acceptable * prior_acceptable
        numerator_unacc = likelihood_unacceptable * prior_unacceptable
        total = numerator_acc + numerator_unacc

        posterior_acceptable = numerator_acc / total
        posterior_unacceptable = numerator_unacc / total

        st.markdown(f"""
        - **Posterior Probability (Acceptable)**: {posterior_acceptable:.2f}
        - **Posterior Probability (Unacceptable)**: {posterior_unacceptable:.2f}
        """)

        if posterior_unacceptable > 0.7:
            st.error("⚠️ High likelihood of unacceptable exposure. Consider control measures or reassessment.")
        elif posterior_acceptable > 0.7:
            st.success("✅ Exposure likely acceptable. Continue monitoring.")
        else:
            st.warning("⚠️ Uncertainty remains. Additional sampling or expert review recommended.")
        # --- Visualization ---
        st.subheader("📉 Exposure Distribution")

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.hist(exposures, bins=10, color="#4C72B0", edgecolor="white", alpha=0.8)
        ax.axvline(limit, color="red", linestyle="--", label=f"Limit ({limit} ppm)")
        ax.axvline(mean, color="green", linestyle="--", label=f"Mean ({mean:.2f} ppm)")
        ax.set_xlabel("Exposure (ppm)")
        ax.set_ylabel("Frequency")
        ax.set_title("Exposure Histogram")
        ax.legend()

        st.pyplot(fig)

        # --- Summary Box ---
        st.subheader("📦 Summary")

        st.markdown(f"""
        <div style='
            background-color:#f9f9f9;
            border-left:5px solid {color};
            padding:15px;
            font-size:16px;
        '>
            <strong>Exposure Category:</strong> <span style='color:{color}; font-weight:bold;'>{category}</span><br>
            <strong>Mean Exposure:</strong> {mean:.2f} ppm<br>
            <strong>95% CI:</strong> ({ci_low:.2f}, {ci_high:.2f}) ppm<br>
            <strong>Posterior (Unacceptable):</strong> {posterior_unacceptable:.2f}<br>
            <strong>Recommendation:</strong> {
                "Implement controls and reassess." if posterior_unacceptable > 0.7 else
                "Continue monitoring and maintain controls." if posterior_acceptable > 0.7 else
                "Consider additional sampling or expert review."
            }
        </div>
        """, unsafe_allow_html=True)

        # --- Option to Start Over ---
        if st.button("🔄 Start New Assessment"):
            for key in ["organization", "location", "process", "exposure_type", "limit", "df", "run_analysis"]:
                st.session_state.pop(key, None)
            st.rerun()
