import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration (The "One Screen" Setup)
st.set_page_config(layout="wide", page_title="Relationship between Countries' Health Expenditure and Healthcare Indicators")

# 2. Load Your Data (Cache it so it doesn't reload every interaction)
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\catar\Downloads\merged_health_data.csv")
    return df

df = load_data()

# 3. Sidebar for Interaction
st.sidebar.header("Filter Options")
# Example: Filter by category
selected_category = st.sidebar.multiselect(
    "Select Category:",
    options=df["category"].unique(),
    default=df["category"].unique()
)
# Filter the dataframe based on selection
filtered_df = df[df["category"].isin(selected_category)]

# 4. Main Dashboard Area
st.title("Project Findings Dashboard")
st.markdown("This dashboard visualizes key insights from the Profiling and Modeling stages.")

# Layout: Create columns for a grid view
col1, col2 = st.columns(2)

# Visualization 1: Feature Distribution (Wrangle/Profile Stage)
with col1:
    st.subheader("1. Distribution of Key Feature")
    fig1 = px.histogram(filtered_df, x="feature_x", color="category", 
                        title="Distribution with Color Encoding")
    st.plotly_chart(fig1, use_container_width=True)

# Visualization 2: Correlation/Scatter (Wrangle Stage)
with col2:
    st.subheader("2. Relationship between X and Y")
    fig2 = px.scatter(filtered_df, x="feature_x", y="feature_y", 
                      color="category", size="importance_metric",
                      hover_data=['id'])
    st.plotly_chart(fig2, use_container_width=True)

# Visualization 3: Model Performance (Model Stage)
col3, col4 = st.columns(2)
with col3:
    st.subheader("3. Model Predictions vs Actual")
    # Assuming you have prediction columns in your dataframe
    fig3 = px.line(filtered_df, x="date", y=["actual", "predicted"],
                   title="Model Accuracy Over Time")
    st.plotly_chart(fig3, use_container_width=True)

# Visualization 4: Interesting Feature/Heatmap
with col4:
    st.subheader("4. Correlation Heatmap")
    fig4 = px.imshow(filtered_df.corr(), text_auto=True, aspect="auto")
    st.plotly_chart(fig4, use_container_width=True)