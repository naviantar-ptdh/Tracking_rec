import streamlit as st
import pandas as pd

# ======================
# CONFIG
# ======================
st.set_page_config(
    page_title="Tracking Candidate",
    layout="wide"
)

st.title("🔍 Candidate & Position Tracking")

# ======================
# LOAD DATA
# ======================
@st.cache_data(ttl=60)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1eysrca2wIWsx2LZeP3z2qlRawLzdRBYxsDf6JizcaZc/export?format=csv"
    return pd.read_csv(url)

df = load_data()

if df.empty:
    st.warning("No data available")
    st.stop()

df.columns = df.columns.str.lower()

# ======================
# CLEANING
# ======================
for col in ["candidate_id", "position_name", "departement", "level", "loc", "status1", "last_progress"]:
    if col in df.columns:
        df[col] = df[col].fillna("Unknown")

# ======================
# SEARCH MODE
# ======================
mode = st.radio(
    "Search Mode",
    ["By Position", "By Candidate"],
    horizontal=True
)

# ======================
# COLOR FUNCTION
# ======================
def color_status(val):
    val = str(val).upper()
    if val == "OPEN":
        return "color: orange; font-weight: bold;"
    elif val == "FAILED":
        return "color: red; font-weight: bold;"
    elif val == "CLOSE":
        return "color: green; font-weight: bold;"
    else:
        return ""

# =========================================================
# ===================== BY POSITION ========================
# =========================================================
if mode == "By Position":

    pos_list = sorted(df["position_name"].dropna().unique())

    selected_pos = st.selectbox(
        "Select Position",
        pos_list
    )

    filtered = df[df["position_name"] == selected_pos]

    st.subheader(f"Candidates for: {selected_pos}")

    display_df = filtered[[
        "candidate_id",
        "position_name",
        "departement",
        "level",
        "loc",
        "status1",
        "last_progress"
    ]]

    st.dataframe(
        display_df.style.map(color_status, subset=["status"]),
        use_container_width=True
    )

    st.metric("Total Candidate", len(display_df))


# =========================================================
# ===================== BY CANDIDATE =======================
# =========================================================
else:

    cand_list = sorted(df["candidate_id"].dropna().unique())

    selected_cand = st.selectbox(
        "Select Candidate",
        cand_list
    )

    filtered = df[df["candidate_id"] == selected_cand]

    st.subheader(f"Detail Candidate: {selected_cand}")

    display_df = filtered[[
        "candidate_id",
        "position_name",
        "departement",
        "level",
        "loc",
        "status",
        "last_progress"
    ]]

    st.dataframe(
        display_df.style.map(color_status, subset=["status"]),
        use_container_width=True
    )
