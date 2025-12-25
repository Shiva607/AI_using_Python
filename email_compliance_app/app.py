import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from streamlit_extras.add_vertical_space import add_vertical_space

from preprocessing.cleaner import preprocess_text
from preprocessing.rules import detect_category, detect_priority
from llm.gpt_classifier import classify_with_gpt
from models.email_schema import EmailOutput


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="📧 Email Compliance Analyzer",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def safe_str(value):
    """Convert NaN / None to empty string"""
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.title("📧 Email Compliance Analysis Dashboard")
st.markdown(
    "Analyze corporate emails for **compliance risk**, **priority**, "
    "and **behavioral red flags** using **Rules + LLM**."
)

add_vertical_space(1)


# --------------------------------------------------
# SIDEBAR FILTERS (UI ONLY)
# --------------------------------------------------
st.sidebar.header("🔍 Filters (Optional)")

CATEGORY_OPTIONS = [
    "Secrecy",
    "Market Manipulation",
    "Market Bribery",
    "Change in Communication",
    "Complaints",
    "Employee Ethics",
    "Secrecy + Market Manipulation",
    "Market Bribery + Employee Ethics",
]

PRIORITY_OPTIONS = ["Critical", "High", "Medium", "Low"]

category_filter = st.sidebar.multiselect("Category", CATEGORY_OPTIONS)
priority_filter = st.sidebar.multiselect("Priority", PRIORITY_OPTIONS)

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Upload New File"):
    st.session_state.clear()
    st.rerun()


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
st.markdown("### 📥 Upload Email Dataset")

uploaded = st.file_uploader(
    "Drag & drop your Excel file here",
    type=["xlsx"],
)

if not uploaded:
    st.info("⬆️ Upload an Excel file to start analysis")
    st.stop()


# --------------------------------------------------
# RESET STATE ON NEW FILE
# --------------------------------------------------
if (
    "last_uploaded_filename" not in st.session_state
    or st.session_state.last_uploaded_filename != uploaded.name
):
    st.session_state.last_uploaded_filename = uploaded.name
    st.session_state.pop("processed_df", None)

st.success(f"✅ File uploaded: **{uploaded.name}**")


# --------------------------------------------------
# PROCESS EMAILS (RUN ONCE PER FILE)
# --------------------------------------------------
if "processed_df" not in st.session_state:

    with st.spinner("📄 Reading Excel file…"):
        df = pd.read_excel(uploaded)

    # Sanitize NaN
    df = df.fillna("")

    results = []
    progress = st.progress(0, text="🧠 Classifying emails…")

    for i, row in df.iterrows():

        cleaned, junk = preprocess_text(
            safe_str(row.get("Email Body (BEFORE Preprocessing – with Junk)"))
        )

        rule_cat = detect_category(cleaned)
        rule_pri = detect_priority(rule_cat)

        try:
            llm = classify_with_gpt(cleaned, rule_cat, rule_pri)
            final_cat = llm.final_category
            final_pri = llm.final_priority
        except Exception:
            final_cat = rule_cat
            final_pri = rule_pri

        record = EmailOutput(
            unique_id=int(row.get("Unique ID", 0)),
            from_email=safe_str(row.get("From")),
            to_email=safe_str(row.get("To")),
            subject=safe_str(row.get("Subject")),
            email_body=safe_str(
                row.get("Email Body (BEFORE Preprocessing – with Junk)")
            ),
            category=final_cat,
            priority=final_pri,
            junk_removed=junk,
            cleaned_text=cleaned,
        )

        results.append(record.dict())
        progress.progress((i + 1) / len(df))

    st.session_state.processed_df = pd.DataFrame(results)
    st.toast("✅ Classification complete", icon="✅")


# --------------------------------------------------
# DATA SOURCE
# --------------------------------------------------
out_df = st.session_state.processed_df.copy()


# --------------------------------------------------
# APPLY FILTERS (SAFE)
# --------------------------------------------------
filtered_df = out_df.copy()

if category_filter:
    filtered_df = filtered_df[filtered_df["category"].isin(category_filter)]

if priority_filter:
    filtered_df = filtered_df[filtered_df["priority"].isin(priority_filter)]


# --------------------------------------------------
# EXECUTIVE SUMMARY (ALWAYS FULL DATA)
# --------------------------------------------------
st.markdown(
    f"""
## 📌 Compliance Summary (Overall Dataset)

- **Total Emails:** {len(out_df)}
- 🔴 **Critical:** {(out_df['priority'] == 'Critical').sum()}
- 🟠 **High:** {(out_df['priority'] == 'High').sum()}
- 🟡 **Medium:** {(out_df['priority'] == 'Medium').sum()}
- 🟢 **Low:** {(out_df['priority'] == 'Low').sum()}
"""
)

