"""
데이터 로더 모듈
SQLite 데이터베이스와 CSV 파일로부터 데이터를 로드하는 기능 제공
"""

import sqlite3
import pandas as pd
import streamlit as st
import os
from pathlib import Path
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            if not os.path.exists(_self.db_path):
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
    
    @st.cache_data
    def _load_from_csv_fallback(_self):
        """CSV 파일에서 직접 데이터 로드 (대체 방법)"""
        try:
            all_dfs = []
            
            for category, filename in _self.csv_files.items():
                file_path = _self.data_dir / filename
                
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
                    logger.warning(f"CSV file {filename} not found")
            
            if all_dfs:
                combined_df = pd.concat(all_dfs, ignore_index=True)
                combined_df['created_at'] = pd.Timestamp.now()
                logger.info(f"Combined {len(combined_df)} records from CSV files")
                return combined_df
            else:
                logger.error("No CSV files found")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"CSV loading error: {str(e)}")
            return pd.DataFrame()
    
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
    
    def get_summary_stats(self, df):
        """데이터 요약 통계 반환"""
        if df.empty:
            return {}
        
        stats = {
            'total_jobs': len(df),
            'unique_companies': df['company_name'].nunique(),
            'categories': df['job_category'].value_counts().to_dict(),
            'regions': df['address_region'].value_counts().head(10).to_dict(),
            'hiring_count': len(df[df['status_code'] == 'HIRING']),
            'partner_count': len(df[df['is_partner'] == 1])
        }
        
        if 'join_reward' in df.columns:
            reward_df = df[df['join_reward'] > 0]
            if not reward_df.empty:
                stats['avg_reward'] = reward_df['join_reward'].mean()
                stats['max_reward'] = reward_df['join_reward'].max()
        
        return stats
    
    def validate_data(self, df):
        """데이터 유효성 검사"""
        issues = []
        
        if df.empty:
            issues.append("데이터가 비어있습니다.")
            return issues
        
        # 필수 컬럼 확인
        required_columns = ['id', 'job_category', 'company_name', 'title']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            issues.append(f"필수 컬럼이 누락되었습니다: {missing_columns}")
        
        # 중복 ID 확인
        if df['id'].duplicated().any():
            issues.append("중복된 ID가 있습니다.")
        
        # NULL 값 확인
        null_counts = df.isnull().sum()
        high_null_columns = null_counts[null_counts > len(df) * 0.5].index.tolist()
        if high_null_columns:
            issues.append(f"NULL 값이 많은 컬럼들: {high_null_columns}")
        
        return issues

# 전역 데이터 로더 인스턴스
data_loader = DataLoader()
