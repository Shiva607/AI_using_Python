# email_compliance_app\app.py

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
# IMPROVED CSS - BEAUTIFUL IN DARK & LIGHT MODE
# --------------------------------------------------
st.markdown("""
    <style>
    .main-header { 
        font-size: 3.2rem; 
        font-weight: 800; 
        text-align: center;
        color: var(--text-color);
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        font-size: 1.4rem;
        color: var(--text-color);
        opacity: 0.85;
        margin-bottom: 3rem;
    }
    .section-header { 
        font-size: 2.3rem; 
        color: var(--primary-color); 
        margin: 4rem 0 2rem 0; 
        font-weight: 700;
        border-bottom: 3px solid var(--primary-color);
        padding-bottom: 0.8rem;
        text-align: center;
    }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(30, 30, 40, 0.6) !important;
        backdrop-filter: blur(10px);
        border: 3px solid var(--primary-color) !important;
        padding: 2.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        transition: all 0.4s ease;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin: 0.5rem;
    }
    .metric-card:hover {
        transform: translateY(-12px) scale(1.02);
        box-shadow: 0 20px 40px rgba(139, 92, 246, 0.4);
        border-color: #A78BFA !important;
    }
    .metric-label {
        font-size: 1.4rem;
        color: var(--text-color);
        opacity: 0.9;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .metric-value {
        font-size: 3.8rem;
        font-weight: 900;
        color: #E0E7FF;
        text-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
    }
    
    @media (prefers-color-scheme: light) {
        .metric-card {
            background: rgba(255, 255, 255, 0.8) !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .metric-value {
            color: #4C1D95;
            text-shadow: none;
        }
    }
    
    /* Priority badges */
    .critical-badge { background-color: #FEE2E2; color: #991B1B; }
    .high-badge     { background-color: #FEF3C7; color: #92400E; }
    .medium-badge   { background-color: #FEFCE8; color: #854D0E; }
    .low-badge      { background-color: #DCFCE7; color: #166534; }
    
    .badge {
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.95rem;
        display: inline-flex;
        align-items: center;
        height: 32px;
        line-height: 1;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def safe_str(value):
    return "" if value is None or pd.isna(value) else str(value).strip()

def get_priority_badge(priority):
    badges = {
        "Critical": '<span class="critical-badge badge">Critical</span>',
        "High":     '<span class="high-badge badge">High</span>',
        "Medium":   '<span class="medium-badge badge">Medium</span>',
        "Low":      '<span class="low-badge badge">Low</span>',
    }
    return badges.get(priority, priority)


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown('<h1 class="main-header">📧 Email Compliance Analysis Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Hybrid Rule-based + LLM-powered detection of compliance risks and behavioral red flags in corporate emails</p>', unsafe_allow_html=True)

# --------------------------------------------------
# SIDEBAR - FILTERS ALWAYS VISIBLE & STABLE
# --------------------------------------------------
with st.sidebar:
    st.header("🔍 Filters")

    CATEGORY_OPTIONS = [
        "Secrecy", "Market Manipulation", "Market Bribery",
        "Change in Communication", "Complaints", "Employee Ethics",
        "Secrecy + Market Manipulation", "Market Bribery + Employee Ethics",
    ]
    PRIORITY_OPTIONS = ["Critical", "High", "Medium", "Low"]

    category_filter = st.multiselect(
        "Risk Category",
        CATEGORY_OPTIONS,
        default=st.session_state.get("category_filter", []),
        key="category_multiselect"
    )
    priority_filter = st.multiselect(
        "Priority Level",
        PRIORITY_OPTIONS,
        default=st.session_state.get("priority_filter", []),
        key="priority_multiselect"
    )

    st.session_state.category_filter = category_filter
    st.session_state.priority_filter = priority_filter

    add_vertical_space(2)

    if st.button("🗑️ Start Over", width="stretch", type="secondary"):
        st.session_state.clear()
        st.rerun()
    st.caption("Clears all current results, filters, and lets you upload a new dataset")

    add_vertical_space(2)

    st.markdown("---")
    st.markdown("### 💡 Tips & Info")
    st.caption("Apply filters after analysis to drill down into specific risks")
    st.caption("Theme automatically adapts to your system setting (Light/Dark mode)")
    st.caption("Use the clear button to start over with a new dataset")


# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
st.markdown("### 📥 Upload Email Dataset")
uploaded = st.file_uploader(
    "Drop your Excel file here (.xlsx)",
    type=["xlsx"],
    help="Required columns: Unique ID, From, To, Subject, Email Body (BEFORE Preprocessing – with Junk)"
)

if not uploaded:
    st.info("⬆️ Please upload an Excel file to begin analysis")
    st.stop()

if "last_uploaded_filename" not in st.session_state or st.session_state.last_uploaded_filename != uploaded.name:
    st.session_state.last_uploaded_filename = uploaded.name
    st.session_state.pop("processed_df", None)

st.success(f"✅ Successfully loaded: **{uploaded.name}**")


# --------------------------------------------------
# PROCESSING
# --------------------------------------------------
if "processed_df" not in st.session_state:
    with st.spinner("🔄 Analyzing emails with Rules + AI intelligence..."):
        df = pd.read_excel(uploaded).fillna("")

        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for i, row in df.iterrows():
            status_text.text(f"Processing email {i + 1} of {len(df)}...")

            raw_body = safe_str(row.get("Email Body (BEFORE Preprocessing – with Junk)"))
            cleaned, junk = preprocess_text(raw_body)

            rule_cat = detect_category(cleaned)
            rule_pri = detect_priority(rule_cat)

            # Default: assume success
            llm_success = True
            final_score = 0.0
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0

            try:
                llm_result = classify_with_gpt(cleaned, rule_cat, rule_pri)
                final_cat = llm_result.final_category
                final_pri = llm_result.final_priority
                final_score = llm_result.score
                llm_success = llm_result.llm_success
                prompt_tokens = llm_result.prompt_tokens
                completion_tokens = llm_result.completion_tokens
                total_tokens = llm_result.total_tokens
            except Exception as e:
                print(f"LLM failed for email {i+1}: {e}")
                final_cat = rule_cat
                final_pri = rule_pri
                final_score = 0.0
                llm_success = False
                prompt_tokens = 0
                completion_tokens = 0
                total_tokens = 0

            record = EmailOutput(
                unique_id=int(row.get("Unique ID", 0)),
                from_email=safe_str(row.get("From")),
                to_email=safe_str(row.get("To")),
                subject=safe_str(row.get("Subject")),
                email_body=raw_body,
                category=final_cat,
                priority=final_pri,
                junk_removed=junk,
                cleaned_text=cleaned,
                score=final_score,
                llm_success=llm_success,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens
            )
            results.append(record.dict())
            progress_bar.progress((i + 1) / len(df))

        st.session_state.processed_df = pd.DataFrame(results)
        status_text.empty()
        progress_bar.empty()

    st.success("🎉 Analysis Completed Successfully!")
    st.info("👆 Use the filters in the sidebar to explore specific risks")
    st.toast("✅ All emails classified successfully!", icon="✅")
    st.balloons()


# --------------------------------------------------
# DATA & FILTERING
# --------------------------------------------------
df_full = st.session_state.processed_df.copy()
df_filtered = df_full.copy()

if category_filter:
    df_filtered = df_filtered[df_filtered["category"].isin(category_filter)]
if priority_filter:
    df_filtered = df_filtered[df_filtered["priority"].isin(priority_filter)]

display_df = df_filtered if not df_filtered.empty else df_full
show_full_warning = df_filtered.empty and (category_filter or priority_filter)


# --------------------------------------------------
# EXECUTIVE SUMMARY
# --------------------------------------------------
# st.markdown('<h2 class="section-header">📌 Compliance Overview</h2>', unsafe_allow_html=True)

# priority_counts = df_full["priority"].value_counts()

# # Calculate total token usage
# total_prompt = df_full["prompt_tokens"].sum()
# total_completion = df_full["completion_tokens"].sum()
# total_tokens_used = df_full["total_tokens"].sum()

# col1, col2, col3, col4, col5, col6 = st.columns(6)  # Now 6 columns

# with col1:
#     st.markdown(f"""
#         <div class="metric-card">
#             <div class="metric-label">Total Emails</div>
#             <div class="metric-value">{len(df_full)}</div>
#         </div>
#     """, unsafe_allow_html=True)

# with col2:
#     st.markdown(f"""
#         <div class="metric-card">
#             <div class="metric-label">Critical</div>
#             <div class="metric-value">{priority_counts.get('Critical', 0)}</div>
#         </div>
#     """, unsafe_allow_html=True)

# with col3:
#     st.markdown(f"""
#         <div class="metric-card">
#             <div class="metric-label">High</div>
#             <div class="metric-value">{priority_counts.get('High', 0)}</div>
#         </div>
#     """, unsafe_allow_html=True)

# with col4:
#     st.markdown(f"""
#         <div class="metric-card">
#             <div class="metric-label">Medium</div>
#             <div class="metric-value">{priority_counts.get('Medium', 0)}</div>
#         </div>
#     """, unsafe_allow_html=True)

# with col5:
#     st.markdown(f"""
#         <div class="metric-card">
#             <div class="metric-label">Low</div>
#             <div class="metric-value">{priority_counts.get('Low', 0)}</div>
#         </div>
#     """, unsafe_allow_html=True)

# with col6:
#     st.markdown(f"""
#         <div class="metric-card">
#             <div class="metric-label">Total Tokens Used</div>
#             <div class="metric-value">{total_tokens_used:,}</div>
#         </div>
#     """, unsafe_allow_html=True)

# add_vertical_space(2)

# # Optional: Show breakdown
# st.caption(f"Token breakdown: Prompt: {total_prompt:,} | Completion: {total_completion:,} | Total: {total_tokens_used:,}")

# add_vertical_space(4)

# --------------------------------------------------
# EXECUTIVE SUMMARY - CLEAN 2-ROW LAYOUT
# --------------------------------------------------
st.markdown('<h2 class="section-header">📌 Compliance Overview</h2>', unsafe_allow_html=True)

priority_counts = df_full["priority"].value_counts()

# Calculate total token usage
total_prompt = df_full["prompt_tokens"].sum()
total_completion = df_full["completion_tokens"].sum()
total_tokens_used = df_full["total_tokens"].sum()

# First row: Total Emails + Total Tokens
col_total, col_tokens = st.columns(2)

with col_total:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Emails Processed</div>
            <div class="metric-value">{len(df_full)}</div>
        </div>
    """, unsafe_allow_html=True)

with col_tokens:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Tokens Used</div>
            <div class="metric-value">{total_tokens_used:,}</div>
        </div>
    """, unsafe_allow_html=True)

