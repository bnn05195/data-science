import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

@st.cache_data
def load_sctg2_description() -> dict:
    # 엑셀 파일이 없어도 무조건 이름이 뜨도록 하드코딩된 딕셔너리로 대체
    return {
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

def filter_truck(df: pd.DataFrame) -> pd.DataFrame:
    """트럭만 (dms_mode == 1). dms_mode 는 int64."""
    return df.loc[df["dms_mode"] == 1].copy()

# 1. 데이터 불러오기
faf_raw = load_faf()
SCTG2_DESC_MAP = load_sctg2_description()

year_cols = [c for c in faf_raw.columns if c.startswith("tons_")]
available_years = sorted([c.replace("tons_", "") for c in year_cols])

selected_year = st.selectbox("연도 선택", options=available_years, index=0)
target_year_col = f"tons_{selected_year}"

# 2. 결측치 제거 + 트럭 필터링
required_cols = ["dms_mode", "sctg2", target_year_col]
missing_cols = [c for c in required_cols if c not in faf_raw.columns]

if missing_cols:
    st.error(f"FAF 데이터에 필요한 컬럼이 없습니다: {missing_cols}")
    st.stop()

clean_df = faf_raw.dropna(subset=required_cols)
truck_df = filter_truck(clean_df)

# 3. 선택된 연도 트럭 운송 품목 전체 가로 막대 그래프
top10_truck = (
    truck_df.groupby("sctg2", as_index=True)[target_year_col]
    .sum()
    .sort_values(ascending=False)
)

top10_df = top10_truck.reset_index().rename(columns={"sctg2": "sctg2_code"})
top10_df["sctg2_num"] = pd.to_numeric(top10_df["sctg2_code"], errors="coerce").astype("Int64")
top10_df["label"] = top10_df["sctg2_num"].map(SCTG2_DESC_MAP)
top10_df["label"] = top10_df["label"].fillna(top10_df["sctg2_code"].astype(str))

n_items = len(top10_df)
fig_w, fig_h = 20, max(14, n_items * 0.55)
fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=100)

sns.barplot(
    y="label",
    x=target_year_col,
    data=top10_df,
    order=top10_df["label"],
    palette="Blues_r",
    ax=ax,
)

# 막대 끝부분에 값 표시
vals = top10_df[target_year_col].values
for i, patch in enumerate(ax.patches):
    if i >= len(vals):
        break
    val = vals[i]
    if pd.isna(val):
        continue
    x_end = patch.get_x() + patch.get_width()
    y_center = patch.get_y() + patch.get_height() / 2
    ax.annotate(
        f"{val:,.0f}",
        (x_end, y_center),
        xytext=(5, 0),
        textcoords="offset points",
        ha="left",
        va="center",
        fontsize=9,
        color="black",
    )

ax.set_xlabel("물동량 (천 톤, thousand tons)", fontsize=14)
ax.set_ylabel("품목 이름 (Commodity)", fontsize=14)
ax.set_title(f"{selected_year}년 트럭 운송 품목별 물동량 (전체)", fontweight="bold", fontsize=16)
ax.tick_params(axis="y", labelsize=11)
ax.tick_params(axis="x", labelsize=12)

from matplotlib.ticker import ScalarFormatter

formatter = ScalarFormatter(useOffset=False)
formatter.set_scientific(False)
ax.xaxis.set_major_formatter(formatter)

cur_xlim = ax.get_xlim()
ax.set_xlim(cur_xlim[0], cur_xlim[1] * 1.08)

st.pyplot(fig, use_container_width=True)

