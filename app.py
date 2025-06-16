# app.py - Rallit 스마트 채용 대시보드 (최종 완성본, 보험자 통계 API 연동)

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import logging
import random
import re
import requests
import xml.etree.ElementTree as ET
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
    .problem-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 15px; color: white; margin: 0.5rem 0; box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37); min-height: 180px; }
    .skill-match { display: inline-block; background: #e8f5e8; padding: 0.3rem 0.6rem; border-radius: 15px; border: 1px solid #4caf50; margin: 0.2rem; font-size: 0.9em; color: #145a32; }
    .skill-gap { display: inline-block; background: #fff3e0; padding: 0.3rem 0.6rem; border-radius: 15px; border: 1px solid #ff9800; margin: 0.2rem; font-size: 0.9em; color: #9c5400;}
    .growth-indicator { background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%); padding: 0.8rem; border-radius: 10px; margin: 0.5rem 0; }
    h3 { padding-bottom: 10px; }
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
            return df
        except Exception: return self._load_sample_data()
    def _create_database_from_csv(self):
        df = self._load_from_csv_fallback()
        if not df.empty: conn = sqlite3.connect(self.db_path); df.to_sql('jobs', conn, if_exists='replace', index=False); conn.close()
    def _load_sample_data(self):
        st.warning("📁 데이터 파일을 찾을 수 없어 샘플 데이터를 표시합니다."); categories = ['DEVELOPER', 'DESIGN', 'MARKETING', 'MANAGEMENT']; regions = ['PANGYO', 'GANGNAM', 'HONGDAE', 'JONGNO']; companies = ['테크컴퍼니A', '스타트업B', '대기업C', 'AI스타트업G']; skills = {'DEVELOPER': ['Python', 'JavaScript', 'React', 'Node.js', 'Java', 'Docker', 'AWS'], 'DESIGN': ['Figma', 'Sketch', 'Adobe XD', 'Zeplin'], 'MARKETING': ['Google Analytics', 'SEO', 'Content Marketing'], 'MANAGEMENT': ['Project Management', 'Agile', 'Scrum']}; data = []
        for i in range(150): cat = random.choice(categories); data.append({'id': i, 'job_category': cat, 'address_region': random.choice(regions), 'company_name': random.choice(companies), 'title': f'{cat.title()} 채용 - {random.choice(companies)}', 'status_name': random.choice(['모집 중', '마감']), 'status_code': 'HIRING', 'is_partner': random.choice([0, 1]), 'is_bookmarked': 0, 'join_reward': random.choice([0, 50000, 100000, 200000, 500000]), 'job_skill_keywords': ','.join(random.sample(skills[cat], k=random.randint(2, 4))), 'job_level': random.choice(['JUNIOR', 'SENIOR', 'LEAD', 'IRRELEVANT']), 'created_at': datetime.now()})
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
# 4. 뷰 함수 정의
# ==============================================================================
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

# --- 신규 함수: 보험자 통계 API 연동 및 시각화 ---
@st.cache_data(ttl=3600)
def fetch_insured_stats(closStdrYm, rsdAreaCd, sxdsCd, ageCd):
    url = "https://eis.work24.go.kr/opi/ipsApi.do" # 피보험자 API URL로 수정
    auth_key = st.secrets.get("EIS_AUTH_KEY")
    if not auth_key: return None, "NO_KEY"
    
    params = {
        'authKey': auth_key, 'apiSecd': 'OPIB', 'rernSecd': 'XML', 'display': 100,
        'closStdrYm': closStdrYm, 'rsdAreaCd': rsdAreaCd, 'sxdsCd': sxdsCd, 'ageCd': ageCd
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200 or '<!DOCTYPE html>' in response.text:
            logger.error(f"API Error: Status {response.status_code}. Response: {response.text[:200]}")
            return None, "API_ERROR"
        root = ET.fromstring(response.text)
        data_list = [{'기준년월': item.findtext('dwClosYm'), '시군구': item.findtext('rsdAreaCdnm'), '성별': item.findtext('sxdn'), '연령': item.findtext('ageCdnm'), '피보험자수': int(item.findtext('prtyIpnb', '0')), '취득자수': int(item.findtext('prtyAcqsNmpr', '0')), '상실자수': int(item.findtext('prtyFrftNmpr', '0'))} for item in root.findall('.//rqst')]
        return pd.DataFrame(data_list), "SUCCESS"
    except (requests.exceptions.RequestException, ET.ParseError) as e:
        logger.error(f"API Request or XML Parsing failed: {e}")
        return None, "REQUEST_FAIL"

def render_insured_stat_analysis():
    st.header("📊 고용노동부 피보험자 통계 분석")
    
    # 사용자 입력 필터
    col1, col2, col3, col4 = st.columns(4)
    with col1: closStdrYm = st.text_input("📅 기준년월 (YYYYMM)", value=datetime.now().strftime('%Y%m'))
    with col2: rsdAreaCd = st.selectbox("🏙️ 지역코드", {"서울 강남구": "11680", "서울 종로구": "11110", "부산 해운대구": "26350"}.keys())
    with col3: sxdsCd = st.radio("👫 성별", ["1", "2"], format_func=lambda x: "남성" if x=="1" else "여성", horizontal=True)
    with col4: ageCd = st.selectbox("🎂 연령대", {"25~29세": "04", "30~34세": "05", "35~39세": "06"}.keys())

    # 딕셔너리 키를 코드로 변환
    area_code_map = {"서울 강남구": "11680", "서울 종로구": "11110", "부산 해운대구": "26350"}
    age_code_map = {"25~29세": "04", "30~34세": "05", "35~39세": "06"}
    
    with st.spinner("API에서 보험자 통계 데이터를 불러오는 중..."):
        df, status = fetch_insured_stats(closStdrYm, area_code_map[rsdAreaCd], sxdsCd, age_code_map[ageCd])
    
    if status == "SUCCESS" and not df.empty:
        st.dataframe(df, use_container_width=True)
        st.subheader("📈 피보험자/취득자/상실자 비교")
        chart_df = df.melt(id_vars=["시군구", "연령"], value_vars=["피보험자수", "취득자수", "상실자수"], var_name="구분", value_name="인원수")
        fig = px.bar(chart_df, x="구분", y="인원수", color="구분", title=f"{closStdrYm} {rsdAreaCd} 보험자 지표", labels={'인원수': '인원 수'})
        st.plotly_chart(fig, use_container_width=True)
    elif status == "NO_KEY":
        st.error("🚨 API 인증키가 설정되지 않았습니다. Streamlit Cloud의 Secrets에 `EIS_AUTH_KEY`를 추가해주세요.")
    else:
        st.warning(f"데이터를 불러오지 못했습니다. (상태: {status})")

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
    with st.expander("✨ 대시보드 기획 의도 자세히 보기"):
        st.markdown("## 🎯 해결하고자 하는 문제들")
        c1,c2,c3 = st.columns(3); c1.markdown('<div class="problem-card"><h3>👤 구직자 문제</h3><ul><li>적합한 공고 찾기 어려움</li><li>JD-스펙 미스매칭</li><li>성장과정 평가 부족</li></ul></div>', unsafe_allow_html=True); c2.markdown('<div class="problem-card"><h3>🏢 기업 문제</h3><ul><li>실무역량 판단 어려움</li><li>정량적 기준 부족</li><li>성과 예측 불가능</li></ul></div>', unsafe_allow_html=True); c3.markdown('<div class="problem-card"><h3>🔧 플랫폼 문제</h3><ul><li>성장여정 미반영</li><li>단순 키워드 매칭</li><li>최신 트렌드 부족</li></ul></div>', unsafe_allow_html=True)
    st.markdown("---")
    
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

    tabs = st.tabs(["🎯 스마트 매칭", "📊 시장 분석", "📊 보험자 통계", "📈 성장 경로", "🏢 기업 인사이트", "🔮 예측 분석", "📋 상세 데이터"])
    with tabs[0]: render_smart_matching(filtered_df, user_profile, matching_engine, df)
    with tabs[1]: render_market_analysis(filtered_df)
    with tabs[2]: render_insured_stat_analysis()
    with tabs[3]: render_growth_path(df, user_profile, user_category, matching_engine)
    with tabs[4]: render_company_insight(filtered_df)
    with tabs[5]: render_prediction_analysis()
    with tabs[6]: render_detail_table(filtered_df)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"애플리케이션 실행 중 오류가 발생했습니다: {e}"); logger.error(f"Application error: {e}", exc_info=True)
