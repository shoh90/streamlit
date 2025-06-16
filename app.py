# app.py - Rallit 스마트 채용 대시보드 (최종 통합 완성본)

<이전 코드 유지>

# 신규 함수 추가
import requests
import folium
from streamlit_folium import st_folium

def fetch_labor_trend_data():
    url = "https://eis.work24.go.kr/eisps/opiv/selectOpivList.do"
    headers = {"Content-Type": "application/json"}
    payload = {
        "searchCnd": "",
        "searchWrd": "",
        "pageIndex": 1,
        "pageUnit": 50,
        "pageSize": 50
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json().get('resultList', [])
        else:
            return []
    except:
        return []

def render_labor_trend_analysis():
    st.header("📊 노동시장 통계 기반 트렌드 분석")

    # 상용직 증가 시각화
    st.subheader("📌 상용직 증가 추이 시각화")
    years = [2020, 2021, 2022, 2023, 2024, 2025]
    increase = [20.1, 22.3, 25.7, 28.6, 33.0, 37.5]  # 단위: 만 명
    fig = px.line(x=years, y=increase, markers=True, title="2020~2025 상용직 근로자 수 증가 추이",
                  labels={'x': '연도', 'y': '상용직 근로자 수 (만 명)'})
    fig.update_traces(line=dict(color="#1f77b4", width=4))
    st.plotly_chart(fig, use_container_width=True)

    # 직무별 증감 추이 시각화 예시 데이터
    st.subheader("📈 직무별 채용 수요 증감 추이")
    job_trend_df = pd.DataFrame({
        '연도': [2023, 2024, 2025]*3,
        '직무': ['데이터 분석가']*3 + ['AI 개발자']*3 + ['요양보호사']*3,
        '수요': [120, 150, 180, 100, 160, 210, 200, 190, 170]
    })
    fig_job_trend = px.line(job_trend_df, x='연도', y='수요', color='직무', markers=True, title="직무별 채용 수요 변화 추이")
    st.plotly_chart(fig_job_trend, use_container_width=True)

    # API 호출 결과 시각화
    trend_data = fetch_labor_trend_data()
    if trend_data:
        st.subheader("📈 최신 노동시장 키워드")
        trends_df = pd.DataFrame(trend_data)
        top_jobs = trends_df['occptNm'].value_counts().head(10)
        fig2 = px.bar(top_jobs, x=top_jobs.values, y=top_jobs.index, orientation='h', title="최신 인기 직종 순위")
        st.plotly_chart(fig2, use_container_width=True)

        # 지역별 일자리 수 맵 (간단 시각화)
        st.subheader("📍 지역 기반 채용 수요 (상위 지역)")
        top_regions = trends_df['ctpvNm'].value_counts().head(10)
        fig3 = px.bar(top_regions, x=top_regions.values, y=top_regions.index, orientation='h',
                     title="최근 채용공고 상위 지역")
        st.plotly_chart(fig3, use_container_width=True)

        # 지도 기반 시각화
        st.subheader("🗺️ 지도 기반 채용 수요 시각화")
        location_dict = {
            "서울": [37.5665, 126.9780], "부산": [35.1796, 129.0756], "대구": [35.8714, 128.6014],
            "인천": [37.4563, 126.7052], "광주": [35.1595, 126.8526], "대전": [36.3504, 127.3845],
            "울산": [35.5384, 129.3114], "세종": [36.4801, 127.2891], "경기": [37.4138, 127.5183],
            "강원": [37.8228, 128.1555], "충북": [36.6358, 127.4917], "충남": [36.5184, 126.8000],
            "전북": [35.7167, 127.1442], "전남": [34.8161, 126.4630], "경북": [36.4919, 128.8889],
            "경남": [35.4606, 128.2132], "제주": [33.4996, 126.5312]
        }
        region_counts = trends_df['ctpvNm'].value_counts()
        m = folium.Map(location=[36.5, 127.8], zoom_start=7)
        for region, count in region_counts.items():
            if region in location_dict:
                folium.CircleMarker(
                    location=location_dict[region],
                    radius=min(20, count / 10),
                    popup=f"{region}: {count}건",
                    color='blue',
                    fill=True,
                    fill_color='blue'
                ).add_to(m)
        st_folium(m, width=800, height=500)

        # 고령자 맞춤 공고 비율 샘플
        st.subheader("👴 고령자 맞춤 채용 공고 비율")
        senior_related = trends_df[trends_df['ageClNm'].str.contains('60', na=False)]
        ratio = len(senior_related) / len(trends_df) if len(trends_df) > 0 else 0
        st.markdown(f"60세 이상 지원 가능 공고 비율: **{ratio*100:.1f}%**")
        st.progress(ratio)
    else:
        st.warning("⚠️ 고용노동부 API에서 데이터를 불러오지 못했습니다.")

# main 내부 탭 연결
# 기존 탭 정의 이후:
    with tabs[6]:
        render_labor_trend_analysis()
