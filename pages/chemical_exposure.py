import streamlit as st
import pandas as pd
from datetime import datetime
import json, os

st.set_page_config(page_title="Chemical Exposure", layout="wide")
st.title("🧪 Chemical Exposure Assessment")

SESSIONS_FILE = "chemical_sessions.json"

# --- Session Helpers ---
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

# --- Sidebar: Load/Delete Sessions ---
st.sidebar.header("📂 Saved Chemical Sessions")
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

# --- Input Form ---
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

# --- Metadata ---
st.subheader("📝 Assessment Metadata")
org = st.text_input("Organization", value="Acme Chemicals Ltd.")
loc = st.text_input("Location", value="Norwich, UK")
proc = st.text_input("Process", value="Batch Reactor Cleaning")
etype = st.selectbox("Exposure Type", ["Full-shift", "Short-term", "Instantaneous"])
limit = st.number_input("Exposure Limit (ppm)", min_value=0.0, value=50.0)

# --- Preview & Run ---
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
