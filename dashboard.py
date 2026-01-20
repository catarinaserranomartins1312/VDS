import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration (The "One Screen" Setup)
st.set_page_config(layout="wide", page_title="Relationship between Countries' Health Expenditure and Healthcare Indicators")

if "selected_indices" not in st.session_state:
    st.session_state.selected_indices = None

def update_brush(fig_key):
    sel = st.session_state.get(fig_key, {}).get("selection", {})
    points = sel.get("points", [])
    if points:
        st.session_state.selected_indices = [p["point_index"] for p in points]

# 2. Load Your Data (Cache it so it doesn't reload every interaction)
@st.cache_data
def load_data():
    df = pd.read_csv("merged_health_data.csv")
    return df

df = load_data()
#st.write(df.columns)

all_countries = df['country_x'].unique()
selected_countries = st.sidebar.multiselect(
    "Select Countries to Compare:", 
    options=all_countries, 
    default=all_countries[:5] 
)

# Year Filter (Slider is better for time)
min_year = int(df['year'].min())
max_year = int(df['year'].max())
selected_year = st.sidebar.slider("Select Year", min_year, max_year, max_year)

# Filter the dataframe based on selection
filtered_df = df[df['country_x'].isin(selected_countries)]
# specific slice for the selected year for the scatter plots
year_df = filtered_df[filtered_df['year'] == selected_year]

def apply_brush(df):
    if st.session_state.selected_indices is None:
        return df
    return df.iloc[st.session_state.selected_indices]

brushed_df = apply_brush(year_df)

# 4. Main Dashboard Area
st.title("Analysis: Health Expenditure vs. Health Indicators")
st.markdown(f"Exploring the relationship between healthcare spending and health maternal and infant indicators for the year **{selected_year}**.")

# Grid with 2 columns
col1, col2 = st.columns(2)

#Insight 1: The Preston Curve
with col1:
    st.subheader("1. Preston Curve Variation")
    st.markdown("*Does higher spending lead to longer lives?*")
    
    # Scatter: Expenditure vs Life Expectancy
    fig1 = px.scatter(brushed_df, 
                      x="Health expenditure per capita - Total", 
                      y="life_expect", 
                      color="country_x", 
                      size="life_expect", 
                      labels={
                          "life_expect": "Life Expectancy (Years)",
                          "Health expenditure per capita - Total": "Health Expenditure (PPP USD, log scale)"
                      },
                      hover_name="country_x",
                      title=f"Health Expenditure vs. Life Expectancy ({selected_year})")
    # st.plotly_chart(fig1, use_container_width=True)

    st.plotly_chart(
        fig1,
        use_container_width=True,
        selection_mode="points",
        on_select="rerun",
        key="fig1"
    )
    
    update_brush("fig1")
    ## new

#Insight 2: Influence on Mortality
with col2:
    st.subheader("2. Spending vs. Mortality")
    st.markdown("*Impact of spending on Infant Mortality.*")
    
    # Scatter: Expenditure vs Infant Mortality
    fig2 = px.scatter(brushed_df, 
                      x="Health expenditure per capita - Total", 
                      y="infant_mortality", # Using your actual column name
                      color="country_x",
                      size="infant_mortality",
                      labels = {
                          "infant_mortality": "Infant Mortality",
                          "Health expenditure per capita - Total": "Health Expenditure (PPP USD, log scale)"
                      },
                      hover_name="country_x",
                      title=f"Health Expenditure vs. Infant Mortality ({selected_year})")
    # st.plotly_chart(fig2, use_container_width=True)

    st.plotly_chart(
        fig2,
        use_container_width=True,
        selection_mode="points",
        on_select="rerun",
        key="fig2"
    )

    update_brush("fig2")

# Row 2
col3, col4 = st.columns(2)

#Insight 3: Influence on Malnourishment
with col3:
    st.subheader("3. Spending vs. Prevalence of Undernourishment")
    st.markdown("*Impact of spending on Undernourishment.*")
    
    undernourishment_col = [c for c in df.columns if "prev_unde" in c][0]

    fig3 = px.scatter(brushed_df, 
                      x="Health expenditure per capita - Total", 
                      y="prev_undernourishment",
                      color="country_x",
                      hover_name="country_x",
                      labels = {
                          "prev_undernourishment": "Prevalence of Undernourishment",
                          "Health expenditure per capita - Total": "Health Expenditure (PPP USD, log scale)"
                      },
                      title=f"Health Expenditure vs. Prevalence of Undernourishment ({selected_year})")
    # st.plotly_chart(fig3, use_container_width=True)

    st.plotly_chart(
        fig3,
        use_container_width=True,
        selection_mode="points",
        on_select="rerun",
        key="fig3"
    )

    update_brush("fig3")

#Insight 4: Influence on Neonatal Mortality
with col4:
    st.subheader("4. Spending vs. Neonatal Mortality")
    st.markdown("*Impact of spending on Neonatal Mortality.*")
    
    undernourishment_col = [c for c in df.columns if "neonatal_mortality" in c][0]

    fig4 = px.scatter(brushed_df, 
                      x="Health expenditure per capita - Total", 
                      y="neonatal_mortality",
                      color="country_x",
                      hover_name="country_x",
                      labels = {
                          "neonatal_mortality": "Neonatal Mortality",
                          "Health expenditure per capita - Total": "Health Expenditure (PPP USD, log scale)"
                      },
                      title=f"Health Expenditure vs. Neonatal Mortality ({selected_year})")
    # st.plotly_chart(fig4, use_container_width=True)

    st.plotly_chart(
        fig4,
        use_container_width=True,
        selection_mode="points",
        on_select="rerun",
        key="fig4"
    )

    update_brush("fig4")

# Row 3
col5, col6 = st.columns(2)

#Insight 5: Correlation Matrix ---
with col5:
    st.subheader("5. Global Correlations")
    st.markdown("*Heatmap of the relationship between all numerical features.*")
    
    # Select only numeric columns to avoid errors
    numeric_df = brushed_df.select_dtypes(include=['float64', 'int64'])
    corr = numeric_df.corr()
    
    fig5 = px.imshow(corr, text_auto=False, aspect="auto", title="Correlation Heatmap")
    st.plotly_chart(fig5, use_container_width=True)
## new
st.markdown("---")
if st.button("🔄 Clear Selection"):
    st.session_state.selected_indices = None
    st.experimental_rerun()
## new












