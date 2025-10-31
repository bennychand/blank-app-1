# Part 1: Setup & Input Form

# Install dependencies (only needed once)
!pip install streamlit pyngrok pandas matplotlib numpy
!rm /root/.config/ngrok/ngrok.yml
!ngrok config add-authtoken 34psrvilPjiI6fpcHzYHL0nXWJM_73fuzSpY4Ftd5znTMxoH9

# Import libraries
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyngrok import ngrok
public_url = ngrok.connect(8501)
print(f"Streamlit app running at: {public_url}")

# Streamlit config
st.set_page_config(page_title="Chemical Exposure Analyzer", layout="wide")

if "run_analysis" not in st.session_state:
    st.session_state["run_analysis"] = False

st.title("🧪 Chemical Exposure Analyzer")

# Input Form
if not st.session_state["run_analysis"]:
    st.header("📥 Enter Exposure Data and Assessment Details")

    input_method = st.radio("Choose input method:", ["Manual Entry", "Upload CSV"])
    df = pd.DataFrame()

    if input_method == "Manual Entry":
        chemical_name = st.text_input("Chemical Name", value="Chemical A")
        exposure_text = st.text_area("Exposure Values (comma or line separated)", "12, 45, 60, 5, 80")
        try:
            raw_values = exposure_text.replace("\n", ",").split(",")
            exposure_values = [float(val.strip()) for val in raw_values if val.strip()]
            df = pd.DataFrame({"Chemical": [chemical_name] * len(exposure_values), "Exposure": exposure_values})
        except:
            st.warning("Please enter valid numeric exposure values.")
    else:
        uploaded_file = st.file_uploader("Upload CSV with 'Chemical' and 'Exposure' columns", type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)

    st.markdown("### 📝 Assessment Metadata")
    organization = st.text_input("Organization Name", value="Acme Chemicals Ltd.")
    location = st.text_input("Location of Assessment", value="Norwich, UK")
    process = st.text_input("Process During Sampling", value="Batch Reactor Cleaning")
    exposure_type = st.selectbox("Exposure Type", ["Full-shift exposure", "Short-term exposure", "Instantaneous exposure"])
    limit = st.number_input("Exposure Limit (ppm)", min_value=0.0, value=50.0)

    if st.button("▶️ Run Analysis", key="run_button"):
        st.session_state["run_analysis"] = True
        st.session_state["df"] = df
        st.session_state["organization"] = organization
        st.session_state["location"] = location
        st.session_state["process"] = process
        st.session_state["exposure_type"] = exposure_type
        st.session_state["limit"] = limit
        st.rerun()
# Part 2: Results Page & Distribution Charts

