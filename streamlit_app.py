if st.session_state.section == "Home":
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

    # Inject hover effects and JS navigation
    st.markdown("""
        <style>
        .emoji-button {
            font-size: 100px;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            background: none;
            border: none;
            padding: 0;
            margin-bottom: 10px;
            text-align: center;
            width: 100%;
        }
        .emoji-button:hover {
            transform: scale(1.1);
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
        }
        .emoji-label {
            font-size: 18px;
            font-weight: bold;
            text-align: center;
        }
        </style>
        <script>
        function setSection(section) {
            window.parent.postMessage({type: 'streamlit:setSessionState', key: 'section', value: section}, '*');
            window.parent.postMessage({type: 'streamlit:rerun'}, '*');
        }
        </script>
    """, unsafe_allow_html=True)

    # Render emojis in rows of 3 using st.columns
    emoji_items = list(exposures.items())
    for i in range(0, len(emoji_items), 3):
        row = emoji_items[i:i+3]
        cols = st.columns(len(row))
        for col, (emoji, label) in zip(cols, row):
            with col:
                st.markdown(f"""
                <div style='text-align:center;'>
                    <button onclick="setSection('{label}')" class="emoji-button">{emoji}</button>
                    <div class="emoji-label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
