import streamlit as st
import pandas as pd
import plotly.express as px

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Health Expenditure Dashboard")

# 2. SESSION STATE SETUP
if "selected_indices" not in st.session_state:
    st.session_state.selected_indices = []

if "country_selection" not in st.session_state:
    st.session_state.country_selection = [] 

# 3. DATA LOADING
@st.cache_data
def load_data():
    df = pd.read_csv("merged_health_data.csv")
    return df

df = load_data()

# 4. SIDEBAR FILTERS
st.sidebar.header("Filter Options")

# Prevent reset bug
all_countries = df["country_x"].unique().tolist()
if not st.session_state.country_selection:
    st.session_state.country_selection = all_countries[:5]

selected_countries = st.sidebar.multiselect(
    "Select Countries to Compare",
    options=all_countries,
    key="country_selection"
)

min_year = int(df["year"].min())
max_year = int(df["year"].max())
selected_year = st.sidebar.slider("Select Year", min_year, max_year, max_year)

# 5. DATA PREPARATION
# Base Data for this Year
year_df = df[
    (df["country_x"].isin(selected_countries)) & 
    (df["year"] == selected_year)
]

# 6. BRUSHING LOGIC
def update_brush(fig_key):
    sel = st.session_state.get(fig_key, {}).get("selection", {})
    points = sel.get("points", [])
    if points:
        st.session_state.selected_indices = [p["point_index"] for p in points]

# Create the Filtered Dataframe
if st.session_state.selected_indices:
    brushed_df = year_df.iloc[st.session_state.selected_indices]
else:
    brushed_df = year_df  # If nothing selected, show everything

# 7. DASHBOARD LAYOUT
st.title("Analysis: Health Expenditure vs. Health Indicators")
st.markdown(f"Exploring relationships for the year **{selected_year}**.")

col1, col2 = st.columns(2)

# --- CHART 1: THE "CONTROLLER" ---
with col1:
    st.subheader("1. Preston Curve (Selector)")
    st.caption("Click points here to filter the other charts!")
    
    # We use 'year_df' here so you always see all points to click on
    fig1 = px.scatter(
        year_df, 
        x="Health expenditure per capita - Total",
        y="life_expect",
        color="country_x",
        size="life_expect",
        hover_name="country_x",
        labels={"life_expect": "Life Expectancy", "Health expenditure per capita - Total": "Health Expenditure"},
        title="Expenditure vs. Life Expectancy"
    )
    # The interaction source
    st.plotly_chart(
        fig1, use_container_width=True,
        selection_mode="points", on_select="rerun", key="fig1"
    )
    update_brush("fig1")

# --- CHART 2: REACTIVE ---
with col2:
    st.subheader("2. Spending vs. Infant Mortality")
    
    # FIX: Use 'brushed_df' so this chart updates!
    fig2 = px.scatter(
        brushed_df,
        x="Health expenditure per capita - Total",
        y="infant_mortality",
        color="country_x",
        size="infant_mortality",
        hover_name="country_x",
        labels={"infant_mortality": "Infant Mortality", "Health expenditure per capita - Total": "Health Expenditure"},
        title="Expenditure vs. Infant Mortality (Filtered)"
    )
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

# --- CHART 3: REACTIVE ---
with col3:
    st.subheader("3. Spending vs. Undernourishment")
    under_cols = [c for c in df.columns if "prev_unde" in c]
    y_col_3 = under_cols[0] if under_cols else "life_expect"

    # FIX: Use 'brushed_df'
    fig3 = px.scatter(
        brushed_df,
        x="Health expenditure per capita - Total",
        y=y_col_3,
        color="country_x",
        hover_name="country_x",
        labels={y_col_3: "Undernourishment", "Health expenditure per capita - Total": "Health Expenditure"},
        title="Expenditure vs. Undernourishment (Filtered)"
    )
    st.plotly_chart(fig3, use_container_width=True)

# --- CHART 4: REACTIVE ---
with col4:
    st.subheader("4. Spending vs. Neonatal Mortality")
    neo_cols = [c for c in df.columns if "neonatal_mortality" in c]
    y_col_4 = neo_cols[0] if neo_cols else "infant_mortality"

    # FIX: Use 'brushed_df'
    fig4 = px.scatter(
        brushed_df,
        x="Health expenditure per capita - Total",
        y=y_col_4,
        color="country_x",
        hover_name="country_x",
        labels={y_col_4: "Neonatal Mortality", "Health expenditure per capita - Total": "Health Expenditure"},
        title="Expenditure vs. Neonatal Mortality (Filtered)"
    )
    st.plotly_chart(fig4, use_container_width=True)

# --- HEATMAP ---
st.subheader("5. Global Correlations (Filtered)")
col5, _ = st.columns(2)
with col5:
    # Use brushed_df for heatmap too
    numeric_df = brushed_df.select_dtypes(include=["float64", "int64"])
    if len(numeric_df) > 1:
        corr = numeric_df.corr()
        fig5 = px.imshow(corr, aspect="auto", title="Correlation Heatmap")
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Select more points to see correlations.")

# CLEAR BUTTON
st.markdown("---")
if st.button("🔄 Clear Selection"):
    st.session_state.selected_indices = []
    st.rerun()