add_vertical_space(2)

# Second row: Priority breakdown
col_crit, col_high, col_med, col_low = st.columns(4)

with col_crit:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Critical</div>
            <div class="metric-value">{priority_counts.get('Critical', 0)}</div>
        </div>
    """, unsafe_allow_html=True)

with col_high:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">High</div>
            <div class="metric-value">{priority_counts.get('High', 0)}</div>
        </div>
    """, unsafe_allow_html=True)

with col_med:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Medium</div>
            <div class="metric-value">{priority_counts.get('Medium', 0)}</div>
        </div>
    """, unsafe_allow_html=True)

with col_low:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Low</div>
            <div class="metric-value">{priority_counts.get('Low', 0)}</div>
        </div>
    """, unsafe_allow_html=True)

add_vertical_space(2)

# Optional caption with token breakdown
st.caption(f"Token breakdown: Prompt: {total_prompt:,} | Completion: {total_completion:,} | Total: {total_tokens_used:,}")

add_vertical_space(4)

# --------------------------------------------------
# CHARTS
# --------------------------------------------------
st.markdown('<h2 class="section-header">📊 Risk Distribution</h2>', unsafe_allow_html=True)

if show_full_warning:
    st.warning("⚠️ No emails match current filters — showing full dataset")

col1, col2 = st.columns(2)

