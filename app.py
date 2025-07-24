
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
from collections import defaultdict
from initialized_titles import titles_with_date

# 活動分類關鍵字
categories = {
    "青年交流": ["青年", "学生", "实习", "研学营", "交流月", "冬令营", "体育营", "职场", "青创", "打卡"],
    "文化宗教": ["文化", "祭祖", "诗词", "书画", "论语", "文昌", "大禹", "神农", "嫘祖", "黄帝", "汉服"],
    "節慶民俗": ["元宵", "春节", "年味", "中秋", "春茶", "三月三", "联谊", "灯火", "非遗"],
    "經貿產業": ["招商", "经贸", "产业", "合作", "金融", "链", "座谈", "营商", "发展"],
    "地方社區": ["参访", "慰问", "服务平台", "建桥", "条例", "法", "宣传", "普法", "连心"],
    "體育藝術": ["篮球", "街舞", "杂技", "书画", "艺术", "演出"]
}

def classify(title):
    for cat, kw_list in categories.items():
        if any(kw in title for kw in kw_list):
            return cat
    return "未分類"

def render_exchange_analysis():
    st.set_page_config(page_title="交往交流分析", layout="wide")
    st.title("🌐 交往交流欄目分析（已初始化）")

    stat = defaultdict(int)
    detail_rows = []

    for date_str, title in titles_with_date:
        cat = classify(title)
        stat[cat] += 1
        if cat != "未分類":
            detail_rows.append((cat, title))

    df_summary = pd.DataFrame(stat.items(), columns=["類別", "數量"]).sort_values("數量", ascending=False)
    df_detail = pd.DataFrame(detail_rows, columns=["分類", "標題"]).sort_values("分類")

    st.markdown("### 🎯 六類活動類別統計")
    st.dataframe(df_summary)

    # 時間趨勢資料處理
    date_category_data = []
    for date_str, title in titles_with_date:
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            year_month = date_obj.strftime("%Y-%m")
            category = classify(title)
            if category != "未分類":
                date_category_data.append((year_month, category, title))
        except ValueError:
            continue

    time_trend_data = defaultdict(lambda: defaultdict(int))
    for year_month, category, _ in date_category_data:
        time_trend_data[year_month][category] += 1

    time_trend_rows = []
    for year_month, categories_count in time_trend_data.items():
        for category, count in categories_count.items():
            time_trend_rows.append({"年月": year_month, "類別": category, "數量": count})

    if time_trend_rows:
        df_time_trend = pd.DataFrame(time_trend_rows)
        df_time_trend["年月"] = pd.to_datetime(df_time_trend["年月"])
        df_time_trend = df_time_trend.sort_values("年月")
        df_time_trend["年月"] = df_time_trend["年月"].dt.strftime("%Y-%m")

        pivot_df = pd.pivot_table(
            df_time_trend,
            index="年月",
            columns="類別",
            values="數量",
            fill_value=0
        ).reset_index()

        st.markdown("### 📈 六類活動時間趨勢")
        fig_trend = go.Figure()
        for category in pivot_df.columns[1:]:
            fig_trend.add_trace(go.Scatter(
                x=pivot_df["年月"],
                y=pivot_df[category],
                mode="lines+markers",
                name=category,
                connectgaps=True
            ))
        fig_trend.update_layout(
            title="六類活動隨時間變化",
            xaxis_title="年月",
            yaxis_title="活動數量",
            legend_title="活動類別",
            height=500
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown("### 📰 活動標題彙整（依分類）")
    for cat in df_detail["分類"].unique():
        with st.expander(f"{cat} 的活動標題"):
            for t in df_detail[df_detail["分類"] == cat]["標題"]:
                st.markdown(f"- {t}")

# 執行頁面
if __name__ == "__main__":
    render_exchange_analysis()

# ----------- 🗺️ 地理分布圖 (出現次數 by 城市) -----------

import plotly.express as px

# 假設你有這份資料
location_df = pd.DataFrame({
    "城市": ["北京", "上海", "廣州", "成都", "武漢", "南京"],
    "出現次數": [120, 180, 95, 210, 260, 80],
    "lat": [39.9042, 31.2304, 23.1291, 30.5728, 30.5928, 32.0603],
    "lon": [116.4074, 121.4737, 113.2644, 104.0668, 114.3055, 118.7969]
})

st.markdown("### 🗺️ 城市出現次數地圖")
fig_geo = px.scatter_geo(
    location_df,
    lat="lat",
    lon="lon",
    size="出現次數",
    color="出現次數",
    color_continuous_scale="Reds",
    projection="natural earth",
    hover_name="城市"
)
fig_geo.update_geos(fitbounds="locations", visible=False)
fig_geo.update_layout(height=500, coloraxis_colorbar=dict(title="出現次數"))
st.plotly_chart(fig_geo, use_container_width=True)
