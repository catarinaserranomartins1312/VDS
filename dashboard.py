import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="Health Expenditure Dashboard")

# --- SESSION STATE INITIALIZATION ---
# Initialize brushing state
if "selected_indices" not in st.session_state:
    st.session_state.selected_indices = None

# --- HELPER FUNCTIONS ---
def update_brush(fig_key):
    # Get the selection state from the specific chart (fig_key)
    sel = st.session_state.get(fig_key, {}).get("selection", {})
    points = sel.get("points", [])
    
    # Update global selected_indices if points are found
    if points:
        # Uses 'point_index' (snake_case) to match new Streamlit updates
        st.session_state.selected_indices = [p["point_index"] for p in points]

# 2. Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("merged_health_data.csv")
    return df

df = load_data()

# --- SIDEBAR FILTERS (FIXED) ---
st.sidebar.header("Filter Options")

# Fix 1: Convert numpy array to standard list to prevent Streamlit from thinking data changed
all_countries = df['country_x'].unique().tolist()

# Fix 2: Initialize the selection in session state manually
# This prevents the widget from resetting on every rerun
if "country_selection" not in st.session_state:
    st.session_state["country_selection"] = all_countries[:5]

# The Widget: We use 'key' to bind it to the session state we just set up.
# We do NOT use 'default' here because 'key' handles the value.
selected_countries = st.sidebar.multiselect(
    "Select Countries to Compare:", 
    options=all_countries,
    key="country_selection" 
)

# Year Filter
min_year = int(df['year'].min())
max_year = int(df['year'].max())
selected_year = st.sidebar.slider("Select Year", min_year, max_year, max_year)

# --- FILTERING LOGIC ---

# Step 1: Filter by Sidebar
filtered_df = df[df['country_x'].isin(selected_countries)]
year_df = filtered_df[filtered_df['year'] == selected_year]

# Step 2: Apply Brush (Highlighting logic)
def apply_brush(input_df):
    if st.session_state.selected_indices is None:
        return input_df
    # Filter based on the indices of the points selected in the charts
    return input_df.iloc[st.session_state.selected_indices]

brushed_df = apply_brush(year_df)

# --- DASHBOARD LAYOUT ---

st.title("Analysis: Health Expenditure vs. Health Indicators")
st.markdown(f"Exploring the relationship between healthcare spending and health maternal and infant indicators for the year **{selected_year}**.")

# Grid: Row 1
col1, col2 = st.columns(2)

# Insight 1: The Preston Curve
with col1:
    st.subheader("1. Preston Curve Variation")
    st.markdown("*Does higher spending lead to longer lives?*")
    
    fig1 = px.scatter(brushed_df, 
                      x="Health expenditure per capita - Total", 
                      y="life_expect", 
                      color="country_x", 
                      size="life_expect", 
                      labels={
                          "life_expect": "Life Expectancy (Years)",
                          "Health expenditure per capita - Total": "Health Expenditure (PPP USD)"
                      },
                      hover_name="country_x",
                      title=f"Expenditure vs. Life Expectancy ({selected_year})")
    
    st.plotly_chart(
        fig1,
        use_container_width=True,
        selection_mode="points",
        on_select="rerun",
        key="fig1"
    )
    update_brush("fig1")

# Insight 2: Influence on Infant Mortality
with col2:
    st.subheader("2. Spending vs. Infant Mortality")
    st.markdown("*Impact of spending on Infant Mortality.*")
    
    fig2 = px.scatter(brushed_df, 
                      x="Health expenditure per capita - Total", 
                      y="infant_mortality", 
                      color="country_x",
                      size="infant_mortality",
                      labels={
                          "infant_mortality": "Infant Mortality",
                          "Health expenditure per capita - Total": "Health Expenditure (PPP USD)"
                      },
                      hover_name="country_x",
                      title=f"Expenditure vs. Infant Mortality ({selected_year})")
    
    st.plotly_chart(
        fig2,
        use_container_width=True,
        selection_mode="points",
        on_select="rerun",
        key="fig2"
    )
    update_brush("fig2")

# Grid: Row 2
col3, col4 = st.columns(2)

# Insight 3: Influence on Malnourishment
with col3:
    st.subheader("3. Spending vs. Undernourishment")
    st.markdown("*Impact of spending on Undernourishment.*")
    
    # Safe column finder
    undernourish_cols = [c for c in df.columns if "prev_unde" in c]
    y_col_3 = undernourish_cols[0] if undernourish_cols else "life_expect"

    fig3 = px.scatter(brushed_df, 
                      x="Health expenditure per capita - Total", 
                      y=y_col_3,
                      color="country_x",
                      hover_name="country_x",
                      labels={
                          y_col_3: "Prevalence of Undernourishment",
                          "Health expenditure per capita - Total": "Health Expenditure (PPP USD)"
                      },
                      title=f"Expenditure vs. Undernourishment ({selected_year})")
    
    st.plotly_chart(
        fig3,
        use_container_width=True,
        selection_mode="points",
        on_select="rerun",
        key="fig3"
    )
    update_brush("fig3")

# Insight 4: Influence on Neonatal Mortality
with col4:
    st.subheader("4. Spending vs. Neonatal Mortality")
    st.markdown("*Impact of spending on Neonatal Mortality.*")
    
    # Safe column finder
    neonatal_cols = [c for c in df.columns if "neonatal_mortality" in c]
    y_col_4 = neonatal_cols[0] if neonatal_cols else "infant_mortality"

    fig4 = px.scatter(brushed_df, 
                      x="Health expenditure per capita - Total", 
                      y=y_col_4,
                      color="country_x",
                      hover_name="country_x",
                      labels={
                          y_col_4: "Neonatal Mortality",
                          "Health expenditure per capita - Total": "Health Expenditure (PPP USD)"
                      },
                      title=f"Expenditure vs. Neonatal Mortality ({selected_year})")
    
    st.plotly_chart(
        fig4,
        use_container_width=True,
        selection_mode="points",
        on_select="rerun",
        key="fig4"
    )
    update_brush("fig4")

# Grid: Row 3 (Heatmap)
col5, col6 = st.columns(2)

with col5:
    st.subheader("5. Global Correlations")
    st.markdown("*Heatmap of the relationship between all numerical features.*")
    
    # Only use numeric columns for correlation to avoid errors
    numeric_df = brushed_df.select_dtypes(include=['float64', 'int64'])
    corr = numeric_df.corr()
    
    fig5 = px.imshow(corr, text_auto=False, aspect="auto", title="Correlation Heatmap")
    st.plotly_chart(fig5, use_container_width=True)

# --- CLEAR BUTTON ---
st.markdown("---")
if st.button("🔄 Clear Selection"):
    st.session_state.selected_indices = None
    st.rerun()
