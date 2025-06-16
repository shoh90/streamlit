"""
Rallit Jobs Dashboard - 메인 Streamlit 애플리케이션
GitHub Pages/Streamlit Cloud 배포용
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime
import logging
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="Rallit 채용 정보 대시보드",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-username/rallit-jobs-dashboard',
        'Report a bug': "https://github.com/your-username/rallit-jobs-dashboard/issues",
        'About': "# Rallit Jobs Dashboard\n채용 정보를 시각화하는 대시보드입니다."
    }
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
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    .stSelectbox > div > div {
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 로더 클래스
class DataLoader:
    """데이터 로딩 및 관리 클래스"""
    
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
        """SQLite 데이터베이스에서 데이터 로드"""
        try:
            if not Path(_self.db_path).exists():
                logger.warning(f"Database file {_self.db_path} not found. Creating from CSV files...")
                _self._create_database_from_csv()
            
            conn = sqlite3.connect(_self.db_path)
            query = """
            SELECT 
                id, job_category, address_region, company_id, company_name,
                company_representative_image, ended_at, is_bookmarked, is_partner,
                job_level, job_levels, job_skill_keywords, join_reward,
                started_at, status_code, status_name, title, url, created_at
            FROM jobs
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            logger.info(f"Loaded {len(df)} records from database")
            return df
            
        except Exception as e:
            logger.error(f"Database loading error: {str(e)}")
            return _self._load_from_csv_fallback()
    
    def _load_from_csv_fallback(self):
        """CSV 파일에서 직접 데이터 로드 (대체 방법)"""
        try:
            all_dfs = []
            
            for category, filename in self.csv_files.items():
                file_path = self.data_dir / filename
                
                if file_path.exists():
                    df = pd.read_csv(file_path)
                    df['job_category'] = category
                    
                    # 컬럼명 정규화
                    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
                    
                    # Boolean 값 변환
                    if 'isbookmarked' in df.columns:
                        df['isbookmarked'] = df['isbookmarked'].map({'True': 1, 'False': 0, True: 1, False: 0})
                    if 'ispartner' in df.columns:
                        df['ispartner'] = df['ispartner'].map({'True': 1, 'False': 0, True: 1, False: 0})
                    
                    # 컬럼명 매핑
                    column_mapping = {
                        'addressregion': 'address_region',
                        'companyid': 'company_id',
                        'companyname': 'company_name',
                        'companyrepresentativeimage': 'company_representative_image',
                        'endedat': 'ended_at',
                        'isbookmarked': 'is_bookmarked',
                        'ispartner': 'is_partner',
                        'joblevel': 'job_level',
                        'joblevels': 'job_levels',
                        'jobskillkeywords': 'job_skill_keywords',
                        'joinreward': 'join_reward',
                        'partnerlogo': 'partner_logo',
                        'startedat': 'started_at',
                    }
                    
                    df = df.rename(columns=column_mapping)
                    all_dfs.append(df)
                    
                    logger.info(f"Loaded {len(df)} records from {filename}")
                else:
                    logger.warning(f"CSV file {filename} not found in {file_path}")
            
            if all_dfs:
                combined_df = pd.concat(all_dfs, ignore_index=True)
                combined_df['created_at'] = pd.Timestamp.now()
                logger.info(f"Combined {len(combined_df)} records from CSV files")
                return combined_df
            else:
                logger.error("No CSV files found, loading sample data")
                return self._load_sample_data()
                
        except Exception as e:
            logger.error(f"CSV loading error: {str(e)}")
            return self._load_sample_data()
    
    def _create_database_from_csv(self):
        """CSV 파일로부터 SQLite 데이터베이스 생성"""
        try:
            df = self._load_from_csv_fallback()
            
            if not df.empty:
                conn = sqlite3.connect(self.db_path)
                
                # 테이블 생성
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY,
                    job_category TEXT NOT NULL,
                    address_region TEXT,
                    company_id INTEGER,
                    company_name TEXT,
                    company_representative_image TEXT,
                    ended_at TEXT,
                    is_bookmarked BOOLEAN,
                    is_partner BOOLEAN,
                    job_level TEXT,
                    job_levels TEXT,
                    job_skill_keywords TEXT,
                    join_reward INTEGER,
                    partner_logo TEXT,
                    started_at TEXT,
                    status_code TEXT,
                    status_name TEXT,
                    title TEXT,
                    url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                
                conn.execute(create_table_sql)
                
                # 데이터 삽입
                df.to_sql('jobs', conn, if_exists='replace', index=False)
                
                # 인덱스 생성
                indexes = [
                    "CREATE INDEX IF NOT EXISTS idx_job_category ON jobs(job_category);",
                    "CREATE INDEX IF NOT EXISTS idx_company_id ON jobs(company_id);",
                    "CREATE INDEX IF NOT EXISTS idx_status_code ON jobs(status_code);",
                    "CREATE INDEX IF NOT EXISTS idx_address_region ON jobs(address_region);",
                    "CREATE INDEX IF NOT EXISTS idx_job_level ON jobs(job_level);"
                ]
                
                for index_sql in indexes:
                    conn.execute(index_sql)
                
                conn.commit()
                conn.close()
                
                logger.info(f"Database created successfully with {len(df)} records")
                
        except Exception as e:
            logger.error(f"Database creation error: {str(e)}")
    
    def _load_sample_data(self):
        """샘플 데이터 생성 (CSV 파일이 없을 때 사용)"""
        import random
        
        categories = ['DEVELOPER', 'DESIGN', 'MARKETING', 'MANAGEMENT']
        regions = ['PANGYO', 'GANGNAM', 'HONGDAE', 'JONGNO', 'YEOUIDO', 'BUNDANG', 'SEOCHO']
        companies = ['테크컴퍼니A', '스타트업B', '대기업C', '중견기업D', '벤처E', '글로벌기업F', 'AI스타트업G']
        skills = {
            'DEVELOPER': ['Python', 'JavaScript', 'React', 'Node.js', 'Java', 'Spring', 'Django', 'Vue.js'],
            'DESIGN': ['Figma', 'Sketch', 'Adobe XD', 'Photoshop', 'Illustrator', 'Principle', 'Zeplin'],
            'MARKETING': ['Google Analytics', 'Facebook Ads', 'SEO', 'Content Marketing', 'Social Media'],
            'MANAGEMENT': ['Project Management', 'Team Leadership', 'Strategic Planning', 'Business Analysis']
        }
        
        sample_data = []
        
        for i in range(150):
            category = random.choice(categories)
            region = random.choice(regions)
            company = random.choice(companies)
            
            sample_data.append({
                'id': i + 1,
                'job_category': category,
                'address_region': region,
                'company_id': random.randint(1, 50),
                'company_name': company,
                'title': f'{category.title()} 채용공고 - {company}',
                'status_code': random.choice(['HIRING', 'CLOSED']),
                'status_name': random.choice(['모집 중', '마감']),
                'is_partner': random.choice([0, 1]),
                'is_bookmarked': random.choice([0, 1]),
                'join_reward': random.choice([0, 50000, 100000, 200000, 300000, 500000]),
                'job_skill_keywords': ', '.join(random.sample(skills[category], k=random.randint(2, 4))),
                'job_level': random.choice(['IRRELEVANT', 'JUNIOR', 'SENIOR', 'LEAD']),
                'job_levels': random.choice(['INTERN', 'JUNIOR', 'SENIOR', 'MANAGER']),
                'created_at': datetime.now(),
                'company_representative_image': f'https://via.placeholder.com/100x100?text={company[:2]}',
                'url': f'https://www.rallit.com/positions/{i+1}',
                'started_at': '2024-01-01',
                'ended_at': '2024-12-31'
            })
        
        st.warning("📁 CSV 파일을 찾을 수 없어 샘플 데이터를 표시합니다. 실제 데이터를 보려면 data/ 폴더에 CSV 파일들을 업로드해주세요.")
        return pd.DataFrame(sample_data)

