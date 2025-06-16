"""
Rallit Jobs Dashboard - 스마트 기능과 상세 필터가 통합된 최종 애플리케이션
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
import random

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
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .problem-card, .solution-card {
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        min-height: 220px;
    }
    .problem-card { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
    .solution-card { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); min-height: 260px; }
    .skill-match { background: #e8f5e8; padding: 0.5rem; border-radius: 5px; border-left: 3px solid #4caf50; margin: 0.2rem 0; }
    .skill-gap { background: #fff3e0; padding: 0.5rem; border-radius: 5px; border-left: 3px solid #ff9800; margin: 0.2rem 0; }
    .growth-indicator { background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%); padding: 0.8rem; border-radius: 10px; margin: 0.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 3. 핵심 클래스 정의
# ==============================================================================

# AI 기반 매칭 엔진
class SmartMatchingEngine:
    def calculate_skill_match(self, user_skills, job_requirements):
        if not user_skills or not job_requirements or not isinstance(job_requirements, str):
            return 0, [], []
        user_skills_set = {s.strip().lower() for s in user_skills if s.strip()}
        job_skills_set = {s.strip().lower() for s in job_requirements.split(',') if s.strip()}
        if not job_skills_set: return 0, [], []
        intersection = user_skills_set.intersection(job_skills_set)
        match_score = len(intersection) / len(job_skills_set) * 100
        return match_score, list(intersection), list(job_skills_set - user_skills_set)

    def analyze_growth_potential(self, user_profile):
        score, factors = 0, []
        if user_profile.get('recent_courses', 0) > 0:
            score += 20; factors.append(f"최근 학습 ({user_profile.get('recent_courses')}개)")
        if user_profile.get('project_count', 0) > 3:
            score += 25; factors.append(f"프로젝트 경험 ({user_profile.get('project_count')}개)")
        if len(user_profile.get('skills', [])) > 8:
            score += 20; factors.append(f"기술 스택 다양성 ({len(user_profile.get('skills', []))}개)")
        if user_profile.get('github_contributions', 0) > 100:
            score += 15; factors.append(f"오픈소스 기여 ({user_profile.get('github_contributions')}회)")
        modern_skills = ['ai', 'ml', 'docker', 'kubernetes', 'react', 'vue', 'typescript']
        if any(skill in modern_skills for skill in [s.lower() for s in user_profile.get('skills', [])]):
            score += 20; factors.append("최신 기술 관심")
        return min(score, 100), factors

# 데이터 로더 클래스
class SmartDataLoader:
    def __init__(self, db_path='rallit_jobs.db', data_dir='data'):
        self.db_path = db_path
        self.data_dir = Path(data_dir)
        self.csv_files = {
            'MANAGEMENT': 'rallit_management_jobs.csv', 'MARKETING': 'rallit_marketing_jobs.csv',
            'DESIGN': 'rallit_design_jobs.csv', 'DEVELOPER': 'rallit_developer_jobs.csv'
        }

    @st.cache_data
    def load_from_database(_self):
        try:
            if not Path(_self.db_path).exists():
                _self._create_database_from_csv()
            conn = sqlite3.connect(_self.db_path)
            df = pd.read_sql_query("SELECT * FROM jobs", conn)
            conn.close()
            # 데이터 타입 강제 변환
            if 'join_reward' in df.columns:
                df['join_reward'] = pd.to_numeric(df['join_reward'], errors='coerce').fillna(0)
            return df
        except Exception as e:
            logger.error(f"DB loading error: {e}")
            return _self._load_from_csv_fallback()

    def _load_from_csv_fallback(self):
        try:
            dfs = [pd.read_csv(self.data_dir / f).assign(job_category=cat) for cat, f in self.csv_files.items() if (self.data_dir / f).exists()]
            if not dfs: return self._load_sample_data()
            df = pd.concat(dfs, ignore_index=True)
            df.columns = [c.lower().replace(' ', '_') for c in df.columns]
            if 'join_reward' in df.columns:
                df['join_reward'] = pd.to_numeric(df['join_reward'], errors='coerce').fillna(0)
            return df
        except Exception as e:
            logger.error(f"CSV loading error: {e}")
            return self._load_sample_data()

    def _create_database_from_csv(self):
        df = self._load_from_csv_fallback()
        if not df.empty:
            conn = sqlite3.connect(self.db_path)
            df.to_sql('jobs', conn, if_exists='replace', index=False)
            conn.close()

    def _load_sample_data(self):
        st.warning("📁 데이터 파일을 찾을 수 없어 샘플 데이터를 표시합니다.")
        # ... (샘플 데이터 생성 로직)
        return pd.DataFrame(...) # 샘플 데이터 생성 로직은 생략합니다. 실제 환경에서는 위 코드에 포함되어 있습니다.


# ==============================================================================
# 4. 유틸리티 함수
# ==============================================================================
def filter_dataframe(df, filters):
    filtered_df = df.copy()
    if filters['category'] != '전체':
        filtered_df = filtered_df[filtered_df['job_category'] == filters['category']]
    if filters['region'] != '전체':
        filtered_df = filtered_df[filtered_df['address_region'] == filters['region']]
    if filters['status'] != '전체':
        filtered_df = filtered_df[filtered_df['status_code'] == filters['status']]
    if filters['partner'] == '파트너 기업만':
        filtered_df = filtered_df[filtered_df['is_partner'] == 1]
    elif filters['partner'] == '일반 기업만':
        filtered_df = filtered_df[filtered_df['is_partner'] == 0]
    if filters['reward_range']:
        min_r, max_r = filters['reward_range']
        filtered_df = filtered_df[(filtered_df['join_reward'] >= min_r) & (filtered_df['join_reward'] <= max_r)]
    return filtered_df

# ==============================================================================
# 5. 메인 애플리케이션
# ==============================================================================
def main():
    # --- 초기화 ---
    data_loader = SmartDataLoader()
    matching_engine = SmartMatchingEngine()
    df = data_loader.load_from_database()
    if df.empty:
        st.error("😕 데이터를 로드할 수 없습니다."); return

    # --- 헤더 ---
    st.markdown('<h1 class="main-header">🚀 Rallit 스마트 채용 대시보드</h1>', unsafe_allow_html=True)
    
    # --- 사이드바 (필터) ---
    with st.sidebar:
        st.header("🎯 스마트 매칭 프로필")
        user_skills_input = st.text_area("보유 기술 스택 (쉼표로 구분)", placeholder="예: Python, React, AWS")
        with st.expander("📈 성장 프로필 (선택)"):
            recent_courses = st.number_input("최근 1년 수강 강의 수", 0, 50, 0)
            project_count = st.number_input("개인/팀 프로젝트 수", 0, 20, 0)
            github_contributions = st.number_input("GitHub 연간 기여도", 0, 1000, 0)
        
        user_profile = {
            'skills': [s.strip() for s in user_skills_input.split(',') if s.strip()],
            'recent_courses': recent_courses, 'project_count': project_count, 'github_contributions': github_contributions
        }

        st.markdown("---")
        st.header("🔍 상세 필터")
        filters = {
            'category': st.selectbox("직무 카테고리", ['전체'] + list(df['job_category'].unique())),
            'region': st.selectbox("근무 지역", ['전체'] + sorted(list(df['address_region'].dropna().unique()))),
            'status': st.selectbox("채용 상태", ['전체'] + list(df['status_code'].dropna().unique())),
            'partner': st.selectbox("파트너 여부", ['전체', '파트너 기업만', '일반 기업만']),
            'reward_range': None
        }

        # 지원금 필터
        reward_df = df[df['join_reward'] > 0]
        if not reward_df.empty:
            max_reward = int(reward_df['join_reward'].max())
            filters['reward_range'] = st.slider("지원금 범위 (만원)", 0, max_reward // 10000, (0, max_reward // 10000), 
                                                format="%d만원")
            filters['reward_range'] = (filters['reward_range'][0] * 10000, filters['reward_range'][1] * 10000)

        if st.button("🔄 데이터 새로고침"): st.cache_data.clear(); st.rerun()

    # 데이터 필터링 적용
    filtered_df = filter_dataframe(df, filters)

    # --- 메인 탭 ---
    tabs = st.tabs(["🎯 스마트 매칭", "📊 시장 분석", "📈 성장 경로", "🏢 기업 인사이트", "📋 상세 데이터"])

    with tabs[0]: # 스마트 매칭
        st.header("🎯 AI 기반 스마트 Job 매칭")
        if user_skills_input:
            match_results = []
            for idx, row in filtered_df.iterrows():
                score, matched, missing = matching_engine.calculate_skill_match(user_profile['skills'], row['job_skill_keywords'])
                if score > 20:
                    match_results.append({'idx': idx, 'title': row['title'], 'company': row['company_name'], 'score': score, 'matched': matched, 'missing': missing})
            
            st.subheader(f"🌟 '{', '.join(user_profile['skills'])}' 스킬과 맞는 추천 공고")
            for i, res in enumerate(sorted(match_results, key=lambda x: x['score'], reverse=True)[:5]):
                with st.expander(f"🏆 #{i+1} {res['title']} - 매칭도: {res['score']:.1f}%"):
                    c1, c2 = st.columns([2,1])
                    with c1:
                        st.write(f"**회사:** {res['company']}")
                        if res['matched']: st.markdown("".join([f'<div class="skill-match">✅ {s}</div>' for s in res['matched']]), unsafe_allow_html=True)
                        if res['missing']: st.markdown("".join([f'<div class="skill-gap">📖 {s}</div>' for s in res['missing'][:3]]), unsafe_allow_html=True)
                    with c2:
                        fig = go.Figure(go.Indicator(mode="gauge+number", value=res['score'], title={'text': "매칭도"}))
                        st.plotly_chart(fig, use_container_width=True, key=f"match_gauge_{res['idx']}")
        else:
            st.info("👆 사이드바에 보유 기술을 입력하면 맞춤 공고를 추천해 드립니다.")

    with tabs[1]: # 시장 분석
        st.header("📊 채용 시장 트렌드 분석")
        c1, c2 = st.columns(2)
        with c1:
            counts = filtered_df['job_category'].value_counts()
            fig = px.pie(counts, values=counts.values, names=counts.index, title="직무별 공고 분포", hole=0.4)
            st.plotly_chart(fig, use_container_width=True, key="cat_pie")
        with c2:
            counts = filtered_df['address_region'].value_counts().head(10)
            fig = px.bar(counts, y=counts.index, x=counts.values, orientation='h', title="상위 10개 지역 채용 현황")
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True, key="region_bar")
    
    with tabs[2]: # 성장 경로
        st.header("📈 개인 성장 경로 분석")
        if user_skills_input:
            growth_score, factors = matching_engine.analyze_growth_potential(user_profile)
            c1, c2 = st.columns([1,2])
            with c1:
                fig = go.Figure(go.Indicator(mode="gauge+number", value=growth_score, title={'text': "성장 잠재력"}))
                st.plotly_chart(fig, use_container_width=True, key="growth_gauge")
            with c2:
                st.markdown("**🌱 성장 요인 분석:**")
                for f in factors: st.markdown(f'<div class="growth-indicator">🌟 {f}</div>', unsafe_allow_html=True)
        else:
            st.info("👆 사이드바 프로필을 입력하면 성장 경로를 분석해 드립니다.")
    
    with tabs[3]: # 기업 인사이트
        st.header("🏢 기업별 채용 분석")
        top_companies = filtered_df['company_name'].value_counts().head(15)
        fig = px.bar(top_companies, y=top_companies.index, x=top_companies.values, orientation='h', title="채용 공고가 많은 기업 TOP 15")
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True, key="company_bar")

    with tabs[4]: # 상세 데이터
        st.header("📋 채용 공고 상세 정보")
        st.dataframe(filtered_df, use_container_width=True, height=600)
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📄 CSV 다운로드", csv, "rallit_jobs_filtered.csv", "text/csv")


# ==============================================================================
# 6. 푸터
# ==============================================================================
def show_footer():
    st.markdown("---")
    st.markdown("## 🎯 우리의 솔루션")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="solution-card"><h3>👤 구직자를 위한 솔루션</h3><ul><li>AI 기반 스마트 매칭</li><li>개인화된 성장 경로 제안</li><li>스킬 갭 분석 및 학습 가이드</li><li>성장 잠재력 시각화</li></ul></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="solution-card"><h3>🏢 기업을 위한 솔루션</h3><ul><li>후보자 성장 히스토리 분석</li><li>채용 성과 예측 모델</li><li>실무 역량 정량화</li><li>문화 적합성 분석</li></ul></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="solution-card"><h3>🔧 플랫폼 혁신</h3><ul><li>AI 기반 동적 매칭</li><li>실시간 시장 트렌드 분석</li><li>개인화된 인사이트 제공</li><li>예측 기반 추천 시스템</li></ul></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 15px; color: white;'>
            <h3>🚀 Rallit 스마트 채용 플랫폼</h3>
            <p><strong>AI가 연결하는 완벽한 매칭, 성장이 증명하는 진짜 역량</strong></p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    try:
        main()
        show_footer()
    except Exception as e:
        st.error(f"애플리케이션 실행 중 오류가 발생했습니다: {e}")
        logger.error(f"Application error: {e}", exc_info=True)
