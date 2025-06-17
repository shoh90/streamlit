# Enhanced Rallit Smart Recruitment Dashboard
# 고도화된 Rallit 스마트 채용 대시보드

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from pathlib import Path
import logging
import random
import re
import requests
from bs4 import BeautifulSoup
import folium
from streamlit_folium import st_folium
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from typing import Dict, List, Tuple, Optional
import hashlib

# ==============================================================================
# 1. 페이지 및 환경 설정
# ==============================================================================
st.set_page_config(
    page_title="갓생라이프/커리어하이어 - AI 기반 성장형 채용 플랫폼",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==============================================================================
# 2. 고도화된 커스텀 CSS 및 스타일링
# ==============================================================================
st.markdown("""
<style>
    /* 전체 레이아웃 스타일링 */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* KPI 카드 디자인 개선 */
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border: none;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
        text-align: center;
        height: 100%;
        color: white;
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    .kpi-card h3 {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .kpi-card p {
        font-size: 2.2rem;
        font-weight: 700;
        color: white;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .kpi-card small {
        font-size: 0.85rem;
        color: rgba(255, 255, 255, 0.7);
    }
    
    /* 매칭 결과 카드 */
    .match-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
        transition: transform 0.3s ease;
    }
    
    .match-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    }
    
    /* 스킬 태그 디자인 */
    .skill-match {
        display: inline-block;
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.85em;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
    }
    
    .skill-gap {
        display: inline-block;
        background: linear-gradient(135deg, #FF9800, #F57C00);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.85em;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
    }
    
    /* 성장 지표 카드 */
    .growth-indicator {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* 탭 스타일링 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #333;
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(102, 126, 234, 0.1);
    }
    
    /* 사이드바 스타일링 */
    .sidebar-section {
        background: rgba(255, 255, 255, 0.95);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* 애니메이션 */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* 진행률 바 */
    .progress-bar {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 8px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    /* 성공 확률 게이지 */
    .success-gauge {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    
    /* 알림 스타일 */
    .alert-info {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, #fdcb6e, #e17055);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #55a3ff, #667eea);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* 차트 컨테이너 */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. 고도화된 데이터 모델 및 클래스
# ==============================================================================

class EnhancedSmartDataLoader:
    """고도화된 데이터 로더 클래스"""
    
    def __init__(self, db_path='rallit_jobs.db', data_dir='data'):
        self.db_path = db_path
        self.data_dir = Path(data_dir)
        self.csv_files = {
            'MANAGEMENT': 'rallit_management_jobs.csv',
            'MARKETING': 'rallit_marketing_jobs.csv', 
            'DESIGN': 'rallit_design_jobs.csv',
            'DEVELOPER': 'rallit_developer_jobs.csv'
        }
        
    @st.cache_data(ttl=3600)  # 1시간 캐시
    def load_from_database(_self):
        """데이터베이스에서 데이터 로드"""
        try:
            if not Path(_self.db_path).exists():
                _self._create_database_from_csv()
            
            conn = sqlite3.connect(_self.db_path)
            df = pd.read_sql_query("SELECT * FROM jobs", conn)
            conn.close()
            
            # 데이터 타입 최적화
            df = _self._optimize_dataframes(df)
            return df
            
        except Exception as e:
            logger.error(f"Database loading error: {e}")
            return _self._load_from_csv_fallback()
    
    def _optimize_dataframes(self, df):
        """데이터프레임 최적화"""
        # 수치형 컬럼 최적화
        numeric_columns = ['join_reward', 'is_partner', 'is_bookmarked', 'age']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # 날짜 컬럼 최적화
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        
        # 범주형 컬럼 최적화
        categorical_columns = ['job_category', 'address_region', 'status_code', 'job_level', 'gender']
        for col in categorical_columns:
            if col in df.columns:
                df[col] = df[col].astype('category')
        
        return df
    
    def _load_from_csv_fallback(self):
        """CSV 파일에서 폴백 로드"""
        try:
            dfs = []
            for category, filename in self.csv_files.items():
                file_path = self.data_dir / filename
                if file_path.exists():
                    temp_df = pd.read_csv(file_path)
                    temp_df['job_category'] = category
                    dfs.append(temp_df)
            
            if not dfs:
                return self._generate_enhanced_sample_data()
            
            df = pd.concat(dfs, ignore_index=True)
            df.columns = [c.lower().replace(' ', '_').replace('.', '_') for c in df.columns]
            
            # 추가 데이터 엔리치먼트
            df = self._enrich_data(df)
            return self._optimize_dataframes(df)
            
        except Exception as e:
            logger.error(f"CSV loading error: {e}")
            return self._generate_enhanced_sample_data()
    
    def _enrich_data(self, df):
        """데이터 엔리치먼트"""
        # 인구통계학적 데이터 추가
        if 'age' not in df.columns:
            df['age'] = np.random.normal(32, 8, len(df)).clip(22, 65).astype(int)
        
        if 'gender' not in df.columns:
            df['gender'] = np.random.choice(['남성', '여성'], len(df), p=[0.52, 0.48])
        
        if 'experience_years' not in df.columns:
            df['experience_years'] = np.random.gamma(2, 2, len(df)).clip(0, 20).astype(int)
        
        if 'education_level' not in df.columns:
            df['education_level'] = np.random.choice(
                ['고등학교', '전문대', '대학교', '대학원'], 
                len(df), 
                p=[0.1, 0.2, 0.6, 0.1]
            )
        
        # 기술 스택 강화
        if 'job_skill_keywords' not in df.columns or df['job_skill_keywords'].isna().all():
            df['job_skill_keywords'] = df['job_category'].apply(self._generate_skills_by_category)
        
        # 생성 날짜 추가
        if 'created_at' not in df.columns:
            start_date = datetime.now() - timedelta(days=365)
            df['created_at'] = [
                start_date + timedelta(days=random.randint(0, 365))
                for _ in range(len(df))
            ]
        
        # 회사 규모 추가
        if 'company_size' not in df.columns:
            df['company_size'] = np.random.choice(
                ['스타트업(1-50명)', '중소기업(51-300명)', '중견기업(301-1000명)', '대기업(1000명+)'],
                len(df),
                p=[0.4, 0.35, 0.15, 0.1]
            )
        
        # 원격근무 가능 여부
        if 'remote_possible' not in df.columns:
            df['remote_possible'] = np.random.choice([0, 1], len(df), p=[0.6, 0.4])
        
        return df
    
    def _generate_skills_by_category(self, category):
        """카테고리별 기술 스택 생성"""
        skill_pools = {
            'DEVELOPER': ['Python', 'Java', 'JavaScript', 'React', 'Vue.js', 'Node.js', 'Spring', 'Docker', 'Kubernetes', 'AWS', 'GCP', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Git', 'Jenkins', 'TypeScript', 'Go', 'Kotlin'],
            'DESIGN': ['Figma', 'Sketch', 'Adobe XD', 'Photoshop', 'Illustrator', 'Principle', 'Zeplin', 'InVision', 'Framer', 'After Effects', 'UI/UX', 'Prototyping', 'Wireframing', 'User Research'],
            'MARKETING': ['Google Analytics', 'Facebook Ads', 'Google Ads', 'SEO', 'SEM', 'Content Marketing', 'Email Marketing', 'Social Media', 'Adobe Creative Suite', 'Hootsuite', 'Mailchimp', 'HubSpot', 'Salesforce'],
            'MANAGEMENT': ['Agile', 'Scrum', 'Kanban', 'Jira', 'Confluence', 'Slack', 'Notion', 'Excel', 'PowerPoint', 'Project Management', 'Leadership', 'Team Building', 'Strategic Planning']
        }
        
        skills = skill_pools.get(category, ['Communication', 'Teamwork', 'Problem Solving'])
        selected_skills = random.sample(skills, min(random.randint(3, 8), len(skills)))
        return ', '.join(selected_skills)
    
    def _generate_enhanced_sample_data(self):
        """고도화된 샘플 데이터 생성"""
        st.warning("📁 실제 데이터 파일을 찾을 수 없어 고도화된 샘플 데이터를 생성합니다.")
        
        sample_size = 1000
        categories = ['DEVELOPER', 'DESIGN', 'MARKETING', 'MANAGEMENT']
        regions = ['PANGYO', 'GANGNAM', 'HONGDAE', 'JONGNO', 'SEONGSU', 'YEOUIDO', 'BUNDANG', 'ILSAN']
        
        companies = [
            '테크스타트업A', 'AI컴퍼니B', '빅데이터C', '핀테크D', '이커머스E', 
            '게임회사F', '엔터테인먼트G', '로지스틱스H', '헬스케어I', '에듀테크J',
            '삼성전자', 'LG전자', '네이버', '카카오', '쿠팡', '배달의민족', 'KB국민은행', 'SK텔레콤'
        ]
        
        job_levels = ['ENTRY', 'JUNIOR', 'SENIOR', 'LEAD', 'MANAGER', 'DIRECTOR']
        
        data = []
        for i in range(sample_size):
            category = random.choice(categories)
            data.append({
                'id': i + 1,
                'job_category': category,
                'address_region': random.choice(regions),
                'company_name': random.choice(companies),
                'title': f'{category} 개발자' if category == 'DEVELOPER' else f'{category} 전문가',
                'is_partner': random.choice([0, 1]),
                'join_reward': random.choice([0, 50000, 100000, 200000, 300000, 500000, 1000000]),
                'job_skill_keywords': self._generate_skills_by_category(category),
                'job_level': random.choice(job_levels),
                'status_code': random.choice(['RECRUITING', 'CLOSED', 'PENDING']),
                'age': random.randint(22, 65),
                'gender': random.choice(['남성', '여성']),
                'experience_years': random.randint(0, 20),
                'education_level': random.choice(['고등학교', '전문대', '대학교', '대학원']),
                'company_size': random.choice(['스타트업(1-50명)', '중소기업(51-300명)', '중견기업(301-1000명)', '대기업(1000명+)']),
                'remote_possible': random.choice([0, 1]),
                'created_at': datetime.now() - timedelta(days=random.randint(0, 365))
            })
        
        return pd.DataFrame(data)

class AdvancedMatchingEngine:
    """고도화된 AI 매칭 엔진"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
        self.skill_weights = {
            'python': 1.2, 'java': 1.1, 'javascript': 1.1, 'react': 1.15,
            'aws': 1.2, 'docker': 1.1, 'kubernetes': 1.1, 'ai': 1.3, 'ml': 1.3,
            'figma': 1.1, 'adobe': 1.0, 'google analytics': 1.1
        }
    
    def calculate_advanced_skill_match(self, user_skills: List[str], job_requirements: str, 
                                     job_category: str = None) -> Tuple[float, List[str], List[str], Dict]:
        """고도화된 스킬 매칭 계산"""
        if not user_skills or not job_requirements:
            return 0, [], [], {}
        
        user_skills_clean = [s.strip().lower() for s in user_skills if s.strip()]
        job_skills_clean = [s.strip().lower() for s in job_requirements.split(',') if s.strip()]
        
        if not job_skills_clean:
            return 0, [], [], {}
        
        # 기본 매칭 계산
        user_set = set(user_skills_clean)
        job_set = set(job_skills_clean)
        intersection = user_set.intersection(job_set)
        missing = job_set - user_set
        
        # 가중치 적용 매칭 점수
        weighted_score = 0
        total_weight = 0
        
        for skill in job_skills_clean:
            weight = self.skill_weights.get(skill, 1.0)
            total_weight += weight
            if skill in user_skills_clean:
                weighted_score += weight
        
        match_score = (weighted_score / total_weight * 100) if total_weight > 0 else 0
        
        # 유사 스킬 매칭 (예: React ↔ Vue.js)
        similar_matches = self._find_similar_skills(user_skills_clean, list(missing))
        
        # 카테고리별 보너스
        category_bonus = self._calculate_category_bonus(user_skills_clean, job_category)
        
        final_score = min(match_score + category_bonus, 100)
        
        analysis = {
            'basic_score': len(intersection) / len(job_set) * 100,
            'weighted_score': match_score,
            'category_bonus': category_bonus,
            'similar_matches': similar_matches,
            'total_required': len(job_set),
            'matched_count': len(intersection)
        }
        
        return final_score, list(intersection), list(missing), analysis
    
    def _find_similar_skills(self, user_skills: List[str], missing_skills: List[str]) -> List[Tuple[str, str]]:
        """유사 스킬 찾기"""
        similar_skills = {
            'react': ['vue.js', 'angular', 'svelte'],
            'vue.js': ['react', 'angular'],
            'python': ['java', 'go', 'kotlin'],
            'aws': ['gcp', 'azure'],
            'mysql': ['postgresql', 'mongodb'],
            'figma': ['sketch', 'adobe xd'],
            'photoshop': ['illustrator', 'gimp']
        }
        
        matches = []
        for user_skill in user_skills:
            for missing_skill in missing_skills:
                if missing_skill in similar_skills.get(user_skill, []):
                    matches.append((user_skill, missing_skill))
        
        return matches
    
    def _calculate_category_bonus(self, user_skills: List[str], job_category: str) -> float:
        """카테고리별 보너스 점수 계산"""
        if not job_category:
            return 0
        
        category_skills = {
            'DEVELOPER': ['python', 'java', 'javascript', 'react', 'docker', 'aws'],
            'DESIGN': ['figma', 'sketch', 'photoshop', 'illustrator', 'ui/ux'],
            'MARKETING': ['google analytics', 'facebook ads', 'seo', 'content marketing'],
            'MANAGEMENT': ['agile', 'scrum', 'jira', 'leadership']
        }
        
        relevant_skills = category_skills.get(job_category, [])
        matching_relevant = sum(1 for skill in user_skills if skill in relevant_skills)
        
        return min(matching_relevant * 2, 10)  # 최대 10점 보너스
    
    def analyze_advanced_growth_potential(self, user_profile: Dict) -> Tuple[float, List[str], Dict]:
        """고도화된 성장 잠재력 분석"""
        score = 0
        factors = []
        detailed_analysis = {}
        
        # 학습 활동 점수 (0-25점)
        recent_courses = user_profile.get('recent_courses', 0)
        if recent_courses > 0:
            learning_score = min(recent_courses * 5, 25)
            score += learning_score
            factors.append(f"적극적 학습 활동 ({recent_courses}개 강의)")
            detailed_analysis['learning_score'] = learning_score
        
        # 프로젝트 경험 (0-30점)
        project_count = user_profile.get('project_count', 0)
        if project_count > 0:
            project_score = min(project_count * 5, 30)
            score += project_score
            factors.append(f"실무 프로젝트 경험 ({project_count}개)")
            detailed_analysis['project_score'] = project_score
        
        # 기술 다양성 (0-20점)
        skills_count = len(user_profile.get('skills', []))
        if skills_count > 0:
            diversity_score = min(skills_count * 2, 20)
            score += diversity_score
            factors.append(f"기술 스택 다양성 ({skills_count}개)")
            detailed_analysis['diversity_score'] = diversity_score
        
        # 오픈소스 기여 (0-15점)
        github_contributions = user_profile.get('github_contributions', 0)
        if github_contributions > 0:
            oss_score = min(github_contributions / 10, 15)
            score += oss_score
            factors.append(f"오픈소스 기여 ({github_contributions}회)")
            detailed_analysis['oss_score'] = oss_score
        
        # 최신 기술 트렌드 (0-10점)
        modern_skills = ['ai', 'ml', 'kubernetes', 'react', 'typescript', 'go', 'rust']
        user_skills_lower = [s.lower() for s in user_profile.get('skills', [])]
        modern_count = sum(1 for skill in modern_skills if skill in user_skills_lower)
        if modern_count > 0:
            trend_score = min(modern_count * 2, 10)
            score += trend_score
            factors.append(f"최신 기술 트렌드 관심 ({modern_count}개)")
            detailed_analysis['trend_score'] = trend_score
        
        final_score = min(score, 100)
        detailed_analysis['total_score'] = final_score
        
        return final_score, factors, detailed_analysis
    
    def predict_advanced_success_probability(self, skill_score: float, growth_score: float, 
                                           experience_match: bool = False, 
                                           company_size_match: bool = False) -> Dict:
        """고도화된 성공 확률 예측"""
        base_probability = skill_score * 0.6 + growth_score * 0.3
        
        # 추가 요인들
        experience_bonus = 5 if experience_match else 0
        company_bonus = 3 if company_size_match else 0
        
        final_probability = min(base_probability + experience_bonus + company_bonus, 95)
        
        # 신뢰구간 계산
        confidence = max(60, min(90, (skill_score + growth_score) / 2))
        
        return {
            'probability': round(final_probability, 1),
            'confidence': round(confidence, 1),
            'factors': {
                'skill_contribution': skill_score * 0.6,
                'growth_contribution': growth_score * 0.3,
                'experience_bonus': experience_bonus,
                'company_bonus': company_bonus
            }
        }

class TrendAnalyzer:
    """채용 트렌드 분석기"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def analyze_skill_trends(self) -> Dict:
        """기술 스택 트렌드 분석"""
        if 'job_skill_keywords' not in self.df.columns:
            return {}
        
        # 최근 6개월 데이터
        recent_cutoff = datetime.now() - timedelta(days=180)
        recent_df = self.df[self.df['created_at'] >= recent_cutoff] if 'created_at' in self.df.columns else self.df
        
        # 전체 기간 vs 최근 기간 비교
        all_skills = self._extract_skills(self.df)
        recent_skills = self._extract_skills(recent_df)
        
        # 성장률 계산
        growth_rates = {}
        for skill in set(all_skills.keys()) | set(recent_skills.keys()):
            all_count = all_skills.get(skill, 0)
            recent_count = recent_skills.get(skill, 0)
            
            if all_count > 0:
                # 6개월치 데이터를 연간으로 환산하여 성장률 계산
                annualized_recent = recent_count * 2  # 6개월 -> 12개월 환산
                growth_rate = ((annualized_recent - all_count) / all_count) * 100
                growth_rates[skill] = growth_rate
        
        return {
            'all_period': all_skills,
            'recent_period': recent_skills,
            'growth_rates': growth_rates,
            'trending_up': dict(sorted(growth_rates.items(), key=lambda x: x[1], reverse=True)[:10]),
            'trending_down': dict(sorted(growth_rates.items(), key=lambda x: x[1])[:5])
        }
    
    def _extract_skills(self, df: pd.DataFrame) -> Dict[str, int]:
        """데이터프레임에서 스킬 추출"""
        skills_series = df['job_skill_keywords'].dropna().str.split(',').explode().str.strip().str.lower()
        return skills_series[skills_series != ''].value_counts().to_dict()
    
    def analyze_salary_trends(self) -> Dict:
        """지원금/연봉 트렌드 분석"""
        if 'join_reward' not in self.df.columns:
            return {}
        
        reward_stats = {
            'mean': self.df['join_reward'].mean(),
            'median': self.df['join_reward'].median(),
            'std': self.df['join_reward'].std(),
            'percentiles': {
                '25th': self.df['join_reward'].quantile(0.25),
                '75th': self.df['join_reward'].quantile(0.75),
                '90th': self.df['join_reward'].quantile(0.90)
            }
        }
        
        # 카테고리별 지원금 분석
        category_rewards = self.df.groupby('job_category')['join_reward'].agg(['mean', 'median', 'count']).round(0)
        
        return {
            'overall_stats': reward_stats,
            'by_category': category_rewards.to_dict(),
            'high_reward_jobs': self.df.nlargest(10, 'join_reward')[['title', 'company_name', 'join_reward']].to_dict('records')
        }
    
    def analyze_regional_trends(self) -> Dict:
        """지역별 채용 트렌드 분석"""
        regional_stats = self.df.groupby('address_region').agg({
            'id': 'count',
            'join_reward': ['mean', 'median'],
            'is_partner': 'sum'
        }).round(0)
        
        regional_stats.columns = ['job_count', 'avg_reward', 'median_reward', 'partner_count']
        
        return {
            'regional_distribution': regional_stats.to_dict(),
            'top_regions': regional_stats.nlargest(10, 'job_count').to_dict('records')
        }

class GrowthPathGenerator:
    """개인 성장 경로 생성기"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.career_paths = {
            'DEVELOPER': {
                'entry_level': ['HTML/CSS', 'JavaScript', 'Git', 'Basic Programming'],
                'junior_level': ['React/Vue', 'Node.js', 'Database', 'API Development'],
                'senior_level': ['System Architecture', 'DevOps', 'Cloud Services', 'Team Leadership'],
                'lead_level': ['Technical Strategy', 'Mentoring', 'Project Management', 'Business Acumen']
            },
            'DESIGN': {
                'entry_level': ['Figma/Sketch', 'Design Principles', 'Typography', 'Color Theory'],
                'junior_level': ['UI/UX Design', 'Prototyping', 'User Research', 'Design Systems'],
                'senior_level': ['Design Strategy', 'Team Collaboration', 'Business Understanding', 'Advanced Tools'],
                'lead_level': ['Design Leadership', 'Strategy Planning', 'Team Management', 'Innovation']
            },
            'MARKETING': {
                'entry_level': ['Digital Marketing Basics', 'Google Analytics', 'Content Writing', 'Social Media'],
                'junior_level': ['SEO/SEM', 'Campaign Management', 'Data Analysis', 'Marketing Automation'],
                'senior_level': ['Marketing Strategy', 'ROI Analysis', 'Team Leadership', 'Cross-channel Integration'],
                'lead_level': ['Strategic Planning', 'Budget Management', 'Team Development', 'Innovation']
            },
            'MANAGEMENT': {
                'entry_level': ['Project Coordination', 'Basic Analytics', 'Communication', 'Time Management'],
                'junior_level': ['Project Management', 'Team Coordination', 'Process Improvement', 'Stakeholder Management'],
                'senior_level': ['Strategic Planning', 'Team Leadership', 'Budget Management', 'Performance Management'],
                'lead_level': ['Executive Leadership', 'Organizational Strategy', 'Change Management', 'Innovation']
            }
        }
    
    def generate_personalized_path(self, user_profile: Dict, target_category: str) -> Dict:
        """개인 맞춤 성장 경로 생성"""
        user_skills = [skill.lower().strip() for skill in user_profile.get('skills', [])]
        career_path = self.career_paths.get(target_category, {})
        
        current_level = self._assess_current_level(user_skills, career_path)
        next_skills = self._recommend_next_skills(user_skills, career_path, current_level)
        learning_resources = self._suggest_learning_resources(next_skills)
        
        return {
            'current_level': current_level,
            'next_skills': next_skills,
            'learning_resources': learning_resources,
            'career_roadmap': self._create_roadmap(career_path, user_skills)
        }
    
    def _assess_current_level(self, user_skills: List[str], career_path: Dict) -> str:
        """현재 레벨 평가"""
        level_scores = {}
        
        for level, required_skills in career_path.items():
            required_lower = [skill.lower() for skill in required_skills]
            matches = sum(1 for user_skill in user_skills if any(req in user_skill or user_skill in req for req in required_lower))
            level_scores[level] = matches / len(required_skills) if required_skills else 0
        
        # 70% 이상 만족하는 가장 높은 레벨 반환
        for level in ['lead_level', 'senior_level', 'junior_level', 'entry_level']:
            if level_scores.get(level, 0) >= 0.7:
                return level
        
        return 'entry_level'
    
    def _recommend_next_skills(self, user_skills: List[str], career_path: Dict, current_level: str) -> List[str]:
        """다음 학습 스킬 추천"""
        level_order = ['entry_level', 'junior_level', 'senior_level', 'lead_level']
        current_index = level_order.index(current_level)
        
        recommendations = []
        
        # 현재 레벨에서 부족한 스킬
        current_skills = career_path.get(current_level, [])
        current_lower = [skill.lower() for skill in current_skills]
        missing_current = [skill for skill in current_skills 
                          if not any(user_skill in skill.lower() or skill.lower() in user_skill 
                                   for user_skill in user_skills)]
        recommendations.extend(missing_current[:3])
        
        # 다음 레벨 스킬
        if current_index < len(level_order) - 1:
            next_level = level_order[current_index + 1]
            next_skills = career_path.get(next_level, [])[:3]
            recommendations.extend(next_skills)
        
        return recommendations[:5]  # 최대 5개 추천
    
    def _suggest_learning_resources(self, skills: List[str]) -> Dict:
        """학습 리소스 제안"""
        resource_mapping = {
            'javascript': {'platform': 'JavaScript.info', 'type': '무료 튜토리얼'},
            'react': {'platform': 'React 공식 문서', 'type': '공식 가이드'},
            'python': {'platform': 'Python.org Tutorial', 'type': '무료 튜토리얼'},
            'figma': {'platform': 'Figma Academy', 'type': '무료 강의'},
            'google analytics': {'platform': 'Google Analytics Academy', 'type': '무료 인증'},
            'project management': {'platform': 'PMP 자격증', 'type': '전문 자격'},
        }
        
        resources = {}
        for skill in skills:
            skill_lower = skill.lower()
            for key, resource in resource_mapping.items():
                if key in skill_lower:
                    resources[skill] = resource
                    break
            else:
                resources[skill] = {'platform': 'Coursera/Udemy', 'type': '온라인 강의'}
        
        return resources
    
    def _create_roadmap(self, career_path: Dict, user_skills: List[str]) -> List[Dict]:
        """커리어 로드맵 생성"""
        roadmap = []
        level_names = {
            'entry_level': '입문자',
            'junior_level': '주니어',
            'senior_level': '시니어',
            'lead_level': '리드/매니저'
        }
        
        for level, skills in career_path.items():
            user_skills_lower = [skill.lower() for skill in user_skills]
            completed = sum(1 for skill in skills if any(us in skill.lower() or skill.lower() in us for us in user_skills_lower))
            
            roadmap.append({
                'level': level_names.get(level, level),
                'skills': skills,
                'completion_rate': completed / len(skills) * 100 if skills else 0,
                'completed_skills': completed,
                'total_skills': len(skills)
            })
        
        return roadmap

# ==============================================================================
# 4. 고도화된 시각화 컴포넌트
# ==============================================================================

def create_advanced_kpi_cards(df: pd.DataFrame):
    """고도화된 KPI 카드 생성"""
    cols = st.columns(4)
    
    # 총 채용공고 수
    with cols[0]:
        total_jobs = len(df)
        active_jobs = len(df[df['status_code'] == 'RECRUITING']) if 'status_code' in df.columns else total_jobs
        st.markdown(f"""
        <div class="kpi-card">
            <h3>📊 총 채용공고</h3>
            <p>{total_jobs:,}</p>
            <small>활성: {active_jobs:,}개</small>
        </div>
        """, unsafe_allow_html=True)
    
    # 평균 지원금
    with cols[1]:
        avg_reward = df['join_reward'].mean() if 'join_reward' in df.columns else 0
        max_reward = df['join_reward'].max() if 'join_reward' in df.columns else 0
        st.markdown(f"""
        <div class="kpi-card">
            <h3>💰 평균 지원금</h3>
            <p>{avg_reward:,.0f}원</p>
            <small>최고: {max_reward:,.0f}원</small>
        </div>
        """, unsafe_allow_html=True)
    
    # 파트너 기업 비율
    with cols[2]:
        partner_rate = (df['is_partner'].sum() / len(df) * 100) if 'is_partner' in df.columns else 0
        partner_count = df['is_partner'].sum() if 'is_partner' in df.columns else 0
        st.markdown(f"""
        <div class="kpi-card">
            <h3>🤝 파트너 기업</h3>
            <p>{partner_rate:.1f}%</p>
            <small>{partner_count}개 기업</small>
        </div>
        """, unsafe_allow_html=True)
    
    # 원격근무 가능 비율
    with cols[3]:
        remote_rate = (df['remote_possible'].sum() / len(df) * 100) if 'remote_possible' in df.columns else 0
        remote_count = df['remote_possible'].sum() if 'remote_possible' in df.columns else 0
        st.markdown(f"""
        <div class="kpi-card">
            <h3>🏠 원격근무 가능</h3>
            <p>{remote_rate:.1f}%</p>
            <small>{remote_count}개 공고</small>
        </div>
        """, unsafe_allow_html=True)

def create_advanced_skill_visualization(df: pd.DataFrame):
    """고도화된 스킬 시각화"""
    if 'job_skill_keywords' not in df.columns:
        st.warning("스킬 데이터가 없습니다.")
        return
    
    # 스킬 데이터 처리
    skills_series = df['job_skill_keywords'].dropna().str.split(',').explode().str.strip()
    skill_counts = skills_series[skills_series != ''].value_counts().head(20)
    
    if skill_counts.empty:
        st.warning("스킬 데이터가 없습니다.")
        return
    
    # 두 개의 시각화: 바 차트와 워드클라우드 스타일
    col1, col2 = st.columns(2)
    
    with col1:
        fig_bar = px.bar(
            y=skill_counts.index, 
            x=skill_counts.values,
            orientation='h',
            title="📈 TOP 20 인기 기술 스택",
            labels={'x': '언급 횟수', 'y': '기술'},
            color=skill_counts.values,
            color_continuous_scale='viridis'
        )
        fig_bar.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=600,
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # 스킬 카테고리별 분류
        skill_categories = {
            'Frontend': ['javascript', 'react', 'vue', 'angular', 'html', 'css', 'typescript'],
            'Backend': ['python', 'java', 'node.js', 'spring', 'django', 'flask'],
            'DevOps': ['docker', 'kubernetes', 'aws', 'gcp', 'azure', 'jenkins'],
            'Database': ['mysql', 'postgresql', 'mongodb', 'redis'],
            'Design': ['figma', 'sketch', 'photoshop', 'illustrator', 'adobe xd'],
            'Marketing': ['google analytics', 'facebook ads', 'seo', 'content marketing']
        }
        
        categorized_skills = {'기타': []}
        for skill in skill_counts.index:
            skill_lower = skill.lower()
            categorized = False
            for category, category_skills in skill_categories.items():
                if any(cat_skill in skill_lower for cat_skill in category_skills):
                    if category not in categorized_skills:
                        categorized_skills[category] = []
                    categorized_skills[category].append(skill)
                    categorized = True
                    break
            if not categorized:
                categorized_skills['기타'].append(skill)
        
        # 카테고리별 스킬 수 계산
        category_counts = {cat: len(skills) for cat, skills in categorized_skills.items() if skills}
        
        fig_pie = px.pie(
            values=list(category_counts.values()),
            names=list(category_counts.keys()),
            title="🎯 기술 카테고리별 분포",
            hole=0.4
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

def create_market_trend_dashboard(df: pd.DataFrame):
    """시장 트렌드 대시보드"""
    trend_analyzer = TrendAnalyzer(df)
    
    # 스킬 트렌드 분석
    skill_trends = trend_analyzer.analyze_skill_trends()
    
    if skill_trends:
        st.subheader("📈 기술 트렌드 분석")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🚀 급상승 기술**")
            trending_up = skill_trends.get('trending_up', {})
            if trending_up:
                for i, (skill, growth) in enumerate(list(trending_up.items())[:5]):
                    if growth > 0:
                        st.markdown(f"""
                        <div class="growth-indicator">
                            <strong>{skill.title()}</strong>
                            <span style="color: #4CAF50; font-weight: bold;">▲ {growth:.1f}%</span>
                        </div>
                        """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**📉 하락 기술**")
            trending_down = skill_trends.get('trending_down', {})
            if trending_down:
                for i, (skill, decline) in enumerate(list(trending_down.items())[:5]):
                    if decline < 0:
                        st.markdown(f"""
                        <div class="growth-indicator" style="background: linear-gradient(135deg, #ffcdd2 0%, #f8bbd9 100%);">
                            <strong>{skill.title()}</strong>
                            <span style="color: #f44336; font-weight: bold;">▼ {abs(decline):.1f}%</span>
                        </div>
                        """, unsafe_allow_html=True)
    
    # 지역별 분석
    st.subheader("🌍 지역별 채용 현황")
    regional_trends = trend_analyzer.analyze_regional_trends()
    
    if regional_trends:
        regional_data = regional_trends['regional_distribution']
        
        # 지역별 채용 공고 수와 평균 지원금
        fig_regional = make_subplots(
            rows=1, cols=2,
            subplot_titles=('지역별 채용 공고 수', '지역별 평균 지원금'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        regions = list(regional_data['job_count'].keys())
        job_counts = list(regional_data['job_count'].values())
        avg_rewards = list(regional_data['avg_reward'].values())
        
        fig_regional.add_trace(
            go.Bar(x=regions, y=job_counts, name="채용 공고 수", marker_color='lightblue'),
            row=1, col=1
        )
        
        fig_regional.add_trace(
            go.Bar(x=regions, y=avg_rewards, name="평균 지원금", marker_color='lightcoral'),
            row=1, col=2
        )
        
        fig_regional.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_regional, use_container_width=True)

# ==============================================================================
# 5. 고도화된 페이지 렌더링 함수들
# ==============================================================================

def render_enhanced_main_summary(df: pd.DataFrame):
    """고도화된 메인 요약 페이지"""
    # 헤더
    st.markdown("""
    <div class="main-header fade-in">
        <h1>🚀 갓생라이프/커리어하이어</h1>
        <p>AI 기반 성장형 채용 플랫폼 - "성장을 증명하고, 신뢰를 연결하다"</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI 카드
    create_advanced_kpi_cards(df)
    
    st.markdown("---")
    
    # 주요 인사이트
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 주요 채용 인사이트")
        
        # 카테고리별 분포
        category_counts = df['job_category'].value_counts()
        fig_category = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="직무 카테고리별 채용 분포",
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_category.update_traces(textposition='inside', textinfo='percent+label')
        fig_category.update_layout(height=400)
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        st.subheader("📊 Quick Stats")
        
        # 빠른 통계
        total_companies = df['company_name'].nunique()
        avg_reward = df['join_reward'].mean() if 'join_reward' in df.columns else 0
        top_region = df['address_region'].mode().iloc[0] if not df['address_region'].empty else "N/A"
        
        st.metric("참여 기업 수", f"{total_companies:,}개")
        st.metric("평균 지원금", f"{avg_reward:,.0f}원")
        st.metric("핫플레이스", top_region)
        
        # 최신 트렌드 알림
        st.markdown("""
        <div class="alert-info">
            <strong>🔥 최신 트렌드</strong><br>
            • AI/ML 개발자 수요 급증<br>
            • 원격근무 지원 확대<br>
            • 스킬 기반 채용 증가
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 시장 동향
    create_market_trend_dashboard(df)

def render_enhanced_smart_matching(filtered_df: pd.DataFrame, user_profile: Dict, 
                                 matching_engine: AdvancedMatchingEngine, all_df: pd.DataFrame):
    """고도화된 스마트 매칭 페이지"""
    st.header("🎯 AI 기반 스마트 매칭")
    
    if not user_profile['skills']:
        st.markdown("""
        <div class="alert-info">
            <h4>🌟 개인 맞춤 채용 매칭을 시작하세요!</h4>
            <p>사이드바에 보유 기술을 입력하면 AI가 분석한 맞춤 공고를 추천해드립니다.</p>
            <ul>
                <li>JD 적합도 분석</li>
                <li>성장 잠재력 평가</li>
                <li>최종 합격 확률 예측</li>
                <li>개인 맞춤 성장 경로 제안</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # 사용자 프로필 분석
    growth_score, growth_factors, growth_analysis = matching_engine.analyze_advanced_growth_potential(user_profile)
    
    # 프로필 요약 카드
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <h3>🧠 성장 잠재력</h3>
            <p>{growth_score:.0f}점</p>
            <small>AI 분석 결과</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        skill_count = len(user_profile['skills'])
        st.markdown(f"""
        <div class="kpi-card">
            <h3>⚡ 보유 기술</h3>
            <p>{skill_count}개</p>
            <small>등록된 스킬</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        matching_jobs = len(filtered_df)
        st.markdown(f"""
        <div class="kpi-card">
            <h3>🎯 매칭 공고</h3>
            <p>{matching_jobs}개</p>
            <small>조건 맞는 공고</small>
        </div>
        """, unsafe_allow_html=True)
    
    # 매칭 결과 계산
    match_results = []
    for idx, row in filtered_df.iterrows():
        skill_score, matched, missing, analysis = matching_engine.calculate_advanced_skill_match(
            user_profile['skills'], 
            row.get('job_skill_keywords', ''),
            row.get('job_category')
        )
        
        if skill_score > 15:  # 최소 매칭 기준
            success_prediction = matching_engine.predict_advanced_success_probability(
                skill_score, growth_score
            )
            
            match_results.append({
                'idx': idx,
                'title': row['title'],
                'company': row['company_name'],
                'category': row['job_category'],
                'region': row.get('address_region', 'N/A'),
                'reward': row.get('join_reward', 0),
                'skill_score': skill_score,
                'success_prob': success_prediction['probability'],
                'confidence': success_prediction['confidence'],
                'matched': matched,
                'missing': missing,
                'analysis': analysis
            })
    
    if not match_results:
        st.markdown("""
        <div class="alert-warning">
            <h4>😔 현재 조건에 맞는 추천 공고가 없습니다</h4>
            <p>다음을 시도해보세요:</p>
            <ul>
                <li>필터 조건을 더 넓게 설정</li>
                <li>다른 직무 카테고리 탐색</li>
                <li>보유 기술 스택 확장</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # 대안 제안
        with st.expander("💡 성장 제안 - 이런 스킬을 추가해보세요"):
            all_skills = all_df['job_skill_keywords'].dropna().str.split(',').explode().str.strip().str.lower()
            popular_skills = all_skills.value_counts().head(10)
            user_skills_lower = [s.lower() for s in user_profile['skills']]
            
            suggested_skills = [skill for skill in popular_skills.index 
                              if skill not in user_skills_lower][:5]
            
            for skill in suggested_skills:
                st.markdown(f"• **{skill.title()}** - {popular_skills[skill]}개 공고에서 요구")
        
        return
    
    # 매칭 결과 표시
    st.subheader(f"🌟 맞춤 추천 공고 ({len(match_results)}개)")
    
    # 상위 5개 결과 상세 표시
    top_matches = sorted(match_results, key=lambda x: x['success_prob'], reverse=True)[:5]
    
    for i, result in enumerate(top_matches):
        with st.expander(f"🏆 #{i+1} {result['title']} @ {result['company']} - 합격 확률 {result['success_prob']}%", expanded=(i == 0)):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # 기본 정보
                st.markdown(f"""
                **회사:** {result['company']}  
                **직무:** {result['category']}  
                **지역:** {result['region']}  
                **지원금:** {result['reward']:,}원
                """)
                
                # 스킬 매칭 상세
                st.markdown("**🎯 스킬 매칭 분석**")
                
                if result['matched']:
                    st.markdown("**보유 스킬 매치:** " + 
                              "".join([f'<span class="skill-match">✅ {s.title()}</span>' 
                                     for s in result['matched']]), unsafe_allow_html=True)
                
                if result['missing']:
                    st.markdown("**추가 학습 필요:** " + 
                              "".join([f'<span class="skill-gap">📚 {s.title()}</span>' 
                                     for s in result['missing'][:4]]), unsafe_allow_html=True)
                
                # 상세 분석
                analysis = result['analysis']
                st.markdown(f"""
                **📊 상세 분석:**
                - 기본 매칭도: {analysis['basic_score']:.1f}%
                - 가중 매칭도: {analysis['weighted_score']:.1f}%
                - 카테고리 보너스: +{analysis['category_bonus']:.1f}점
                """)
            
            with col2:
                # 성공 확률 게이지
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=result['success_prob'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "합격 확률"},
                    delta={'reference': 50},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "#667eea"},
                        'steps': [
                            {'range': [0, 25], 'color': "#ffcdd2"},
                            {'range': [25, 50], 'color': "#fff9c4"},
                            {'range': [50, 75], 'color': "#c8e6c9"},
                            {'range': [75, 100], 'color': "#a5d6a7"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                
                fig_gauge.update_layout(
                    height=200,
                    margin=dict(l=20, r=20, t=40, b=20),
                    font={'size': 12}
                )
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                # 신뢰도 표시
                st.metric("신뢰도", f"{result['confidence']:.0f}%")
                
                # 지원 버튼 (시뮬레이션)
                if st.button(f"지원하기 📤", key=f"apply_{result['idx']}"):
                    st.success("✅ 지원이 완료되었습니다! (시뮬레이션)")

def render_advanced_growth_path(df: pd.DataFrame, user_profile: Dict, target_category: str, 
                              matching_engine: AdvancedMatchingEngine):
    """고도화된 성장 경로 페이지"""
    st.header("📈 AI 기반 개인 성장 경로")
    
    if not user_profile['skills']:
        st.info("👆 사이드바에 보유 기술을 입력하면 맞춤 성장 경로를 분석해드립니다.")
        return
    
    # 성장 경로 생성기 초기화
    growth_generator = GrowthPathGenerator(df)
    
    # 성장 잠재력 분석
    growth_score, factors, detailed_analysis = matching_engine.analyze_advanced_growth_potential(user_profile)
    
    # 개인 성장 경로 생성
    if target_category != '전체':
        personalized_path = growth_generator.generate_personalized_path(user_profile, target_category)
    else:
        personalized_path = growth_generator.generate_personalized_path(user_profile, 'DEVELOPER')  # 기본값
    
    # 성장 현황 대시보드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <h3>🚀 성장 잠재력</h3>
            <p>{growth_score:.0f}/100</p>
            <small>AI 종합 평가</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        current_level = personalized_path.get('current_level', 'entry_level')
        level_names = {
            'entry_level': '입문자', 'junior_level': '주니어',
            'senior_level': '시니어', 'lead_level': '리드'
        }
        st.markdown(f"""
        <div class="kpi-card">
            <h3>📊 현재 레벨</h3>
            <p>{level_names.get(current_level, '평가중')}</p>
            <small>스킬 기반 평가</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        skill_count = len(user_profile['skills'])
        st.markdown(f"""
        <div class="kpi-card">
            <h3>⚡ 보유 스킬</h3>
            <p>{skill_count}개</p>
            <small>등록된 기술</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        next_skills_count = len(personalized_path.get('next_skills', []))
        st.markdown(f"""
        <div class="kpi-card">
            <h3>🎯 추천 학습</h3>
            <p>{next_skills_count}개</p>
            <small>다음 스킬</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 성장 요인 분석
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🌱 성장 요인 분석")
        
        if factors:
            for factor in factors:
                st.markdown(f"""
                <div class="growth-indicator">
                    <strong>✅ {factor}</strong>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="alert-info">
                성장 프로필을 더 자세히 입력하면<br>
                정확한 분석이 가능합니다.
            </div>
            """, unsafe_allow_html=True)
        
        # 상세 점수 분해
        if detailed_analysis:
            st.markdown("**📊 점수 상세 분해:**")
            for key, value in detailed_analysis.items():
                if key != 'total_score' and isinstance(value, (int, float)):
                    st.write(f"• {key.replace('_', ' ').title()}: {value:.0f}점")
    
    with col2:
        st.subheader("🎯 성장 잠재력 시각화")
        
        # 성장 잠재력 레이더 차트
        categories = ['학습 활동', '프로젝트 경험', '기술 다양성', '오픈소스 기여', '트렌드 관심']
        values = [
            detailed_analysis.get('learning_score', 0),
            detailed_analysis.get('project_score', 0),
            detailed_analysis.get('diversity_score', 0),
            detailed_analysis.get('oss_score', 0),
            detailed_analysis.get('trend_score', 0)
        ]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='현재 수준',
            line_color='rgb(102, 126, 234)'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 30]
                )),
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    
    st.markdown("---")
    
    # 커리어 로드맵
    st.subheader("🗺️ 개인 맞춤 커리어 로드맵")
    
    roadmap = personalized_path.get('career_roadmap', [])
    
    # 로드맵 진행도 시각화
    levels = [item['level'] for item in roadmap]
    completion_rates = [item['completion_rate'] for item in roadmap]
    
    fig_roadmap = go.Figure()
    fig_roadmap.add_trace(go.Bar(
        x=levels,
        y=completion_rates,
        text=[f"{rate:.0f}%" for rate in completion_rates],
        textposition='auto',
        marker_color=['#4CAF50' if rate >= 70 else '#FF9800' if rate >= 30 else '#f44336' 
                     for rate in completion_rates]
    ))
    
    fig_roadmap.update_layout(
        title="레벨별 스킬 완성도",
        xaxis_title="커리어 레벨",
        yaxis_title="완성도 (%)",
        height=400
    )
    st.plotly_chart(fig_roadmap, use_container_width=True)
    
    # 다음 학습 추천
    st.subheader("📚 추천 학습 스킬")
    
    next_skills = personalized_path.get('next_skills', [])
    learning_resources = personalized_path.get('learning_resources', {})
    
    if next_skills:
        cols = st.columns(min(len(next_skills), 3))
        
        for i, skill in enumerate(next_skills[:3]):
            with cols[i]:
                resource = learning_resources.get(skill, {})
                platform = resource.get('platform', 'Coursera/Udemy')
                resource_type = resource.get('type', '온라인 강의')
                
                st.markdown(f"""
                <div class="match-card">
                    <h4>🎯 {skill}</h4>
                    <p><strong>플랫폼:</strong> {platform}</p>
                    <p><strong>유형:</strong> {resource_type}</p>
                    <button style="background: linear-gradient(135deg, #667eea, #764ba2); 
                                   color: white; border: none; padding: 8px 16px; 
                                   border-radius: 20px; cursor: pointer;">
                        학습 시작하기
                    </button>
                </div>
                """, unsafe_allow_html=True)
    
    # 스킬 갭 분석
    st.subheader("🔍 시장 수요 vs 보유 스킬 분석")
    
    if target_category != '전체':
        target_df = df[df['job_category'] == target_category]
    else:
        target_df = df
    
    if 'job_skill_keywords' in target_df.columns:
        market_skills = target_df['job_skill_keywords'].dropna().str.split(',').explode().str.strip().str.lower()
        market_demand = market_skills.value_counts().head(15)
        
        user_skills_lower = [s.lower().strip() for s in user_profile['skills']]
        
        gap_data = []
        for skill, demand in market_demand.items():
            status = '보유 ✅' if skill in user_skills_lower else '학습 필요 📚'
            gap_data.append({
                'skill': skill.title(),
                'demand': demand,
                'status': status
            })
        
        gap_df = pd.DataFrame(gap_data)
        
        fig_gap = px.bar(
            gap_df,
            x='demand',
            y='skill',
            color='status',
            orientation='h',
            title=f"'{target_category}' 직무 핵심 스킬 수요 vs 보유 현황",
            color_discrete_map={'보유 ✅': '#4CAF50', '학습 필요 📚': '#FF9800'}
        )
        
        fig_gap.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=500
        )
        st.plotly_chart(fig_gap, use_container_width=True)

def render_enhanced_company_insights(filtered_df: pd.DataFrame):
    """고도화된 기업 인사이트 페이지"""
    st.header("🏢 기업별 채용 인사이트")
    
    if filtered_df.empty:
        st.warning("표시할 데이터가 없습니다. 필터를 조정해주세요.")
        return
    
    # 기업 기본 통계
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_companies = filtered_df['company_name'].nunique()
        st.markdown(f"""
        <div class="kpi-card">
            <h3>🏢 참여 기업</h3>
            <p>{total_companies}</p>
            <small>개</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_jobs_per_company = len(filtered_df) / total_companies if total_companies > 0 else 0
        st.markdown(f"""
        <div class="kpi-card">
            <h3>📊 평균 공고</h3>
            <p>{avg_jobs_per_company:.1f}</p>
            <small>개/기업</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        partner_companies = filtered_df[filtered_df['is_partner'] == 1]['company_name'].nunique() if 'is_partner' in filtered_df.columns else 0
        st.markdown(f"""
        <div class="kpi-card">
            <h3>🤝 파트너 기업</h3>
            <p>{partner_companies}</p>
            <small>개</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        high_reward_companies = filtered_df[filtered_df['join_reward'] > 100000]['company_name'].nunique() if 'join_reward' in filtered_df.columns else 0
        st.markdown(f"""
        <div class="kpi-card">
            <h3>💰 고액 지원금</h3>
            <p>{high_reward_companies}</p>
            <small>개 기업</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 상위 채용 기업
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 TOP 채용 기업")
        top_companies = filtered_df['company_name'].value_counts().head(15)
        
        fig_companies = px.bar(
            y=top_companies.index,
            x=top_companies.values,
            orientation='h',
            title="채용 공고 수 기준",
            labels={'x': '공고 수', 'y': '기업명'},
            color=top_companies.values,
            color_continuous_scale='Blues'
        )
        fig_companies.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=500,
            showlegend=False
        )
        st.plotly_chart(fig_companies, use_container_width=True)
    
    with col2:
        st.subheader("💎 기업 규모별 분포")
        
        if 'company_size' in filtered_df.columns:
            size_counts = filtered_df['company_size'].value_counts()
            
            fig_size = px.pie(
                values=size_counts.values,
                names=size_counts.index,
                title="기업 규모별 채용 공고",
                hole=0.4
            )
            fig_size.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_size, use_container_width=True)
        
        # 지원금 상위 기업
        st.subheader("💰 지원금 TOP 기업")
        if 'join_reward' in filtered_df.columns:
            reward_companies = filtered_df.groupby('company_name')['join_reward'].mean().sort_values(ascending=False).head(10)
            
            for i, (company, reward) in enumerate(reward_companies.items()):
                st.markdown(f"""
                <div class="growth-indicator">
                    <strong>#{i+1} {company}</strong><br>
                    <span style="color: #4CAF50; font-weight: bold;">평균 {reward:,.0f}원</span>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 기업별 상세 분석
    st.subheader("🔍 기업별 상세 분석")
    
    # 기업 선택
    selected_company = st.selectbox(
        "기업을 선택하세요:",
        ['전체 분석'] + sorted(filtered_df['company_name'].unique())
    )
    
    if selected_company != '전체 분석':
        company_df = filtered_df[filtered_df['company_name'] == selected_company]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 채용 공고", len(company_df))
            
        with col2:
            avg_reward = company_df['join_reward'].mean() if 'join_reward' in company_df.columns else 0
            st.metric("평균 지원금", f"{avg_reward:,.0f}원")
            
        with col3:
            categories = company_df['job_category'].nunique()
            st.metric("채용 직무 수", categories)
        
        # 해당 기업의 직무별 분포
        if len(company_df) > 1:
            category_dist = company_df['job_category'].value_counts()
            
            fig_company_cat = px.bar(
                x=category_dist.index,
                y=category_dist.values,
                title=f"{selected_company} 직무별 채용 현황",
                labels={'x': '직무', 'y': '공고 수'}
            )
            st.plotly_chart(fig_company_cat, use_container_width=True)
        
        # 요구 스킬 분석
        if 'job_skill_keywords' in company_df.columns:
            company_skills = company_df['job_skill_keywords'].dropna().str.split(',').explode().str.strip()
            skill_counts = company_skills[company_skills != ''].value_counts().head(10)
            
            if not skill_counts.empty:
                st.subheader(f"{selected_company} 주요 요구 스킬")
                
                fig_skills = px.bar(
                    x=skill_counts.values,
                    y=skill_counts.index,
                    orientation='h',
                    title="기술별 요구 빈도"
                )
                fig_skills.update_layout(yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig_skills, use_container_width=True)

def render_enhanced_prediction_analysis(df: pd.DataFrame):
    """고도화된 예측 분석 페이지"""
    st.header("🔮 AI 예측 분석 센터")
    
    # 예측 분석 소개
    st.markdown("""
    <div class="main-header fade-in">
        <h2>🤖 미래 채용 시장을 예측합니다</h2>
        <p>AI와 빅데이터 분석으로 채용 트렌드의 미래를 내다봅니다</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 현재 제공 가능한 예측 분석
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 스킬 트렌드 예측")
        
        # 간단한 트렌드 분석 (시뮬레이션)
        if 'job_skill_keywords' in df.columns:
            # 최근 데이터 기반 트렌드 예측
            skills_series = df['job_skill_keywords'].dropna().str.split(',').explode().str.strip().str.lower()
            skill_counts = skills_series[skills_series != ''].value_counts().head(10)
            
            # 성장률 시뮬레이션 (실제로는 시계열 분석 필요)
            predicted_growth = {}
            for skill in skill_counts.index:
                # AI/ML 관련 기술은 높은 성장률 예측
                if any(keyword in skill for keyword in ['ai', 'ml', 'python', 'react', 'kubernetes']):
                    growth = random.uniform(15, 30)
                else:
                    growth = random.uniform(-5, 15)
                predicted_growth[skill] = growth
            
            # 예측 결과 시각화
            growth_df = pd.DataFrame([
                {'skill': k.title(), 'current_demand': skill_counts[k], 'predicted_growth': v}
                for k, v in predicted_growth.items()
            ])
            
            fig_prediction = px.scatter(
                growth_df,
                x='current_demand',
                y='predicted_growth',
                text='skill',
                title="스킬별 현재 수요 vs 예측 성장률",
                labels={'current_demand': '현재 수요', 'predicted_growth': '예측 성장률 (%)'}
            )
            fig_prediction.update_traces(textposition="top center")
            st.plotly_chart(fig_prediction, use_container_width=True)
    
    with col2:
        st.subheader("💰 지원금 트렌드 예측")
        
        if 'join_reward' in df.columns and 'job_category' in df.columns:
            category_rewards = df.groupby('job_category')['join_reward'].mean()
            
            # 카테고리별 예측 성장률 (시뮬레이션)
            predicted_reward_growth = {
                'DEVELOPER': 12.5,
                'DESIGN': 8.3,
                'MARKETING': 6.7,
                'MANAGEMENT': 5.2
            }
            
            prediction_data = []
            for category in category_rewards.index:
                current_reward = category_rewards[category]
                growth_rate = predicted_reward_growth.get(category, 5.0)
                predicted_reward = current_reward * (1 + growth_rate/100)
                
                prediction_data.append({
                    'category': category,
                    'current': current_reward,
                    'predicted': predicted_reward,
                    'growth_rate': growth_rate
                })
            
            pred_df = pd.DataFrame(prediction_data)
            
            fig_reward = go.Figure()
            fig_reward.add_trace(go.Bar(
                name='현재 평균',
                x=pred_df['category'],
                y=pred_df['current'],
                marker_color='lightblue'
            ))
            fig_reward.add_trace(go.Bar(
                name='2025년 예측',
                x=pred_df['category'],
                y=pred_df['predicted'],
                marker_color='orange'
            ))
            
            fig_reward.update_layout(
                title="직무별 지원금 트렌드 예측",
                barmode='group',
                yaxis_title="지원금 (원)"
            )
            st.plotly_chart(fig_reward, use_container_width=True)
    
    st.markdown("---")
    
    # Coming Soon 기능들
    st.subheader("🚀 개발 예정 기능")
    
    future_features = [
        {
            "title": "📊 개인 연봉 예측 AI",
            "description": "보유 스킬, 경력, 지역 등을 종합하여 예상 연봉을 정확히 예측합니다.",
            "progress": 75,
            "eta": "2024년 Q2"
        },
        {
            "title": "🎯 커리어 성공 확률 예측",
            "description": "목표 직무로의 전환 성공 확률과 필요한 준비 기간을 예측합니다.",
            "progress": 60,
            "eta": "2024년 Q3"
        },
        {
            "title": "🏢 기업 문화 적합도 분석",
            "description": "개인 성향과 기업 문화를 매칭하여 최적의 직장을 추천합니다.",
            "progress": 40,
            "eta": "2024년 Q4"
        },
        {
            "title": "🌐 글로벌 채용 시장 분석",
            "description": "해외 취업 기회와 글로벌 스킬 트렌드를 분석합니다.",
            "progress": 25,
            "eta": "2025년 Q1"
        }
    ]
    
    for feature in future_features:
        st.markdown(f"""
        <div class="match-card">
            <h4>{feature['title']}</h4>
            <p>{feature['description']}</p>
            <div style="background-color: #f0f0f0; border-radius: 10px; overflow: hidden; margin: 10px 0;">
                <div style="background: linear-gradient(90deg, #667eea, #764ba2); 
                           height: 8px; width: {feature['progress']}%;"></div>
            </div>
            <small>진행률: {feature['progress']}% | 출시 예정: {feature['eta']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    # 사용자 피드백 섹션
    st.markdown("---")
    st.subheader("💬 원하는 예측 기능이 있나요?")
    
    user_feedback = st.text_area(
        "어떤 예측 기능이 필요한지 알려주세요:",
        placeholder="예: 특정 기업의 채용 패턴 예측, 산업별 성장 전망 등"
    )
    
    if st.button("피드백 제출"):
        if user_feedback.strip():
            st.success("✅ 소중한 피드백을 받았습니다! 개발 시 참고하겠습니다.")
        else:
            st.warning("피드백 내용을 입력해주세요.")

# ==============================================================================
# 6. 고도화된 사이드바 컴포넌트
# ==============================================================================

def render_enhanced_sidebar(df: pd.DataFrame):
    """고도화된 사이드바"""
    with st.sidebar:
        # 로고 및 브랜딩
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; margin-bottom: 1rem; color: white;">
            <h2>🚀 갓생라이프</h2>
            <p style="margin: 0; opacity: 0.9;">AI 기반 성장형 채용</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 사용자 프로필 섹션
        st.header("👤 개인 프로필")
        
        # 기본 정보
        user_name = st.text_input("이름 (선택)", placeholder="홍길동")
        user_email = st.text_input("이메일 (선택)", placeholder="user@example.com")
        
        # 스킬 입력
        st.subheader("⚡ 보유 기술 스택")
        user_skills_input = st.text_area(
            "기술을 쉼표로 구분하여 입력하세요",
            placeholder="Python, React, AWS, Figma",
            help="정확한 매칭을 위해 구체적으로 입력해주세요"
        )
        
        # 경력 정보
        st.subheader("💼 경력 정보")
        experience_years = st.slider("총 경력 (년)", 0, 20, 2)
        current_position = st.selectbox("현재 직급", 
                                       ["인턴", "주니어", "시니어", "리드", "매니저", "디렉터"])
        
        # 성장 프로필
        with st.expander("📈 성장 프로필", expanded=False):
            recent_courses = st.number_input("최근 1년 수강 강의 수", 0, 50, 0)
            project_count = st.number_input("개인/팀 프로젝트 수", 0, 20, 0)
            github_contributions = st.number_input("GitHub 연간 기여도", 0, 1000, 0)
            
            # 추가 성장 지표
            certification_count = st.number_input("보유 자격증 수", 0, 20, 0)
            blog_posts = st.number_input("기술 블로그 포스팅 수", 0, 100, 0)
            mentoring_experience = st.checkbox("멘토링 경험 있음")
        
        # 선호도 설정
        st.subheader("🎯 선호 조건")
        preferred_company_size = st.multiselect(
            "선호 기업 규모",
            ["스타트업(1-50명)", "중소기업(51-300명)", "중견기업(301-1000명)", "대기업(1000명+)"],
            default=["스타트업(1-50명)", "중소기업(51-300명)"]
        )
        
        remote_preference = st.select_slider(
            "원격근무 선호도",
            options=["완전 출근", "하이브리드", "완전 원격"],
            value="하이브리드"
        )
        
        min_salary = st.number_input("최소 희망 연봉 (만원)", 0, 20000, 3000, step=500)
        
        st.markdown("---")
        
        # 필터 섹션
        st.header("🔍 스마트 필터")
        
        # 기본 필터
        user_category = st.selectbox("관심 직무", 
                                    ['전체'] + sorted(list(df['job_category'].dropna().unique())))
        
        selected_region = st.selectbox("📍 근무 지역", 
                                      ['전체'] + sorted(list(df['address_region'].dropna().unique())))
        
        # 고급 필터
        with st.expander("🔧 고급 필터"):
            reward_filter = st.checkbox("💰 지원금 있는 공고만")
            partner_filter = st.checkbox("🤝 파트너 기업만")
            remote_filter = st.checkbox("🏠 원격근무 가능")
            
            # 지원금 범위
            if 'join_reward' in df.columns:
                min_r, max_r = int(df['join_reward'].min()), int(df['join_reward'].max())
                join_reward_range = st.slider("💵 지원금 범위 (원)", min_r, max_r, (min_r, max_r))
            else:
                join_reward_range = (0, 1000000)
            
            # 직무 레벨
            if 'job_level' in df.columns:
                available_levels = df['job_level'].dropna().unique()
                selected_levels = st.multiselect("📈 직무 레벨", 
                                                available_levels, 
                                                default=list(available_levels))
            else:
                selected_levels = []
            
            # 기업 규모 필터
            if 'company_size' in df.columns:
                available_sizes = df['company_size'].dropna().unique()
                selected_sizes = st.multiselect("🏢 기업 규모", 
                                               available_sizes,
                                               default=list(available_sizes))
            else:
                selected_sizes = []
        
        # 키워드 검색
        keyword_input = st.text_input("🔍 키워드 검색", 
                                     placeholder="회사명, 공고명 검색")
        
        # 즉시 매칭 버튼
        if st.button("🎯 즉시 매칭", type="primary"):
            st.success("✅ 매칭 조건이 적용되었습니다!")
        
        # 데이터 새로고침
        if st.button("🔄 데이터 새로고침"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        
        # 퀵 통계
        st.subheader("📊 퀵 통계")
        total_jobs = len(df)
        active_jobs = len(df[df['status_code'] == 'RECRUITING']) if 'status_code' in df.columns else total_jobs
        
        st.metric("총 공고", f"{total_jobs:,}개")
        st.metric("활성 공고", f"{active_jobs:,}개")
        
        if 'join_reward' in df.columns:
            avg_reward = df['join_reward'].mean()
            st.metric("평균 지원금", f"{avg_reward:,.0f}원")
        
        # 사용자 프로필 반환
        user_profile = {
            'name': user_name,
            'email': user_email,
            'skills': [s.strip() for s in user_skills_input.split(',') if s.strip()],
            'experience_years': experience_years,
            'current_position': current_position,
            'recent_courses': recent_courses,
            'project_count': project_count,
            'github_contributions': github_contributions,
            'certification_count': certification_count,
            'blog_posts': blog_posts,
            'mentoring_experience': mentoring_experience,
            'preferred_company_size': preferred_company_size,
            'remote_preference': remote_preference,
            'min_salary': min_salary
        }
        
        filter_conditions = {
            'user_category': user_category,
            'selected_region': selected_region,
            'reward_filter': reward_filter,
            'partner_filter': partner_filter,
            'remote_filter': remote_filter,
            'join_reward_range': join_reward_range,
            'selected_levels': selected_levels,
            'selected_sizes': selected_sizes,
            'keyword_input': keyword_input
        }
        
        return user_profile, filter_conditions

def apply_filters(df: pd.DataFrame, filter_conditions: Dict, user_profile: Dict = None) -> pd.DataFrame:
    """필터 조건 적용"""
    filtered_df = df.copy()
    
    # 기본 필터 적용
    if filter_conditions['user_category'] != '전체':
        filtered_df = filtered_df[filtered_df['job_category'] == filter_conditions['user_category']]
    
    if filter_conditions['selected_region'] != '전체':
        filtered_df = filtered_df[filtered_df['address_region'] == filter_conditions['selected_region']]
    
    # 고급 필터 적용
    if filter_conditions['reward_filter'] and 'join_reward' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['join_reward'] > 0]
    
    if filter_conditions['partner_filter'] and 'is_partner' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['is_partner'] == 1]
    
    if filter_conditions['remote_filter'] and 'remote_possible' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['remote_possible'] == 1]
    
    # 지원금 범위
    if 'join_reward' in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df['join_reward'].between(
                filter_conditions['join_reward_range'][0],
                filter_conditions['join_reward_range'][1]
            )
        ]
    
    # 직무 레벨
    if filter_conditions['selected_levels'] and 'job_level' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['job_level'].isin(filter_conditions['selected_levels'])]
    
    # 기업 규모
    if filter_conditions['selected_sizes'] and 'company_size' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['company_size'].isin(filter_conditions['selected_sizes'])]
    
    # 키워드 검색
    if filter_conditions['keyword_input']:
        keyword = filter_conditions['keyword_input'].lower()
        mask = (
            filtered_df['title'].str.lower().str.contains(keyword, na=False) |
            filtered_df['company_name'].str.lower().str.contains(keyword, na=False)
        )
        if 'job_skill_keywords' in filtered_df.columns:
            mask |= filtered_df['job_skill_keywords'].str.lower().str.contains(keyword, na=False)
        filtered_df = filtered_df[mask]
    
    # 스킬 기반 필터링 (사용자가 스킬을 입력한 경우)
    if user_profile and user_profile['skills'] and 'job_skill_keywords' in filtered_df.columns:
        user_skills_pattern = '|'.join([re.escape(skill.strip()) for skill in user_profile['skills']])
        skill_match_mask = filtered_df['job_skill_keywords'].str.contains(
            user_skills_pattern, case=False, na=False
        )
        # 스킬 매칭된 공고를 상위에 배치 (완전 필터링하지 않음)
        matched_jobs = filtered_df[skill_match_mask]
        other_jobs = filtered_df[~skill_match_mask]
        filtered_df = pd.concat([matched_jobs, other_jobs], ignore_index=True)
    
    return filtered_df

# ==============================================================================
# 7. 메인 애플리케이션
# ==============================================================================

def main():
    """메인 애플리케이션 실행"""
    # 데이터 로딩
    data_loader = EnhancedSmartDataLoader()
    matching_engine = AdvancedMatchingEngine()
    
    # 데이터 로드
    with st.spinner("🔄 데이터를 로딩 중입니다..."):
        df = data_loader.load_from_database()
    
    if df.empty:
        st.error("😕 데이터를 로드할 수 없습니다. 관리자에게 문의해주세요.")
        return
    
    # 사이드바 렌더링
    user_profile, filter_conditions = render_enhanced_sidebar(df)
    
    # 필터 적용
    filtered_df = apply_filters(df, filter_conditions, user_profile)
    
    # 필터 요약 표시
    active_filters = []
    if user_profile['skills']:
        active_filters.append(f"스킬: {', '.join(user_profile['skills'][:3])}{'...' if len(user_profile['skills']) > 3 else ''}")
    if filter_conditions['user_category'] != '전체':
        active_filters.append(f"직무: {filter_conditions['user_category']}")
    if filter_conditions['selected_region'] != '전체':
        active_filters.append(f"지역: {filter_conditions['selected_region']}")
    if filter_conditions['keyword_input']:
        active_filters.append(f"키워드: {filter_conditions['keyword_input']}")
    
    filter_summary = " | ".join(active_filters) if active_filters else "전체 조건"
    
    st.markdown(f"""
    <div class="alert-success">
        <strong>🔍 적용된 필터:</strong> {filter_summary}<br>
        <strong>📊 검색 결과:</strong> {len(filtered_df):,}개의 채용 공고
    </div>
    """, unsafe_allow_html=True)
    
    # 탭 구성
    tabs = st.tabs([
        "⭐ 메인 대시보드",
        "🎯 AI 스마트 매칭", 
        "📈 개인 성장 경로",
        "📊 시장 트렌드 분석",
        "🏢 기업 인사이트",
        "🔮 예측 분석",
        "📋 상세 데이터"
    ])
    
    # 각 탭 렌더링
    with tabs[0]:
        render_enhanced_main_summary(df)
    
    with tabs[1]:
        render_enhanced_smart_matching(filtered_df, user_profile, matching_engine, df)
    
    with tabs[2]:
        render_advanced_growth_path(df, user_profile, filter_conditions['user_category'], matching_engine)
    
    with tabs[3]:
        create_market_trend_dashboard(df)
        create_advanced_skill_visualization(filtered_df)
    
    with tabs[4]:
        render_enhanced_company_insights(filtered_df)
    
    with tabs[5]:
        render_enhanced_prediction_analysis(df)
    
    with tabs[6]:
        st.header("📋 상세 데이터 테이블")
        
        if not filtered_df.empty:
            # 컬럼 선택
            available_columns = filtered_df.columns.tolist()
            default_columns = [col for col in ['title', 'company_name', 'job_category', 'address_region', 'join_reward'] 
                             if col in available_columns]
            
            selected_columns = st.multiselect(
                "표시할 컬럼을 선택하세요:",
                available_columns,
                default=default_columns
            )
            
            if selected_columns:
                display_df = filtered_df[selected_columns]
                
                # 페이지네이션
                page_size = st.selectbox("페이지당 행 수", [10, 25, 50, 100], index=1)
                total_pages = len(display_df) // page_size + (1 if len(display_df) % page_size > 0 else 0)
                
                if total_pages > 1:
                    page_number = st.selectbox("페이지", range(1, total_pages + 1))
                    start_idx = (page_number - 1) * page_size
                    end_idx = start_idx + page_size
                    display_df = display_df.iloc[start_idx:end_idx]
                
                st.dataframe(display_df, use_container_width=True, height=400)
                
                # 다운로드 버튼
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        "📄 CSV 다운로드",
                        csv,
                        "rallit_jobs_filtered.csv",
                        "text/csv"
                    )
                
                with col2:
                    json_data = filtered_df.to_json(orient='records', force_ascii=False, indent=2)
                    st.download_button(
                        "📄 JSON 다운로드",
                        json_data,
                        "rallit_jobs_filtered.json",
                        "application/json"
                    )
                
                with col3:
                    # 요약 리포트 생성
                    summary_report = f"""
# 갓생라이프/커리어하이어 분석 리포트

## 검색 조건
- 필터 조건: {filter_summary}
- 검색 결과: {len(filtered_df)}개 공고

## 주요 통계
- 참여 기업 수: {filtered_df['company_name'].nunique()}개
- 평균 지원금: {filtered_df['join_reward'].mean():,.0f}원 (지원금 제공 공고 기준)
- 주요 직무: {', '.join(filtered_df['job_category'].value_counts().head(3).index)}

## 지역별 분포
{filtered_df['address_region'].value_counts().head(5).to_string()}

생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
                    st.download_button(
                        "📊 요약 리포트",
                        summary_report,
                        "rallit_analysis_report.md",
                        "text/markdown"
                    )
            else:
                st.warning("표시할 컬럼을 선택해주세요.")
        else:
            st.warning("표시할 데이터가 없습니다. 필터 조건을 조정해주세요.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"애플리케이션 실행 중 오류가 발생했습니다: {e}")
        logger.error(f"Application error: {e}", exc_info=True)
        
        # 디버그 정보 (개발 환경에서만)
        if st.secrets.get("DEBUG", False):
            st.exception(e)
