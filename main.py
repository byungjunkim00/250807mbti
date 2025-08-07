import streamlit as st
import pandas as pd
import altair as alt

# --- Load CSV data ---
@st.cache_data
def load_data():
    df = pd.read_csv("countriesMBTI_16types.csv")
    return df

df = load_data()
mbti_columns = df.columns[1:]

# --- Find dominant MBTI type per country ---
df["Dominant_Type"] = df[mbti_columns].idxmax(axis=1)
df["Dominant_Value"] = df[mbti_columns].max(axis=1)

# --- Page title ---
st.title("🌍 국가별 MBTI 분석 대시보드")

# --- Tabs for different functionalities ---
tab1, tab2 = st.tabs(["📊 국가별 MBTI 비율", "🏆 국가별 최빈 MBTI 유형"])

# ---------------------
# Tab 1: 국가별 MBTI 비율
# ---------------------
with tab1:
    st.header("📊 선택한 국가의 MBTI 분석")

    # --- 나라 선택
    country_list = sorted(df["Country"].unique())
    selected_country = st.selectbox("국가를 선택하세요:", country_list)

    # --- 해당 국가 데이터 추출
    country_data = df[df["Country"] == selected_country].iloc[0]
    mbti_values = country_data[mbti_columns]

    # --- MBTI 16유형 비율 시각화
    mbti_df = pd.DataFrame({
        "MBTI": mbti_columns,
        "Percentage": mbti_values.values
    }).sort_values(by="Percentage", ascending=False)

    chart_16 = alt.Chart(mbti_df).mark_bar().encode(
        x=alt.X("MBTI:N", sort="-y"),
        y=alt.Y("Percentage:Q", title="비율"),
        tooltip=["MBTI", "Percentage"]
    ).properties(
        title=f"{selected_country}의 16가지 MBTI 비율",
        width=700,
        height=400
    )
    st.altair_chart(chart_16, use_container_width=True)

    # --- MBTI 그룹화 분석
    st.subheader("🧠 MBTI 네 가지 축 분석")

    # MBTI 그룹화 함수
    def group_mbti(values):
        groups = {
            "I": sum(values[type_] for type_ in mbti_columns if type_.startswith("I")),
            "E": sum(values[type_] for type_ in mbti_columns if type_.startswith("E")),
            "S": sum(values[type_] for type_ in mbti_columns if type_[1] == "S"),
            "N": sum(values[type_] for type_ in mbti_columns if type_[1] == "N"),
            "T": sum(values[type_] for type_ in mbti_columns if type_[2] == "T"),
            "F": sum(values[type_] for type_ in mbti_columns if type_[2] == "F"),
            "J": sum(values[type_] for type_ in mbti_columns if type_[3] == "J"),
            "P": sum(values[type_] for type_ in mbti_columns if type_[3] == "P"),
        }
        return groups

    grouped = group_mbti(country_data)

    # 시각화용 데이터프레임 생성
    grouped_df = pd.DataFrame({
        "Dimension": ["I/E", "S/N", "T/F", "J/P"],
        "Type1": ["I", "S", "T", "J"],
        "Type2": ["E", "N", "F", "P"],
        "Value1": [grouped["I"], grouped["S"], grouped["T"], grouped["J"]],
        "Value2": [grouped["E"], grouped["N"], grouped["F"], grouped["P"]],
    })

    # Melt for stacked bar chart
    melt_df = pd.melt(grouped_df,
                      id_vars=["Dimension"],
                      value_vars=["Value1", "Value2"],
                      var_name="Group",
                      value_name="Percentage")

    # Mapping label back
    melt_df["Type"] = melt_df.apply(
        lambda row: grouped_df.loc[row.name // 2, "Type1"] if row["Group"] == "Value1"
        else grouped_df.loc[row.name // 2, "Type2"],
        axis=1
    )

    chart_group = alt.Chart(melt_df).mark_bar().encode(
        x=alt.X("Dimension:N", title="MBTI 축"),
        y=alt.Y("Percentage:Q", stack="normalize", title="비율 (%)"),
        color=alt.Color("Type:N", title="MBTI"),
        tooltip=["Dimension", "Type", "Percentage"]
    ).properties(
        title=f"{selected_country}의 MBTI 성향 (I/E, S/N, T/F, J/P)",
        width=600,
        height=400
    )

    st.altair_chart(chart_group, use_container_width=True)

    # --- 데이터 테이블 보기
    with st.expander("📋 MBTI 데이터 테이블 보기"):
        st.dataframe(mbti_df.reset_index(drop=True))


# ---------------------
# Tab 2: 국가별 최빈 MBTI
# ---------------------
with tab2:
    st.header("🏆 각 국가의 최빈 MBTI 유형")

    selected_country2 = st.selectbox("국가 필터링 (전체 또는 선택)", ["(전체)"] + country_list)

    chart_data = df.copy()
    if selected_country2 != "(전체)":
        chart_data = chart_data[chart_data["Country"] == selected_country2]

    bar_chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X("Country:N", sort="-y", title="국가"),
        y=alt.Y("Dominant_Value:Q", title="가장 높은 비율"),
        color=alt.Color("Dominant_Type:N", title="MBTI 유형"),
        tooltip=["Country", "Dominant_Type", "Dominant_Value"]
    ).properties(
        width=800,
        height=500
    )

    st.altair_chart(bar_chart, use_container_width=True)

    with st.expander("📋 전체 국가별 최빈 MBTI 테이블"):
        st.dataframe(df[["Country", "Dominant_Type", "Dominant_Value"]].sort_values(by="Dominant_Value", ascending=False))