add_vertical_space(1)


# --------------------------------------------------
# GRAPHS (FILTER SAFE)
# --------------------------------------------------
st.subheader("📊 Compliance Overview")

chart_df = filtered_df if not filtered_df.empty else out_df

if filtered_df.empty:
    st.warning("⚠️ No emails match the selected filters. Showing overall trends.")

col1, col2 = st.columns(2)

with col1:
    cat_counts = (
        chart_df["category"]
        .value_counts()
        .reset_index(name="count")
        .rename(columns={"index": "category"})
    )

    fig_cat = px.bar(
        cat_counts,
        x="category",
        y="count",
        title="Category Distribution",
        color_discrete_sequence=["#9EE6CF"],
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col2:
    pri_counts = (
        chart_df["priority"]
        .value_counts()
        .reset_index(name="count")
        .rename(columns={"index": "priority"})
    )

    fig_pri = px.bar(
        pri_counts,
        x="priority",
        y="count",
        title="Priority Distribution",
        color_discrete_sequence=["#FFB703"],
    )
    st.plotly_chart(fig_pri, use_container_width=True)

add_vertical_space(1)


# --------------------------------------------------
# EMAIL COMPARISON VIEW (EXPANDERS + SIDE-BY-SIDE)
# --------------------------------------------------
display_df = filtered_df if not filtered_df.empty else out_df
cmp_df = display_df  # already filter-safe

cmp_critical = (cmp_df["priority"] == "Critical").sum()
cmp_high = (cmp_df["priority"] == "High").sum()
cmp_medium = (cmp_df["priority"] == "Medium").sum()
cmp_low = (cmp_df["priority"] == "Low").sum()
cmp_total = len(cmp_df)

st.markdown(
    f"""
### 🧾 Email Comparison View  
🔴 **{cmp_critical} Critical** &nbsp;&nbsp;
🟠 **{cmp_high} High** &nbsp;&nbsp;
🟡 **{cmp_medium} Medium** &nbsp;&nbsp;
🟢 **{cmp_low} Low** &nbsp;&nbsp;
📄 **Total: {cmp_total}**
"""
)

if display_df.empty:
    st.info("No emails to display.")
else:
    for _, row in display_df.iterrows():

        expander_title = f"📧 {safe_str(row['subject'])}  |  {row['priority']}"

        with st.expander(expander_title, expanded=False):

            left_col, right_col = st.columns(2, gap="large")

            # LEFT — RAW EMAIL
            with left_col:
                st.markdown("### 📩 Raw Email")
                st.markdown(f"**From:** {row['from_email']}")
                st.markdown(f"**To:** {row['to_email']}")
                st.markdown(f"**Subject:** {row['subject']}")
                st.markdown("**Email Body:**")
                st.text_area(
                    "",
                    row["email_body"],
                    height=220,
                    disabled=True,
                )

            # RIGHT — COMPLIANCE
            with right_col:
                st.markdown("### 🛡️ Compliance Analysis")
                st.markdown(
                    f"""
**Category:** `{row['category']}`  
**Priority:** `{row['priority']}`
"""
                )
                st.markdown("**Cleaned Insight:**")
                st.text_area(
                    "",
                    row["cleaned_text"],
                    height=220,
                    disabled=True,
                )


# --------------------------------------------------
# TABLE VIEW WITH VISUAL COUNTS
# --------------------------------------------------
critical = (display_df["priority"] == "Critical").sum()
high = (display_df["priority"] == "High").sum()
medium = (display_df["priority"] == "Medium").sum()
low = (display_df["priority"] == "Low").sum()

st.markdown(
    f"""
### 📋 Email Table View  
🔴 **{critical} Critical** &nbsp;&nbsp;
🟠 **{high} High** &nbsp;&nbsp;
🟡 **{medium} Medium** &nbsp;&nbsp;
🟢 **{low} Low** &nbsp;&nbsp;
📄 **Total: {len(display_df)}**
"""
)

st.dataframe(display_df, use_container_width=True)


# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------
buffer = BytesIO()
display_df.to_excel(buffer, index=False)
buffer.seek(0)

st.download_button(
    "📥 Download Excel",
    buffer,
    file_name="email_compliance_output.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
