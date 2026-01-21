import streamlit as st
import pandas as pd
import plotly.express as px

# 1. PAGE CONFIG
st.set_page_config(layout="wide", page_title="Health Expenditure Dashboard")

# 2. SESSION STATE SETUP
# We use a set to store selected indices (rows) to keep it fast
if "selected_indices" not in st.session_state:
    st.session_state.selected_indices = []

# Initialize country selection to avoid "Reset" bugs
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

# FIX: Convert to standard list to stop the "Reset" bug
all_countries = df["country_x"].unique().tolist()

# Set default selection manually if empty
if not st.session_state.country_selection:
    st.session_state.country_selection = all_countries[:5]

# The Widget (Notice: No 'default' param, 'key' handles it)
selected_countries = st.sidebar.multiselect(
    "Select Countries to Compare",
    options=all_countries,
    key="country_selection"
)

# Year Slider
min_year = int(df["year"].min())
max_year = int(df["year"].max())
selected_year = st.sidebar.slider("Select Year", min_year, max_year, max_year)

# 5. DATA FILTERING
# Create the main dataframe for this year
year_df = df[
    (df["country_x"].isin(selected_countries)) & 
    (df["year"] == selected_year)
]

# 6. BRUSHING FUNCTION
# This function updates the global selection based on clicks
def update_brush(fig_key):
    # Get the selection data from the chart
    sel = st.session_state.get(fig_key, {}).get("selection", {})
    points = sel.get("points", [])
    
    if points:
        # FIX: We use 'point_index' which is always available and safe
        st.session_state.selected_indices = [p["point_index"] for p in points]

# Helper to apply the selection to data
def get_brushed_df(data):
    if not st.session_state.selected_indices:
        return data # Return all data if nothing selected
    # Filter data by the selected row numbers
    return data.iloc[st.session_state.selected_indices]

# 7. DASHBOARD LAYOUT
st.title("Analysis: Health Expenditure vs. Health Indicators")
st.markdown(f"Exploring relationships for the year **{selected_year}**.")

# --- ROW 1 ---
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
        labels={"life_expect": "Life Expectancy", "Health expenditure per capita - Total": "Health Expenditure"},
        title="Expenditure vs. Life Expectancy"
    )
    # The Chart with Interaction
    st.plotly_chart(
        fig1, use_container_width=True,
        selection_mode="points", on_select="rerun", key="fig1"
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
        labels={"infant_mortality": "Infant Mortality", "Health expenditure per capita - Total": "Health Expenditure"},
        title="Expenditure vs. Infant Mortality"
    )
    st.plotly_chart(
        fig2, use_container_width=True,
        selection_mode="points", on_select="rerun", key="fig2"
    )
    update_brush("fig2")

# --- ROW 2 ---
col3, col4 = st.columns(2)

with col3:
    st.subheader("3. Spending vs. Undernourishment")
    # Safe column finder
    under_cols = [c for c in df.columns if "prev_unde" in c]
    y_col_3 = under_cols[0] if under_cols else "life_expect"

    fig3 = px.scatter(
        year_df,
        x="Health expenditure per capita - Total",
        y=y_col_3,
        color="country_x",
        hover_name="country_x",
        labels={y_col_3: "Undernourishment", "Health expenditure per capita - Total": "Health Expenditure"},
        title="Expenditure vs. Undernourishment"
    )
    st.plotly_chart(
        fig3, use_container_width=True,
        selection_mode="points", on_select="rerun", key="fig3"
    )
    update_brush("fig3")

with col4:
    st.subheader("4. Spending vs. Neonatal Mortality")
    # Safe column finder
    neo_cols = [c for c in df.columns if "neonatal_mortality" in c]
    y_col_4 = neo_cols[0] if neo_cols else "infant_mortality"

    fig4 = px.scatter(
        year_df,
        x="Health expenditure per capita - Total",
        y=y_col_4,
        color="country_x",
        hover_name="country_x",
        labels={y_col_4: "Neonatal Mortality", "Health expenditure per capita - Total": "Health Expenditure"},
        title="Expenditure vs. Neonatal Mortality"
    )
    st.plotly_chart(
        fig4, use_container_width=True,
        selection_mode="points", on_select="rerun", key="fig4"
    )
    update_brush("fig4")

# --- ROW 3 (Correlations) ---
st.subheader("5. Global Correlations (Filtered)")
col5, _ = st.columns(2)

with col5:
    # Get the data corresponding to the brush
    brushed_data = get_brushed_df(year_df)
    
    # Filter only numeric columns for correlation
    numeric_df = brushed_data.select_dtypes(include=["float64", "int64"])
    
    # Show heatmap only if we have enough data
    if len(numeric_df) > 1:
        corr = numeric_df.corr()
        fig5 = px.imshow(corr, aspect="auto", title="Correlation Heatmap")
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Please select more points to view correlations.")

# 8. CLEAR SELECTION BUTTON
st.markdown("---")
if st.button("🔄 Clear Selection"):
    st.session_state.selected_indices = []
    st.rerun()