# 유틸리티 함수들
def format_currency(amount):
    """금액을 한국 원화 형식으로 포맷팅"""
    if pd.isna(amount) or amount == 0:
        return "0원"
    
    if amount >= 100000000:  # 1억 이상
        return f"{amount/100000000:.1f}억원"
    elif amount >= 10000:  # 1만 이상
        return f"{amount/10000:.0f}만원"
    else:
        return f"{amount:,.0f}원"

def calculate_metrics(df):
    """데이터프레임에서 주요 메트릭 계산"""
    if df.empty:
        return {
            'total_jobs': 0,
            'hiring_count': 0,
            'hiring_percentage': 0,
            'partner_count': 0,
            'partner_percentage': 0,
            'unique_companies': 0,
            'avg_reward': 0
        }
    
    total_jobs = len(df)
    hiring_count = len(df[df['status_code'] == 'HIRING']) if 'status_code' in df.columns else 0
    partner_count = len(df[df['is_partner'] == 1]) if 'is_partner' in df.columns else 0
    unique_companies = df['company_name'].nunique() if 'company_name' in df.columns else 0
    
    hiring_percentage = (hiring_count / total_jobs * 100) if total_jobs > 0 else 0
    partner_percentage = (partner_count / total_jobs * 100) if total_jobs > 0 else 0
    
    avg_reward = 0
    if 'join_reward' in df.columns:
        reward_df = df[df['join_reward'] > 0]
        avg_reward = reward_df['join_reward'].mean() if not reward_df.empty else 0
    
    return {
        'total_jobs': total_jobs,
        'hiring_count': hiring_count,
        'hiring_percentage': hiring_percentage,
        'partner_count': partner_count,
        'partner_percentage': partner_percentage,
        'unique_companies': unique_companies,
        'avg_reward': avg_reward
    }

