# Graph RAG & Hybrid 메뉴 추천 시스템 (V2)

> **Neo4j 지식 그래프와 Llama-3 LLM을 결합하여, 상황(Context)과 취향(Taste)을 모두 고려한 설명 가능한 초개인화 추천 시스템**

## 프로젝트 개요
기존의 키오스크는 단순히 많이 팔린 메뉴만 추천하여, 사용자의 개별적인 상황(날씨, 인원 등)이나 취향을 반영하지 못했습니다.
본 프로젝트는 지식 그래프(Knowledge Graph)를 통해 데이터 간의 복잡한 관계를 모델링하고, **Graph RAG** 기술을 적용하여 AI가 추천의 근거를 논리적으로 설명해 주는 지능형 추천 시스템입니다.

## 주요 기능
1.  **상황 기반 추천 (Context-Aware):** 인원, 날씨, 시간, 예산을 고려한 가중치 검색 알고리즘.
2.  **나와 비슷한 유저 Pick (Collaborative Filtering):** 나와 유사한 주문 패턴을 가진 그룹을 분석하여 메뉴 추천.
3.  **AI 설명 (Explainable AI):** Llama-3 모델이 "비 오는 날 따뜻한 국물을 선호하는..."과 같이 구체적인 추천 사유를 생성.
4.  **시스템 최적화:** 4-bit Quantization을 통한 온프레미스 LLM 경량화 (VRAM 60% 절감).

## 기술 스택 (Tech Stack)
* **Backend:** Python 3.11, FastAPI
* **Database:** Neo4j (Graph DB), MySQL (RDBMS)
* **AI/LLM:** Meta Llama-3.1-8B-Instruct, HuggingFace, LangChain
* **Frontend:** HTML5, JavaScript (Vanilla)
* **DevOps:** Docker

## 📂 프로젝트 구조
📦 Graph-RAG-Recommendation ├── app │ ├── api # API 엔드포인트 (Auth, Order, Recommend) │ ├── database.py # DB 연결 설정 (Neo4j, MySQL) │ ├── main.py # FastAPI 실행 파일 │ ├── services # 비즈니스 로직 │ │ └── hf_llm.py # Llama-3 모델 로딩 및 프롬프트 엔지니어링 │ └── templates # 프론트엔드 HTML ├── .env.example # 환경변수 예시 ├── requirements.txt # 의존성 패키지 └── README.md

## 설치 및 실행 방법
###  모델 다운 및 환경 설정
### AI 모델 다운로드 (필수)
본 프로젝트는 **Meta Llama-3.1-8B-Instruct** 모델을 로컬에서 구동합니다.
용량 문제로 GitHub에는 모델 파일이 포함되어 있지 않으므로, 아래 스크립트로 직접 다운로드해야 합니다.

**사전 준비:**
1. [Hugging Face](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct)에 가입 및 로그인.
2. 위 링크에서 모델 사용 승인(Agree) 버튼 클릭.
3. [Settings > Access Tokens](https://huggingface.co/settings/tokens)에서 토큰 생성 (`Read` 권한).

**실행 명령어:**
```bash
# 1. 패키지 설치
pip install huggingface-hub

# 2. 다운로드 스크립트 실행
python download_model.py
# (토큰을 입력하라고 뜨면 복사한 토큰을 붙여넣기 하세요)

```bash
# 저장소 클론
git clone [레포지토리 주소]

# 패키지 설치
pip install -r requirements.txt

2. 데이터베이스 설정 (Docker)
# Neo4j 실행
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest

3. 환경 변수 설정
.env.example 파일을 복사하여 .env 파일을 생성하고, DB 정보를 입력하세요.

4. 서버 실행
uvicorn app.main:app --reload

성과
응답 속도: 평균 3초 이내 (Graph 검색 + LLM 추론)

사용자 만족도: V1(Rule-based) 대비 4.6/5.0점으로 대폭 상승

할루시네이션 억제: Dynamic Prompting 기술로 없는 재료 언급 문제 해결
