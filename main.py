import streamlit as st
import pandas as pd
import altair as alt

# --- Load CSV data ---
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

# --- Find dominant MBTI type per country ---
mbti_columns = df.columns[1:]
df["Dominant_Type"] = df[mbti_columns].idxmax(axis=1)
df["Dominant_Value"] = df[mbti_columns].max(axis=1)

# --- Title ---
st.title("🌍 Countries and Their Dominant MBTI Type")

# --- Country filter ---
selected_country = st.selectbox("Select a country to highlight", ["(All)"] + sorted(df["Country"].tolist()))

# --- Altair Bar Chart ---
chart_data = df.copy()

highlight = alt.selection_single(fields=["Country"], bind="legend")

base = alt.Chart(chart_data).mark_bar().encode(
    x=alt.X("Country:N", sort="-y", title="Country"),
    y=alt.Y("Dominant_Value:Q", title="Dominant MBTI Proportion"),
    color=alt.Color("Dominant_Type:N", legend=alt.Legend(title="MBTI Type")),
    tooltip=["Country", "Dominant_Type", "Dominant_Value"]
).properties(
    width=800,
    height=500
)

if selected_country != "(All)":
    chart_data = chart_data[chart_data["Country"] == selected_country]
    base = base.transform_filter(
        alt.datum.Country == selected_country
    )

st.altair_chart(base, use_container_width=True)

# --- Optional: Data Table ---
with st.expander("📋 Show Data Table"):
    st.dataframe(df[["Country", "Dominant_Type", "Dominant_Value"]].sort_values(by="Dominant_Value", ascending=False))
