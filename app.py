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

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.data_loader import data_loader
    from src.visualizations import visualizer
    from src.utils import format_currency, calculate_metrics, filter_dataframe
except ImportError as e:
    st.error(f"모듈 import 오류: {e}")
    st.stop()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    .stSelectbox > div > div {
        background-color: #f0f2f6;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """메인 애플리케이션 함수"""
    
    # 헤더
    st.markdown('<h1 class="main-header">💼 Rallit 채용 정보 대시보드</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 데이터 유효성 검사
    data_issues = data_loader.validate_data(df)
    if data_issues:
        with st.expander("⚠️ 데이터 품질 이슈", expanded=False):
            for issue in data_issues:
                st.warning(issue)
    
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
    if 'join_reward' in df.columns:
        reward_df = df[df['join_reward'] > 0]
        if not reward_df.empty:
            min_reward = int(reward_df['join_reward'].min())
            max_reward = int(reward_df['join_reward'].max())
            reward_range = st.sidebar.slider(
                "지원금 범위 (원)",
                min_value=min_reward,
                max_value=max_reward,
                value=(min_reward, max_reward),
                step=10000,
                format="%d",
                help="원하는 지원금 범위를 설정하세요"
            )
        else:
            reward_range = None
    
    st.sidebar.markdown("---")
    
    # 데이터 새로고침 버튼
    if st.sidebar.button("🔄 데이터 새로고침"):
        st.cache_data.clear()
        st.experimental_rerun()
    
    # 데이터 필터링
    filtered_df = filter_dataframe(
        df, selected_category, selected_region, selected_status, 
        selected_partner, reward_range if 'reward_range' in locals() else None
    )
    
    # 메인 메트릭
    metrics = calculate_metrics(filtered_df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "총 채용 공고",
            metrics['total_jobs'],
            delta=None,
            help="필터링된 전체 채용 공고 수"
        )
    
    with col2:
        st.metric(
            "모집중",
            metrics['hiring_count'],
            delta=f"{metrics['hiring_percentage']:.1f}%",
            help="현재 모집중인 채용 공고 수"
        )
    
    with col3:
        st.metric(
            "파트너 기업",
            metrics['partner_count'],
            delta=f"{metrics['partner_percentage']:.1f}%",
            help="파트너 기업의 채용 공고 수"
        )
    
    with col4:
        st.metric(
            "참여 기업 수",
            metrics['unique_companies'],
            delta=None,
            help="채용 공고를 올린 고유 기업 수"
        )
    
    st.markdown("---")
    
    # 탭으로 섹션 구분
    tab1, tab2, tab3, tab4 = st.tabs(["📊 기본 분석", "🏢 기업 분석", "💻 기술 분석", "📋 상세 데이터"])
    
    with tab1:
        st.header("📊 기본 채용 정보 분석")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 직무 카테고리 분포
            if not filtered_df.empty:
                fig_pie = visualizer.create_category_pie_chart(filtered_df)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.warning("표시할 데이터가 없습니다.")
        
        with col2:
            # 지역별 분포
            if not filtered_df.empty:
                fig_region = visualizer.create_region_bar_chart(filtered_df)
                st.plotly_chart(fig_region, use_container_width=True)
        
        # 채용 상태 및 직급 분포
        col1, col2 = st.columns(2)
        
        with col1:
            if not filtered_df.empty:
                fig_status = visualizer.create_status_donut_chart(filtered_df)
                st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            if not filtered_df.empty:
                fig_level = visualizer.create_level_distribution(filtered_df)
                st.plotly_chart(fig_level, use_container_width=True)
    
    with tab2:
        st.header("🏢 기업별 채용 분석")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 상위 채용 기업
            if not filtered_df.empty:
                fig_companies = visualizer.create_companies_chart(filtered_df)
                st.plotly_chart(fig_companies, use_container_width=True)
        
        with col2:
            # 회사 규모별 분포
            if not filtered_df.empty:
                fig_size = visualizer.create_company_size_chart(filtered_df)
                st.plotly_chart(fig_size, use_container_width=True)
        
        # 카테고리별 다중 비교
        if not filtered_df.empty:
            fig_multi = visualizer.create_multi_category_comparison(filtered_df)
            st.plotly_chart(fig_multi, use_container_width=True)
    
    with tab3:
        st.header("💻 기술 스택 및 지원금 분석")
        
        # 기술 스택 분석 (개발자 직군 포함된 경우에만)
        if selected_category in ['전체', 'DEVELOPER'] and not filtered_df.empty:
            dev_df = filtered_df[filtered_df['job_category'] == 'DEVELOPER'] if selected_category == '전체' else filtered_df
            
            if not dev_df.empty:
                fig_skills = visualizer.create_skills_chart(dev_df)
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
                    fig_reward_hist = visualizer.create_reward_histogram(filtered_df)
                    if fig_reward_hist:
                        st.plotly_chart(fig_reward_hist, use_container_width=True)
                
                # 카테고리별 지원금 박스플롯
                fig_reward_box = visualizer.create_reward_boxplot(filtered_df)
                if fig_reward_box:
                    st.plotly_chart(fig_reward_box, use_container_width=True)
            else:
                st.info("지원금 정보가 있는 채용 공고가 없습니다.")
    
    with tab4:
        st.header("📋 채용 공고 상세 정보")
        
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
        
        if display_columns and not filtered_df.empty:
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
                
                # 데이터 다운로드
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    csv = display_df_sorted[display_columns].to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 CSV 다운로드",
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
                        label="📄 JSON 다운로드",
                        data=json_data,
                        file_name=f"rallit_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        help="필터링된 데이터를 JSON 파일로 다운로드"
                    )
            else:
                st.warning("검색 조건에 맞는 데이터가 없습니다.")
        
        elif not display_columns:
            st.warning("표시할 컬럼을 선택해주세요.")
        
        else:
            st.warning("표시할 데이터가 없습니다.")
    
    # 푸터
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>💼 Rallit Jobs Dashboard | 
            📊 데이터 기반 채용 정보 분석 | 
            🔗 <a href='https://github.com/your-username/rallit-jobs-dashboard' target='_blank'>GitHub</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"애플리케이션 실행 중 오류가 발생했습니다: {str(e)}")
        logger.error(f"Application error: {str(e)}", exc_info=True)로딩 상태 표시
    with st.spinner('데이터를 로딩중입니다...'):
        df = data_loader.load_from_database()
    
    if df.empty:
        st.error("😕 데이터를 로드할 수 없습니다.")
        st.info("📋 CSV 파일들이 data/ 디렉토리에 있는지 확인해주세요:")
        st.code("""
        data/
        ├── rallit_management_jobs.csv
        ├── rallit_marketing_jobs.csv
        ├── rallit_design_jobs.csv
        └── rallit_developer_jobs.csv
        """)
        st.stop()
    
    # 데이터
