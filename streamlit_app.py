import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Initialize session state
if "section" not in st.session_state:
    st.session_state.section = "Home"

section = st.session_state.section

# 🏠 Homepage
if section == "Home":
    st.title("🧪 Workplace Exposure Analyzer")
    st.markdown("### Choose an Exposure Type")

    exposures = {
        "🧪": "Chemical Exposure",
        "🔊": "Noise Exposure",
        "☢️": "Radiation Exposure",
        "🦠": "Legionella",
        "🌡️": "Heat Stress",
        "🤲": "Vibration Exposure"
    }

    # Inject CSS (unchanged)
    st.markdown("""
        <style>
        .emoji-tile {
            font-size: 100px;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            background: none;
            border: none;
            padding: 10px;
            margin-bottom: 10px;
            text-align: center;
            width: 100%;
        }
        .emoji-tile:hover {
            transform: scale(1.1);
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
        }
        .emoji-label {
            font-size: 18px;
            font-weight: bold;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Render emoji tiles using columns and hidden buttons
    emoji_items = list(exposures.items())
    for i in range(0, len(emoji_items), 3):
        row = emoji_items[i:i+3]
        cols = st.columns(len(row))
        for col, (emoji, label) in zip(cols, row):
            with col:
                with st.form(key=f"{label}_form", clear_on_submit=True):
                    st.markdown(f"""
                    <div class="emoji-tile">{emoji}<br>
                        <div class="emoji-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    clicked = st.form_submit_button(label="", use_container_width=True)
                    if clicked:
                        st.session_state.section = label
                        st.rerun()


# 🧪 Chemical Exposure Section
elif section == "Chemical Exposure":
    st.title("🧪 Chemical Exposure Assessment")

    st.subheader("📥 Enter Exposure Data")
    input_method = st.radio("Input method", ["Manual Entry", "Upload CSV"], key="input_method")
    df = pd.DataFrame()

    # Continue building your chemical exposure logic here...
    if input_method == "Manual Entry":
        chem_name = st.text_input("Chemical Name", key="chem_name")
        values = st.text_area("Exposure Values (comma-separated)", key="manual_values")
        try:
            exposure_values = [float(v.strip()) for v in values.split(",") if v.strip()]
            df = pd.DataFrame({"Chemical": [chem_name] * len(exposure_values), "Exposure": exposure_values})
        except:
            st.warning("Please enter valid numeric values.")
    else:
        file = st.file_uploader("Upload CSV", type=["csv"], key="csv_upload")
        if file:
            df = pd.read_csv(file)
            if "Chemical" not in df.columns or "Exposure" not in df.columns:
                st.error("CSV must contain 'Chemical' and 'Exposure' columns.")

    st.subheader("📝 Assessment Metadata")
    org = st.text_input("Organization", key="org")
    loc = st.text_input("Location", key="loc")
    proc = st.text_input("Process", key="proc")
    etype = st.selectbox("Exposure Type", ["Full-shift", "Short-term", "Instantaneous"], key="etype")
    limit = st.number_input("Exposure Limit (ppm)", min_value=0.0, key="limit")

    if not df.empty:
        if st.button("▶️ Run Analysis", key="run_analysis_btn"):
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

    if st.button("⬅️ Back to Home", key="back_home_chemical"):
        st.session_state.section = "Home"
        st.rerun()
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

    st.subheader("🧠 Bayesian Decision Analysis")

    prior_acceptable = 0.5
    prior_unacceptable = 0.5
    likelihood_acceptable = 1.0 if mean < limit else 0.3
    likelihood_unacceptable = 1.0 if mean > limit else 0.3

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

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Start New Assessment", key="new_assessment"):
            for key in ["organization", "location", "process", "exposure_type", "limit", "df", "run_analysis"]:
                st.session_state.pop(key, None)
            st.session_state.section = "Chemical Exposure"
            st.rerun()
    with col2:
        if st.button("⬅️ Back to Home", key="back_home_analysis"):
            for key in ["organization", "location", "process", "exposure_type", "limit", "df", "run_analysis"]:
                st.session_state.pop(key, None)
            st.session_state.section = "Home"
            st.rerun()
