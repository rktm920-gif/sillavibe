import streamlit as st
import pandas as pd
import plotly.express as px

# --- 페이지 설정 ---
st.set_page_config(
    page_title="연도별/지역별 고용지표 분석 대시보드",
    page_icon="📊",
    layout="wide",
)

# --- 사이드바 스타일 적용 ---
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #2E2E2E;
}
[data-testid="stSidebar"] * {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# --- 데이터 로딩 및 캐싱 ---
@st.cache_data
def load_data():
    """CSV 파일을 로드하고 취업률/실업률을 계산합니다."""
    file_path = '경제활동_통합.csv'
    df = pd.read_csv(file_path)
    df['지역'] = df['지역'].replace('계', '전국')
    df['취업률'] = (df['취업자 (천명)'] / df['경제활동인구 (천명)'] * 100).round(2)
    df['실업률'] = (df['실업자 (천명)'] / df['경제활동인구 (천명)'] * 100).round(2)
    df.fillna(0, inplace=True)
    return df

df = load_data()

# --- 사이드바 필터 (FR-02) ---
st.sidebar.header("📊 필터 옵션")
all_years = sorted(df['년도'].unique(), reverse=True)
all_regions = sorted(df['지역'].unique())
selected_years = st.sidebar.multiselect(
    '연도 선택',
    all_years,
    default=all_years[:1]
)
selected_regions = st.sidebar.multiselect(
    '지역 선택',
    all_regions,
    default=['전국', '서울특별시', '부산광역시']
)

st.sidebar.markdown("---")
st.sidebar.header("🎨 테마 설정")
theme_options = {
    '흰색 배경': 'plotly_white',
    '어두운 배경': 'plotly_dark',
    '기본': 'plotly',
    'ggplot 스타일': 'ggplot2',
    'Seaborn 스타일': 'seaborn',
    '단순 스타일': 'simple_white'
}
selected_korean_theme = st.sidebar.selectbox(
    '차트 테마를 선택하세요.',
    list(theme_options.keys()),
    index=0
)
selected_theme = theme_options[selected_korean_theme]

# --- 동적 메인 테마 적용 (진단용) ---
main_bg_color = "#0E1117"  # 어두운 테마로 고정
main_text_color = "white"

st.markdown(f"""
<style>
.main .block-container {{
    background-color: {main_bg_color};
    color: {main_text_color};
}}
h1, h2, h3, h4, h5, h6 {{
    color: {main_text_color};
}}
.stRadio label {{
    color: {main_text_color};
}}
</style>
""", unsafe_allow_html=True)

# 데이터 필터링
if not selected_years or not selected_regions:
    st.warning("사이드바에서 하나 이상의 연도와 지역을 선택하세요.")
    st.stop()

filtered_df = df[df['년도'].isin(selected_years) & df['지역'].isin(selected_regions)]

# --- 메인 대시보드 ---
st.title("📊 연도별/지역별 고용지표 분석 대시보드")
st.markdown("PRD 요구사항에 따라 제작된 인터랙티브 대시보드입니다.")

# --- 요약 정보 카드 (FR-4.3.1) ---
st.subheader("요약 정보")
avg_employment_rate = filtered_df['취업률'].mean()
avg_unemployment_rate = filtered_df['실업률'].mean()
col1, col2 = st.columns(2)
with col1:
    st.metric(label="평균 취업률", value=f"{avg_employment_rate:.2f} %")
with col2:
    st.metric(label="평균 실업률", value=f"{avg_unemployment_rate:.2f} %")

st.markdown("---")

# --- 시각화 (FR-4.3.2 & 4.3.3) ---
st.subheader("데이터 시각화")
metric_to_show = st.radio(
    "어떤 지표를 보시겠습니까?",
    ('취업률', '실업률'),
    horizontal=True
)

if len(selected_years) == 1:
    st.markdown(f"#### {selected_years[0]}년 지역별 {metric_to_show} 비교")
    fig = px.bar(
        filtered_df.sort_values(by=metric_to_show, ascending=False),
        x='지역',
        y=metric_to_show,
        color='지역',
        title=f"{selected_years[0]}년 지역별 {metric_to_show}",
        template=selected_theme
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.markdown(f"#### 연도별 {metric_to_show} 변화 추이")
    fig = px.line(
        filtered_df.sort_values(by=['년도', '지역']),
        x='년도',
        y=metric_to_show,
        color='지역',
        markers=True,
        title=f"지역별 {metric_to_show} 변화 추이",
        template=selected_theme
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- 상세 데이터 테이블 (FR-4.3.4) ---
st.subheader("상세 데이터")
st.dataframe(filtered_df, use_container_width=True)