with col1:
    cat_data = display_df["category"].value_counts().reset_index()
    fig_cat = px.bar(cat_data, x="category", y="count", title="Category Distribution", text="count", color_discrete_sequence=["#60A5FA"])
    fig_cat.update_traces(textposition="outside")
    fig_cat.update_layout(xaxis_tickangle=45, showlegend=False, height=600)
    st.plotly_chart(fig_cat, width="stretch", height=600)

with col2:
    pri_data = display_df["priority"].value_counts().reset_index()
    colors = {"Critical": "#EF4444", "High": "#F59E0B", "Medium": "#EAB308", "Low": "#22C55E"}
    fig_pri = px.bar(pri_data, x="priority", y="count", title="Priority Distribution", text="count", color="priority", color_discrete_map=colors)
    fig_pri.update_traces(textposition="outside")
    fig_pri.update_layout(showlegend=False, height=600)
    st.plotly_chart(fig_pri, width="stretch", height=600)

add_vertical_space(4)


# --------------------------------------------------
# DETAILED REVIEW
# --------------------------------------------------
st.markdown('<h2 class="section-header">🔍 Detailed Email Review</h2>', unsafe_allow_html=True)

priority_display = display_df["priority"].value_counts()

st.markdown(f"""
**Showing {len(display_df)} emails**  
🔴 {priority_display.get("Critical", 0)} Critical &nbsp; 
🟠 {priority_display.get("High", 0)} High &nbsp; 
🟡 {priority_display.get("Medium", 0)} Medium &nbsp; 
🟢 {priority_display.get("Low", 0)} Low
""")