def filter_dataframe(df, category='전체', region='전체', status='전체', partner='전체', reward_range=None):
    """다중 필터를 적용하여 데이터프레임 필터링"""
    filtered_df = df.copy()
    
    # 카테고리 필터
    if category != '전체' and 'job_category' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['job_category'] == category]
    
    # 지역 필터
    if region != '전체' and 'address_region' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['address_region'] == region]
    
    # 상태 필터
    if status != '전체' and 'status_code' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['status_code'] == status]
    
    # 파트너 필터
    if partner != '전체' and 'is_partner' in filtered_df.columns:
        if partner == '파트너 기업만':
            filtered_df = filtered_df[filtered_df['is_partner'] == 1]
        elif partner == '일반 기업만':
            filtered_df = filtered_df[filtered_df['is_partner'] == 0]
    
    # 지원금 범위 필터
    if reward_range and 'join_reward' in filtered_df.columns:
        min_reward, max_reward = reward_range
        filtered_df = filtered_df[
            (filtered_df['join_reward'] >= min_reward) & 
            (filtered_df['join_reward'] <= max_reward)
        ]
    
    return filtered_df

def extract_skills(df, top_n=20):
    """job_skill_keywords에서 기술 스택 추출 및 분석"""
    all_skills = []
    for skills_str in df['job_skill_keywords'].dropna():
        if isinstance(skills_str, str):
            skills = [skill.strip() for skill in skills_str.split(',')]
            skills = [skill for skill in skills if skill]  # 빈 문자열 제거
            all_skills.extend(skills)
    
    if not all_skills:
        return pd.Series(dtype=int)
    
    skill_counts = pd.Series(all_skills).value_counts()
    return skill_counts.head(top_n)

# 시각화 함수들
def create_category_pie_chart(df):
    """직무 카테고리별 파이 차트 생성"""
    category_counts = df['job_category'].value_counts()
    
    fig = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title="직무 카테고리별 채용 공고 분포",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>개수: %{value}<br>비율: %{percent}<extra></extra>'
    )
    
    fig.update_layout(height=400, showlegend=True)
    return fig

def create_region_bar_chart(df, top_n=10):
    """지역별 수평 막대 차트 생성"""
    region_counts = df['address_region'].value_counts().head(top_n)
    
    fig = px.bar(
        x=region_counts.values,
        y=region_counts.index,
        orientation='h',
        title=f"지역별 채용 공고 수 (상위 {top_n}개)",
        labels={'x': '채용 공고 수', 'y': '지역'},
        color=region_counts.values,
        color_continuous_scale='viridis',
        text=region_counts.values
    )
    
    fig.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>채용 공고 수: %{x}<extra></extra>'
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=400,
        showlegend=False
    )
    
    return fig

