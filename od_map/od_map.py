import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
import platform
import plotly.graph_objects as go
import plotly.express as px

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# 운영체제에 따라 폰트 다르게 설정하기
os_name = platform.system()
if os_name == "Windows":
    plt.rc("font", family="Malgun Gothic")  # 윈도우
elif os_name == "Darwin":
    plt.rc("font", family="AppleGothic")  # 맥(Mac)
else:
    plt.rc("font", family="NanumGothic")  # 리눅스 (스트림릿 클라우드)

# 마이너스(-) 기호 깨짐 방지
plt.rcParams["axes.unicode_minus"] = False

# ---------------------------------------------------------
# 1. 데이터 로드 및 전처리 
# ---------------------------------------------------------
@st.cache_data
def load_faf():
    url = "https://github.com/bnn05195/data-science/releases/download/v1.0/FAF5.parquet"
    return pd.read_parquet(url)

@st.cache_data
def load_sctg2_description():
    try:
        meta = pd.read_excel("../data/FAF5_metadata.xlsx", sheet_name="Commodity (SCTG2)")
        meta = meta.dropna(subset=["Numeric Label", "Description"])
        return {str(int(float(row["Numeric Label"]))): str(row["Description"]) for _, row in meta.iterrows()}
    except: return {}

@st.cache_data
def load_state_description():
    try:
        meta = pd.read_excel("../data/FAF5_metadata.xlsx", sheet_name="State")
        meta = meta.dropna(subset=["Numeric Label", "Description"])
        return {str(int(float(row["Numeric Label"]))): str(row["Description"]) for _, row in meta.iterrows()}
    except: return {}


STATE_CENTROIDS = {
    'AL': [32.8, -86.7], 'AK': [61.3, -152.4], 'AZ': [34.1, -111.9], 'AR': [34.9, -92.3], 'CA': [36.1, -119.6],
    'CO': [39.0, -105.7], 'CT': [41.5, -72.7], 'DE': [39.3, -75.5], 'FL': [27.7, -81.6], 'GA': [33.0, -83.6],
    'HI': [21.0, -157.8], 'ID': [44.2, -114.4], 'IL': [40.3, -88.9], 'IN': [39.8, -86.2], 'IA': [42.0, -93.4],
    'KS': [38.5, -98.3], 'KY': [37.6, -84.6], 'LA': [31.1, -91.8], 'ME': [44.6, -69.3], 'MD': [39.0, -76.8],
    'MA': [42.2, -71.8], 'MI': [43.3, -84.5], 'MN': [45.6, -93.9], 'MS': [32.7, -89.6], 'MO': [38.4, -92.2],
    'MT': [46.9, -110.4], 'NE': [41.1, -98.2], 'NV': [38.3, -117.0], 'NH': [43.4, -71.5], 'NJ': [40.2, -74.5],
    'NM': [34.8, -106.2], 'NY': [42.1, -74.9], 'NC': [35.6, -79.8], 'ND': [47.5, -100.5], 'OH': [40.3, -82.7],
    'OK': [35.5, -96.9], 'OR': [44.5, -122.1], 'PA': [40.5, -77.2], 'RI': [41.6, -71.5], 'SC': [33.8, -80.9],
    'SD': [44.2, -99.4], 'TN': [35.7, -86.6], 'TX': [31.0, -97.5], 'UT': [40.1, -111.8], 'VT': [44.0, -72.7],
    'VA': [37.7, -78.1], 'WA': [47.4, -121.4], 'WV': [38.4, -80.9], 'WI': [44.2, -89.6], 'WY': [42.7, -107.3],
    'DC': [38.9, -77.0]
}

STATE_ABBR = {
    '1': 'AL', '2': 'AK', '4': 'AZ', '5': 'AR', '6': 'CA', '8': 'CO', '9': 'CT', '10': 'DE',
    '11': 'DC', '12': 'FL', '13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN', '19': 'IA',
    '20': 'KS', '21': 'KY', '22': 'LA', '23': 'ME', '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN',
    '28': 'MS', '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH', '34': 'NJ', '35': 'NM',
    '36': 'NY', '37': 'NC', '38': 'ND', '39': 'OH', '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI',
    '45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT', '50': 'VT', '51': 'VA', '53': 'WA',
    '54': 'WV', '55': 'WI', '56': 'WY'
}

# 데이터 준비
faf_raw = load_faf()
SCTG2_DESC_MAP = load_sctg2_description()
STATE_DESC_MAP = load_state_description()

year_cols = [c for c in faf_raw.columns if c.startswith("tons_")]
available_years = sorted([c.replace("tons_", "") for c in year_cols])

truck_df = faf_raw.dropna(subset=["dms_mode", "sctg2", "dms_orig", "dms_dest"]).copy()
truck_df = truck_df[truck_df["dms_mode"] == 1]

