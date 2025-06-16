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
                        # <<< 수정: 고유한 key 추가
                        st.plotly_chart(fig, use_container_width=True, key=f"match_gauge_{i}")

            growth_score, factors = matching_engine.analyze_growth_potential(user_profile)
            st.markdown("---"); st.subheader("📈 당신의 성장 잠재력")
            col1, col2 = st.columns([1, 2])
            with col1:
                fig = go.Figure(go.Indicator(mode="gauge+number", value=growth_score, title={'text': "성장 잠재력"}))
                # <<< 수정: 고유한 key 추가 (반복문은 아니지만 안전을 위해)
                st.plotly_chart(fig, use_container_width=True, key="growth_potential_gauge")
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
            # <<< 수정: 고유한 key 추가
            st.plotly_chart(fig, use_container_width=True, key="category_pie")
        with col2:
            counts = filtered_df['address_region'].value_counts().head(8)
            fig = px.bar(x=counts.values, y=counts.index, orientation='h', title="상위 8개 지역 채용 현황")
            # <<< 수정: 고유한 key 추가
            st.plotly_chart(fig, use_container_width=True, key="region_bar")
        
        st.subheader("🔥 인기 기술 스택 트렌드")
        skills = filtered_df['job_skill_keywords'].dropna().str.split(',').explode().str.strip()
        skill_counts = skills[skills != ''].value_counts().head(15)
        fig = px.bar(x=skill_counts.values, y=skill_counts.index, orientation='h', title="TOP 15 인기 기술")
        # <<< 수정: 고유한 key 추가
        st.plotly_chart(fig, use_container_width=True, key="skills_bar")

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
            # <<< 수정: 고유한 key 추가
            st.plotly_chart(fig, use_container_width=True, key="skill_gap_bar")
        else:
            st.info("👆 사이드바에서 프로필을 입력하면 성장 경로를 분석해 드립니다!")

    with tabs[3]:
        st.header("🏢 기업 인사이트")
        top_companies = filtered_df['company_name'].value_counts().head(10)
        st.bar_chart(top_companies, height=400) # st.bar_chart는 key가 필수는 아님

    with tabs[4]:
        st.header("🔮 예측 분석")
        st.info("AI 기반 예측 기능은 곧 출시될 예정입니다. 🚀")
        
    with tabs[5]:
        st.header("📋 채용 공고 상세 정보")
        st.dataframe(filtered_df, use_container_width=True)
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📄 CSV 다운로드", data=csv, file_name="rallit_jobs.csv")
