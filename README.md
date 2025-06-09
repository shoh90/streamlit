# 💼 Rallit Jobs Dashboard

**Rallit 채용 정보를 시각화하고 분석하는 대화형 대시보드**

## 🚀 주요 기능

### 📊 실시간 데이터 분석
- **다중 필터링**: 직무 카테고리, 지역, 채용 상태, 파트너 여부별 필터링
- **핵심 지표**: 총 채용 공고, 모집중 공고, 파트너 기업, 참여 기업 수
- **실시간 통계**: 선택된 필터에 따른 동적 통계 업데이트

### 🎨 시각화 차트
- **파이 차트**: 직무 카테고리별 분포
- **막대 차트**: 지역별, 기업별 채용 공고 분포
- **기술 스택 분석**: 개발자 직군 인기 기술 TOP 20
- **지원금 분석**: 분포도 및 카테고리별 박스플롯

### 🔍 상세 데이터 테이블
- **동적 컬럼 선택**: 원하는 정보만 표시
- **실시간 검색**: 제목, 회사명 기반 검색
- **정렬 및 페이지네이션**: 대용량 데이터 효율적 처리
- **다중 포맷 다운로드**: CSV, JSON, 요약 리포트

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Database**: SQLite
- **Deployment**: Streamlit Cloud / Heroku
- **CI/CD**: GitHub Actions

## 📦 설치 및 실행

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/rallit-jobs-dashboard.git
cd rallit-jobs-dashboard
```

### 2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 데이터 준비
CSV 파일들을 `data/` 디렉토리에 배치:
```
data/
├── rallit_management_jobs.csv
├── rallit_marketing_jobs.csv
├── rallit_design_jobs.csv
└── rallit_developer_jobs.csv
```

### 5. 데이터베이스 생성 (선택사항)
```bash
python data_processor.py
```

### 6. 애플리케이션 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하세요.

## 🌐 배포

### Streamlit Cloud 배포
1. GitHub에 코드 푸시
2. [Streamlit Cloud](https://share.streamlit.io)에서 새 앱 생성
3. 저장소 연결 및 `app.py` 지정
4. 자동 배포 완료

### Heroku 배포
1. Heroku CLI 설치
2. 앱 생성 및 배포:
```bash
heroku create your-app-name
git push heroku main
```

## 📁 프로젝트 구조

```
rallit-jobs-dashboard/
├── .streamlit/
│   └── config.toml              # Streamlit 설정
├── .github/
│   └── workflows/
│       └── deploy.yml           # CI/CD 워크플로우
├── data/                        # CSV 데이터 파일
│   ├── rallit_management_jobs.csv
│   ├── rallit_marketing_jobs.csv
│   ├── rallit_design_jobs.csv
│   └── rallit_developer_jobs.csv
├── src/                         # 소스 코드 모듈
│   ├── __init__.py
│   ├── data_loader.py          # 데이터 로딩 로직
│   ├── visualizations.py       # 시각화 함수들
│   └── utils.py                # 유틸리티 함수들
├── tests/                       # 테스트 코드
│   ├── __init__.py
│   └── test_data_loader.py
├── .gitignore
├── requirements.txt             # Python 의존성
├── README.md
├── LICENSE
├── app.py                       # 메인 Streamlit 앱
└── data_processor.py           # CSV to SQLite 변환
```

## 📊 데이터 스키마

### jobs 테이블
| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| id | INTEGER | 채용 공고 고유 ID |
| job_category | TEXT | 직무 카테고리 (MANAGEMENT, MARKETING, DESIGN, DEVELOPER) |
| address_region | TEXT | 근무 지역 |
| company_name | TEXT | 회사명 |
| title | TEXT | 채용 공고 제목 |
| status_code | TEXT | 채용 상태 코드 |
| join_reward | INTEGER | 입사 지원금 |
| job_skill_keywords | TEXT | 직무 관련 키워드 |
| ... | ... | [전체 스키마 보기](docs/schema.md) |

## 🎯 주요 화면

### 1. 기본 분석 대시보드
- 직무 카테고리별 분포
- 지역별 채용 공고 분포
- 채용 상태별 통계

### 2. 기업 분석
- 상위 채용 기업 순위
- 회사 규모별 분포
- 카테고리별 지역 분포

### 3. 기술 스택 분석
- 인기 기술 스택 TOP 20
- 지원금 통계 및 분포
- 카테고리별 지원금 비교

### 4. 상세 데이터
- 동적 테이블 뷰
- 고급 필터링 및 검색
- 데이터 다운로드

## 🔧 개발 가이드

### 로컬 개발
```bash
# 개발 모드로 실행
streamlit run app.py --server.runOnSave=true

# 테스트 실행
python -m pytest tests/

# 코드 스타일 검사
flake8 .
```

### 새로운 기능 추가
1. `src/` 디렉토리에 모듈 추가
2. `app.py`에서 import 및 사용
3. 테스트 코드 작성
4. 문서 업데이트

### 데이터 업데이트
```bash
# 새로운 CSV 파일을 data/ 디렉토리에 추가
# 데이터베이스 재생성
python data_processor.py
```

## 📈 성능 최적화

- **데이터 캐싱**: `@st.cache_data` 데코레이터 사용
- **효율적 쿼리**: SQLite 인덱스 활용
- **페이지네이션**: 대용량 데이터 처리
- **컴포넌트 분리**: 모듈화된 시각화 함수

## 🤝 기여하기

1. Fork 생성
2. Feature 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치 푸시 (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙋‍♂️ 지원 및 문의

- **이슈 리포트**: [GitHub Issues](https://github.com/your-username/rallit-jobs-dashboard/issues)
- **기능 요청**: [GitHub Discussions](https://github.com/your-username/rallit-jobs-dashboard/discussions)
- **이메일**: contact@example.com

## 🔗 관련 링크

- [Streamlit 공식 문서](https://docs.streamlit.io)
- [Plotly 공식 문서](https://plotly.com/python/)
- [Pandas 공식 문서](https://pandas.pydata.org/docs/)
- [Rallit 공식 사이