if st.session_state["run_analysis"]:
    df = st.session_state["df"]
    organization = st.session_state["organization"]
    location = st.session_state["location"]
    process = st.session_state["process"]
    exposure_type = st.session_state["exposure_type"]
    limit = st.session_state["limit"]

    st.subheader("📋 Assessment Context")
    st.markdown(f"**Organization:** {organization}")
    st.markdown(f"**Location:** {location}")
    st.markdown(f"**Process:** {process}")
    st.markdown(f"**Exposure Type:** {exposure_type}")

    st.subheader("📊 Raw Data")
    if "Timestamp" not in df.columns and df.shape[1] == 3:
        df.columns = ["Chemical", "Exposure", "Timestamp"]
    elif df.shape[1] == 2:
        df.columns = ["Chemical", "Exposure"]
    df["Exposure"] = pd.to_numeric(df["Exposure"], errors="coerce")
    df = df.dropna(subset=["Exposure"])

    chemicals = df["Chemical"].unique()
    bayesian_summary = {}

    category_colors = ["#006400", "#90EE90", "#FFFF00", "#FFBF00", "#FF0000"]
    labels = ["<1%", "1–10%", "10–50%", "50–100%", ">100%"]
    descriptions = [
        "Negligible exposure",
        "Very low exposure",
        "Low to moderate exposure",
        "Approaching exposure limit",
        "Exceeds exposure limit"
    ]

    for chem in chemicals:
        subset = df[df["Chemical"] == chem]
        exposures = subset["Exposure"].values
        total = len(exposures)

        mean = np.mean(exposures)
        sd = np.std(exposures)
        min_val = np.min(exposures)
        max_val = np.max(exposures)
        p95 = np.percentile(exposures, 95)
        positive_vals = exposures[exposures > 0]
        gm = np.exp(np.mean(np.log(positive_vals)))
        gsd = np.exp(np.std(np.log(positive_vals)))

        cats = [0, 0, 0, 0, 0]
        for val in exposures:
            if val < 0.01 * limit:
                cats[0] += 1
            elif val < 0.1 * limit:
                cats[1] += 1
            elif val < 0.5 * limit:
                cats[2] += 1
            elif val <= limit:
                cats[3] += 1
            else:
                cats[4] += 1

        percentages = [round((c / total) * 100, 2) for c in cats]

        # === Summary Table 1: Statistical Metrics ===
        st.markdown(f"#### {chem} - Statistical Summary")
        stats_df = pd.DataFrame({
            "Metric": ["Arithmetic Mean (AM)", "Standard Deviation (SD)", "Geometric Mean (GM)", "Geometric SD (GSD)", "95th Percentile", "Minimum", "Maximum"],
            "Value": [round(mean, 2), round(sd, 2), round(gm, 2), round(gsd, 2), round(p95, 2), round(min_val, 2), round(max_val, 2)]
        })
        st.dataframe(stats_df, use_container_width=True)

        # === Summary Table 2: Category Distribution ===
        st.markdown(f"#### {chem} - Exposure Category Distribution")
        cat_df = pd.DataFrame({
            "Category": labels,
            "Description": descriptions,
            "Count": cats,
            "Percentage": percentages
        })
        st.dataframe(cat_df, use_container_width=True)

        # === Exposure Distribution Charts ===
        st.markdown(f"### {chem} - Exposure Distribution")
        col1, col2 = st.columns(2)

        # Bar Chart
        with col1:
            fig, ax = plt.subplots(figsize=(6, 4))
            bars = ax.bar(labels, percentages, color=category_colors)
            ax.set_ylabel("Percentage")
            ax.set_title(f"{chem} - Bar Chart", pad=20)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha='right')
            for bar, percent in zip(bars, percentages):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                        f"{percent}%", ha='center', va='bottom', fontsize=10,
                        bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
            ax.text(0, max(percentages) + 10,
                    "Categories:\n<1% = Negligible\n1–10% = Very Low\n10–50% = Moderate\n50–100% = Near Limit\n>100% = Hazard",
                    fontsize=9, va='top', ha='left', transform=ax.transAxes,
                    bbox=dict(facecolor='white', edgecolor='gray', alpha=0.8))
            fig.tight_layout()
            st.pyplot(fig)

        # Pie Chart (exclude zero categories)
        with col2:
            nonzero_labels = [f"{label} ({desc})" for label, desc, pct in zip(labels, descriptions, percentages) if pct > 0]
            nonzero_pcts = [pct for pct in percentages if pct > 0]
            nonzero_colors = [color for pct, color in zip(percentages, category_colors) if pct > 0]

            fig2, ax2 = plt.subplots(figsize=(5, 5))
            ax2.pie(nonzero_pcts, labels=nonzero_labels, autopct='%1.1f%%',
                    startangle=90, pctdistance=0.85, labeldistance=1.1,
                    colors=nonzero_colors)
            ax2.set_title(f"{chem} - Pie Chart")
            fig2.tight_layout()
            st.pyplot(fig2)
            st.caption("Category meanings: <1% = Negligible, 1–10% = Very Low, 10–50% = Moderate, 50–100% = Near Limit, >100% = Hazard")
