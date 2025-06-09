"""
유틸리티 함수 모듈
공통으로 사용되는 헬퍼 함수들
"""

import pandas as pd
import streamlit as st
from typing import Optional, Tuple, Dict, Any

def format_currency(amount: float) -> str:
    """금액을 한국 원화 형식으로 포맷팅"""
    if pd.isna(amount) or amount == 0:
        return "0원"
    
    if amount >= 100000000:  # 1억 이상
        return f"{amount/100000000:.1f}억원"
    elif amount >= 10000:  # 1만 이상
        return f"{amount/10000:.0f}만원"
    else:
        return f"{amount:,.0f}원"

def calculate_metrics(df: pd.DataFrame) -> Dict[str, Any]:
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

def filter_dataframe(
    df: pd.DataFrame,
    category: str = '전체',
    region: str = '전체',
    status: str = '전체',
    partner: str = '전체',
    reward_range: Optional[Tuple[int, int]] = None
) -> pd.DataFrame:
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

def get_top_skills(df: pd.DataFrame, top_n: int = 20) -> pd.Series:
    """기술 스택 키워드에서 상위 N개 기술 추출"""
    all_skills = []
    
    for skills_str in df['job_skill_keywords'].dropna():
        if isinstance(skills_str, str):
            # 쉼표로 분리하고 공백 제거
            skills = [skill.strip() for skill in skills_str.split(',')]
            # 빈 문자열 제거
            skills = [skill for skill in skills if skill]
            all_skills.extend(skills)
    
    if not all_skills:
        return pd.Series(dtype=int)
    
    skill_counts = pd.Series(all_skills).value_counts()
    return skill_counts.head(top_n)

def analyze_keyword_trends(df: pd.DataFrame, category: str = None) -> Dict[str, int]:
    """키워드 트렌드 분석"""
    if category:
        df = df[df['job_category'] == category]
    
    # 제목에서 자주 나오는 키워드 분석
    all_titles = ' '.join(df['title'].dropna().astype(str))
    
    # 간단한 키워드 추출 (실제로는 더 정교한 NLP 처리 필요)
    common_keywords = [
        '시니어', '주니어', '신입', '경력', '개발자', '디자이너', 
        '마케팅', '매니저', '팀장', '리드', 'Frontend', 'Backend',
        'Full-Stack', 'UI/UX', '데이터', '분석', 'AI', '머신러닝'
    ]
    
    keyword_counts = {}
    for keyword in common_keywords:
        count = all_titles.lower().count(keyword.lower())
        if count > 0:
            keyword_counts[keyword] = count
    
    return keyword_counts

def validate_filters(df: pd.DataFrame, **filters) -> Dict[str, bool]:
    """필터 유효성 검사"""
    validation_result = {}
    
    for filter_name, filter_value in filters.items():
        if filter_value == '전체':
            validation_result[filter_name] = True
            continue
        
        if filter_name == 'category' and 'job_category' in df.columns:
            validation_result[filter_name] = filter_value in df['job_category'].unique()
        elif filter_name == 'region' and 'address_region' in df.columns:
            validation_result[filter_name] = filter_value in df['address_region'].unique()
        elif filter_name == 'status' and 'status_code' in df.columns:
            validation_result[filter_name] = filter_value in df['status_code'].unique()
        else:
            validation_result[filter_name] = True
    
    return validation_result

def create_summary_report(df: pd.DataFrame) -> str:
    """데이터 요약 리포트 생성"""
    if df.empty:
        return "데이터가 없습니다."
    
    metrics = calculate_metrics(df)
    
    report = f"""
    ## 📊 데이터 요약 리포트
    
    ### 기본 통계
    - **총 채용 공고**: {metrics['total_jobs']:,}개
    - **모집중인 공고**: {metrics['hiring_count']:,}개 ({metrics['hiring_percentage']:.1f}%)
    - **파트너 기업 공고**: {metrics['partner_count']:,}개 ({metrics['partner_percentage']:.1f}%)
    - **참여 기업 수**: {metrics['unique_companies']:,}개
    
    ### 카테고리별 분포
    """
    
    if 'job_category' in df.columns:
        category_counts = df['job_category'].value_counts()
        for category, count in category_counts.items():
            percentage = (count / len(df)) * 100
            report += f"- **{category}**: {count:,}개 ({percentage:.1f}%)\n"
    
    if 'join_reward' in df.columns:
        reward_df = df[df['join_reward'] > 0]
        if not reward_df.empty:
            avg_reward = reward_df['join_reward'].mean()
            max_reward = reward_df['join_reward'].max()
            report += f"""
    ### 지원금 정보
    - **평균 지원금**: {format_currency(avg_reward)}
    - **최대 지원금**: {format_currency(max_reward)}
    - **지원금 제공 공고**: {len(reward_df):,}개 ({len(reward_df)/len(df)*100:.1f}%)
    """
    
    return report

def export_filtered_data(df: pd.DataFrame, format: str = 'csv') -> bytes:
    """필터링된 데이터를 지정된 형식으로 내보내기"""
    if format.lower() == 'csv':
        return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    elif format.lower() == 'json':
        return df.to_json(orient='records', force_ascii=False, indent=2).encode('utf-8')
    elif format.lower() == 'excel':
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Jobs')
        return output.getvalue()
    else:
        raise ValueError(f"Unsupported format: {format}")

def check_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """데이터 품질 검사"""
    quality_report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': {},
        'duplicate_rows': 0,
        'data_types': {},
        'quality_score': 0
    }
    
    if df.empty:
        return quality_report
    
    # 결측값 분석
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        missing_percentage = (missing_count / len(df)) * 100
        quality_report['missing_values'][col] = {
            'count': missing_count,
            'percentage': missing_percentage
        }
    
    # 중복 행 검사
    quality_report['duplicate_rows'] = df.duplicated().sum()
    
    # 데이터 타입 정보
    quality_report['data_types'] = df.dtypes.to_dict()
    
    # 품질 점수 계산 (0-100)
    missing_penalty = sum([info['percentage'] for info in quality_report['missing_values'].values()]) / len(df.columns)
    duplicate_penalty = (quality_report['duplicate_rows'] / len(df)) * 100
    
    quality_score = max(0, 100 - missing_penalty - duplicate_penalty)
    quality_report['quality_score'] = round(quality_score, 2)
    
    return quality_report

@st.cache_data
def load_sample_data() -> pd.DataFrame:
    """샘플 데이터 생성 (CSV 파일이 없을 때 사용)"""
    import random
    from datetime import datetime, timedelta
    
    categories = ['DEVELOPER', 'DESIGN', 'MARKETING', 'MANAGEMENT']
    regions = ['PANGYO', 'GANGNAM', 'HONGDAE', 'JONGNO', 'YEOUIDO']
    companies = ['테크컴퍼니A', '스타트업B', '대기업C', '중견기업D', '벤처E']
    
    sample_data = []
    
    for i in range(100):
        sample_data.append({
            'id': i + 1,
            'job_category': random.choice(categories),
            'address_region': random.choice(regions),
            'company_id': random.randint(1, 50),
            'company_name': random.choice(companies),
            'title': f'샘플 채용공고 {i+1}',
            'status_code': random.choice(['HIRING', 'CLOSED']),
            'status_name': random.choice(['모집 중', '마감']),
            'is_partner': random.choice([0, 1]),
            'is_bookmarked': random.choice([0, 1]),
            'join_reward': random.choice([0, 50000, 100000, 200000]),
            'job_skill_keywords': 'Python, JavaScript, React, Django',
            'created_at': datetime.now()
        })
    
    return pd.DataFrame(sample_data)
