# app.py - 통합된 Rallit 스마트 채용 대시보드

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from components.loader import SmartDataLoader
from components.matcher import SmartMatchingEngine

st.set_page_config(
    page_title="Rallit 스마트 채용 대시보드",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    st.markdown("---")

    # 데이터 로딩
    data_loader = SmartDataLoader()
    matching_engine = SmartMatchingEngine()
    with st.spinner('데이터를 로딩중입니다...'):
        df = data_loader.load_from_database()

    if df.empty:
        st.error("😕 데이터를 로드할 수 없습니다.")
        return

    # --- 사이드바 필터 --- #
    st.sidebar.header("🎯 스마트 매칭 필터")
    st.sidebar.subheader("👤 당신의 프로필")
    user_skills_input = st.sidebar.text_area("보유 기술 스택 (쉼표로 구분)", placeholder="예: Python, React, AWS")
    job_categories = ['전체'] + sorted(df['job_category'].dropna().unique().tolist())
    user_category = st.sidebar.selectbox("관심 직무", job_categories)

    with st.sidebar.expander("📈 성장 프로필 (선택)"):
        recent_courses = st.number_input("최근 1년 수강 강의 수", 0, 50, 0)
        project_count = st.number_input("개인/팀 프로젝트 수", 0, 20, 0)
        github_contributions = st.number_input("GitHub 연간 기여도", 0, 1000, 0)

    user_profile = {
        'skills': [s.strip() for s in user_skills_input.split(',') if s.strip()],
        'recent_courses': recent_courses,
        'project_count': project_count,
        'github_contributions': github_contributions
    }

    st.sidebar.markdown("---")
    st.sidebar.header("🔍 고급 필터")
    selected_region = st.sidebar.selectbox("📍 근무 지역", ['전체'] + sorted(df['address_region'].dropna().unique()))
    reward_filter = st.sidebar.checkbox("💰 지원금 있는 공고만 보기")
    partner_filter = st.sidebar.checkbox("🤝 파트너 기업만 보기")
    selected_status = st.sidebar.multiselect("📌 공고 상태", df['status_name'].dropna().unique(), default=df['status_name'].dropna().unique())
    join_reward_range = st.sidebar.slider("💵 지원금 범위 (원)", int(df['join_reward'].min()), int(df['join_reward'].max()), (int(df['join_reward'].min()), int(df['join_reward'].max())))
    selected_levels = st.sidebar.multiselect("📈 직무 레벨", df['job_level'].dropna().unique(), default=df['job_level'].dropna().unique())
    keyword_input = st.sidebar.text_input("🔍 키워드 검색 (공고명/회사명)", "")

    if st.sidebar.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()

    # 필터 적용
    filtered_df = df.copy()
    if user_category != '전체':
        filtered_df = filtered_df[filtered_df['job_category'] == user_category]
    if selected_region != '전체':
        filtered_df = filtered_df[filtered_df['address_region'] == selected_region]
    if reward_filter:
        filtered_df = filtered_df[filtered_df['join_reward'] > 0]
    if partner_filter:
        filtered_df = filtered_df[filtered_df['is_partner'] == 1]
    if selected_status:
        filtered_df = filtered_df[filtered_df['status_name'].isin(selected_status)]
    if selected_levels:
        filtered_df = filtered_df[filtered_df['job_level'].isin(selected_levels)]
    filtered_df = filtered_df[(filtered_df['join_reward'] >= join_reward_range[0]) & (filtered_df['join_reward'] <= join_reward_range[1])]
    if keyword_input:
        keyword = keyword_input.lower()
        filtered_df = filtered_df[filtered_df['title'].str.lower().str.contains(keyword) | filtered_df['company_name'].str.lower().str.contains(keyword)]

    # --- 탭 구성 --- #
    tabs = st.tabs(["🎯 스마트 매칭", "📊 시장 분석", "📈 성장 경로", "🏢 기업 인사이트", "🔮 예측 분석", "📋 상세 데이터"])

    with tabs[0]:
        from views.smart_matching import render_smart_matching
        render_smart_matching(filtered_df, user_profile, matching_engine)

    with tabs[1]:
        from views.market_analysis import render_market_analysis
        render_market_analysis(filtered_df)

    with tabs[2]:
        from views.growth_path import render_growth_path
        render_growth_path(df, user_profile, user_category)

    with tabs[3]:
        from views.company_insight import render_company_insight
        render_company_insight(filtered_df)

    with tabs[4]:
        st.header("🔮 예측 분석")
        st.info("AI 기반 예측 기능은 곧 출시될 예정입니다. 🚀")

    with tabs[5]:
        from views.detail_table import render_detail_table
        render_detail_table(filtered_df)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"애플리케이션 실행 중 오류가 발생했습니다: {str(e)}")
