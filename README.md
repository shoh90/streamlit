# 🚀 갓생라이프/커리어하이어 - AI 기반 성장형 채용 플랫폼

<div align="center">

**"성장을 증명하고, 신뢰를 연결하다"**

AI 기반 데이터 분석으로 구직자의 성장을 정량화하고, 기업에는 신뢰 가능한 인재 정보를 제공하는 혁신적인 채용 플랫폼

[🎯 라이브 데모](https://app-basic2.streamlit.app)

</div>

---

## 📋 목차

- [✨ 주요 기능](#-주요-기능)
- [🎯 서비스 비전](#-서비스-비전)
- [🛠️ 기술 스택](#️-기술-스택)
- [⚡ 빠른 시작](#-빠른-시작)
- [📊 핵심 기능 상세](#-핵심-기능-상세)
- [🎨 스크린샷](#-스크린샷)
- [📈 로드맵](#-로드맵)
- [🤝 기여하기](#-기여하기)
- [📝 라이선스](#-라이선스)

---

## ✨ 주요 기능

### 🎯 AI 기반 스마트 매칭
- **TF-IDF 기반 스킬 유사도 분석**으로 정확한 매칭
- **가중치 적용 점수 시스템**으로 최신 기술 우대
- **성공 확률 예측 AI**로 합격 가능성 제시
- **유사 스킬 매칭** (React ↔ Vue.js 등)

### 📈 개인 성장 경로 분석
- **AI 기반 성장 잠재력 평가** (100점 만점)
- **레벨별 커리어 로드맵** 제시 (입문자 → 리드)
- **맞춤형 학습 리소스** 추천
- **시장 수요 vs 보유 스킬** 갭 분석

### 📊 시장 트렌드 인사이트
- **실시간 기술 트렌드** 분석 (+/- 성장률)
- **지역별/직무별** 채용 현황
- **지원금 트렌드** 예측
- **기업 규모별** 채용 패턴

### 🏢 기업 인사이트
- **데이터 기반 채용 리포트** 생성
- **파트너 기업** 우선 노출
- **스킬 기반 인재 필터링**
- **온보딩 예측** 시스템

---

## 🎯 서비스 비전

### 구직자를 위한 가치
- ✅ **JD 기반 성장 분석**으로 명확한 방향성 제시
- ✅ **AI 첨삭**을 통한 이력서 완성도 향상
- ✅ **정량화된 성장 히스토리** 관리
- ✅ **맞춤형 공고 추천**으로 효율적 구직

### 기업을 위한 가치
- 💼 **검증된 인재**의 정량적 데이터 제공
- 💼 **JD 적합도 점수**로 객관적 평가
- 💼 **온보딩 예측**으로 채용 리스크 감소
- 💼 **최신 트렌드 반영** JD 작성 지원

---

## 🛠️ 기술 스택

| 분야 | 기술 |
|------|------|
| **Frontend** | Streamlit, Plotly |
| **Backend** | Python, Pandas, NumPy |
| **AI/ML** | scikit-learn, TF-IDF |
| **Database** | SQLite, CSV |
| **Deployment** | Streamlit Cloud, Heroku, Docker |

---

## ⚡ 빠른 시작

### 1️⃣ 저장소 클론
```bash
git clone https://github.com/your-username/rallit-smart-dashboard.git
cd rallit-smart-dashboard
```

### 2️⃣ 가상환경 설정
```bash
# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3️⃣ 의존성 설치
```bash
pip install -r requirements.txt
```

### 4️⃣ 데이터 준비 (선택사항)
```bash
# data/ 디렉토리 생성
mkdir data

# CSV 파일 배치 (있는 경우)
# data/rallit_management_jobs.csv
# data/rallit_marketing_jobs.csv
# data/rallit_design_jobs.csv
# data/rallit_developer_jobs.csv
```

### 5️⃣ 애플리케이션 실행
```bash
streamlit run app.py
```

🎉 브라우저에서 `http://localhost:8501`로 접속하세요!

---

## 📊 핵심 기능 상세

### 🎯 AI 스마트 매칭 엔진

```python
# 고도화된 매칭 알고리즘 예시
def calculate_advanced_skill_match(user_skills, job_requirements, job_category):
    # TF-IDF 기반 유사도 계산
    vectorizer = TfidfVectorizer()
    similarity_score = cosine_similarity(user_vector, job_vector)
    
    # 가중치 적용
    weighted_score = apply_skill_weights(similarity_score, modern_skills)
    
    # 카테고리 보너스
    category_bonus = calculate_category_bonus(user_skills, job_category)
    
    return final_score, matched_skills, missing_skills
```

### 📈 성장 잠재력 분석

| 평가 요소 | 가중치 | 설명 |
|-----------|--------|------|
| 학습 활동 | 25% | 최근 1년 강의 수강 이력 |
| 프로젝트 경험 | 30% | 개인/팀 프로젝트 수행 능력 |
| 기술 다양성 | 20% | 보유 기술 스택의 폭 |
| 오픈소스 기여 | 15% | GitHub 활동 및 커뮤니티 참여 |
| 트렌드 관심도 | 10% | 최신 기술에 대한 관심과 학습 |

### 🏢 기업용 리포트 생성

```
📊 인재 분석 리포트
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 지원자: 홍길동
🎯 JD 적합도: 87.5% (매우 높음)
📈 성장 잠재력: 92.0/100
🚀 합격 예상 확률: 89.3%
⏱️ 예상 온보딩 기간: 1.2개월
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 매칭 스킬: Python, React, AWS, Docker
📚 추가 학습 권장: Kubernetes, TypeScript
💡 추천 사유: 최신 기술 트렌드에 적극적이며,
              프로젝트 경험이 풍부함
```

---

## 🎨 스크린샷

<details>
<summary>📱 메인 대시보드</summary>

```
🚀 갓생라이프/커리어하이어
AI 기반 성장형 채용 플랫폼 - "성장을 증명하고, 신뢰를 연결하다"

┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│  📊 총 채용공고  │  💰 평균 지원금  │  🤝 파트너 기업  │  🏠 원격근무 가능 │
│     1,247개     │    425,000원    │      67.3%      │      43.2%      │
│   활성: 892개   │ 최고: 2,000,000원│    84개 기업    │    539개 공고   │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

</details>

<details>
<summary>🎯 AI 스마트 매칭</summary>

```
🎯 AI 기반 스마트 매칭
┌─────────────────┬─────────────────┬─────────────────┐
│  🧠 성장 잠재력  │   ⚡ 보유 기술   │  🎯 매칭 공고   │
│      92점       │      7개        │     23개       │
│   AI 분석 결과  │   등록된 스킬   │   조건 맞는 공고 │
└─────────────────┴─────────────────┴─────────────────┘

🌟 맞춤 추천 공고 (23개)

🏆 #1 Senior Frontend Developer @ 테크스타트업A - 합격 확률 89%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
회사: 테크스타트업A | 직무: DEVELOPER | 지역: PANGYO | 지원금: 500,000원

🎯 스킬 매칭 분석:
✅ React  ✅ JavaScript  ✅ TypeScript  ✅ AWS
📚 Docker  📚 Kubernetes

📊 상세 분석:
- 기본 매칭도: 85.0%
- 가중 매칭도: 87.5%  
- 카테고리 보너스: +2.0점
```

</details>

---

## 📈 로드맵

### 🎯 Phase 1: MVP 완성 (현재)
- [x] AI 기반 스킬 매칭 엔진
- [x] 개인 성장 경로 분석
- [x] 시장 트렌드 대시보드
- [x] 기업 인사이트 리포트

### 🚀 Phase 2: 고도화 (2024 Q2)
- [ ] **GPT 기반 이력서 첨삭** 기능
- [ ] **실시간 알림** 시스템
- [ ] **모바일 최적화** UI/UX
- [ ] **API 연동** (실제 채용 사이트)

### 🌟 Phase 3: 확장 (2024 Q3-Q4)
- [ ] **개인 연봉 예측** AI 모델
- [ ] **기업 문화 적합도** 분석
- [ ] **추천 시스템** 개인화
- [ ] **멀티 플랫폼** 지원

### 🌍 Phase 4: 글로벌 (2025)
- [ ] **다국어 지원** (영어, 일본어)
- [ ] **해외 채용 시장** 연동
- [ ] **글로벌 스킬 트렌드** 분석
- [ ] **원격근무** 전문 매칭

---

## 🏗️ 프로젝트 구조

```
rallit-smart-dashboard/
├── 📁 .streamlit/
│   └── config.toml              # Streamlit 설정
├── 📁 data/                     # 데이터 파일
│   ├── rallit_management_jobs.csv
│   ├── rallit_marketing_jobs.csv
│   ├── rallit_design_jobs.csv
│   └── rallit_developer_jobs.csv
├── 📁 docs/                     # 문서
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── CONTRIBUTING.md
├── 📁 tests/                    # 테스트 코드
│   ├── test_matching_engine.py
│   ├── test_data_loader.py
│   └── test_visualization.py
├── 📁 assets/                   # 리소스
│   ├── images/
│   └── styles/
├── 🐍 app.py                    # 메인 애플리케이션
├── 📋 requirements.txt          # Python 의존성
├── 🐳 Dockerfile               # Docker 설정
├── ⚙️ .github/workflows/       # CI/CD
└── 📖 README.md                # 프로젝트 문서
```

---

## 🧪 테스트

```bash
# 전체 테스트 실행
pytest tests/

# 특정 테스트 실행
pytest tests/test_matching_engine.py -v

# 커버리지 리포트
pytest --cov=app tests/
```

---

## 🚀 배포

### Streamlit Cloud 배포
1. GitHub에 코드 푸시
2. [Streamlit Cloud](https://share.streamlit.io) 접속
3. 리포지토리 연결 후 `app.py` 선택
4. 자동 배포 완료 ✨

### Docker 배포
```bash
# Docker 이미지 빌드
docker build -t rallit-dashboard .

# 컨테이너 실행
docker run -p 8501:8501 rallit-dashboard
```

### Heroku 배포
```bash
# Heroku CLI 설치 후
heroku create rallit-smart-dashboard
git push heroku main
heroku open
```

---

## 🤝 기여하기

이 프로젝트에 기여해주셔서 감사합니다! 

### 기여 방법
1. **Fork** 이 리포지토리
2. **Feature 브랜치** 생성 (`git checkout -b feature/AmazingFeature`)
3. **변경사항 커밋** (`git commit -m 'Add some AmazingFeature'`)
4. **브랜치 푸시** (`git push origin feature/AmazingFeature`)
5. **Pull Request** 생성

### 개발 가이드라인
- 코드 스타일: [PEP 8](https://www.python.org/dev/peps/pep-0008/) 준수
- 커밋 메시지: [Conventional Commits](https://www.conventionalcommits.org/) 형식
- 테스트: 새로운 기능에는 반드시 테스트 코드 작성

### 이슈 리포트
버그를 발견하거나 새로운 기능을 제안하고 싶다면 [Issues](https://github.com/your-repo/issues)에 등록해주세요.

---

## 👥 기여자

**현재 개발팀**
- 💻 홍길동 - Lead Developer
- 🤖 김영희 - AI/ML Engineer
- 🎨 이철수 - UI/UX Designer
- 📊 박민수 - Data Analyst

---

## 📞 지원 및 문의

- 📧 **이메일**: contact@godsaenglife.com
- 💬 **디스코드**: [커뮤니티 참여](https://discord.gg/godsaenglife)
- 📱 **카카오톡**: @갓생라이프
- 🐛 **버그 리포트**: [GitHub Issues](https://github.com/your-repo/issues)
- 💡 **기능 제안**: [GitHub Discussions](https://github.com/your-repo/discussions)

---

## 🏆 인정 및 감사

- **Streamlit Team**: 훌륭한 프레임워크 제공
- **Plotly**: 강력한 시각화 라이브러리
- **오픈소스 커뮤니티**: 지속적인 영감과 도움

---

## 📝 라이선스

이 프로젝트는 [MIT License](LICENSE) 하에 배포됩니다.

```
MIT License

Copyright (c) 2024 갓생라이프/커리어하이어

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software...
```

---

## 📈 프로젝트 현황

- **개발 상태**: MVP 완성
- **지원 Python 버전**: 3.8+
- **라이선스**: MIT
- **최근 업데이트**: 2024년 1월

---

<div align="center">

**⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요! ⭐**

Made with ❤️ by [갓생라이프/커리어하이어](https://github.com/your-organization)

</div>
