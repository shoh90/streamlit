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

    # 강수량 컬럼명 자동 탐지
    rain_col = [col for col in df.columns if '강수량' in col][0]
    df[rain_col] = pd.to_numeric(df[rain_col], errors='coerce')
    df = df.rename(columns={rain_col: '일강수량(mm)'})

    # 습도 컬럼명 자동 탐지
    humid_col = [col for col in df.columns if '습도' in col][0]
    df[humid_col] = pd.to_numeric(df[humid_col], errors='coerce')
    df = df.rename(columns={humid_col: '평균 상대습도(%)'})

    # 풍속 컬럼명 자동 탐지
    wind_col = [col for col in df.columns if '풍속' in col][0]
    df[wind_col] = pd.to_numeric(df[wind_col], errors='coerce')
    df = df.rename(columns={wind_col: '평균 풍속(m/s)'})

    return df.dropna(subset=['일시'])

df = load_data()
df['연월'] = df['일시'].dt.to_period('M').astype(str)

stations = [
    {"name": "제주시", "lat": 33.4996, "lon": 126.5312},
    {"name": "서귀포", "lat": 33.2540, "lon": 126.5618},
    {"name": "한림", "lat": 33.4125, "lon": 126.2614},
    {"name": "성산", "lat": 33.3875, "lon": 126.8808},
]

# 탭 구성
tabs = ["📊 월별 기후 변화", "🍊 감귤 적합 일자", "🌵 이상기후 경고", "🧭 작물 조건 비교", "📧 기상 알림", "🗺️ 지도 시각화"]
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(tabs)

with tab1:
    st.subheader("📊 지점별 월별 기후 변화")
    selected_sites = st.multiselect('지점을 선택하세요', df['지점명'].unique(), default=df['지점명'].unique())
    df_filtered = df[df['지점명'].isin(selected_sites)]
    df_filtered['연월'] = df_filtered['일시'].dt.to_period('M').astype(str)

    monthly = df_filtered.groupby(['연월', '지점명'])[['평균기온(°C)', '일강수량(mm)', '평균 상대습도(%)']].mean().reset_index()

    for y_col, title in [('평균기온(°C)', '월별 평균기온'), ('일강수량(mm)', '월별 평균강수량'), ('평균 상대습도(%)', '월별 평균습도')]:
        fig = px.line(monthly, x='연월', y=y_col, color='지점명', markers=True, title=title)
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("🍊 감귤 재배 적합 일자")
    cond = df['평균기온(°C)'].between(12, 18) & df['평균 상대습도(%)'].between(60, 85)
    citrus_df = df[cond][['일시', '지점명', '평균기온(°C)', '평균 상대습도(%)']]
    st.dataframe(citrus_df)

with tab3:
    st.subheader("🌵 이상기후 경고 (5일 무강수 + 고온 + 강풍)")
    df['무강수'] = (df['일강수량(mm)'] == 0).astype(int)
    df['연속무강수'] = df['무강수'] * (df['무강수'].groupby((df['무강수'] != df['무강수'].shift()).cumsum()).cumcount() + 1)
    df['고온경고'] = df['평균기온(°C)'] >= 30
    df['강풍경고'] = df['평균 풍속(m/s)'] >= 14

    alerts_df = df[(df['연속무강수'] >= 5) | (df['고온경고']) | (df['강풍경고'])]
    st.dataframe(alerts_df[['일시', '지점명', '평균기온(°C)', '평균 풍속(m/s)', '연속무강수', '고온경고', '강풍경고']])

with tab4:
    st.subheader("🧭 작물 재배 적합 조건 비교")
    crops = {
        "감귤": {'기온': (12, 18), '습도': (60, 85)},
        "무": {'기온': (5, 20), '습도': (50, 75)},
        "고추": {'기온': (20, 27), '습도': (40, 70)}
    }
    crop = st.selectbox("작물을 선택하세요", list(crops.keys()))
    cmin, cmax = crops[crop]['기온']
    hmin, hmax = crops[crop]['습도']

    crop_df = df[df['평균기온(°C)'].between(cmin, cmax) & df['평균 상대습도(%)'].between(hmin, hmax)]
    st.dataframe(crop_df[['일시', '지점명', '평균기온(°C)', '평균 상대습도(%)']])

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
    df_latest = df[df['일시'] == latest]

    fmap = folium.Map(location=[33.37, 126.55], zoom_start=10)

    for station in stations:
        name, lat, lon = station['name'], station['lat'], station['lon']
        latest_data = df_latest[df_latest['지점명'] == name].iloc[0] if name in df_latest['지점명'].values else None
        if latest_data is None:
            continue

        temp = latest_data['평균기온(°C)']
        humid = latest_data['평균 상대습도(%)']
        rain = latest_data['일강수량(mm)']

        tooltip = f"{name}<br>{latest.strftime('%Y-%m-%d')}<br>🌡 {temp}°C<br>💧 {humid}%<br>☔ {rain}mm"
        color = 'green' if (12 <= temp <= 18 and 60 <= humid <= 85) else 'gray'

        folium.CircleMarker(
            location=[lat, lon],
            radius=10, color=color, fill=True,
            popup=tooltip, fill_opacity=0.8
        ).add_to(fmap)

    html(fmap._repr_html_(), height=550, width=750)