if display_df.empty:
    st.info("No emails to display.")
else:
    for _, row in display_df.iterrows():
        subject = safe_str(row['subject']) or "No Subject"
        badge = get_priority_badge(row['priority'])
        
        priority_emoji = {
            "Critical": "🔴",
            "High": "🟠",
            "Medium": "🟡",
            "Low": "🟢"
        }.get(row['priority'], "⚪")

        with st.expander(f"📧 **{subject}** &nbsp;&nbsp; {priority_emoji} {row['priority']} &nbsp;&nbsp; `{row['category']}`"):
            c1, c2 = st.columns(2, gap="large")
            
            with c1:
                st.subheader("📩 Original Email")
                st.write(f"**From:** {row['from_email']}")
                st.write(f"**To:** {row['to_email']}")
                st.write(f"**Subject:** {subject}")
                st.text_area("Body", row["email_body"], height=300, disabled=True, label_visibility="collapsed")
            
            with c2:
                st.subheader("🛡️ Compliance Analysis")
                
                source_text = "AI (LLM)" if row.get('llm_success', True) else "Rule-based fallback"
                st.markdown(f"**Source:** {source_text}")
                
                if row.get('llm_success', True):
                    st.success("✅ AI analysis successful")
                else:
                    st.error("❌ AI analysis failed — using rule-based fallback")
                    st.caption("Possible causes: Invalid API key, network issue, rate limit, or model error")
                
                st.markdown(f"**Risk Category:** `{row['category']}`")
                st.markdown(f"**Priority Level:** {badge}", unsafe_allow_html=True)

                st.markdown("### 📊 Scoring Breakdown")
                score = row.get("score", 0.0)
                st.markdown(f"**Final Risk Score:** `{score}/100`")

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Category Weight", "60%")
                with col_b:
                    st.metric("Confidence Weight", "30%")
                with col_c:
                    st.metric("Language Risk Weight", "10%")

                st.caption("Score = 100 × (0.60 × norm_category + 0.30 × confidence + 0.10 × language_risk)")

                # TOKEN USAGE DISPLAY
                if row.get('llm_success', True) and row.get('total_tokens', 0) > 0:
                    col_t1, col_t2, col_t3 = st.columns(3)
                    with col_t1:
                        st.metric("Prompt Tokens", row['prompt_tokens'])
                    with col_t2:
                        st.metric("Completion Tokens", row['completion_tokens'])
                    with col_t3:
                        st.metric("Total Tokens", row['total_tokens'])
                    st.caption("Token usage for this email classification (cost monitoring)")
                elif not row.get('llm_success', True):
                    st.caption("Token usage not available — AI analysis failed")

                st.text_area("Cleaned Text", row["cleaned_text"], height=300, disabled=True, label_visibility="collapsed")

add_vertical_space(4)


# --------------------------------------------------
# TABLE & DOWNLOAD - EXACT FORMAT
# --------------------------------------------------
st.markdown('<h2 class="section-header">📋 Full Results Table</h2>', unsafe_allow_html=True)

column_order = [
    "unique_id", "from_email", "to_email", "subject",
    "email_body", "junk_removed", "cleaned_text",
    "category", "priority", "score"
]

display_table = display_df[column_order].copy()

display_table = display_table.rename(columns={
    "unique_id": "Unique ID",
    "from_email": "From",
    "to_email": "To",
    "subject": "Subject",
    "email_body": "Email Body (BEFORE Preprocessing - with Junk)",
    "junk_removed": "What Gets Removed (Junk Preprocessing)",
    "cleaned_text": "Cleaned Text (AFTER Preprocessing)",
    "category": "Category",
    "priority": "Priority",
    "score": "Risk Score /100"
})

display_table["Risk Score /100"] = display_table["Risk Score /100"].round(0).astype(int)

st.dataframe(display_table, width="stretch", height=600)

add_vertical_space(3)

st.markdown('<h2 class="section-header">📥 Export Results</h2>', unsafe_allow_html=True)

buffer = BytesIO()
with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    display_table.to_excel(writer, index=False, sheet_name="Compliance Analysis")
buffer.seek(0)

st.download_button(
    label="📥 Download Full Results as Excel",
    data=buffer,
    file_name=f"email_compliance_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    width="stretch"
)

st.caption("Report includes all columns: Unique ID, From, To, Subject, Original Body, Junk Removed, Cleaned Text, Category, Priority, and Risk Score")