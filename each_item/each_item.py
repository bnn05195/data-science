import sys
from pathlib import Path
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import platform

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


@st.cache_data
def load_faf() -> pd.DataFrame:
    url = "https://github.com/bnn05195/data-science/releases/download/v1.0/FAF5.parquet"
    return pd.read_parquet(url)


SCTG2_MAP = {
    1: 'Live animals/fish', 2: 'Cereal grains', 3: 'Other ag prods.', 4: 'Animal feed',
    5: 'Meat/seafood', 6: 'Milled grain prods.', 7: 'Other foodstuffs', 8: 'Alcoholic beverages',
    9: 'Tobacco prods.', 10: 'Monumental or building stone', 11: 'Natural sands', 12: 'Gravel and crushed stone',
    13: 'Nonmetallic minerals', 14: 'Metallic ores', 15: 'Coal', 16: 'Crude petroleum',
    17: 'Gasoline', 18: 'Fuel oils', 19: 'Coal and hydrocarbon products', 20: 'Basic chemicals',
    21: 'Pharmaceuticals', 22: 'Fertilizers', 23: 'Chemical prods.', 24: 'Plastics/rubber',
    25: 'Logs', 26: 'Wood prods.', 27: 'Newsprint/paper', 28: 'Paper articles',
    29: 'Printed prods.', 30: 'Textiles/leather', 31: 'Nonmetal min. prods.', 32: 'Base metals',
    33: 'Articles of base metal', 34: 'Machinery', 35: 'Electronics', 36: 'Motor vehicles',
    37: 'Transport equip.', 38: 'Precision instruments', 39: 'Furniture', 40: 'Misc. mfg. prods.',
    41: 'Waste/scrap', 43: 'Mixed freight', 99: 'Unknown'
}

# 셀렉트박스로 품목 선택
selected_commodity = st.selectbox(
    "품목 선택",
    options=list(SCTG2_MAP.values()),
    index=0
)

# 선택된 품목의 이름으로 딕셔너리에서 코드를 역추적하여 기존 변수에 할당
SCTG2_CODE = [code for code, name in SCTG2_MAP.items() if name == selected_commodity][0]
COMMODITY_EN = selected_commodity


FAF5_COLUMNS = [
    "fr_orig",
    "dms_orig",
    "dms_dest",
    "fr_dest",
    "fr_inmode",
    "dms_mode",
    "fr_outmode",
    "sctg2",
    "trade_type",
    "dist_band",
    "tons_2018",
    "tons_2019",
    "tons_2020",
    "tons_2021",
    "tons_2022",
    "tons_2023",
    "tons_2024",
    "value_2018",
    "value_2019",
    "value_2020",
    "value_2021",
    "value_2022",
    "value_2023",
    "value_2024",
    "current_value_2018",
    "current_value_2019",
    "current_value_2020",
    "current_value_2021",
    "current_value_2022",
    "current_value_2023",
    "current_value_2024",
    "tmiles_2018",
    "tmiles_2019",
    "tmiles_2020",
    "tmiles_2021",
    "tmiles_2022",
    "tmiles_2023",
    "tmiles_2024",
]


def filter_truck(df: pd.DataFrame) -> pd.DataFrame:
    """트럭만 (dms_mode == 1). dms_mode 는 int64."""
    return df.loc[df["dms_mode"] == 1].copy()

# 1. 데이터 불러오기
faf_raw = load_faf()

YEARS = list(range(2018, 2025))
TONS_COLS = [f"tons_{y}" for y in YEARS]

# 2. 결측치 제거 + 트럭 + 해당 품목(sctg2)만
required_cols = ["dms_mode", "sctg2"] + TONS_COLS
missing_cols = [c for c in required_cols if c not in faf_raw.columns]

if missing_cols:
    st.error(f"FAF 데이터에 필요한 컬럼이 없습니다: {missing_cols}")
    st.stop()

clean_df = faf_raw.dropna(subset=required_cols)
truck_df = filter_truck(clean_df)
item_df = truck_df[truck_df["sctg2"] == SCTG2_CODE].copy()

# 연도별 해당 품목 트럭 물동량 합계 (천 톤)
tons_by_year = [float(item_df[f"tons_{y}"].sum()) for y in YEARS]

# 3. 꺾은선 그래프: 가로축=연도, 세로축=물동량
fig, ax = plt.subplots(figsize=(14, 7), dpi=100)

ax.plot(
    YEARS,
    tons_by_year,
    marker="o",
    linewidth=2,
    color="steelblue",
    label="트럭 물동량 (천 톤)",
)

ax.set_xlabel("연도", fontsize=14)
ax.set_ylabel("물동량 (천 톤, thousand tons)", fontsize=12)
ax.set_xticks(YEARS)
ax.set_title(
    f"연도별 트럭 물동량: {COMMODITY_EN} (SCTG2={SCTG2_CODE}, 2018–2024)",
    fontweight="bold",
    fontsize=14,
)

from matplotlib.ticker import ScalarFormatter

fmt = ScalarFormatter(useOffset=False)
fmt.set_scientific(False)
ax.yaxis.set_major_formatter(fmt)

for x, y in zip(YEARS, tons_by_year):
    if np.isfinite(y):
        ax.annotate(
            f"{y:,.0f}",
            xy=(x, y),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            fontsize=8,
            color="steelblue",
        )

ax.legend(loc="best")
fig.tight_layout()
st.pyplot(fig, use_container_width=True)

st.write(
    f"- 품목: **{COMMODITY_EN}** (`sctg2={SCTG2_CODE}`), 트럭(`faf_parquet.filter_truck` → `dms_mode==1`)만 사용합니다."
)
st.write(
    "- 결측치 제거: `dms_mode`, `sctg2`, `tons_2018`~`tons_2024` 중 하나라도 NaN이면 행을 제외한 뒤 트럭만 골라 해당 품목을 집계합니다."
)
st.write(
    "- 꺾은선은 연도별 `tons_연도` 합계(천 톤)로, 같은 품목의 연도 간 물동량 차이를 보여 줍니다."
)