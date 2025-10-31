import streamlit as st

st.set_page_config(page_title="Exposure Dashboard", layout="wide")
st.title("🧪 Workplace Exposure Analyzer")

st.markdown("### Select an Exposure Type")

# Define exposure categories with emoji and page filenames
exposures = {
    "🧪": ("Chemical Exposure", "Chemical Exposure"),
    "🔊": ("Noise Exposure", "Noise Exposure"),
    "☢️": ("Radiation Exposure", "Radiation Exposure"),
    "🦠": ("Legionella", "Legionella"),
    "🌡️": ("Heat Stress", "Heat Stress"),
    "🤲": ("Vibration Exposure", "Vibration Exposure")
}

# Create responsive layout
emojis = list(exposures.keys())
cols = st.columns(3)

for i in range(0, len(emojis), 3):
    row = emojis[i:i+3]
    row_cols = st.columns(len(row))
    for j, emoji in enumerate(row):
        label, page = exposures[emoji]
        with row_cols[j]:
            st.markdown(
                f"<div style='text-align:center; font-size:80px;'>{emoji}</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='text-align:center; font-weight:bold; font-size:18px;'>{label}</div>",
                unsafe_allow_html=True
            )
            if st.button(f"Go to {label}", key=label):
    st.switch_page(page)
