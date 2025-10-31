import streamlit as st

st.set_page_config(page_title="Exposure Dashboard", layout="wide")
st.title("🧪 Workplace Exposure Analyzer")

st.markdown("### Select an Exposure Type to Begin")

# Define exposure categories with emojis and page links
exposures = {
    "🧪 Chemical Exposure": "chemical_exposure",
    "🔊 Noise Exposure": "noise_exposure",
    "☢️ Radiation Exposure": "radiation_exposure",
    "🦠 Legionella": "legionella",
    "🌡️ Heat Stress": "heat_stress",
    "🤲 Vibration Exposure": "vibration_exposure"
}

# Create responsive layout
cols = st.columns(3)
keys = list(exposures.keys())

for i in range(0, len(keys), 3):
    row = keys[i:i+3]
    row_cols = st.columns(len(row))
    for j, label in enumerate(row):
        with row_cols[j]:
            st.markdown(f"<div style='font-size:60px; text-align:center;'>{label.split()[0]}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align:center; font-weight:bold;'>{label.split(' ', 1)[1]}</div>", unsafe_allow_html=True)
            if st.button(f"Go to {label}", key=label):
                st.session_state["selected_exposure"] = label
                st.switch_page(f"{exposures[label]}.py")
