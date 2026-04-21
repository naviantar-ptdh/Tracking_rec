import streamlit as st
import pandas as pd

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="Candidate Tracking",
    layout="wide"
)

# ======================
# HEADER
# ======================
col_logo, col_title = st.columns([1, 8], vertical_alignment="center")

with col_logo:
    st.image("logo_solid.png", width=70)

with col_title:
    st.markdown(
        "<h1 style='margin:0;'>Candidate Tracking System</h1>",
        unsafe_allow_html=True
    )

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
for col in ["position_name", "candidate_id", "status", "last_progress"]:
    if col in df.columns:
        df[col] = df[col].fillna("Unknown")

# ======================
# HELPER: CURRENT STAGE
# ======================
def get_stage(row):
    if pd.notna(row.get("date_onboarding")):
        return "Onboarding"
    elif pd.notna(row.get("start_fu_mcu")):
        return "Follow Up MCU"
    elif pd.notna(row.get("start_review_mcu")):
        return "Review MCU"
    elif pd.notna(row.get("start_mcu")):
        return "MCU"
    elif pd.notna(row.get("start_offering")):
        return "Offering"
    elif pd.notna(row.get("start_psychotest")):
        return "Psychotest"
    elif pd.notna(row.get("start_interview_user")):
        return "User Interview"
    elif pd.notna(row.get("start_interview_hr")):
        return "HR Interview"
    elif pd.notna(row.get("start_screening_cv")):
        return "Screening CV"
    else:
        return "Not Started"

df["current_stage"] = df.apply(get_stage, axis=1)

# ======================
# MODE SWITCH
# ======================
mode = st.radio(
    "Select Mode",
    ["🔎 By Position", "👤 By Candidate"],
    horizontal=True
)

# =========================================================
# 🔎 MODE 1: BY POSITION
# =========================================================
if mode == "🔎 By Position":

    st.subheader("Search by Position")

    selected_pos = st.selectbox(
        "Select Position",
        sorted(df["position_name"].dropna().unique())
    )

    result = df[df["position_name"] == selected_pos]

    st.write(f"### Total Candidate: {len(result)}")

    # STATUS COLOR
    def color_status(val):
        if val == "OPEN":
            return "background-color: orange"
        elif val == "CLOSE":
            return "background-color: lightgreen"
        elif val == "FAILED":
            return "background-color: red"
        return ""

    display_df = result[[
        "candidate_id",
        "status",
        "last_progress",
        "current_stage"
    ]]

    st.dataframe(
        display_df.style.applymap(color_status, subset=["status"]),
        use_container_width=True
    )

# =========================================================
# 👤 MODE 2: BY CANDIDATE
# =========================================================
else:

    st.subheader("Search Candidate")

    selected_candidate = st.selectbox(
        "Select Candidate",
        sorted(df["candidate_id"].dropna().unique())
    )

    result = df[df["candidate_id"] == selected_candidate]

    if not result.empty:
        data = result.iloc[0]

        # ======================
        # BASIC INFO
        # ======================
        st.markdown("### Candidate Info")

        c1, c2, c3 = st.columns(3)

        c1.metric("Name", data["candidate_id"])
        c2.metric("Position", data["position_name"])
        c3.metric("Current Stage", data["current_stage"])

        # STATUS COLOR
        if data["status"] == "OPEN":
            st.warning("On Progress")
        elif data["status"] == "CLOSE":
            st.success("Hired")
        elif data["status"] == "FAILED":
            st.error("Failed")

        st.write("Last Progress:", data["last_progress"])

        # ======================
        # TIMELINE
        # ======================
        st.markdown("### Progress Timeline")

        timeline_cols = [
            ("Screening CV", "start_screening_cv"),
            ("HR Interview", "start_interview_hr"),
            ("User Interview", "start_interview_user"),
            ("Psychotest", "start_psychotest"),
            ("Offering", "start_offering"),
            ("MCU", "start_mcu"),
            ("Review MCU", "start_review_mcu"),
            ("Follow Up MCU", "start_fu_mcu"),
            ("Onboarding", "date_onboarding")
        ]

        for label, col in timeline_cols:
            if col in data and pd.notna(data[col]):
                st.success(f"{label} ✅ ({data[col]})")
            else:
                st.info(f"{label} ⏳")
