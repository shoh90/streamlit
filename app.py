# app.py - 단일 파일 통합 버전 (시각화 추가)

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ------------------------
# 클래스 정의
# ------------------------

class SmartDataLoader:
    def __init__(self, db_path='rallit_jobs.db'):
        self.db_path = db_path

    def load_from_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query("SELECT * FROM jobs", conn)
            conn.close()
            return df
        except Exception as e:
            st.error(f"데이터베이스 로드 실패: {e}")
            return pd.DataFrame()

class SmartMatchingEngine:
    def calculate_skill_match(self, user_skills, job_requirements):
        if not user_skills or not job_requirements:
            return 0, [], []
        user_set = set([s.strip().lower() for s in user_skills])
        job_set = set([s.strip().lower() for s in job_requirements.split(',')])
        matched = user_set & job_set
        missing = job_set - user_set
        score = len(matched) / len(job_set) * 100 if job_set else 0
        return score, list(matched), list(missing)

    def analyze_growth_potential(self, profile):
        score = 0
        details = []
        if profile.get("recent_courses", 0) > 0:
            score += 20
            details.append("학습 활동 활발")
        if profile.get("project_count", 0) > 3:
            score += 30
            details.append("다양한 프로젝트 경험")
        if profile.get("github_contributions", 0) > 100:
            score += 20
            details.append("개발 커밋 활발")
        return min(score, 100), details

# ------------------------
# 페이지 설정
# ------------------------

st.set_page_config(
    page_title="Rallit 스마트 채용 대시보드",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------
# 메인 함수
# ------------------------

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
    st.markdown("## 🧭 기획 목적")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### ✅ 구직자 관점
        - 빠르게 변화하는 채용 트렌드(AI, 코딩 등)에 기반한 성장 가이드 제공  
        - JD 기반 역량 분석을 통해 나의 현재 위치와 개선 방향을 명확히 파악  
        - AI 첨삭 및 성장 히스토리를 통해 실력과 준비도를 '보여줄 수 있는' 구조 제공  
        - 지원 가능한 공고를 맞춤형으로 추천 받아, 더 정확하게 이직·입사 가능성 확보
        """)
    with col2:
        st.markdown("""
        ### 💼 기업 관점
        - 스펙이 아닌, 성장 히스토리와 역량 기반으로 ‘준비된 인재’ 확보 가능  
        - JD 기반 적합도 점수 및 온보딩·근속 예측 등 정량 지표 기반 검토 가능  
        - 기업이 원하는 역량 중심으로 구직자를 필터링하고 접근 가능  
        - AI 기반 최신 채용공고 작성 포맷으로 더 나은 공고 품질 확보 및 채용률 제고  
        """)

    # ------------------------
    # 데이터 로딩 및 시각화 요약
    # ------------------------

    st.markdown("---")
    data_loader = SmartDataLoader()
    matching_engine = SmartMatchingEngine()
    with st.spinner('데이터를 로딩중입니다...'):
        df = data_loader.load_from_database()

    if df.empty:
        st.error("😕 데이터를 로드할 수 없습니다.")
        return

    st.subheader("📊 전체 채용 시장 요약")
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(df, names='job_category', title="직무별 공고 비중", hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        top_regions = df['address_region'].value_counts().head(7)
        fig2 = px.bar(x=top_regions.values, y=top_regions.index, orientation='h', title="지역별 공고 수 Top7")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ------------------------
    # 사이드바 필터 및 매칭
    # ------------------------

    st.sidebar.header("🎯 스마트 매칭 필터")
    user_skills_input = st.sidebar.text_area("보유 기술 스택 (쉼표로 구분)", placeholder="예: Python, React, AWS")
    job_categories = ['전체'] + sorted(df['job_category'].dropna().unique().tolist())
    user_category = st.sidebar.selectbox("관심 직무", job_categories)

    user_profile = {
        'skills': [s.strip() for s in user_skills_input.split(',') if s.strip()],
        'recent_courses': st.sidebar.number_input("최근 1년 수강 강의 수", 0, 50, 0),
        'project_count': st.sidebar.number_input("개인/팀 프로젝트 수", 0, 20, 0),
        'github_contributions': st.sidebar.number_input("GitHub 연간 기여도", 0, 1000, 0)
    }

    st.sidebar.markdown("---")
    st.sidebar.header("🔍 고급 필터")
    selected_region = st.sidebar.selectbox("📍 근무 지역", ['전체'] + sorted(df['address_region'].dropna().unique()))
    reward_filter = st.sidebar.checkbox("💰 지원금 있는 공고만 보기")

    filtered_df = df.copy()
    if user_category != '전체':
        filtered_df = filtered_df[filtered_df['job_category'] == user_category]
    if selected_region != '전체':
        filtered_df = filtered_df[filtered_df['address_region'] == selected_region]
    if reward_filter:
        filtered_df = filtered_df[filtered_df['join_reward'] > 0]

    st.header("🎯 스마트 매칭 결과")
    if user_skills_input:
        results = []
        for _, row in filtered_df.iterrows():
            score, matched, missing = matching_engine.calculate_skill_match(user_profile['skills'], row['job_skill_keywords'])
            if score > 20:
                results.append({
                    '공고명': row['title'],
                    '회사명': row['company_name'],
                    '매칭도': f"{score:.1f}%",
                    '보유 스킬': ', '.join(matched),
                    '필요 스킬': ', '.join(missing[:3])
                })
        if results:
            st.dataframe(pd.DataFrame(results))
        else:
            st.info("🔍 입력하신 기술에 맞는 공고가 없습니다.")
    else:
        st.info("👈 사이드바에서 기술 스택을 입력해주세요.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"애플리케이션 실행 중 오류가 발생했습니다: {str(e)}")
