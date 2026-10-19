# ============================================================
# GITHUB INTELLIGENCE DASHBOARD
# Built with Streamlit
# ============================================================

import re
from urllib.parse import quote
from datetime import datetime, timezone

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="GitHub Intelligence Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
/* Main page */
.stApp {
    background: #f7f9fc !important;
}

.block-container {
    padding-top: 5rem !important;
    padding-bottom: 1rem !important;
    max-width: 1500px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101c32 0%, #172743 100%) !important;
}

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #1d2d49 !important;
    color: #ffffff !important;
    border: 1px solid #405574 !important;
}

section[data-testid="stSidebar"] hr {
    border-color: #405574 !important;
}

/* Header */
.main-title {
    font-size: 34px;
    line-height: 1.1;
    font-weight: 800;
    color: #172554;
    margin: 0;
}

.subtitle {
    color: #64748b;
    font-size: 14px;
    margin-top: 8px;
    margin-bottom: 16px;
}

/* Cards */
.metric-card {
    min-height: 105px;
    padding: 17px 18px;
    border-radius: 10px;
    border: 1px solid #d8e1ec;
    box-sizing: border-box;
}

.metric-blue {
    background: linear-gradient(135deg, #eaf4ff, #dceeff);
}

.metric-green {
    background: linear-gradient(135deg, #eafaf2, #dff7ec);
}

.metric-purple {
    background: linear-gradient(135deg, #f4edff, #eee4ff);
}

.metric-red {
    background: linear-gradient(135deg, #fff1f2, #ffe6e8);
}

.metric-icon {
    float: left;
    width: 42px;
    height: 42px;
    line-height: 42px;
    text-align: center;
    border-radius: 9px;
    margin-right: 12px;
    font-size: 25px;
    background: rgba(255,255,255,.65);
}

.metric-label {
    padding-top: 1px;
    color: #334155;
    font-size: 13px;
    font-weight: 650;
}

.metric-value {
    color: #0f172a;
    font-size: 27px;
    font-weight: 800;
    margin-top: 5px;
}

/* Section titles */
.section-title {
    color: #172554;
    font-size: 19px;
    font-weight: 750;
    margin-top: 13px;
    margin-bottom: 7px;
}

/* Insight */
.insight-box {
    background: linear-gradient(135deg, #eaf9ef, #e4f8ed);
    border: 1px solid #bde5cb;
    border-radius: 10px;
    padding: 17px 20px;
    min-height: 280px;
    box-sizing: border-box;
}

.insight-title {
    color: #172554;
    font-size: 18px;
    font-weight: 750;
    margin-bottom: 12px;
}

.insight-box ul {
    padding-left: 20px;
    margin: 0;
}

.insight-box li {
    color: #164e35;
    font-size: 14px;
    margin-bottom: 12px;
}

/* HTML tables */
.custom-table-wrap {
    width: 100%;
    overflow-x: auto;
    border: 1px solid #d9e2ec;
    border-radius: 8px;
    background: #ffffff;
}

.custom-table {
    width: 100%;
    border-collapse: collapse;
    background: #ffffff;
    color: #172033;
    font-size: 13px;
}

.custom-table th {
    background: #f8fafc;
    color: #334155;
    font-weight: 700;
    padding: 9px 10px;
    border-bottom: 1px solid #dbe4ee;
    border-right: 1px solid #e7edf3;
    text-align: left;
    white-space: nowrap;
}

.custom-table td {
    padding: 8px 10px;
    border-bottom: 1px solid #e7edf3;
    border-right: 1px solid #edf2f7;
    white-space: nowrap;
}

.custom-table tr:last-child td {
    border-bottom: none;
}

.custom-table tr:hover td {
    background: #f8fbff;
}

.repo-link {
    color: #1976d2;
    text-decoration: underline;
    font-weight: 600;
}

/* Footer */
.footer {
    text-align: center;
    color: #94a3b8;
    font-size: 12px;
    padding: 18px 0 5px 0;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================

def format_number(value):
    return f"{float(value):,.0f}"


def format_compact(value):
    value = float(value)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.0f}K"
    return f"{value:,.0f}"


def get_github_url(repo):
    repo_text = str(repo).strip()
    if repo_text.startswith("http://") or repo_text.startswith("https://"):
        return repo_text
    if "/" in repo_text:
        return f"https://github.com/{repo_text}"
    return f"https://github.com/search?q={quote(repo_text)}&type=repositories"


def make_html_table(dataframe):
    table = dataframe.copy()
    html = '<div class="custom-table-wrap"><table class="custom-table"><thead><tr>'
    for column in table.columns:
        html += f"<th>{column}</th>"
    html += "</tr></thead><tbody>"

    for _, row in table.iterrows():
        html += "<tr>"
        for column in table.columns:
            value = row[column]
            if pd.isna(value):
                value = ""
            if column == "Repository":
                repo_name = str(value)
                repo_url = get_github_url(repo_name)
                value = f'<a class="repo-link" href="{repo_url}" target="_blank" rel="noopener noreferrer">{repo_name}</a>'
            html += f"<td>{value}</td>"
        html += "</tr>"
    html += "</tbody></table></div>"
    return html


def make_plot_white(fig, height=330):
    fig.update_layout(
        height=height,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#334155", family="Arial"),
        margin=dict(l=45, r=25, t=15, b=55),
        legend=dict(font=dict(color="#334155"))
    )
    fig.update_xaxes(gridcolor="#e2e8f0", zerolinecolor="#cbd5e1")
    fig.update_yaxes(gridcolor="#e2e8f0", zerolinecolor="#cbd5e1")
    return fig


# ============================================================
# DATA LOADING (FROM SAVED CSV)
# ============================================================

@st.cache_data
def load_data():
    file_path = "data/github_intelligence_data (1).xls.csv"
    data = pd.read_csv(file_path)
    data.columns = data.columns.str.strip()

    # Handle column naming flexibility
    if "Primary Language" in data.columns and "Language" not in data.columns:
        data.rename(columns={"Primary Language": "Language"}, inplace=True)

    required_columns = ["Repository", "Stars", "Forks", "Open Issues", "Language", "Last Updated"]
    missing_columns = [col for col in required_columns if col not in data.columns]

    if missing_columns:
        st.error("Missing columns in CSV: " + ", ".join(missing_columns))
        st.stop()

    for col in ["Stars", "Forks", "Open Issues"]:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    data["Language"] = data["Language"].fillna("Unknown").astype(str)

    data["Last Updated"] = pd.to_datetime(
        data["Last Updated"],
        errors="coerce",
        utc=True
    ).dt.tz_convert(None)

    data["Stars per Fork"] = data["Stars"] / data["Forks"].replace(0, 1)
    return data


try:
    df = load_data()
except Exception as e:
    st.error(f"❌ CSV file load nahi ho paayi. Error: {e}")
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("""
<div style="font-size:24px;font-weight:800;color:white;margin-bottom:12px;">
🐙 GitHub Intelligence<br>Dashboard
</div>
""", unsafe_allow_html=True)

st.sidebar.write(
    "Explore and analyze top open-source repositories "
    "across major programming languages securely using local cache."
)

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")

# Dynamic languages list based on CSV data
unique_languages = sorted(df["Language"].dropna().unique().tolist())
language_options = ["All"] + unique_languages

selected_language = st.sidebar.selectbox(
    "Programming Language",
    language_options
)

minimum_stars = st.sidebar.selectbox(
    "Minimum Stars",
    [0, 10000, 50000, 100000, 150000]
)

sort_option = st.sidebar.selectbox(
    "Sort by",
    [
        "Stars (High to Low)",
        "Stars (Low to High)",
        "Forks (High to Low)",
        "Open Issues (High to Low)",
        "Repository Name"
    ]
)


# ============================================================
# APPLY FILTERS
# ============================================================

filtered_df = df.copy()

if selected_language != "All":
    filtered_df = filtered_df[filtered_df["Language"] == selected_language]

filtered_df = filtered_df[filtered_df["Stars"] >= minimum_stars]

if sort_option == "Stars (High to Low)":
    filtered_df = filtered_df.sort_values("Stars", ascending=False)
elif sort_option == "Stars (Low to High)":
    filtered_df = filtered_df.sort_values("Stars", ascending=True)
elif sort_option == "Forks (High to Low)":
    filtered_df = filtered_df.sort_values("Forks", ascending=False)
elif sort_option == "Open Issues (High to Low)":
    filtered_df = filtered_df.sort_values("Open Issues", ascending=False)
else:
    filtered_df = filtered_df.sort_values("Repository", ascending=True)


# ============================================================
# MAIN HEADER
# ============================================================

header_col1, header_col2 = st.columns([8, 2])

with header_col1:
    st.markdown('<div class="main-title">GitHub Intelligence Dashboard 🚀</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">'
        'Repository Insights &nbsp;•&nbsp; Popularity &nbsp;•&nbsp; '
        'Activity &nbsp;•&nbsp; Language Trends'
        '</div>',
        unsafe_allow_html=True
    )

with header_col2:
    st.markdown("""
<div style="text-align:right;color:#64748b;font-size:12px;margin-top:10px;">
Made with Streamlit ❤️
</div>
""", unsafe_allow_html=True)


# ============================================================
# EMPTY DATA CHECK
# ============================================================

if filtered_df.empty:
    st.warning("No repositories match the selected filters.")
    st.stop()


# ============================================================
# METRICS
# ============================================================

total_repositories = len(filtered_df)
total_stars = filtered_df["Stars"].sum()
total_forks = filtered_df["Forks"].sum()
total_issues = filtered_df["Open Issues"].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f'<div class="metric-card metric-blue">'
        f'<div class="metric-icon">📄</div>'
        f'<div class="metric-label">Total Repositories</div>'
        f'<div class="metric-value">{total_repositories:,}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f'<div class="metric-card metric-green">'
        f'<div class="metric-icon">☆</div>'
        f'<div class="metric-label">Total Stars</div>'
        f'<div class="metric-value">{format_compact(total_stars)}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f'<div class="metric-card metric-purple">'
        f'<div class="metric-icon">⑂</div>'
        f'<div class="metric-label">Total Forks</div>'
        f'<div class="metric-value">{format_compact(total_forks)}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        f'<div class="metric-card metric-red">'
        f'<div class="metric-icon">◷</div>'
        f'<div class="metric-label">Total Open Issues</div>'
        f'<div class="metric-value">{total_issues:,.0f}</div>'
        f'</div>',
        unsafe_allow_html=True
    )


# ============================================================
# REPOSITORY OVERVIEW TABLE
# ============================================================

st.markdown('<div class="section-title">▣ Repository Overview</div>', unsafe_allow_html=True)

overview_df = filtered_df.copy()
overview_df.insert(0, "#", range(1, len(overview_df) + 1))

overview_display = overview_df[
    ["#", "Repository", "Stars", "Forks", "Open Issues", "Last Updated", "Language"]
].copy()

overview_display["Stars"] = overview_display["Stars"].map(format_number)
overview_display["Forks"] = overview_display["Forks"].map(format_number)
overview_display["Open Issues"] = overview_display["Open Issues"].map(format_number)
overview_display["Last Updated"] = pd.to_datetime(overview_display["Last Updated"], errors="coerce").dt.strftime("%Y-%m-%d").fillna("-")

st.markdown(make_html_table(overview_display), unsafe_allow_html=True)


# ============================================================
# ROW 1: STARS VS FORKS + LANGUAGE DISTRIBUTION
# ============================================================

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown('<div class="section-title">▧ Stars vs Forks</div>', unsafe_allow_html=True)
    fig_scatter = px.scatter(
        filtered_df,
        x="Stars",
        y="Forks",
        color="Repository",
        hover_name="Repository",
        hover_data=["Stars", "Forks", "Open Issues"],
        template="plotly_white"
    )
    fig_scatter = make_plot_white(fig_scatter)
    fig_scatter.update_traces(marker=dict(size=12, opacity=1), selector=dict(mode="markers"))
    st.plotly_chart(fig_scatter, use_container_width=True, config={"displayModeBar": False})

with chart_col2:
    st.markdown('<div class="section-title">♙ Language Distribution</div>', unsafe_allow_html=True)
    language_counts = filtered_df["Language"].value_counts().reset_index()
    language_counts.columns = ["Language", "Count"]

    fig_language = px.pie(
        language_counts,
        names="Language",
        values="Count",
        hole=0.60,
        template="plotly_white"
    )
    fig_language = make_plot_white(fig_language)
    fig_language.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_language, use_container_width=True, config={"displayModeBar": False})


# ============================================================
# ROW 2: ACTIVITY + KEY INSIGHTS
# ============================================================

chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.markdown('<div class="section-title">▣ Repository Activity (Hours Ago)</div>', unsafe_allow_html=True)
    activity_df = filtered_df.copy()
    
    updated_dates = pd.to_datetime(activity_df["Last Updated"], errors="coerce").dt.tz_localize(None)
    now = pd.Timestamp.now().tz_localize(None)

    # Hours calculate karna taaki exact recency pata chale (0 ki jagah hours dikhenge)
    activity_df["Hours Since Update"] = (now - updated_dates).dt.total_seconds() / 3600
    activity_df["Hours Since Update"] = activity_df["Hours Since Update"].fillna(0).clip(lower=0).round(1)

    fig_activity = px.bar(
        activity_df,
        x="Repository",
        y="Hours Since Update",
        text="Hours Since Update",
        template="plotly_white"
    )
    fig_activity = make_plot_white(fig_activity)
    fig_activity.update_traces(textposition="outside")
    fig_activity.update_layout(xaxis_title="", yaxis_title="Hours since last update")
    st.plotly_chart(fig_activity, use_container_width=True, config={"displayModeBar": False})

with chart_col4:
    max_star_repo = filtered_df.loc[filtered_df["Stars"].idxmax(), "Repository"] if not filtered_df.empty else "N/A"
    max_star_val = filtered_df["Stars"].max() if not filtered_df.empty else 0
    top_lang = filtered_df["Language"].mode().iloc[0] if not filtered_df.empty else "N/A"

    st.markdown(
        f'<div class="insight-box">'
        f'<div class="insight-title">💡 Key Insights</div>'
        f'<ul>'
        f'<li><b>{max_star_repo}</b> has the highest number of stars ({max_star_val:,.0f}).</li>'
        f'<li><b>{top_lang}</b> is the most prominent language in the current selection.</li>'
        f'<li>Total repositories analyzed: <b>{len(filtered_df)}</b></li>'
        f'<li>Total stars combined: <b>{filtered_df["Stars"].sum():,.0f}</b></li>'
        f'<li>Total forks combined: <b>{filtered_df["Forks"].sum():,.0f}</b></li>'
        f'</ul>'
        f'</div>',
        unsafe_allow_html=True
    )


# ============================================================
# ROW 3: TOP REPOSITORIES + LANGUAGE POPULARITY
# ============================================================

chart_col5, chart_col6 = st.columns(2)

with chart_col5:
    st.markdown('<div class="section-title">☆ Top Repositories by Stars</div>', unsafe_allow_html=True)
    top_df = filtered_df.sort_values("Stars", ascending=True).tail(10)

    fig_top = px.bar(
        top_df,
        x="Stars",
        y="Repository",
        orientation="h",
        text="Stars",
        template="plotly_white"
    )
    fig_top = make_plot_white(fig_top)
    fig_top.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_top.update_layout(xaxis_title="Stars", yaxis_title="")
    st.plotly_chart(fig_top, use_container_width=True, config={"displayModeBar": False})

with chart_col6:
    st.markdown('<div class="section-title">✣ Language vs Popularity</div>', unsafe_allow_html=True)
    language_popularity = filtered_df.groupby(["Language", "Repository"], as_index=False)["Stars"].sum()

    fig_popularity = px.bar(
        language_popularity,
        x="Language",
        y="Stars",
        color="Repository",
        barmode="stack",
        template="plotly_white"
    )
    fig_popularity = make_plot_white(fig_popularity)
    fig_popularity.update_layout(xaxis_title="", yaxis_title="Total Stars")
    st.plotly_chart(fig_popularity, use_container_width=True, config={"displayModeBar": False})


# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
GitHub Intelligence Dashboard • Built with Streamlit 🚀
</div>
""", unsafe_allow_html=True)

1