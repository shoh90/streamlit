import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import folium
from streamlit.components.v1 import html

# 데이터 로딩 함수
@st.cache_data
def load_data():
    conn = sqlite3.connect("asos_weather.db")
    df = pd.read_sql("SELECT * FROM asos_weather", conn)
    conn.close()
    df['일시'] = pd.to_datetime(df['일시'], errors='coerce')
    df['평균기온(°C)'] = pd.to_numeric(df['평균기온(°C)'], errors='coerce')
    df['일강수량(mm)'] = pd.to_numeric(df['일강수량(mm)'], errors='coerce')
    df['평균 상대습도(%)'] = pd.to_numeric(df['평균 상대습도(%)'], errors='coerce')
    df['평균 풍속(m/s)'] = pd.to_numeric(df['평균 풍속(m/s)'], errors='coerce')
    return df.dropna(subset=['일시'])

# 데이터 준비
df = load_data()
df['연월'] = df['일시'].dt.to_period('M').astype(str)

# 지점 정보 (예: 서귀포, 한림, 성산 등 가상 위경도)
stations = [
    {"name": "제주시", "lat": 33.4996, "lon": 126.5312},
    {"name": "서귀포", "lat": 33.2540, "lon": 126.5618},
    {"name": "한림", "lat": 33.4125, "lon": 126.2614},
    {"name": "성산", "lat": 33.3875, "lon": 126.8808},
]

# 탭 구성
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 월별 기후 변화", "🍊 감귤 적합 일자", "🌵 이상기후 경고", "🧭 작물 조건 비교", "📧 기상 알림", "🗺️ 지도 시각화"])

with tab1:
    st.subheader("📊 월별 기후 변화")
    monthly = df.groupby('연월')[['평균기온(°C)', '일강수량(mm)', '평균 상대습도(%)']].mean().reset_index()
    fig = px.line(monthly, x='연월', y=['평균기온(°C)', '일강수량(mm)', '평균 상대습도(%)'],
                  markers=True, labels={'value': '값', 'variable': '항목'})
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🍊 감귤 재배 적합 일자")
    cond = df['평균기온(°C)'].between(12, 18) & df['평균 상대습도(%)'].between(60, 85)
    citrus_df = df[cond][['일시', '평균기온(°C)', '평균 상대습도(%)']]
    st.dataframe(citrus_df)

with tab3:
    st.subheader("🌵 이상기후 경고 (5일 이상 무강수)")
    df['무강수'] = (df['일강수량(mm)'] == 0).astype(int)
    df['연속무강수'] = df['무강수'] * (
        df['무강수'].groupby((df['무강수'] != df['무강수'].shift()).cumsum()).cumcount() + 1
    )
    dry_df = df[df['연속무강수'] >= 5][['일시', '일강수량(mm)', '연속무강수']]
    st.dataframe(dry_df)

with tab4:
    st.subheader("🧭 작물 조건 비교")
    crops = {
        "감귤": {'기온': (12, 18), '습도': (60, 85)},
        "무": {'기온': (5, 20), '습도': (50, 75)},
        "고추": {'기온': (20, 27), '습도': (40, 70)}
    }
    crop = st.selectbox("작물 선택", list(crops.keys()))
    cmin, cmax = crops[crop]['기온']
    hmin, hmax = crops[crop]['습도']
    crop_df = df[df['평균기온(°C)'].between(cmin, cmax) & df['평균 상대습도(%)'].between(hmin, hmax)]
    st.dataframe(crop_df[['일시', '평균기온(°C)', '평균 상대습도(%)']])

with tab5:
    st.subheader("📧 실시간 기상 알림")
    latest = df['일시'].max()
    today = df[df['일시'] == latest].iloc[0]

    alerts = []
    if today['일강수량(mm)'] == 0:
        alerts.append("💧 오늘 강수량 0mm → 관수 작업 필요")
    if today['평균 풍속(m/s)'] >= 14:
        alerts.append("🌬️ 강풍 주의! 시설물 점검 필요")
    if not alerts:
        alerts.append("✅ 현재 이상 경고 없음")

    for alert in alerts:
        st.warning(alert)
    st.write(f"🕒 기준 날짜: {latest.strftime('%Y-%m-%d')}")

with tab6:
    st.subheader("🗺️ 제주 주요 지점 기후 지도")
    latest = df['일시'].max()
    fmap = folium.Map(location=[33.37, 126.55], zoom_start=10)

    for station in stations:
        name, lat, lon = station['name'], station['lat'], station['lon']
        latest_data = df[df['일시'] == latest].iloc[0]  # 가상의 동일 데이터 사용
        temp = latest_data['평균기온(°C)']
        humid = latest_data['평균 상대습도(%)']

        suitable = (12 <= temp <= 18) and (60 <= humid <= 85)
        crop_msg = "✅ 감귤 재배 적합" if suitable else "⚠️ 부적합"

        tooltip = f"{name}<br>{latest.strftime('%Y-%m-%d')}<br>🌡 {temp}°C<br>💧 {humid}%<br>{crop_msg}"
        color = 'green' if suitable else 'gray'

        folium.CircleMarker(
            location=[lat, lon],
            radius=10, color=color, fill=True,
            popup=tooltip, fill_opacity=0.8
        ).add_to(fmap)

    html(fmap._repr_html_(), height=550, width=750)
