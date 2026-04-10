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

# 폰트 설정
os_name = platform.system()
if os_name == "Windows":
    plt.rc("font", family="Malgun Gothic")
elif os_name == "Darwin":
    plt.rc("font", family="AppleGothic")
else:
    plt.rc("font", family="NanumGothic")

plt.rcParams["axes.unicode_minus"] = False

@st.cache_data
def load_data():
    df = pd.read_parquet(
        "https://github.com/bnn05195/data-science/releases/download/v1.0/FAF5.parquet"
    )
    meta = pd.read_excel("../data/FAF5_metadata.xlsx", sheet_name="Commodity (SCTG2)")

    meta = meta[["Numeric Label", "Description"]].dropna()
    meta["Numeric Label"] = meta["Numeric Label"].astype(int)

    sctg_map = dict(zip(meta["Numeric Label"], meta["Description"]))

    return df, sctg_map

df, SCTG_MAP = load_data()

# -------------------------------
# 전처리
# -------------------------------
df = df[df["dms_mode"] == 1]
df = df.dropna(subset=["sctg2", "dms_orig"])

df["state_code"] = (df["dms_orig"] // 10).astype(int)

# 텍사스
texas_df = df[df["state_code"] == 48]

# -------------------------------
# 연도 선택 
# -------------------------------
year_cols = [col for col in df.columns if col.startswith("tons_")]
years = sorted([int(col.split("_")[1]) for col in year_cols])

selected_year = st.selectbox("연도 선택", years)

target_col = f"tons_{selected_year}"


texas_df = texas_df.dropna(subset=[target_col])


agg = (
    texas_df.groupby("sctg2")[target_col]
    .sum()
    .sort_values(ascending=False)
)

plot_df = agg.reset_index()
plot_df["sctg2"] = plot_df["sctg2"].astype(int)

# 품목 이름 매핑
plot_df["label"] = plot_df["sctg2"].map(SCTG_MAP)
plot_df["label"] = plot_df["label"].fillna("Unknown")


fig_h = max(10, len(plot_df) * 0.4)
fig, ax = plt.subplots(figsize=(20, fig_h))

sns.barplot(
    y="label",
    x=target_col,
    data=plot_df,
    palette="Blues_r",
    ax=ax
)

ax.set_title(f"Texas 출발 트럭 운송 품목 분석 ({selected_year})", fontsize=26, fontweight="bold")
ax.set_xlabel("물동량 (천 톤)", fontsize=18)
ax.set_ylabel("품목", fontsize=18)

ax.tick_params(axis="y", labelsize=14)
ax.tick_params(axis="x", labelsize=14)


max_val = plot_df[target_col].max()
offset = max_val * 0.02

for i, v in enumerate(plot_df[target_col]):
    ax.text(v + offset, i, f"{v:,.0f}", va="center", fontsize=12)

ax.set_xlim(0, max_val * 1.15)


plt.subplots_adjust(top=0.85)

st.pyplot(fig, use_container_width=True)
