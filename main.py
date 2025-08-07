import streamlit as st
import pandas as pd
import altair as alt

# --- Load CSV data ---
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()

# --- Title ---
st.title("🌐 국가별 MBTI 유형 비율 시각화")

# --- Country selection ---
country_list = sorted(df["Country"].unique())
selected_country = st.selectbox("국가를 선택하세요:", country_list)

# --- Filter selected country ---
country_data = df[df["Country"] == selected_country].iloc[0]
mbti_types = df.columns[1:]
mbti_values = country_data[mbti_types]

# --- Create dataframe for plotting ---
plot_df = pd.DataFrame({
    "MBTI": mbti_types,
    "Percentage": mbti_values.values
}).sort_values(by="Percentage", ascending=False)

# --- Altair Bar Chart ---
chart = alt.Chart(plot_df).mark_bar().encode(
    x=alt.X("MBTI:N", sort="-y"),
    y=alt.Y("Percentage:Q", title="비율"),
    tooltip=["MBTI", "Percentage"]
).properties(
    title=f"{selected_country}의 MBTI 비율",
    width=700,
    height=400
)

st.altair_chart(chart, use_container_width=True)

# --- Show data table ---
with st.expander("📊 데이터 테이블 보기"):
    st.dataframe(plot_df.reset_index(drop=True))