def create_companies_chart(df, top_n=10):
    """상위 채용 기업 차트 생성"""
    top_companies = df['company_name'].value_counts().head(top_n)
    
    fig = px.bar(
        x=top_companies.values,
        y=top_companies.index,
        orientation='h',
        title=f"채용 공고 수 기준 상위 {top_n}개 기업",
        labels={'x': '채용 공고 수', 'y': '회사명'},
        color=top_companies.values,
        color_continuous_scale='blues',
        text=top_companies.values
    )
    
    fig.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>채용 공고 수: %{x}<extra></extra>'
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=400,
        showlegend=False
    )
    
    return fig

def create_skills_chart(df, top_n=20):
    """기술 스택 차트 생성"""
    skill_counts = extract_skills(df, top_n)
    
    if skill_counts.empty:
        return None
    
    fig = px.bar(
        x=skill_counts.values,
        y=skill_counts.index,
        orientation='h',
        title=f"인기 기술 스택 TOP {top_n}",
        labels={'x': '언급 횟수', 'y': '기술'},
        color=skill_counts.values,
        color_continuous_scale='greens',
        text=skill_counts.values
    )
    
    fig.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>언급 횟수: %{x}<extra></extra>'
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        height=600,
        showlegend=False
    )
    
    return fig

def create_reward_histogram(df):
    """지원금 분포 히스토그램"""
    reward_df = df[df['join_reward'] > 0]
    
    if reward_df.empty:
        return None
    
    fig = px.histogram(
        reward_df,
        x='join_reward',
        nbins=20,
        title="지원금 분포",
        labels={'x': '지원금(원)', 'y': '채용 공고 수'},
        color_discrete_sequence=['#FF6B6B']
    )
    
    fig.update_traces(
        hovertemplate='지원금: %{x:,.0f}원<br>공고 수: %{y}<extra></extra>'
    )
    
    fig.update_layout(height=400)
    return fig

