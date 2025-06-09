"""
시각화 모듈
Plotly를 사용한 차트 생성 기능 제공
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class JobsVisualizer:
    """채용 정보 시각화 클래스"""
    
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
        self.theme_colors = {
            'primary': '#FF6B6B',
            'secondary': '#4ECDC4',
            'accent': '#45B7D1',
            'success': '#96CEB4',
            'warning': '#FFEAA7',
            'danger': '#DDA0DD'
        }
    
    def create_category_pie_chart(self, df):
        """직무 카테고리별 파이 차트 생성"""
        category_counts = df['job_category'].value_counts()
        
        fig = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="직무 카테고리별 채용 공고 분포",
            color_discrete_sequence=self.color_palette,
            hole=0.4  # 도넛 차트로 만들기
        )
        
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>개수: %{value}<br>비율: %{percent}<extra></extra>'
        )
        
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5),
            font=dict(size=12),
            height=400
        )
        
        return fig
    
    def create_region_bar_chart(self, df, top_n=10):
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
            xaxis_title="채용 공고 수",
            yaxis_title="지역",
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_companies_chart(self, df, top_n=10):
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
    
    def create_company_size_chart(self, df):
        """회사 규모별 분포 차트"""
        def categorize_company_size(job_count):
            if job_count >= 10:
                return "대기업"
            elif job_count >= 5:
                return "중견기업"
            elif job_count >= 3:
                return "중소기업"
            else:
                return "스타트업"
        
        company_job_counts = df['company_name'].value_counts()
        company_sizes = company_job_counts.apply(categorize_company_size)
        size_counts = company_sizes.value_counts()
        
        fig = px.bar(
            x=size_counts.index,
            y=size_counts.values,
            title="회사 규모별 분포",
            labels={'x': '회사 규모', 'y': '회사 수'},
            color=size_counts.values,
            color_continuous_scale='oranges',
            text=size_counts.values
        )
        
        fig.update_traces(
            texttemplate='%{text}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>회사 수: %{y}<extra></extra>'
        )
        
        fig.update_layout(height=400, showlegend=False)
        
        return fig
    
    def create_skills_chart(self, df, top_n=20):
        """기술 스택 차트 생성"""
        all_skills = []
        for skills_str in df['job_skill_keywords'].dropna():
            if isinstance(skills_str, str):
                skills = [skill.strip() for skill in skills_str.split(',')]
                all_skills.extend(skills)
        
        if not all_skills:
            return None
        
        skill_counts = pd.Series(all_skills).value_counts().head(top_n)
        
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
    
    def create_reward_histogram(self, df):
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
            color_discrete_sequence=[self.theme_colors['primary']]
        )
        
        fig.update_traces(
            hovertemplate='지원금: %{x:,.0f}원<br>공고 수: %{y}<extra></extra>'
        )
        
        fig.update_layout(
            xaxis_title="지원금(원)",
            yaxis_title="채용 공고 수",
            height=400
        )
        
        return fig
    
    def create_status_donut_chart(self, df):
        """채용 상태별 도넛 차트"""
        status_counts = df['status_name'].value_counts()
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="채용 상태별 분포",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.6
        )
        
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>개수: %{value}<br>비율: %{percent}<extra></extra>'
        )
        
        fig.update_layout(
            showlegend=True,
            height=400,
            annotations=[dict(text='채용<br>상태', x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
        
        return fig
    
    def create_level_distribution(self, df):
        """직급별 분포 차트"""
        level_counts = df['job_level'].value_counts()
        
        fig = px.bar(
            x=level_counts.index,
            y=level_counts.values,
            title="직급별 채용 공고 분포",
            labels={'x': '직급', 'y': '채용 공고 수'},
            color=level_counts.values,
            color_continuous_scale='plasma',
            text=level_counts.values
        )
        
        fig.update_traces(
            texttemplate='%{text}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>채용 공고 수: %{y}<extra></extra>'
        )
        
        fig.update_layout(height=400, showlegend=False)
        
        return fig
    
    def create_multi_category_comparison(self, df):
        """카테고리별 다중 비교 차트"""
        # 카테고리별 지역 분포
        category_region = df.groupby(['job_category', 'address_region']).size().unstack(fill_value=0)
        
        fig = px.bar(
            category_region.T,
            title="직무 카테고리별 지역 분포",
            labels={'value': '채용 공고 수', 'index': '지역'},
            height=500
        )
        
        fig.update_layout(
            xaxis_title="지역",
            yaxis_title="채용 공고 수",
            legend_title="직무 카테고리"
        )
        
        return fig
    
    def create_reward_boxplot(self, df):
        """카테고리별 지원금 박스플롯"""
        reward_df = df[df['join_reward'] > 0]
        
        if reward_df.empty:
            return None
        
        fig = px.box(
            reward_df,
            x='job_category',
            y='join_reward',
            title="직무 카테고리별 지원금 분포",
            labels={'x': '직무 카테고리', 'y': '지원금(원)'},
            color='job_category',
            color_discrete_sequence=self.color_palette
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>지원금: %{y:,.0f}원<extra></extra>'
        )
        
        fig.update_layout(
            height=400,
            showlegend=False
        )
        
        return fig

# 전역 시각화 인스턴스
visualizer = JobsVisualizer()
