import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 1. PAGE CONFIG
# --------------------------------------------------
st.set_page_config(layout="wide", page_title="Health Expenditure Dashboard")

# --------------------------------------------------
# 2. SESSION STATE
# --------------------------------------------------
if "selected_ids" not in st.session_state:
    st.session_state.selected_ids = set()

if "country_selection" not in st.session_state:
    st.session_state.country_selection = None

# --------------------------------------------------
# 3. DATA LOADING
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("merged_health_data.csv")
    df = df.reset_index(drop=True)
    df["row_id"] = df.index  # STABLE GLOBAL ID
    return df

df = load_data()

# --------------------------------------------------
# 4. SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("Filter Options")

all_countries = df["country_x"].unique().tolist()

if st.session_state.country_selection is None:
    st.session_state.country_selection = all_countries[:5]

selected_countries = st.sidebar.multiselect(
    "Select Countries to Compare",
    options=all_countries,
    key="country_selection"
)

min_year = int(df["year"].min())
max_year = int(df["year"].max())

selected_year = st.sidebar.slider(
    "Select Year",
    min_year,
    max_year,
    max_year
)

# --------------------------------------------------
# 5. FILTERING (NO BRUSHING HERE!)
# --------------------------------------------------
year_df = df[
    (df["country_x"].isin(selected_countries)) &
    (df["year"] == selected_year)
]

# --------------------------------------------------
# 6. BRUSH HANDLING
# --------------------------------------------------
def update_brush(fig_key):
    sel = st.session_state.get(fig_key, {}).get("selection", {})
    points = sel.get("points", [])
    if points:
        st.session_state.selected_ids = {
            p["customdata"][0] for p in points
        }

def get_brushed_df(df):
    if not st.session_state.selected_ids:
        return df
    return df[df["row_id"].isin(st.session_state.selected_ids)]

# --------------------------------------------------
# 7. DASHBOARD
# --------------------------------------------------
st.title("Analysis: Health Expenditure vs. Health Indicators")
st.markdown(
    f"Exploring the relationship between healthcare spending and health outcomes "
    f"for the year **{selected_year}**."
)

# ---------------- ROW 1 ----------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Preston Curve Variation")

    fig1 = px.scatter(
        year_df,
        x="Health expenditure per capita - Total",
        y="life_expect",
        color="country_x",
        size="life_expect",
        hover_name="country_x",
        custom_data=["row_id"],
        labels={
            "life_expect": "Life Expectancy (Years)",
            "Health expenditure per capita - Total": "Health Expenditure (PPP USD)"
        }
    )

    st.plotly_chart(
        fig1,
        use_container_width=True,
        selection_mode="points",
        on_select="rerun",
        key="fig1"
    )
    update_brush("fig1")

with col2:
    st.subheader("2. Spending vs. Infant Mortality")

    fig2 = px.scatter(
        year_df,
        x="Health expenditure per capita - Total",
        y="infant_mortality",
        color="country_x",
        size="infant_mortality",
        hover_name="country_x",
        custom_data=["row_id"],
        labels={
            "infant_mortality": "Infant Mortality",
            "Health expenditure per capita - Total": "Health Expenditure (PPP USD)"
        }
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
        selection_mode="points",
        on_select="rerun",
        key="fig2"
    )
    update_brush("fig2")

# ---------------- ROW 2 ----------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("3. Spending vs. Undernourishment")

    under_cols = [c for c in df.columns if "prev_unde" in c]
    y_col_3 = under_cols[0] if under_cols else "life_expect"

    fig3 = px.scatter(
        year_df,
        x="Health expenditure per capita - Total",
        y=y_col_3,
        color="country_x",
        hover_name="country_x",
        custom_data=["row_id"],
        labels={
            y_col_3: "Prevalence of Undernourishment",
            "Health expenditure per capita - Total": "Health Expenditure (PPP USD)"
        }
    )

    st.plotly_chart(
        fig3,
        use_container_width=True,
        selection_mode="points",
        on_select="rerun",
        key="fig3"
    )
    update_brush("fig3")

with col4:
    st.subheader("4. Spending vs. Neonatal Mortality")

    neo_cols = [c for c in df.columns if "neonatal_mortality" in c]
    y_col_4 = neo_cols[0] if neo_cols else "infant_mortality"

    fig4 = px.scatter(
        year_df,
        x="Health expenditure per capita - Total",
        y=y_col_4,
        color="country_x",
        hover_name="country_x",
        custom_data=["row_id"],
        labels={
            y_col_4: "Neonatal Mortality",
            "Health expenditure per capita - Total": "Health Expenditure (PPP USD)"
        }
    )

    st.plotly_chart(
        fig4,
        use_container_width=True,
        selection_mode="points",
        on_select="rerun",
        key="fig4"
    )
    update_brush("fig4")

# ---------------- ROW 3 ----------------
col5, _ = st.columns(2)

with col5:
    st.subheader("5. Global Correlations")

    numeric_df = get_brushed_df(year_df).select_dtypes(
        include=["float64", "int64"]
    )

    if len(numeric_df) > 1:
        corr = numeric_df.corr()
        fig5 = px.imshow(corr, aspect="auto")
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Select points to see correlation heatmap.")

# --------------------------------------------------
# 8. CLEAR BUTTON
# --------------------------------------------------
st.markdown("---")

if st.button("🔄 Clear Selection"):
    st.session_state.selected_ids.clear()
    st.rerun()
