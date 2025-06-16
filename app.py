# app.py - Rallit 스마트 채용 대시보드 (최종 통합 완성본 + 고용노동부 보험자 통계 API + 고용행정통계 크롤링)

<기존 코드 유지>

# --- 신규 보험자 통계 API 함수 추가 (XML 응답 파싱) ---
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

@st.cache_data(ttl=3600)
def fetch_insured_stats(closStdrYm="202506", rsdAreaCd="11680", sxdsCd="1", ageCd="04", bgnPage=1, display=100):
    url = "https://eis.work24.go.kr/opi/joApi.do"
    params = {
        "apiSecd": "OPIA",
        "closStdrYm": closStdrYm,
        "rsdAreaCd": rsdAreaCd,
        "sxdsCd": sxdsCd,
        "ageCd": ageCd,
        "rernSecd": "XML",
        "bgnPage": bgnPage,
        "display": display
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            data_list = []
            for item in root.findall(".//rqst"):
                data_list.append({
                    "기준년월": item.findtext("dwClosYm"),
                    "시군구": item.findtext("rsdAreaCdnm"),
                    "성별": item.findtext("sxdn"),
                    "연령": item.findtext("ageCdnm"),
                    "피보험자수": int(item.findtext("prtyIpnb", default="0")),
                    "취득자수": int(item.findtext("prtyAcqsNmpr", default="0")),
                    "상실자수": int(item.findtext("prtyFrftNmpr", default="0"))
                })
            return pd.DataFrame(data_list)
        else:
            st.error(f"❌ API 응답 실패: {response.status_code}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ API 요청 오류: {e}")
        return pd.DataFrame()

# --- 보험자 통계 시각화 탭 ---
def render_insured_stat_analysis():
    st.header("📊 고용노동부 보험자 통계 분석")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        closStdrYm = st.selectbox("📅 기준년월", ["202504", "202505", "202506"], index=2)
    with col2:
        rsdAreaCd = st.selectbox("🏙️ 지역코드", {"서울 강남구": "11680", "서울 종로구": "11110", "부산 해운대구": "26350"})
    with col3:
        sxdsCd = st.radio("👫 성별", ["1", "2"], format_func=lambda x: "남성" if x=="1" else "여성")
    with col4:
        ageCd = st.selectbox("🎂 연령대", {"25~29세": "04", "30~34세": "05", "35~39세": "06"})

    df = fetch_insured_stats(closStdrYm, rsdAreaCd, sxdsCd, ageCd)
    if df.empty:
        st.warning("데이터를 불러오지 못했습니다.")
    else:
        st.dataframe(df, use_container_width=True)
        st.subheader("📈 피보험자/취득자/상실자 비교")
        chart_df = df.melt(id_vars=["기준년월", "시군구"], value_vars=["피보험자수", "취득자수", "상실자수"], var_name="구분", value_name="인원")
        fig = px.bar(chart_df, x="기준년월", y="인원", color="구분", barmode="group", title="기준년월별 보험자 지표")
        st.plotly_chart(fig, use_container_width=True)

# --- 고용행정통계 웹 크롤링 분석 ---
def render_employment_report_list():
    st.header("📚 고용행정통계 보고서 리스트 (크롤링 기반)")
    try:
        url = "https://eis.work24.go.kr/eisps/opiv/selectOpivList.do"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select("table.board_list tbody tr")
        report_data = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                date = cols[0].text.strip()
                title = cols[1].text.strip()
                onclick = cols[1].find("a")["href"]
                seq = onclick.split("'")[1]
                detail_url = f"https://eis.work24.go.kr/eisps/opiv/selectOpivDetail.do?seq={seq}"
                report_data.append({"날짜": date, "제목": title, "링크": detail_url})
        df = pd.DataFrame(report_data)
        st.dataframe(df)
    except Exception as e:
        st.error(f"크롤링 중 오류 발생: {e}")

# --- 메인 탭에 추가 ---
# main 내부에서 마지막 부분 수정
    tabs = st.tabs(["🎯 스마트 매칭", "📊 시장 분석", "📈 성장 경로", "🏢 기업 인사이트", "🔮 예측 분석", "📋 상세 데이터", "📊 보험자 통계", "📚 통계 리포트"])
    with tabs[0]: render_smart_matching(filtered_df, user_profile, matching_engine, df)
    with tabs[1]: render_market_analysis(filtered_df)
    with tabs[2]: render_growth_path(df, user_profile, user_category, matching_engine)
    with tabs[3]: render_company_insight(filtered_df)
    with tabs[4]: render_prediction_analysis()
    with tabs[5]: render_detail_table(filtered_df)
    with tabs[6]: render_insured_stat_analysis()
    with tabs[7]: render_employment_report_list()
