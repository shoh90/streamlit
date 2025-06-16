# app.py - Rallit 스마트 채용 대시보드 (최종 완성본, 구문 오류 수정 및 전체 기능 통합)

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import logging
import random
import re
import requests
from bs4 import BeautifulSoup
import folium
from streamlit_folium import st_folium

# ==============================================================================
# 1. 페이지 및 환경 설정
# ==============================================================================
st.set_page_config(
    page_title="Rallit 스마트 채용 대시보드",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================================================================
# 2. 커스텀 CSS
# ==============================================================================
st.markdown("""
<style>
    .kpi-card {
        background-color: #FFFFFF;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        height: 100%;
    }
    .kpi-card h3 {
        font-size: 1rem;
        color: #616161;
        margin-bottom: 0.5rem;
    }
    .kpi-card p {
        font-size: 1.8rem;
        font-weight: bold;
        color: #212121;
        margin: 0;
    }
    .kpi-card small {
        font-size: 0.8rem;
        color: #757575;
    }
    .st-emotion-cache-1g6go59 { /* Streamlit Metric의 delta 값을 조정 */
        font-size: 0.9rem !important;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 3. 핵심 클래스 정의
# ==============================================================================
class SmartDataLoader:
    def __init__(self, db_path='rallit_jobs.db', data_dir='data'):
        self.db_path = db_path; self.data_dir = Path(data_dir)
        self.csv_files = {'MANAGEMENT': 'rallit_management_jobs.csv', 'MARKETING': 'rallit_marketing_jobs.csv', 'DESIGN': 'rallit_design_jobs.csv', 'DEVELOPER': 'rallit_developer_jobs.csv'}
    @st.cache_data
    def load_from_database(_self):
        try:
            if not Path(_self.db_path).exists(): _self._create_database_from_csv()
            conn = sqlite3.connect(_self.db_path); df = pd.read_sql_query("SELECT * FROM jobs", conn); conn.close()
            for col in ['join_reward', 'is_partner', 'is_bookmarked']:
                if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            if 'created_at' in df.columns: df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
            return df
        except Exception: return _self._load_from_csv_fallback()
    def _load_from_csv_fallback(self):
        try:
            dfs = [pd.read_csv(self.data_dir / f).assign(job_category=cat) for cat, f in self.csv_files.items() if (self.data_dir / f).exists()]
            if not dfs: return self._load_sample_data()
            df = pd.concat(dfs, ignore_index=True)
            df.columns = [c.lower().replace(' ', '_').replace('.', '_') for c in df.columns]
            for col in ['join_reward', 'is_partner', 'is_bookmarked']:
                if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            if 'created_at' not in df.columns: df['created_at'] = datetime.now()
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
            return df
        except Exception: return self._load_sample_data()
    def _create_database_from_csv(self):
        df = self._load_from_csv_fallback()
        if not df.empty: conn = sqlite3.connect(self.db_path); df.to_sql('jobs', conn, if_exists='replace', index=False); conn.close()
    def _load_sample_data(self):
        st.warning("📁 데이터 파일을 찾을 수 없어 샘플 데이터를 표시합니다."); categories = ['DEVELOPER', 'DESIGN', 'MARKETING', 'MANAGEMENT']; regions = ['PANGYO', 'GANGNAM', 'HONGDAE', 'JONGNO']; companies = ['테크컴퍼니A', '스타트업B', '대기업C', 'AI스타트업G']; skills = {'DEVELOPER': ['Python', 'JavaScript', 'React', 'Node.js', 'Java', 'Docker', 'AWS'], 'DESIGN': ['Figma', 'Sketch', 'Adobe XD', 'Zeplin'], 'MARKETING': ['Google Analytics', 'SEO', 'Content Marketing'], 'MANAGEMENT': ['Project Management', 'Agile', 'Scrum']}; data = []
        for i in range(200):
            cat = random.choice(categories)
            birth_date = datetime(random.randint(1960, 2002), random.randint(1, 12), random.randint(1, 28))
            age = (datetime.now() - birth_date).days // 365
            data.append({'id': i, 'job_category': cat, 'address_region': random.choice(regions), 'company_name': random.choice(companies), 'title': f'{cat.title()} 채용 - {random.choice(companies)}', 'status_name': random.choice(['모집 중', '마감']), 'status_code': 'HIRING', 'is_partner': random.choice([0, 1]), 'is_bookmarked': 0, 'join_reward': random.choice([0, 50000, 100000, 200000, 500000]), 'job_skill_keywords': ','.join(random.sample(skills[cat], k=random.randint(2, 4))), 'job_level': random.choice(['JUNIOR', 'SENIOR', 'LEAD', 'IRRELEVANT']), 'created_at': datetime.now() - timedelta(days=random.randint(0, 730)), 'gender': random.choice(['남성', '여성']), 'age': age})
        return pd.DataFrame(data)

class SmartMatchingEngine:
    def calculate_skill_match(self, user_skills, job_requirements):
        if not user_skills or not job_requirements or not isinstance(job_requirements, str): return 0, [], []
        user_skills_set = {s.strip().lower() for s in user_skills if s.strip()}; job_skills_set = {s.strip().lower() for s in job_requirements.split(',') if s.strip()}
        if not job_skills_set: return 0, [], []
        intersection = user_skills_set.intersection(job_skills_set); match_score = (len(intersection) / len(job_skills_set)) * 100 if job_skills_set else 0
        return match_score, list(intersection), list(job_skills_set - user_skills_set)
    def analyze_growth_potential(self, user_profile):
        score, factors = 0, []; modern_skills = ['ai', 'ml', 'docker', 'kubernetes', 'react', 'vue', 'typescript']; user_skills_lower = [s.lower() for s in user_profile.get('skills', [])]
        if user_profile.get('recent_courses', 0) > 0: score += 20; factors.append(f"최근 학습 ({user_profile.get('recent_courses')}개)")
        if user_profile.get('project_count', 0) > 3: score += 25; factors.append(f"프로젝트 경험 ({user_profile.get('project_count')}개)")
        if len(user_profile.get('skills', [])) > 8: score += 20; factors.append(f"기술 스택 다양성 ({len(user_profile.get('skills', []))}개)")
        if user_profile.get('github_contributions', 0) > 100: score += 15; factors.append(f"오픈소스 기여 ({user_profile.get('github_contributions')}회)")
        if any(skill in modern_skills for skill in user_skills_lower): score += 20; factors.append("최신 기술 트렌드 관심")
        return min(score, 100), factors
    def predict_success_probability(self, skill_score, growth_score):
        return round((skill_score * 0.7 + growth_score * 0.3), 1)


# ==============================================================================
# 4. 뷰(View) 함수 정의
# ==============================================================================
def render_main_summary(df):
    st.header("한눈에 보는 고용 현황")
    if df.empty:
        st.warning("요약 정보를 표시할 데이터가 없습니다.")
        return

    # 1. KPI 카드
    c1, c2, c3 = st.columns(3)
    total_insured = len(df)
    with c1: st.markdown(f'<div class="kpi-card"><h3>피보험자 수 (전체)</h3><p>{total_insured:,}명</p></div>', unsafe_allow_html=True)
    with c2:
        unemployment_claims = int(total_insured * random.uniform(0.04, 0.05))
        st.markdown(f'<div class="kpi-card"><h3>실업급여 지급건수 (샘플)</h3><p>{unemployment_claims:,}건</p></div>', unsafe_allow_html=True)
    with c3:
        job_openings = int(total_insured * random.uniform(0.08, 0.12))
        st.markdown(f'<div class="kpi-card"><h3>구인건수 (샘플)</h3><p>{job_openings:,}건</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns([0.6, 0.4])
    with c1:
        st.subheader("지역별 피보험자 분포")
        location_dict = {"서울": [37.5665, 126.9780], "부산": [35.1796, 129.0756], "대구": [35.8714, 128.6014], "인천": [37.4563, 126.7052], "광주": [35.1595, 126.8526], "대전": [36.3504, 127.3845], "울산": [35.5384, 129.3114], "세종": [36.4801, 127.2891], "경기": [37.4138, 127.5183], "강원": [37.8228, 128.1555], "충북": [36.6358, 127.4917], "충남": [36.5184, 126.8000], "전북": [35.7167, 127.1442], "전남": [34.8161, 126.4630], "경북": [36.4919, 128.8889], "경남": [35.4606, 128.2132], "제주": [33.4996, 126.5312], "PANGYO": [37.394776, 127.111195], "GANGNAM": [37.4979, 127.0276], "HONGDAE":[37.5575, 126.9245], "JONGNO":[37.5728, 126.9793]}
        region_counts = df['address_region'].value_counts()
        m = folium.Map(location=[36.5, 127.8], zoom_start=6.5, tiles="cartodbpositron")
        for region, count in region_counts.items():
            if region.upper() in location_dict:
                folium.CircleMarker(location=location_dict[region.upper()], radius=max(5, count / 5), popup=f"{region}: {count}건", color='#3186cc', fill=True, fill_color='#3186cc', fill_opacity=0.6).add_to(m)
        st_folium(m, height=400, use_container_width=True)
    with c2:
        st.subheader("산업별 피보험자 분포")
        category_counts = df['job_category'].value_counts()
        fig = px.pie(category_counts, values=category_counts.values, names=category_counts.index, title="", hole=0.5)
        fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0), height=400)
        fig.update_traces(textinfo='label+percent', textposition='inside')
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("연령별 분포")
        if 'age' in df.columns:
            bins = [0, 29, 39, 49, 59, 100]
            labels = ['29세 이하', '30대', '40대', '50대', '60세 이상']
            df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=True)
            age_counts = df['age_group'].value_counts().sort_index()
            fig_age = px.bar(age_counts, x=age_counts.index, y=age_counts.values, labels={'x': '연령대', 'y': '인원 수'})
            st.plotly_chart(fig_age, use_container_width=True)
    with c2:
        st.subheader("성별 분포")
        if 'gender' in df.columns:
            gender_counts = df['gender'].value_counts()
            male_pct = gender_counts.get('남성', 0) / total_insured * 100
            female_pct = gender_counts.get('여성', 0) / total_insured * 100
            c2_1, c2_2 = st.columns(2)
            with c2_1: st.markdown(f'<div class="kpi-card"><h3>남성 👨‍💼</h3><p>{male_pct:.1f}%</p><small>({gender_counts.get("남성", 0):,}명)</small></div>', unsafe_allow_html=True)
            with c2_2: st.markdown(f'<div class="kpi-card"><h3>여성 👩‍💼</h3><p>{female_pct:.1f}%</p><small>({gender_counts.get("여성", 0):,}명)</small></div>', unsafe_allow_html=True)

def render_smart_matching(filtered_df, user_profile, matching_engine, all_df):
    st.header("🎯 스마트 매칭 결과")
    if not user_profile['skills']: st.info("👆 사이드바에 보유 기술을 입력하면 맞춤 공고를 추천해 드립니다."); return
    growth_score, _ = matching_engine.analyze_growth_potential(user_profile)
    match_results = []
    for idx, row in filtered_df.iterrows():
        skill_score, matched, missing = matching_engine.calculate_skill_match(user_profile['skills'], row.get('job_skill_keywords'))
        if skill_score > 20:
            success_prob = matching_engine.predict_success_probability(skill_score, growth_score)
            match_results.append({'idx': idx, 'title': row['title'], 'company': row['company_name'], 'skill_score': skill_score, 'success_prob': success_prob, 'matched': matched, 'missing': missing})

    st.subheader(f"🌟 '{', '.join(user_profile['skills'])}' 스킬과 맞는 추천 공고")
    if not match_results:
        st.warning("아쉽지만, 현재 필터 조건에 맞는 추천 공고가 없습니다. 필터를 조정해보세요.")
        with st.expander("🤔 혹시 이런 건 어떠세요? (대안 제안 기능)"):
            st.markdown("**다른 직무 찾아보기**"); current_category = filtered_df['job_category'].iloc[0] if not filtered_df.empty else None
            other_categories = [cat for cat in all_df['job_category'].unique() if cat != current_category]
            if other_categories: st.write(f"현재 직무 외에도 이런 직무들이 있습니다: `{'`, `'.join(other_categories[:3])}`")
            st.markdown("**인접 기술 스택 학습하기**"); adjacent_skills = {'React': 'Vue.js', 'Python': 'Go', 'AWS': 'GCP, Azure', 'Docker': 'Kubernetes'}
            suggestions = [f"`{v}`" for k, v in adjacent_skills.items() if k.lower() in [s.lower() for s in user_profile['skills']]]
            if suggestions: st.write(f"현재 보유 스킬 기반으로 이런 기술을 추가 학습하면 좋습니다: {', '.join(suggestions)}")
        return

    for i, res in enumerate(sorted(match_results, key=lambda x: x['success_prob'], reverse=True)[:5]):
        with st.expander(f"🏆 #{i+1} {res['title']} - 최종 합격 확률: {res['success_prob']}%"):
            c1, c2 = st.columns([2, 1]);
            with c1:
                st.write(f"**회사:** {res['company']}")
                st.metric(label="JD-스펙 매칭도", value=f"{res['skill_score']:.1f}%")
                if res['matched']: st.markdown("**🎯 보유 스킬 매치:**" + "".join([f'<div class="skill-match">✅ {s.capitalize()}</div>' for s in res['matched']]), unsafe_allow_html=True)
                if res['missing']: st.markdown("**📚 추가 학습 필요:**" + "".join([f'<div class="skill-gap">📖 {s.capitalize()}</div>' for s in res['missing'][:3]]), unsafe_allow_html=True)
            with c2:
                fig = go.Figure(go.Indicator(mode="gauge+number", value=res['success_prob'], title={'text': "최종 합격 확률"}, domain={'x': [0, 1], 'y': [0, 1]}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#667eea"}}))
                fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20)); st.plotly_chart(fig, use_container_width=True, key=f"match_gauge_{res['idx']}")

def render_market_analysis(filtered_df):
    st.header("📊 채용 시장 트렌드 분석");
    if filtered_df.empty: st.warning("표시할 데이터가 없습니다. 필터를 조정해주세요."); return
    c1, c2 = st.columns(2)
    with c1:
        counts = filtered_df['job_category'].value_counts()
        fig = px.pie(counts, values=counts.values, names=counts.index, title="직무별 공고 분포", hole=0.4)
        st.plotly_chart(fig, use_container_width=True, key="cat_pie_market")
    with c2:
        counts = filtered_df['address_region'].value_counts().head(10)
        fig = px.bar(counts, y=counts.index, x=counts.values, orientation='h', title="상위 10개 지역 채용 현황", labels={'y':'지역', 'x':'공고 수'})
        fig.update_layout(yaxis={'categoryorder':'total ascending'}); st.plotly_chart(fig, use_container_width=True, key="region_bar_market")
    st.subheader("🔥 인기 기술 스택 트렌드")
    if 'job_skill_keywords' in filtered_df.columns:
        skills = filtered_df['job_skill_keywords'].dropna().str.split(',').explode().str.strip()
        skill_counts = skills[skills != ''].value_counts().head(15)
        if not skill_counts.empty:
            fig = px.bar(skill_counts, x=skill_counts.values, y=skill_counts.index, orientation='h', title="TOP 15 인기 기술", labels={'y':'기술', 'x':'언급 횟수'})
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}); st.plotly_chart(fig, use_container_width=True, key="skills_bar_market")

def render_growth_path(df, user_profile, user_category, matching_engine):
    st.header("📈 개인 성장 경로 분석");
    if not user_profile['skills']: st.info("👆 사이드바에 보유 기술을 입력하면 성장 경로를 분석해 드립니다."); return
    st.subheader("🚀 당신의 성장 잠재력"); growth_score, factors = matching_engine.analyze_growth_potential(user_profile); c1, c2 = st.columns([1, 2])
    with c1: fig = go.Figure(go.Indicator(mode="gauge+number", value=growth_score, title={'text': "성장 잠재력"})); st.plotly_chart(fig, use_container_width=True, key="growth_gauge_path")
    with c2:
        st.markdown("**🌱 성장 요인 분석:**");
        if factors: [st.markdown(f'<div class="growth-indicator">{f}</div>', unsafe_allow_html=True) for f in factors]
        else: st.write("성장 프로필을 입력하면 더 정확한 분석이 가능합니다.")
    st.subheader("🎯 스킬 갭 분석")
    if 'job_skill_keywords' in df.columns:
        target_df = df[df['job_category'] == user_category] if user_category != '전체' else df
        req_skills = target_df['job_skill_keywords'].dropna().str.split(',').explode().str.strip()
        req_counts = req_skills[req_skills != ''].value_counts().head(10)
        if not req_counts.empty:
            user_s_lower = [s.lower() for s in user_profile['skills']]
            gap_data = [{'skill': s, 'demand': c, 'status': '보유' if s.lower() in user_s_lower else '학습 필요'} for s, c in req_counts.items()]
            fig = px.bar(pd.DataFrame(gap_data), x='demand', y='skill', color='status', orientation='h', title=f"'{user_category}' 직무 핵심 스킬과 보유 현황", color_discrete_map={'보유': '#4caf50', '학습 필요': '#ff9800'})
            fig.update_layout(yaxis={'categoryorder': 'total ascending'}); st.plotly_chart(fig, use_container_width=True, key="skill_gap_bar_path")

def render_company_insight(filtered_df):
    st.header("🏢 기업별 채용 분석");
    if filtered_df.empty: st.warning("표시할 데이터가 없습니다. 필터를 조정해주세요."); return
    top_companies = filtered_df['company_name'].value_counts().head(15)
    fig = px.bar(top_companies, y=top_companies.index, x=top_companies.values, orientation='h', title="채용 공고가 많은 기업 TOP 15", labels={'y':'기업명', 'x':'공고 수'})
    fig.update_layout(yaxis={'categoryorder':'total ascending'}); st.plotly_chart(fig, use_container_width=True, key="company_bar_insight")

@st.cache_data(ttl=3600)
def fetch_employment_report_list():
    base_url = "https://eis.work24.go.kr"
    list_url = f"{base_url}/eisps/opiv/selectOpivList.do"
    try:
        res = requests.get(list_url, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select(".bbs-list tbody tr")
        if not rows: return pd.DataFrame(), "게시물 목록(rows)을 찾을 수 없습니다."
        report_data = []
        for row in rows[:5]:
            title_cell = row.select_one("td.title")
            if not title_cell or not title_cell.find("a"): continue
            link = title_cell.find("a")
            title = link.text.strip()
            onclick = link.get("onclick")
            if not onclick: continue
            seq_match = re.search(r"fncOpivDetail\('(\d+)'\)", onclick)
            if seq_match:
                seq = seq_match.group(1)
                detail_url = f"https://eis.work24.go.kr/eisps/opiv/selectOpivDetail.do?seq={seq}"
                report_data.append({"제목": title, "링크": detail_url})
        if not report_data: return pd.DataFrame(), "파싱 가능한 리포트를 찾지 못했습니다."
        return pd.DataFrame(report_data), "SUCCESS"
    except Exception as e: return pd.DataFrame(), f"크롤링 오류: {e}"

def render_employment_report_list_tab():
    st.header("📚 고용행정통계 리포트 (크롤링)")
    df, status = fetch_employment_report_list()
    if status == "SUCCESS" and not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True,
                     column_config={"링크": st.column_config.LinkColumn("상세보기", display_text="🔗 바로가기")})
    else:
        st.error(f"리포트 목록을 불러오는 데 실패했습니다. (상태: {status})")

def render_prediction_analysis():
    st.header("🔮 예측 분석 (Coming Soon!)")
    st.image("https://images.unsplash.com/photo-1531297484001-80022131f5a1?q=80&w=2020&auto=format&fit=crop", caption="AI가 당신의 커리어 미래를 예측합니다.")
    st.subheader("준비 중인 기능들")
    c1, c2 = st.columns(2)
    with c1:
        st.info("**📈 미래 채용 시장 예측**\n\n- 직무별/기술별 채용 수요가 어떻게 변할지 예측합니다.")
        st.info("**💰 개인 연봉 예측**\n\n- 나의 스펙과 경력으로 어느 정도의 연봉을 받을 수 있는지 예측합니다.")
    with c2:
        st.info("**🌱 기술 성장률 예측**\n\n- 어떤 기술이 미래에 유망할지 성장률을 예측하여 보여줍니다.")
        st.info("**🏢 기업 문화 적합도 예측**\n\n- 나의 성향과 가장 잘 맞는 기업 문화를 찾아 추천합니다.")

def render_detail_table(filtered_df):
    st.header("📋 상세 데이터");
    if filtered_df.empty: st.warning("표시할 데이터가 없습니다. 필터를 조정해주세요."); return
    st.dataframe(filtered_df, use_container_width=True, height=600)
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📄 CSV 다운로드", csv, "rallit_jobs_filtered.csv", "text/csv")


# ==============================================================================
# 5. 메인 애플리케이션 실행
# ==============================================================================
def main():
    st.title("Rallit 스마트 채용 대시보드")
    
    data_loader = SmartDataLoader(); matching_engine = SmartMatchingEngine(); df = data_loader.load_from_database()
    if df.empty: st.error("😕 데이터를 로드할 수 없습니다."); return

    with st.sidebar:
        st.header("🎯 스마트 매칭 프로필"); user_skills_input = st.text_area("보유 기술 스택 (쉼표로 구분)", placeholder="예: Python, React, AWS")
        with st.expander("📈 성장 프로필 (선택)"): recent_courses = st.number_input("최근 1년 수강 강의 수", 0, 50, 0); project_count = st.number_input("개인/팀 프로젝트 수", 0, 20, 0); github_contributions = st.number_input("GitHub 연간 기여도", 0, 1000, 0)
        user_profile = {'skills': [s.strip() for s in user_skills_input.split(',') if s.strip()], 'recent_courses': recent_courses, 'project_count': project_count, 'github_contributions': github_contributions}
        
        st.markdown("---"); st.header("🔍 고급 필터"); user_category = st.selectbox("관심 직무", ['전체'] + sorted(list(df['job_category'].dropna().unique()))); selected_region = st.selectbox("📍 근무 지역", ['전체'] + sorted(list(df['address_region'].dropna().unique())))
        reward_filter = st.checkbox("💰 지원금 있는 공고만 보기"); partner_filter = st.checkbox("🤝 파트너 기업만 보기")
        min_r, max_r = int(df['join_reward'].min()), int(df['join_reward'].max()); join_reward_range = st.slider("💵 지원금 범위 (원)", min_r, max_r, (min_r, max_r))
        selected_levels = st.multiselect("📈 직무 레벨", df['job_level'].dropna().unique(), default=list(df['job_level'].dropna().unique())); keyword_input = st.text_input("🔍 키워드 검색 (공고명/회사명)", "")
        if st.button("🔄 데이터 새로고침"): st.cache_data.clear(); st.rerun()

    filtered_df = df.copy()
    if user_category != '전체': filtered_df = filtered_df[filtered_df['job_category'] == user_category]
    if selected_region != '전체': filtered_df = filtered_df[filtered_df['address_region'] == selected_region]
    if reward_filter: filtered_df = filtered_df[filtered_df['join_reward'] > 0]
    if partner_filter: filtered_df = filtered_df[filtered_df['is_partner'] == 1]
    if selected_levels: filtered_df = filtered_df[filtered_df['job_level'].isin(selected_levels)]
    filtered_df = filtered_df[filtered_df['join_reward'].between(join_reward_range[0], join_reward_range[1])]
    if keyword_input:
        keyword = keyword_input.lower()
        mask = (filtered_df['title'].str.lower().str.contains(keyword, na=False)) | (filtered_df['company_name'].str.lower().str.contains(keyword, na=False))
        filtered_df = filtered_df[mask]
    if user_profile['skills'] and 'job_skill_keywords' in filtered_df.columns:
        user_skills_pattern = '|'.join([re.escape(skill.strip()) for skill in user_profile['skills']])
        filtered_df = filtered_df[filtered_df['job_skill_keywords'].str.contains(user_skills_pattern, case=False, na=False)]

    summary_list = [f"**보유 스킬:** `{', '.join(user_profile['skills'])}`" if user_profile['skills'] else '', f"**직무:** `{user_category}`" if user_category != '전체' else '', f"**지역:** `{selected_region}`" if selected_region != '전체' else '', f"**키워드:** `{keyword_input}`" if keyword_input else '']
    active_filters = " | ".join(filter(None, summary_list))
    st.success(f"🔍 **필터 요약:** {active_filters if active_filters else '전체 조건'} | **결과:** `{len(filtered_df)}`개의 공고")

    tabs = st.tabs(["⭐ 메인 요약", "🎯 스마트 매칭", "📊 시장 분석", "💡 노동시장 동향", "📈 성장 경로", "🏢 기업 인사이트", "🔮 예측 분석", "📋 상세 데이터"])
    with tabs[0]: render_main_summary(df)
    with tabs[1]: render_smart_matching(filtered_df, user_profile, matching_engine, df)
    with tabs[2]: render_market_analysis(filtered_df)
    with tabs[3]: render_employment_report_list()
    with tabs[4]: render_growth_path(df, user_profile, user_category, matching_engine)
    with tabs[5]: render_company_insight(filtered_df)
    with tabs[6]: render_prediction_analysis()
    with tabs[7]: render_detail_table(filtered_df)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"애플리케이션 실행 중 오류가 발생했습니다: {e}"); logger.error(f"Application error: {e}", exc_info=True)
