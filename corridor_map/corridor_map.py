import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import platform
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
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
# 데이터 로드 및 전처리 
# ---------------------------------------------------------
@st.cache_data
def load_faf():
    url = "https://github.com/bnn05195/data-science/releases/download/v1.0/FAF5.parquet"
    return pd.read_parquet(url)

@st.cache_data
def load_state_description():
    try:
        meta = pd.read_excel("../data/FAF5_metadata.xlsx", sheet_name="State")
        meta = meta.dropna(subset=["Numeric Label", "Description"])
        return {str(int(float(row["Numeric Label"]))): str(row["Description"]) for _, row in meta.iterrows()}
    except: return {}

# 지도 좌표 및 약어 데이터
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

faf_raw = load_faf()
STATE_DESC_MAP = load_state_description()

year_cols = [c for c in faf_raw.columns if c.startswith("tons_")]
available_years = sorted([c.replace("tons_", "") for c in year_cols])

truck_df = faf_raw.dropna(subset=["dms_mode", "dms_orig", "dms_dest"]).copy()
truck_df = truck_df[truck_df["dms_mode"] == 1]
truck_df["orig_state_clean"] = (truck_df["dms_orig"] // 10).astype(int).astype(str)
truck_df["dest_state_clean"] = (truck_df["dms_dest"] // 10).astype(int).astype(str)

# ---------------------------------------------------------
# UI 및 시각화
# ---------------------------------------------------------
st.header("미국 전체 트럭 물류 통로")

# 상위 N개 슬라이더를 제거하고 연도 선택만 남김
selected_year = st.selectbox("연도 선택", options=available_years, index=0)
target_year_col = f"tons_{selected_year}"

# 주 내 이동(출발=도착) 제외
corridor_df = truck_df[truck_df['orig_state_clean'] != truck_df['dest_state_clean']].copy()
corridor_tons = corridor_df.groupby(['orig_state_clean', 'dest_state_clean'])[target_year_col].sum().reset_index()

# 물동량이 0보다 큰 '모든' 유효 경로만 필터링
corridor_tons = corridor_tons[corridor_tons[target_year_col] > 0]

# 약어 및 좌표 매핑
corridor_tons['orig_abbr'] = corridor_tons['orig_state_clean'].map(STATE_ABBR)
corridor_tons['dest_abbr'] = corridor_tons['dest_state_clean'].map(STATE_ABBR)
corridor_tons = corridor_tons.dropna(subset=['orig_abbr', 'dest_abbr'])

corridor_tons['orig_lat'] = corridor_tons['orig_abbr'].apply(lambda x: STATE_CENTROIDS.get(x, [0,0])[0])
corridor_tons['orig_lon'] = corridor_tons['orig_abbr'].apply(lambda x: STATE_CENTROIDS.get(x, [0,0])[1])
corridor_tons['dest_lat'] = corridor_tons['dest_abbr'].apply(lambda x: STATE_CENTROIDS.get(x, [0,0])[0])
corridor_tons['dest_lon'] = corridor_tons['dest_abbr'].apply(lambda x: STATE_CENTROIDS.get(x, [0,0])[1])

fig_network = go.Figure()
max_tons = corridor_tons[target_year_col].max() if not corridor_tons.empty else 1

# 모든 경로 선 그리기
for _, row in corridor_tons.iterrows():
    # 수천 개의 선이 그려지므로, 물동량이 적은 선은 아주 얇게(0.1), 많은 선은 두껍게(6.0) 차이를 극대화함
    line_width = (row[target_year_col] / max_tons) * 6 + 0.1 
    
    fig_network.add_trace(go.Scattergeo(
        lon=[row['orig_lon'], row['dest_lon']], lat=[row['orig_lat'], row['dest_lat']],
        mode='lines', 
        # 투명도를 0.6에서 0.3으로 낮춰 선이 많이 겹치는 주요 경로망이 스스로 진해지도록 유도
        line=dict(width=line_width, color='rgba(30, 136, 229, 0.3)'), 
        hoverinfo='text', text=f"{row['orig_abbr']} → {row['dest_abbr']}: {row[target_year_col]:,.0f} 천 톤"
    ))

# 주 중심점(빨간 점) 그리기
fig_network.add_trace(go.Scattergeo(
    lon=[coords[1] for coords in STATE_CENTROIDS.values()], lat=[coords[0] for coords in STATE_CENTROIDS.values()],
    hoverinfo='text', text=list(STATE_CENTROIDS.keys()), mode='markers',
    marker=dict(size=4, color='rgb(255, 100, 100)', line=dict(width=1, color='darkred'))
))

fig_network.update_layout(
    title=f"<b>[{selected_year}] 미국 전체 트럭 물류 네트워크망</b>",
    showlegend=False,
    geo=dict(scope='usa', projection_type='albers usa', bgcolor='rgba(0,0,0,0)'),
    margin=dict(l=0, r=0, t=50, b=0)
)
st.plotly_chart(fig_network, use_container_width=True)
# ---------------------------------------------------------
# 상위 10개 주 물동량 표 
# ---------------------------------------------------------
st.markdown("---")
st.subheader("물동량 발생 기준 상위 10개 주")

# 출발지(Origin) 기준으로 전체 물동량 합산
top10_states = truck_df.groupby('orig_state_clean')[target_year_col].sum().reset_index()

# 주 이름(Full Name)과 약어(Abbr)를 결합하여 새 컬럼 생성
top10_states['주 이름'] = top10_states['orig_state_clean'].apply(
    lambda x: f"{STATE_DESC_MAP.get(x, x)} ({STATE_ABBR.get(x, x)})"
)

# 물동량 기준 내림차순 정렬 후 상위 10개 추출
top10_states = top10_states.sort_values(by=target_year_col, ascending=False).head(10)

# 필요한 컬럼만 선택 및 이름 변경
top10_states = top10_states[['주 이름', target_year_col]]
top10_states.columns = ['미국 주 (State)', f'{selected_year}년 총 발생 물동량 (천 톤)']

# 가독성을 위해 숫자에 천 단위 콤마 적용
top10_states[f'{selected_year}년 총 발생 물동량 (천 톤)'] = top10_states[f'{selected_year}년 총 발생 물동량 (천 톤)'].apply(lambda x: f"{x:,.0f}")

# 인덱스를 1위부터 10위로 깔끔하게 리셋
top10_states.reset_index(drop=True, inplace=True)
top10_states.index = top10_states.index + 1

# Streamlit 표(Table) 컴포넌트로 출력
st.table(top10_states)