# Part 3: Bayesian Analysis with Enhanced Charts

        # === Bayesian Statistics Section ===
        st.subheader("📊 Statistics Section: Bayesian Distribution")
        st.markdown("This section estimates the probability of exposures falling into each category using Bayesian analysis. It assumes a uniform prior and updates it based on observed data.")

        prior = [1, 1, 1, 1, 1]
        posterior = [(prior[i] + cats[i]) for i in range(5)]
        prior_probs = [round(p / sum(prior) * 100, 2) for p in prior]
        posterior_probs = [round(p / sum(posterior) * 100, 2) for p in posterior]
        bayesian_summary[chem] = posterior_probs

        st.markdown(f"### {chem} - Bayesian Prior vs Posterior")
        col3, col4 = st.columns(2)

        # Prior Chart
        with col3:
            fig_prior, ax_prior = plt.subplots(figsize=(6, 4))
            bars = ax_prior.bar(labels, prior_probs, color=category_colors)
            ax_prior.set_ylabel("Prior Probability (%)")
            ax_prior.set_title(f"{chem} - Prior Distribution", pad=20)
            ax_prior.set_xticks(range(len(labels)))
            ax_prior.set_xticklabels(labels, rotation=45, ha='right')
            for bar, prob in zip(bars, prior_probs):
                ax_prior.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                              f"{prob}%", ha='center', va='bottom', fontsize=10,
                              bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
            ax_prior.text(0, max(prior_probs) + 10,
                          "Categories:\n<1% = Negligible\n1–10% = Very Low\n10–50% = Moderate\n50–100% = Near Limit\n>100% = Hazard",
                          fontsize=9, va='top', ha='left', transform=ax_prior.transAxes,
                          bbox=dict(facecolor='white', edgecolor='gray', alpha=0.8))
            fig_prior.tight_layout()
            st.pyplot(fig_prior)

        # Posterior Chart
        with col4:
            fig_post, ax_post = plt.subplots(figsize=(6, 4))
            bars = ax_post.bar(labels, posterior_probs, color=category_colors)
            ax_post.set_ylabel("Posterior Probability (%)")
            ax_post.set_title(f"{chem} - Posterior Distribution", pad=20)
            ax_post.set_xticks(range(len(labels)))
            ax_post.set_xticklabels(labels, rotation=45, ha='right')
            for bar, prob in zip(bars, posterior_probs):
                ax_post.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                             f"{prob}%", ha='center', va='bottom', fontsize=10,
                             bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))
            ax_post.text(0, max(posterior_probs) + 10,
                         "Categories:\n<1% = Negligible\n1–10% = Very Low\n10–50% = Moderate\n50–100% = Near Limit\n>100% = Hazard",
                         fontsize=9, va='top', ha='left', transform=ax_post.transAxes,
                         bbox=dict(facecolor='white', edgecolor='gray', alpha=0.8))
            fig_post.tight_layout()
            st.pyplot(fig_post)
# Part 4: Recommendations & Reset

    # === Recommendations Section ===
    st.subheader("🛡️ Recommendations to Reduce Exposure")
    st.markdown("Based on the process and organization details provided, here are suggested controls following the Hierarchy of Controls:")

    def generate_recommendations(org, process, posterior_probs):
        cumulative = 0
        apf_required = 0
        for i, prob in enumerate(posterior_probs):
            cumulative += prob
            if cumulative >= 95:
                apf_required = [4, 10, 20, 40, 1000][i]
                break

        return [
            f"**Elimination**: Evaluate whether the task '{process}' at {org} can be redesigned to avoid chemical use entirely.",
            f"**Substitution**: Investigate safer alternatives to the chemicals currently used during '{process}'.",
            f"**Engineering Controls**: Install or upgrade local exhaust ventilation systems near the source of exposure in '{process}'.",
            f"**Administrative Controls**: Rotate workers to limit time spent on '{process}', and provide training on safe handling procedures.",
            f"**Personal Protective Equipment (PPE)**: Recommend respirators with an Assigned Protection Factor (APF) of **{apf_required}** to protect at least 95% of workers during '{process}'."
        ]

    # Use Bayesian posterior from first chemical
    first_chem = chemicals[0]
    posterior_probs = bayesian_summary[first_chem]

    for rec in generate_recommendations(organization, process, posterior_probs):
        st.markdown(f"- {rec}")

    # === Back Button ===
    st.markdown("---")
    if st.button("🔄 Start New Analysis", key="reset_button"):
        st.session_state["run_analysis"] = False
        st.rerun()