truck_df["orig_state_clean"] = (truck_df["dms_orig"] // 10).astype(int).astype(str)
truck_df["dest_state_clean"] = (truck_df["dms_dest"] // 10).astype(int).astype(str)
truck_df["sctg2_clean"] = pd.to_numeric(truck_df["sctg2"], errors="coerce").fillna(-1).astype(int).astype(str)
truck_df["sctg2_name"] = truck_df["sctg2_clean"].map(SCTG2_DESC_MAP).fillna("기타")

# ---------------------------------------------------------
# 2. UI 구성 (분석 모드 추가)
# ---------------------------------------------------------
st.header("미국 주별 기종점 물동량 분석")

# 분석 모드 선택 (라디오 버튼)
analysis_mode = st.radio(
    "분석 관점 선택",
    ["출발지 기준 (어디로 보내는가?)", "도착지 기준 (어디서 들어오는가?)"],
    horizontal=True
)

col1, col2, col3 = st.columns(3)
with col1:
    selected_year = st.selectbox("연도 선택", options=available_years, index=0)

with col2:
    # 모드에 따라 선택 상자의 라벨 변경
    label = "출발 주(Origin) 선택" if "출발지" in analysis_mode else "도착 주(Destination) 선택"
    unique_states = sorted([c for c in truck_df["orig_state_clean"].unique() if c in STATE_DESC_MAP], key=int)
    selected_state_code = st.selectbox(label, options=unique_states, 
                                        format_func=lambda x: f"{STATE_DESC_MAP.get(x)} ({STATE_ABBR.get(x)})")

with col3:
    selected_item = st.selectbox("품목 선택", options=["전체 품목 합계"] + sorted(truck_df["sctg2_name"].unique()))

# ---------------------------------------------------------
# 3. 데이터 필터링 및 시각화 (동적 로직 적용)
# ---------------------------------------------------------
target_year_col = f"tons_{selected_year}"
state_abbr = STATE_ABBR.get(selected_state_code)

# 분석 모드에 따른 필터링 분기
if "출발지" in analysis_mode:
    # 출발지를 고정하고 도착지별 합계 계산
    plot_df = truck_df[truck_df["orig_state_clean"] == selected_state_code].copy()
    group_col = "dest_state_clean"
    mode_text = "출발"
else:
    # 도착지를 고정하고 출발지별 합계 계산
    plot_df = truck_df[truck_df["dest_state_clean"] == selected_state_code].copy()
    group_col = "orig_state_clean"
    mode_text = "도착"

if selected_item != "전체 품목 합계":
    plot_df = plot_df[plot_df["sctg2_name"] == selected_item]

# 데이터 집계
agg_tons = plot_df.groupby(group_col)[target_year_col].sum().reset_index()
agg_tons["state_abbr"] = agg_tons[group_col].map(STATE_ABBR)
agg_tons = agg_tons.dropna(subset=["state_abbr"])

if not agg_tons.empty:
    # 1. 기본 단계구분도
    max_val = agg_tons[target_year_col].quantile(0.9) if not agg_tons.empty else 100
    fig = px.choropleth(
        agg_tons,
        locations="state_abbr",
        locationmode="USA-states",
        color=target_year_col,
        scope="usa",
        color_continuous_scale="Teal", 
        range_color=[0, max_val],
        labels={target_year_col: "물동량(천 톤)"}
    )

    # 2. 선택한 기준 주(State) 강조 레이어 (황금색)
    fig.add_trace(
        go.Choropleth(
            locations=[state_abbr],
            z=[0],
            locationmode="USA-states",
            colorscale=[[0, 'gold'], [1, 'gold']],
            showscale=False,
            marker_line_color='red',
            marker_line_width=2,
            hoverinfo="location+name"
        )
    )

    # 3. 주 이름 텍스트 레이어 
    text_data = [{'abbr': abbr, 'lat': coords[0], 'lon': coords[1]} for abbr, coords in STATE_CENTROIDS.items()]
    df_text = pd.DataFrame(text_data)

    fig.add_trace(
        go.Scattergeo(
            locations=df_text['abbr'],
            locationmode="USA-states",
            lat=df_text['lat'],
            lon=df_text['lon'],
            text=df_text['abbr'],
            mode='text',
            textfont=dict(size=10, color="black"),
            showlegend=False,
            hoverinfo='skip'
        )
    )

    fig.update_layout(
        title=f"<b>[{selected_year}] {STATE_DESC_MAP.get(selected_state_code)} {mode_text} 물류 흐름 ({selected_item})</b>",
        margin=dict(l=0, r=0, t=50, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.warning(f"{STATE_DESC_MAP.get(selected_state_code)} 관련 데이터가 없습니다.")