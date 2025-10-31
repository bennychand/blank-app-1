import streamlit as st

st.set_page_config(page_title="Exposure Dashboard", layout="wide")
st.title("🧪 Workplace Exposure Analyzer")

st.markdown("### Select an Exposure Type")

# Define exposure categories with emoji and page links
exposures = {
    "🧪": ("Chemical Exposure", "chemical_exposure"),
    "🔊": ("Noise Exposure", "noise_exposure"),
    "☢️": ("Radiation Exposure", "radiation_exposure"),
    "🦠": ("Legionella", "legionella"),
    "🌡️": ("Heat Stress", "heat_stress"),
    "🤲": ("Vibration Exposure", "vibration_exposure")
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
            # Create a visually styled emoji button
            button_html = f"""
            <div style='text-align:center; margin-top:20px;'>
                <form action='/{page}'>
                    <button style='
                        font-size:80px;
                        background:none;
                        border:none;
                        cursor:pointer;
                        padding:10px;
                    '>{emoji}</button>
                </form>
                <div style='font-size:18px; font-weight:bold; margin-top:10px;'>{label}</div>
            </div>
            """
            st.markdown(button_html, unsafe_allow_html=True)
