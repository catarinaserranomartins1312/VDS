import streamlit as st
import pandas as pd
import plotly.express as px

# config page
st.set_page_config(layout="wide", page_title="Health Expenditure Dashboard")

# setup settings
if "selected_indices" not in st.session_state:
    st.session_state.selected_indices = []

if "country_selection" not in st.session_state:
    st.session_state.country_selection = [] 

# upload data 
@st.cache_data
def load_data():
    df = pd.read_csv("merged_health_data.csv")
    return df

df = load_data()

# sidebar filters
st.sidebar.header("Filter Options")


# Prevent reset bug
all_countries = sorted(df["country_x"].unique().tolist())

# Default to 5 countries if nothing selected yet
if not st.session_state.country_selection:
    st.session_state.country_selection = all_countries[:5]

selected_countries = st.sidebar.multiselect(
    "Select Countries to Compare",
    options=all_countries,
    default=st.session_state.country_selection,
    key="country_selection"
)

min_year = int(df["year"].min())
max_year = int(df["year"].max())
selected_year = st.sidebar.slider("Select Year", min_year, max_year, max_year)

# base data in year filter
year_df = df[
    (df["country_x"].isin(selected_countries)) &
    (df["year"] == selected_year)
].copy()

# dashboard initial settings
st.title("Analysis: Health Expenditure vs. Health Indicators")
st.markdown(f"Exploring relationships for the year **{selected_year}**.")

col1, col2 = st.columns(2)

BRUSH_KEY = "preston_brush"

# insight 1: variation of a preston curve
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

    fig1.update_layout(dragmode="select")
    
event = st.plotly_chart(
        fig1,
        use_container_width=True,
        selection_mode="points",          
        on_select="rerun",
        key=BRUSH_KEY
    )

selected_points = st.session_state.get(f"_{BRUSH_KEY}_selected", {}).get("points", [])

if selected_points:
    # point_index refers to the row index in the data passed to px.scatter
    selected_indices = [p["point_index"] for p in selected_points]
    brushed_df = year_df.iloc[selected_indices]
    st.session_state.selected_rows = selected_indices
else:
    brushed_df = year_df
    st.session_state.selected_rows = []

# insight 2 - impact of spending in infant mortality
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
        title="Expenditure vs. Infant Mortality"
    )
    st.plotly_chart(fig2, use_container_width=True)

col3, col4 = st.columns(2)

# insight 3 - impact of spending in Undernourishment
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
        title="Expenditure vs. Undernourishment"
    )
    st.plotly_chart(fig3, use_container_width=True)

# insight 4 - impact of spending in Neonatal Mortality
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
        title="Expenditure vs. Neonatal Mortality"
    )
    st.plotly_chart(fig4, use_container_width=True)

# insight 5 - correlation between the variables
st.subheader("5. Global Correlations")
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

# Reset button
if st.button("Clear Selection"):
    if f"_{BRUSH_KEY}_selected" in st.session_state:
        del st.session_state[f"_{BRUSH_KEY}_selected"]
    st.session_state.selected_rows = []
    st.rerun()


