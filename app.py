"""
Rallit Jobs Dashboard - 스마트 기능이 통합된 최종 Streamlit 애플리케이션
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

# 페이지 설정
st.set_page_config(
    page_title="Rallit 스마트 채용 대시보드",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .problem-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        min-height: 220px;
    }
    .solution-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        min-height: 250px;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .skill-match {
        background: #e8f5e8;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 3px solid #4caf50;
        margin: 0.2rem 0;
    }
    .skill-gap {
        background: #fff3e0;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 3px solid #ff9800;
        margin: 0.2rem 0;
    }
    .growth-indicator {
        background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%);
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# AI 기반 매칭 엔진
class SmartMatchingEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        
    def calculate_skill_match(self, user_skills, job_requirements):
        """스킬 매칭 점수 계산"""
        if not user_skills or not job_requirements or not isinstance(job_requirements, str):
            return 0, [], []

        user_skills_set = set([skill.strip().lower() for skill in user_skills])
        job_skills_set = set([skill.strip().lower() for skill in job_requirements.split(',')])
        
        user_skills_set = {s for s in user_skills_set if s}
        job_skills_set = {s for s in job_skills_set if s}

        if not job_skills_set:
            return 0, [], []

        intersection = user_skills_set.intersection(job_skills_set)
        
        match_score = len(intersection) / len(job_skills_set) * 100
        matched_skills = list(intersection)
        missing_skills = list(job_skills_set - user_skills_set)
        
        return match_score, matched_skills, missing_skills
    
    def analyze_growth_potential(self, user_profile):
        """성장 잠재력 분석"""
        growth_score = 0
        growth_factors = []
        
        if user_profile.get('recent_courses', 0) > 0:
            growth_score += 20
            growth_factors.append(f"최근 학습 활동 활발 ({user_profile.get('recent_courses')}개)")
        if user_profile.get('project_count', 0) > 3:
            growth_score += 25
            growth_factors.append(f"다양한 프로젝트 경험 ({user_profile.get('project_count')}개)")
        if len(user_profile.get('skills', [])) > 8:
            growth_score += 20
            growth_factors.append(f"다양한 기술 스택 보유 ({len(user_profile.get('skills', []))}개)")
        if user_profile.get('github_contributions', 0) > 100:
            growth_score += 15
            growth_factors.append(f"활발한 개발 기여 (연 {user_profile.get('github_contributions')}회)")
        
        modern_skills = ['ai', 'ml', 'docker', 'kubernetes', 'react', 'vue', 'typescript']
        user_skills_lower = [s.lower() for s in user_profile.get('skills', [])]
        if any(skill in user_skills_lower for skill in modern_skills):
            growth_score += 20
            growth_factors.append("최신 기술 트렌드 관심")
        
        return min(growth_score, 100), growth_factors


# 데이터 로더 클래스
class SmartDataLoader:
    def __init__(self, db_path='rallit_jobs.db', data_dir='data'):
        self.db_path = db_path
        self.data_dir = Path(data_dir)
        self.csv_files = {
            'MANAGEMENT': 'rallit_management_jobs.csv',
            'MARKETING': 'rallit_marketing_jobs.csv',
            'DESIGN': 'rallit_design_jobs.csv',
            'DEVELOPER': 'rallit_developer_jobs.csv'
        }
    
    @st.cache_data
    def load_from_database(_self):
        try:
            if not Path(_self.db_path).exists():
                logger.warning(f"Database file {_self.db_path} not found. Creating from CSV.")
                _self._create_database_from_csv()
            conn = sqlite3.connect(_self.db_path)
            df = pd.read_sql_query("SELECT * FROM jobs", conn)
            conn.close()
            logger.info(f"Loaded {len(df)} records from database")
            return df
        except Exception as e:
            logger.error(f"DB loading error: {e}. Falling back to CSV.")
            return _self._load_from_csv_fallback()
    
    def _load_from_csv_fallback(self):
        try:
            all_dfs = []
            for category, filename in self.csv_files.items():
                file_path = self.data_dir / filename
                if file_path.exists():
                    df = pd.read_csv(file_path)
                    df['job_category'] = category
                    all_dfs.append(df)
            if all_dfs:
                combined_df = pd.concat(all_dfs, ignore_index=True)
                # 데이터 클리닝 및 타입 변환
                combined_df.columns = [col.lower().replace(' ', '_') for col in combined_df.columns]
                # ... (필요 시 더 많은 클리닝 로직 추가) ...
                logger.info(f"Combined {len(combined_df)} records from CSVs.")
                return combined_df
            else:
                logger.error("No CSVs found. Loading sample data.")
                return _self._load_sample_data()
        except Exception as e:
            logger.error(f"CSV loading error: {e}. Loading sample data.")
            return _self._load_sample_data()

    def _create_database_from_csv(self):
        df = self._load_from_csv_fallback()
        if not df.empty:
            conn = sqlite3.connect(self.db_path)
            df.to_sql('jobs', conn, if_exists='replace', index=False)
            conn.commit()
            conn.close()
            logger.info("Database created from CSVs.")
    
    def _load_sample_data(self):
        st.warning("📁 데이터 파일을 찾을 수 없어 샘플 데이터를 표시합니다.")
        # ... (샘플 데이터 생성 로직은 첫번째 코드에서 가져옴) ...
        categories = ['DEVELOPER', 'DESIGN', 'MARKETING', 'MANAGEMENT']
        regions = ['PANGYO', 'GANGNAM', 'HONGDAE', 'JONGNO', 'YEOUIDO', 'BUNDANG', 'SEOCHO']
        companies = ['테크컴퍼니A', '스타트업B', '대기업C', '중견기업D', '벤처E', '글로벌기업F', 'AI스타트업G']
        skills = {
            'DEVELOPER': ['Python', 'JavaScript', 'React', 'Node.js', 'Java', 'Spring', 'Django', 'Vue.js', 'TypeScript', 'Docker', 'AWS', 'Kubernetes'],
            'DESIGN': ['Figma', 'Sketch', 'Adobe XD', 'Photoshop', 'Illustrator', 'Principle', 'Zeplin', 'InVision', 'Framer'],
            'MARKETING': ['Google Analytics', 'Facebook Ads', 'SEO', 'Content Marketing', 'Social Media', 'Performance Marketing', 'CRM'],
            'MANAGEMENT': ['Project Management', 'Team Leadership', 'Strategic Planning', 'Business Analysis', 'Agile', 'Scrum']
        }
        sample_data = []
        for i in range(200):
            category = random.choice(categories)
            sample_data.append({
                'id': i + 1, 'job_category': category, 'address_region': random.choice(regions),
                'company_id': random.randint(1, 50), 'company_name': random.choice(companies),
                'title': f'{category.title()} 채용공고 - {random.choice(companies)}',
                'status_code': random.choice(['HIRING', 'CLOSED']), 'status_name': random.choice(['모집 중', '마감']),
                'is_partner': random.choice([0, 1]), 'is_bookmarked': random.choice([0, 1]),
                'join_reward': random.choice([0, 50000, 100000, 200000, 300000, 500000]),
                'job_skill_keywords': ', '.join(random.sample(skills[category], k=random.randint(3, 6))),
                'job_level': random.choice(['IRRELEVANT', 'JUNIOR', 'SENIOR', 'LEAD']),
                'job_levels': random.choice(['INTERN', 'JUNIOR', 'SENIOR', 'MANAGER']),
                'created_at': datetime.now(), 'company_representative_image': f'https://via.placeholder.com/100x100?text=Logo',
                'url': f'https://www.rallit.com/positions/{i+1}', 'started_at': '2024-01-01', 'ended_at': '2024-12-31'
            })
        return pd.DataFrame(sample_data)

# 메인 애플리케이션
def main():
    st.markdown('<h1 class="main-header">🚀 Rallit 스마트 채용 대시보드</h1>', unsafe_allow_html=True)
    st.markdown("## 🎯 해결하고자 하는 문제들")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="problem-card"><h3>👤 구직자 문제</h3><ul><li>적합한 공고 찾기 어려움</li><li>JD-스펙 미스매칭</li><li>성장과정 평가 부족</li></ul></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="problem-card"><h3>🏢 기업 문제</h3><ul><li>실무역량 판단 어려움</li><li>정량적 기준 부족</li><li>성과 예측 불가능</li></ul></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="problem-card"><h3>🔧 플랫폼 문제</h3><ul><li>성장여정 미반영</li><li>단순 키워드 매칭</li><li>최신 트렌드 부족</li></ul></div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 데이터 로딩
    data_loader = SmartDataLoader()
    matching_engine = SmartMatchingEngine()
    with st.spinner('데이터를 로딩중입니다...'):
        df = data_loader.load_from_database()
    
    if df.empty:
        st.error("😕 데이터를 로드할 수 없습니다.")
        return

    # --- 사이드바 ---
    st.sidebar.header("🎯 스마트 매칭 필터")
    st.sidebar.subheader("👤 당신의 프로필")
    user_skills_input = st.sidebar.text_area("보유 기술 스택 (쉼표로 구분)", placeholder="예: Python, React, AWS")
    job_categories = ['전체'] + list(df['job_category'].unique())
    user_category = st.sidebar.selectbox("관심 직무", job_categories)
    
    with st.sidebar.expander("📈 성장 프로필 (선택)"):
        recent_courses = st.number_input("최근 1년 수강 강의 수", 0, 50, 0)
        project_count = st.number_input("개인/팀 프로젝트 수", 0, 20, 0)
        github_contributions = st.number_input("GitHub 연간 기여도", 0, 1000, 0)
    
    user_profile = {
        'skills': [s.strip() for s in user_skills_input.split(',') if s.strip()],
        'recent_courses': recent_courses, 'project_count': project_count,
        'github_contributions': github_contributions
    }
    
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 일반 필터")
    regions = ['전체'] + sorted(list(df['address_region'].dropna().unique()))
    selected_region = st.sidebar.selectbox("근무 지역", regions)
    reward_filter = st.sidebar.checkbox("지원금 있는 공고만")
    
    if st.sidebar.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()

    filtered_df = df.copy()
    if user_category != '전체': filtered_df = filtered_df[filtered_df['job_category'] == user_category]
    if selected_region != '전체': filtered_df = filtered_df[filtered_df['address_region'] == selected_region]
    if reward_filter: filtered_df = filtered_df[filtered_df['join_reward'] > 0]

    # --- 메인 탭 ---
    tabs = st.tabs(["🎯 스마트 매칭", "📊 시장 분석", "📈 성장 경로", "🏢 기업 인사이트", "🔮 예측 분석", "📋 상세 데이터"])

    with tabs[0]:
        st.header("🎯 AI 기반 스마트 Job 매칭")
        if user_skills_input:
            matching_results = []
            for _, job in filtered_df.iterrows():
                match_score, matched, missing = matching_engine.calculate_skill_match(user_profile['skills'], job['job_skill_keywords'])
                if match_score > 20: # 최소 매칭 점수
                    matching_results.append({'title': job['title'], 'company': job['company_name'], 'score': match_score, 'matched': matched, 'missing': missing})
            matching_results.sort(key=lambda x: x['score'], reverse=True)

            st.subheader("🌟 맞춤 추천 공고")
            for i, res in enumerate(matching_results[:5]):
                with st.expander(f"🏆 #{i+1} {res['title']} - 매칭도: {res['score']:.1f}%"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**회사:** {res['company']}")
                        if res['matched']: st.markdown("".join([f'<div class="skill-match">✅ {s}</div>' for s in res['matched']]), unsafe_allow_html=True)
                        if res['missing']: st.markdown("".join([f'<div class="skill-gap">📖 {s}</div>' for s in res['missing'][:3]]), unsafe_allow_html=True)
                    with col2:
                        fig = go.Figure(go.Indicator(mode="gauge+number", value=res['score'], title={'text': "매칭도"}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#667eea"}}))
                        fig.update_layout(height=200, margin=dict(l=20,r=20,t=40,b=20))
                        st.plotly_chart(fig, use_container_width=True)

            growth_score, factors = matching_engine.analyze_growth_potential(user_profile)
            st.markdown("---"); st.subheader("📈 당신의 성장 잠재력")
            col1, col2 = st.columns([1, 2])
            with col1:
                fig = go.Figure(go.Indicator(mode="gauge+number", value=growth_score, title={'text': "성장 잠재력"}))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.markdown("**🌱 성장 요인 분석:**")
                for factor in factors: st.markdown(f'<div class="growth-indicator">🌟 {factor}</div>', unsafe_allow_html=True)
        else:
            st.info("👆 사이드바에서 보유 기술 스택을 입력하면 맞춤 공고를 추천해드립니다!")

    with tabs[1]:
        st.header("📊 채용 시장 트렌드 분석")
        col1, col2 = st.columns(2)
        with col1:
            counts = filtered_df['job_category'].value_counts()
            fig = px.pie(values=counts.values, names=counts.index, title="직무별 공고 분포", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            counts = filtered_df['address_region'].value_counts().head(8)
            fig = px.bar(x=counts.values, y=counts.index, orientation='h', title="상위 8개 지역 채용 현황")
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("🔥 인기 기술 스택 트렌드")
        skills = filtered_df['job_skill_keywords'].dropna().str.split(',').explode().str.strip()
        skill_counts = skills[skills != ''].value_counts().head(15)
        fig = px.bar(x=skill_counts.values, y=skill_counts.index, orientation='h', title="TOP 15 인기 기술")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        st.header("📈 개인 성장 경로 분석")
        if user_skills_input:
            target_skills = df[df['job_category'] == user_category]['job_skill_keywords'] if user_category != '전체' else df['job_skill_keywords']
            req_skills = target_skills.dropna().str.split(',').explode().str.strip()
            req_counts = req_skills[req_skills != ''].value_counts().head(10)
            
            user_s = [s.lower() for s in user_profile['skills']]
            gap_data = [{'skill': s, 'demand': c, 'status': '보유' if s.lower() in user_s else '학습 필요'} for s, c in req_counts.items()]
            gap_df = pd.DataFrame(gap_data)

            fig = px.bar(gap_df, x='demand', y='skill', color='status', orientation='h', title=f"{user_category} 핵심 스킬 갭 분석", color_discrete_map={'보유': 'green', '학습 필요': 'orange'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("👆 사이드바에서 프로필을 입력하면 성장 경로를 분석해 드립니다!")

    with tabs[3]:
        st.header("🏢 기업 인사이트")
        top_companies = filtered_df['company_name'].value_counts().head(10)
        st.bar_chart(top_companies, height=400)

    with tabs[4]:
        st.header("🔮 예측 분석")
        st.info("AI 기반 예측 기능은 곧 출시될 예정입니다. 🚀")
        
    with tabs[5]:
        st.header("📋 채용 공고 상세 정보")
        st.dataframe(filtered_df, use_container_width=True)
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📄 CSV 다운로드", data=csv, file_name="rallit_jobs.csv")


def show_solutions():
    st.markdown("## 🎯 우리의 솔루션")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="solution-card"><h3>👤 구직자를 위한 솔루션</h3><ul><li>AI 기반 스마트 매칭</li><li>개인화된 성장 경로 제안</li><li>스킬 갭 분석 및 학습 가이드</li><li>성장 잠재력 시각화</li></ul></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="solution-card"><h3>🏢 기업을 위한 솔루션</h3><ul><li>후보자 성장 히스토리 분석</li><li>채용 성과 예측 모델</li><li>실무 역량 정량화</li><li>문화 적합성 분석</li></ul></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="solution-card"><h3>🔧 플랫폼 혁신</h3><ul><li>AI 기반 동적 매칭</li><li>실시간 시장 트렌드 분석</li><li>개인화된 인사이트 제공</li><li>예측 기반 추천 시스템</li></ul></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    try:
        main()
        st.markdown("---")
        show_solutions()
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 15px; color: white;'>
                <h3>🚀 Rallit 스마트 채용 플랫폼</h3>
                <p><strong>AI가 연결하는 완벽한 매칭, 성장이 증명하는 진짜 역량</strong></p>
                <p>📧 contact@rallit.com | 🌐 www.rallit.com | 📱 Rallit Mobile App</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"애플리케이션 실행 중 오류가 발생했습니다: {e}")
        logger.error(f"Application error: {e}", exc_info=True)
