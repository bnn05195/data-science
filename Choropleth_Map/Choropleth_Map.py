import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import platform
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
# 데이터 로드 함수
# ---------------------------------------------------------
@st.cache_data
def load_faf() -> pd.DataFrame:
    
    url = "https://github.com/bnn05195/data-science/releases/download/v1.0/FAF5.parquet"
    return pd.read_parquet(url)

@st.cache_data
def load_sctg2_description() -> dict:
    try:
        meta = pd.read_excel("../data/FAF5_metadata.xlsx", sheet_name="Commodity (SCTG2)")
        meta = meta.dropna(subset=["Numeric Label", "Description"])
        
        # '01'이든 1.0이든 무조건 정수 1로 바꾼 뒤 다시 문자열 '1'로 통일하여 사전(dict) 생성
        mapping = {}
        for _, row in meta.iterrows():
            try:
                clean_key = str(int(float(row["Numeric Label"])))
                mapping[clean_key] = str(row["Description"])
            except:
                continue
        return mapping
    except Exception:
        return {}

@st.cache_data
def load_state_description() -> dict:
    try:
        meta = pd.read_excel("../data/FAF5_metadata.xlsx", sheet_name="State")
        meta = meta.dropna(subset=["Numeric Label", "Description"])
        
        mapping = {}
        for _, row in meta.iterrows():
            try:
                clean_key = str(int(float(row["Numeric Label"])))
                mapping[clean_key] = str(row["Description"])
            except:
                continue
        return mapping
    except Exception:
        return {}

def filter_truck(df: pd.DataFrame) -> pd.DataFrame:
    """트럭만 (dms_mode == 1) 필터링"""
    return df.loc[df["dms_mode"] == 1].copy()

# 지도를 그리기 위한 미국 2자리 주 약어 사전 (숫자를 문자열 키로 변경)
STATE_ABBR = {
    '1': 'AL', '2': 'AK', '4': 'AZ', '5': 'AR', '6': 'CA', '8': 'CO', '9': 'CT', '10': 'DE',
    '11': 'DC', '12': 'FL', '13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN', '19': 'IA',
    '20': 'KS', '21': 'KY', '22': 'LA', '23': 'ME', '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN',
    '28': 'MS', '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH', '34': 'NJ', '35': 'NM',
    '36': 'NY', '37': 'NC', '38': 'ND', '39': 'OH', '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI',
    '45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT', '50': 'VT', '51': 'VA', '53': 'WA',
    '54': 'WV', '55': 'WI', '56': 'WY'
}

# 1. 데이터 불러오기
faf_raw = load_faf()
SCTG2_DESC_MAP = load_sctg2_description()
STATE_DESC_MAP = load_state_description()

# 연도 컬럼 자동 추출
year_cols = [c for c in faf_raw.columns if c.startswith("tons_")]
available_years = sorted([c.replace("tons_", "") for c in year_cols])

if not available_years:
    st.error("데이터에 연도별 물동량(tons_YYYY) 컬럼이 없습니다.")
    st.stop()

# 2. 결측치 제거 + 트럭 필터링
base_cols = ["dms_mode", "sctg2", "dms_orig", "dms_dest"]
missing_cols = [c for c in base_cols if c not in faf_raw.columns]

if missing_cols:
    st.error(f"FAF 데이터에 필요한 기본 컬럼이 없습니다: {missing_cols}")
    st.stop()

clean_df = faf_raw.dropna(subset=base_cols).copy()
truck_df = filter_truck(clean_df)

# 출발지/도착지 및 품목 코드를 모두 '깔끔한 문자열 숫자(예: "15")'로 통일
truck_df["orig_state_clean"] = (truck_df["dms_orig"] // 10).astype(int).astype(str)
truck_df["dest_state_clean"] = (truck_df["dms_dest"] // 10).astype(int).astype(str)
truck_df["sctg2_clean"] = pd.to_numeric(truck_df["sctg2"], errors="coerce").fillna(-1).astype(int).astype(str)

truck_df["sctg2_name"] = truck_df["sctg2_clean"].map(SCTG2_DESC_MAP)
# 엑셀에 없는 99번 같은 코드들은 번호를 그대로 표시
truck_df["sctg2_name"] = truck_df["sctg2_name"].fillna("미분류 코드 (" + truck_df["sctg2_clean"] + ")")


# ---------------------------------------------------------
# UI 구성
# ---------------------------------------------------------
st.header("미국 트럭 물동량 지도")

col1, col2 = st.columns(2)

with col1:
    default_year_idx = available_years.index("2018") if "2018" in available_years else 0
    selected_year = st.selectbox("연도 선택", options=available_years, index=default_year_idx)

with col2:
    unique_items = sorted(truck_df["sctg2_name"].unique())
    all_items = ["전체 품목 합계"] + unique_items
    selected_item = st.selectbox("품목 선택", options=all_items)

view_option = st.radio("분석 기준", options=["출발지 기준 (생산/수출)", "도착지 기준 (소비/수입)"], horizontal=True)


# ---------------------------------------------------------
# 데이터 필터링 및 지도 그리기
# ---------------------------------------------------------
target_year_col = f"tons_{selected_year}"

if selected_item != "전체 품목 합계":
    plot_df = truck_df[truck_df["sctg2_name"] == selected_item].copy()
else:
    plot_df = truck_df.copy()

plot_df[target_year_col] = plot_df[target_year_col].fillna(0)

if "출발" in view_option:
    group_col = "orig_state_clean"
    color_theme = "Blues"
    title_text = f"[{selected_item}]은 어디서 가장 많이 수출되었나? (출발지 기준)"
else:
    group_col = "dest_state_clean"
    color_theme = "Oranges"
    title_text = f"[{selected_item}]은 어디로 가장 많이 수입되었나? (도착지 기준)"

# 주별 합산
state_tons = plot_df.groupby(group_col)[target_year_col].sum().reset_index()

# 지도용 데이터 병합
state_tons["state_abbr"] = state_tons[group_col].map(STATE_ABBR)
state_tons["state_name"] = state_tons[group_col].map(STATE_DESC_MAP)
state_tons = state_tons.dropna(subset=["state_abbr"])

# 지도 출력
if not state_tons.empty and state_tons[target_year_col].sum() > 0:
    fig = px.choropleth(
        state_tons,
        locations="state_abbr",          
        locationmode="USA-states",       
        color=target_year_col,               
        scope="usa",                     
        hover_name="state_name",         
        color_continuous_scale=color_theme,
        title=title_text,
        labels={target_year_col: "물동량(천 톤)", "state_abbr": "주 코드"}
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning(f"선택하신 조건({selected_year}년, {selected_item})에 해당하는 데이터가 없습니다.")