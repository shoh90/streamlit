# app.py - 단일 파일 통합 버전 (시각화 + UX 개선 + 예측 분석 + 노동시장 변화)

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random

# ------------------------
# 유틸 함수
# ------------------------

def preprocess_dataframe(df):
    for col in ['join_reward', 'is_partner', 'is_bookmarked']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

def apply_filters(df, category, region, reward_only):
    if category != '전체':
        df = df[df['job_category'] == category]
    if region != '전체':
        df = df[df['address_region'] == region]
    if reward_only:
        df = df[df['join_reward'] > 0]
    return df

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
            return preprocess_dataframe(df)
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

    def predict_success_probability(self, score, growth):
        return round((score * 0.7 + growth * 0.3), 1)

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

    st.markdown("---")
    st.markdown("## 🧮 노동시장 변화 분석")
    st.info("📊 최근 노동시장 데이터를 기반으로 새로운 채용 흐름을 분석합니다. 예: 60세 이상 고용 증가 +11.1%, 상용직 증가 +2.4%")

    st.markdown("""
    - **고령자 채용**: 60세 이상 인구의 취업자 수 증가율은 11.1%로 전체 고용 증가를 주도하고 있습니다.  
    - **상용직 증가**: 고용안정성이 높은 상용직이 전년 대비 37.5만 명 증가했습니다.  
    - **산업별 채용 변화**: AI, 플랫폼 서비스 등에서 신직업군 수요가 증가하고 있습니다.  
    """)

    st.markdown("---")
    st.markdown("## 📊 전체 채용 시장 요약")

    data_loader = SmartDataLoader()
    matching_engine = SmartMatchingEngine()
    df = data_loader.load_from_database()

    if df.empty:
        st.error("😕 데이터를 로드할 수 없습니다.")
        return

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.pie(df, names='job_category', title="직무별 공고 비중", hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        top_regions = df['address_region'].value_counts().head(7)
        fig2 = px.bar(x=top_regions.values, y=top_regions.index, orientation='h', title="지역별 공고 수 Top7")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🔥 인기 기술 스택 TOP 10")
    skills = df['job_skill_keywords'].dropna().str.split(',').explode().str.strip()
    skill_counts = skills[skills != ''].value_counts().head(10)
    fig3 = px.bar(skill_counts, x=skill_counts.values, y=skill_counts.index, orientation='h', title="Top 10 기술 키워드")
    st.plotly_chart(fig3, use_container_width=True)

    # 이하 기존 내용 유지...

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"애플리케이션 실행 중 오류가 발생했습니다: {str(e)}")
