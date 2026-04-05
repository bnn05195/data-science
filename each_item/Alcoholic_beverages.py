import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import platform

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from faf_parquet import filter_truck, read_faf5_parquet

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
    return read_faf5_parquet()


SCTG2_CODE = 8
COMMODITY_EN = 'Alcoholic beverages'

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

# 부연 설명
st.write("")
st.write("부연 설명")
st.write("")
st.write(
    f"- 품목: **{COMMODITY_EN}** (`sctg2={SCTG2_CODE}`), 트럭(`faf_parquet.filter_truck` → `dms_mode==1`)만 사용합니다."
)
st.write(
    "- 데이터: GitHub `FAF5.parquet` 또는 로컬 `data/FAF5.parquet` (`faf_parquet.read_faf5_parquet`). 실측 행 2,494,901 / 열 38."
)
st.write(
    "- 결측치 제거: `dms_mode`, `sctg2`, `tons_2018`~`tons_2024` 중 하나라도 NaN이면 행을 제외한 뒤 트럭만 골라 해당 품목을 집계합니다."
)
st.write(
    "- 꺾은선은 연도별 `tons_연도` 합계(천 톤)로, 같은 품목의 연도 간 물동량 차이를 보여 줍니다."
)
