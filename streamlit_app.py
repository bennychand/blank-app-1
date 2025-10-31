import streamlit as st
st.set_page_config(page_title="Exposure Dashboard", layout="wide")
st.title("🧪 Workplace Exposure Analyzer")

st.markdown("### Select an Exposure Type")

# Define emoji buttons and their corresponding page titles
exposures = {
    "🧪": "Chemical Exposure",
    "🔊": "Noise Exposure",
    "☢️": "Radiation Exposure",
    "🦠": "Legionella",
    "🌡️": "Heat Stress",
    "🤲": "Vibration Exposure"
}

# Create responsive layout
emojis = list(exposures.keys())
cols = st.columns(3)

for i in range(0, len(emojis), 3):
    row = emojis[i:i+3]
    row_cols = st.columns(len(row))
    for j, emoji in enumerate(row):
        page_title = exposures[emoji]
        with row_cols[j]:
            st.markdown(
                f"<div style='text-align:center; font-size:80px;'>{emoji}</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='text-align:center; font-weight:bold; font-size:18px;'>{page_title}</div>",
                unsafe_allow_html=True
            )
            if st.button(f"Go to {page_title}", key=page_title):
                st.switch_page(page_title)