# 메인 애플리케이션
def main():
    """메인 애플리케이션 함수"""
    
    # 헤더
    st.markdown('<h1 class="main-header">💼 Rallit 채용 정보 대시보드</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 데이터 로딩
    data_loader = DataLoader()
    
    with st.spinner('데이터를 로딩중입니다...'):
        df = data_loader.load_from_database()
    
    if df.empty:
        st.error("😕 데이터를 로드할 수 없습니다.")
        st.stop()
    
    # 사이드바 필터
    st.sidebar.header("🔍 필터 옵션")
    st.sidebar.markdown("---")
    
    # 직무 카테고리 필터
    job_categories = ['전체'] + list(df['job_category'].unique())
    selected_category = st.sidebar.selectbox(
        "직무 카테고리",
        job_categories,
        help="특정 직무 카테고리를 선택하세요"
    )
    
    # 지역 필터
    regions = ['전체'] + sorted(list(df['address_region'].dropna().unique()))
    selected_region = st.sidebar.selectbox(
        "근무 지역",
        regions,
        help="근무하고 싶은 지역을 선택하세요"
    )
    
    # 상태 필터
    statuses = ['전체'] + list(df['status_code'].dropna().unique())
    selected_status = st.sidebar.selectbox(
        "채용 상태",
        statuses,
        help="채용 진행 상태를 선택하세요"
    )
    
    # 파트너 여부 필터
    partner_options = ['전체', '파트너 기업만', '일반 기업만']
    selected_partner = st.sidebar.selectbox(
        "파트너 여부",
        partner_options,
        help="파트너 기업 여부로 필터링"
    )
    
    # 지원금 필터
    reward_range = None
    if 'join_reward' in df.columns:
        reward_df = df[df['join_reward'] > 0]
        if not reward_df.empty:
            # 실제 데이터의 min/max 값
            raw_min_reward = int(reward_df['join_reward'].min())
            raw_max_reward = int(reward_df['join_reward'].max())
            
            # 지원금 범위에 따라 step 동적 조정
            reward_range_size = raw_max_reward - raw_min_reward
            if reward_range_size <= 100000:  # 10만원 이하
                step_size = 1000  # 1천원 단위
            elif reward_range_size <= 1000000:  # 100만원 이하
                step_size = 5000  # 5천원 단위
            else:
                step_size = 10000  # 1만원 단위
            
            # 슬라이더 범위는 항상 0부터 시작하여 깔끔한 단위로 설정
            slider_min = 0
            slider_max = ((raw_max_reward + step_size - 1) // step_size) * step_size
            
            # 기본값을 강제로 깔끔한 단위로 설정 (실제 데이터와 무관하게)
            if raw_min_reward <= step_size:
                clean_default_min = 0  # 실제 최소값이 step보다 작으면 0으로
            else:
                clean_default_min = (raw_min_reward // step_size) * step_size
            
            clean_default_max = ((raw_max_reward + step_size - 1) // step_size) * step_size
            
            # 슬라이더와 숫자 입력 선택 옵션
            filter_type = st.sidebar.radio(
                "지원금 필터 방식",
                ["슬라이더", "직접 입력"],
                horizontal=True,
                help="필터링 방식을 선택하세요"
            )
            
            if filter_type == "슬라이더":
                reward_range = st.sidebar.slider(
                    "지원금 범위 (원)",
                    min_value=slider_min,
                    max_value=slider_max,
                    value=(clean_default_min, clean_default_max),
                    step=step_size,
                    format="%d",
                    help=f"원하는 지원금 범위를 설정하세요 ({step_size:,}원 단위)"
                )
                
                # 실제 데이터 범위 정보 표시
                st.sidebar.caption(f"💡 실제 데이터 범위: {raw_min_reward:,}원 ~ {raw_max_reward:,}원")
                
            else:
                col1, col2 = st.sidebar.columns(2)
                with col1:
                    min_input = st.number_input(
                        "최소 지원금",
                        min_value=0,
                        max_value=slider_max,
                        value=clean_default_min,  # 강제로 깔끔한 값
                        step=step_size,
                        format="%d"
                    )
                with col2:
                    max_input = st.number_input(
                        "최대 지원금",
                        min_value=0,
                        max_value=slider_max * 2,
                        value=clean_default_max,  # 강제로 깔끔한 값
                        step=step_size,
                        format="%d"
                    )
                reward_range = (min_input, max_input)
                
                # 실제 데이터 범위 정보 표시
                st.sidebar.caption(f"💡 실제 데이터 범위: {raw_min_reward:,}원 ~ {raw_max_reward:,}원")
    
    st.sidebar.markdown("---")
    
    # 데이터 새로고침 버튼
    if st.sidebar.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.rerun()
    
    # 데이터 필터링
    filtered_df = filter_dataframe(
        df, selected_category, selected_region, selected_status, 
        selected_partner, reward_range
    )
    
    # 메인 메트릭
    metrics = calculate_metrics(filtered_df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "총 채용 공고",
            f"{metrics['total_jobs']:,}",
            help="필터링된 전체 채용 공고 수"
        )
    
    with col2:
        st.metric(
            "모집중",
            f"{metrics['hiring_count']:,}",
            delta=f"{metrics['hiring_percentage']:.1f}%",
            help="현재 모집중인 채용 공고 수"
        )
    
    with col3:
        st.metric(
            "파트너 기업",
            f"{metrics['partner_count']:,}",
            delta=f"{metrics['partner_percentage']:.1f}%",
            help="파트너 기업의 채용 공고 수"
        )
    
    with col4:
        st.metric(
            "참여 기업 수",
            f"{metrics['unique_companies']:,}",
            help="채용 공고를 올린 고유 기업 수"
        )
    
    st.markdown("---")
    
    # 탭으로 섹션 구분
    tab1, tab2, tab3, tab4 = st.tabs(["📊 기본 분석", "🏢 기업 분석", "💻 기술 분석", "📋 상세 데이터"])
    
    with tab1:
        st.header("📊 기본 채용 정보 분석")
        
        if not filtered_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # 직무 카테고리 분포
                fig_pie = create_category_pie_chart(filtered_df)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                # 지역별 분포
                fig_region = create_region_bar_chart(filtered_df)
                st.plotly_chart(fig_region, use_container_width=True)
            
            # 추가 통계
            col1, col2 = st.columns(2)
            
            with col1:
                # 채용 상태별 분포
                status_counts = filtered_df['status_name'].value_counts()
                fig_status = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="채용 상태별 분포",
                    hole=0.6,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_status.update_layout(height=400)
                st.plotly_chart(fig_status, use_container_width=True)
            
            with col2:
                # 직급별 분포
                if 'job_level' in filtered_df.columns:
                    level_counts = filtered_df['job_level'].value_counts()
                    fig_level = px.bar(
                        x=level_counts.index,
                        y=level_counts.values,
                        title="직급별 채용 공고 분포",
                        labels={'x': '직급', 'y': '채용 공고 수'},
                        color=level_counts.values,
                        color_continuous_scale='plasma'
                    )
                    fig_level.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig_level, use_container_width=True)
        else:
            st.warning("선택된 필터 조건에 맞는 데이터가 없습니다.")
    
    with tab2:
        st.header("🏢 기업별 채용 분석")
        
        if not filtered_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # 상위 채용 기업
                fig_companies = create_companies_chart(filtered_df)
                st.plotly_chart(fig_companies, use_container_width=True)
            
            with col2:
                # 회사 규모별 분포
                company_job_counts = filtered_df['company_name'].value_counts()
                
                def categorize_company_size(job_count):
                    if job_count >= 10:
                        return "대기업"
                    elif job_count >= 5:
                        return "중견기업"
                    elif job_count >= 3:
                        return "중소기업"
                    else:
                        return "스타트업"
                
                company_sizes = company_job_counts.apply(categorize_company_size)
                size_counts = company_sizes.value_counts()
                
                fig_size = px.bar(
                    x=size_counts.index,
                    y=size_counts.values,
                    title="회사 규모별 분포",
                    labels={'x': '회사 규모', 'y': '회사 수'},
                    color=size_counts.values,
                    color_continuous_scale='oranges'
                )
                fig_size.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_size, use_container_width=True)
            
            # 카테고리별 지역 분포
            if len(filtered_df['job_category'].unique()) > 1:
                category_region = filtered_df.groupby(['job_category', 'address_region']).size().unstack(fill_value=0)
                
                fig_multi = px.bar(
                    category_region.T,
                    title="직무 카테고리별 지역 분포",
                    labels={'value': '채용 공고 수', 'index': '지역'},
                    height=500
                )
                
                fig_multi.update_layout(
                    xaxis_title="지역",
                    yaxis_title="채용 공고 수",
                    legend_title="직무 카테고리"
                )
                st.plotly_chart(fig_multi, use_container_width=True)
        else:
            st.warning("선택된 필터 조건에 맞는 데이터가 없습니다.")
    
    with tab3:
        st.header("💻 기술 스택 및 지원금 분석")
        
        # 기술 스택 분석 (개발자 직군 포함된 경우에만)
        if selected_category in ['전체', 'DEVELOPER'] and not filtered_df.empty:
            dev_df = filtered_df[filtered_df['job_category'] == 'DEVELOPER'] if selected_category == '전체' else filtered_df
            
            if not dev_df.empty:
                fig_skills = create_skills_chart(dev_df)
                if fig_skills:
                    st.plotly_chart(fig_skills, use_container_width=True)
                else:
                    st.info("기술 스택 정보가 없습니다.")
        
        # 지원금 분석
        if 'join_reward' in filtered_df.columns:
            reward_df = filtered_df[filtered_df['join_reward'] > 0]
            
            if not reward_df.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("💰 지원금 통계")
                    avg_reward = reward_df['join_reward'].mean()
                    max_reward = reward_df['join_reward'].max()
                    min_reward = reward_df['join_reward'].min()
                    median_reward = reward_df['join_reward'].median()
                    
                    st.metric("평균 지원금", format_currency(avg_reward))
                    st.metric("최대 지원금", format_currency(max_reward))
                    st.metric("최소 지원금", format_currency(min_reward))
                    st.metric("중간값 지원금", format_currency(median_reward))
                
                with col2:
                    fig_reward_hist = create_reward_histogram(filtered_df)
                    if fig_reward_hist:
                        st.plotly_chart(fig_reward_hist, use_container_width=True)
                
                # 카테고리별 지원금 박스플롯
                if len(reward_df['job_category'].unique()) > 1:
                    fig_reward_box = px.box(
                        reward_df,
                        x='job_category',
                        y='join_reward',
                        title="직무 카테고리별 지원금 분포",
                        labels={'x': '직무 카테고리', 'y': '지원금(원)'},
                        color='job_category',
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    
                    fig_reward_box.update_traces(
                        hovertemplate='<b>%{x}</b><br>지원금: %{y:,.0f}원<extra></extra>'
                    )
                    
                    fig_reward_box.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig_reward_box, use_container_width=True)
            else:
                st.info("지원금 정보가 있는 채용 공고가 없습니다.")
    
    with tab4:
        st.header("📋 채용 공고 상세 정보")
        
        if not filtered_df.empty:
            # 표시할 컬럼 선택
            available_columns = filtered_df.columns.tolist()
            default_columns = [
                'title', 'company_name', 'job_category', 
                'address_region', 'status_name', 'join_reward'
            ]
            
            # 기본 컬럼이 데이터에 있는지 확인
            default_columns = [col for col in default_columns if col in available_columns]
            
            display_columns = st.multiselect(
                "표시할 컬럼 선택",
                options=available_columns,
                default=default_columns,
                help="테이블에 표시할 컬럼을 선택하세요"
            )
            
            if display_columns:
                # 검색 기능
                search_term = st.text_input(
                    "🔍 검색어 입력 (제목, 회사명 기준)",
                    help="채용 공고 제목이나 회사명으로 검색하세요"
                )
                
                display_df = filtered_df.copy()
                
                if search_term:
                    mask = (
                        display_df['title'].str.contains(search_term, case=False, na=False) |
                        display_df['company_name'].str.contains(search_term, case=False, na=False)
                    )
                    display_df = display_df[mask]
                
                # 정렬 옵션
                col1, col2 = st.columns(2)
                with col1:
                    sort_by = st.selectbox("정렬 기준", display_columns)
                with col2:
                    sort_order = st.radio("정렬 순서", ["오름차순", "내림차순"], horizontal=True)
                
                ascending = True if sort_order == "오름차순" else False
                display_df_sorted = display_df.sort_values(sort_by, ascending=ascending)
                
                # 페이지네이션
                rows_per_page = st.selectbox("페이지당 행 수", [10, 25, 50, 100])
                total_rows = len(display_df_sorted)
                
                if total_rows > 0:
                    total_pages = (total_rows - 1) // rows_per_page + 1
                    
                    if total_pages > 1:
                        page = st.number_input(
                            "페이지", 
                            min_value=1, 
                            max_value=total_pages, 
                            value=1,
                            help=f"총 {total_pages}페이지 중 선택"
                        )
                        start_idx = (page - 1) * rows_per_page
                        end_idx = start_idx + rows_per_page
                        paginated_df = display_df_sorted[display_columns].iloc[start_idx:end_idx]
                        
                        st.info(f"📄 {start_idx + 1}-{min(end_idx, total_rows)} / {total_rows}개 표시")
                    else:
                        paginated_df = display_df_sorted[display_columns]
                    
                    # 데이터 테이블 표시
                    st.dataframe(
                        paginated_df,
                        use_container_width=True,
                        height=400
                    )
                    
                    # 데이터 다운로드 섹션
                    st.subheader("📥 데이터 다운로드")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        csv = display_df_sorted[display_columns].to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="📄 CSV 다운로드",
                            data=csv,
                            file_name=f"rallit_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv",
                            help="필터링된 데이터를 CSV 파일로 다운로드"
                        )
                    
                    with col2:
                        json_data = display_df_sorted[display_columns].to_json(
                            orient='records', 
                            force_ascii=False, 
                            indent=2
                        )
                        st.download_button(
                            label="📋 JSON 다운로드",
                            data=json_data,
                            file_name=f"rallit_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            help="필터링된 데이터를 JSON 파일로 다운로드"
                        )
                    
                    with col3:
                        # 요약 리포트 생성
                        summary_report = f"""
# 📊 Rallit 채용 정보 요약 리포트

## 기본 통계
- **총 채용 공고**: {metrics['total_jobs']:,}개
- **모집중인 공고**: {metrics['hiring_count']:,}개 ({metrics['hiring_percentage']:.1f}%)
- **파트너 기업 공고**: {metrics['partner_count']:,}개 ({metrics['partner_percentage']:.1f}%)
- **참여 기업 수**: {metrics['unique_companies']:,}개

## 카테고리별 분포
"""
                        category_counts = filtered_df['job_category'].value_counts()
                        for category, count in category_counts.items():
                            percentage = (count / len(filtered_df)) * 100
                            summary_report += f"- **{category}**: {count:,}개 ({percentage:.1f}%)\n"
                        
                        if metrics['avg_reward'] > 0:
                            summary_report += f"\n## 지원금 정보\n- **평균 지원금**: {format_currency(metrics['avg_reward'])}\n"
                        
                        summary_report += f"\n---\n생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        
                        st.download_button(
                            label="📈 요약 리포트",
                            data=summary_report,
                            file_name=f"rallit_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown",
                            help="필터링된 데이터의 요약 리포트를 다운로드"
                        )
                else:
                    st.warning("검색 조건에 맞는 데이터가 없습니다.")
            else:
                st.warning("표시할 컬럼을 선택해주세요.")
        else:
            st.warning("선택된 필터 조건에 맞는 데이터가 없습니다.")
    
    # 사이드바에 통계 정보 추가
    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 현재 필터 통계")
    st.sidebar.metric("필터된 공고 수", f"{len(filtered_df):,}")
    st.sidebar.metric("전체 공고 대비", f"{len(filtered_df)/len(df)*100:.1f}%")
    
    if not filtered_df.empty:
        # 가장 많은 채용 공고를 올린 회사
        top_company = filtered_df['company_name'].value_counts().index[0]
        top_company_count = filtered_df['company_name'].value_counts().iloc[0]
        st.sidebar.metric("최다 채용 기업", f"{top_company}")
        st.sidebar.caption(f"{top_company_count}개 공고")
        
        # 가장 많은 채용이 있는 지역
        if 'address_region' in filtered_df.columns:
            top_region = filtered_df['address_region'].value_counts().index[0]
            top_region_count = filtered_df['address_region'].value_counts().iloc[0]
            st.sidebar.metric("최다 채용 지역", f"{top_region}")
            st.sidebar.caption(f"{top_region_count}개 공고")
    
    # 푸터
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem; background: linear-gradient(90deg, #f0f0f0, #e0e0e0); border-radius: 10px;'>
            <p><strong>💼 Rallit Jobs Dashboard</strong></p>
            <p>📊 데이터 기반 채용 정보 분석 플랫폼</p>
            <p>🔗 <a href='https://github.com/your-username/rallit-jobs-dashboard' target='_blank' style='color: #FF6B6B;'>GitHub Repository</a> | 
            📧 <a href='mailto:contact@example.com' style='color: #FF6B6B;'>문의하기</a></p>
            <p style='font-size: 0.8rem; margin-top: 1rem;'>
                ⚡ Powered by Streamlit | 🎨 Made with ❤️ | 📅 {datetime.now().strftime('%Y-%m-%d')}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 개발자를 위한 디버그 정보 (선택사항)
    with st.expander("🔧 개발자 정보 (Debug)", expanded=False):
        st.subheader("데이터 정보")
        st.json({
            "total_records": len(df),
            "filtered_records": len(filtered_df),
            "columns": list(df.columns),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "missing_values": {col: int(df[col].isnull().sum()) for col in df.columns},
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
        })
        
        st.subheader("필터 적용 현황")
        st.json({
            "selected_category": selected_category,
            "selected_region": selected_region,
            "selected_status": selected_status,
            "selected_partner": selected_partner,
            "reward_range": reward_range
        })

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"애플리케이션 실행 중 오류가 발생했습니다: {str(e)}")
        logger.error(f"Application error: {str(e)}", exc_info=True)
        
        # 오류 발생 시 대체 동작
        st.subheader("🛠️ 문제 해결 방법")
        st.info("""
        1. **데이터 파일 확인**: data/ 폴더에 CSV 파일들이 있는지 확인하세요
        2. **권한 확인**: 데이터베이스 파일 생성 권한이 있는지 확인하세요
        3. **패키지 확인**: requirements.txt의 모든 패키지가 설치되었는지 확인하세요
        4. **브라우저 새로고침**: 페이지를 새로고침 해보세요
        """)
        
        if st.button("🔄 애플리케이션 재시작"):
            st.cache_data.clear()
            st.rerun()
