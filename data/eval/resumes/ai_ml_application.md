<!-- Synthetic resume for algorithm evaluation. Not a real person. -->
# 오세훈 (Sehun Oh) — AI / ML Application Engineer

> Synthetic resume for algorithm evaluation. Not a real person.

## Summary
AI 애플리케이션 / ML 엔지니어로 약 3년간 문서 QA, 추천/랭킹, LLM 에이전트 프로토타입을 만들어 온
엔지니어입니다. Python + PyTorch + Hugging Face 생태계와 LangChain/LlamaIndex 기반 RAG 파이프라인,
벡터 DB, FastAPI 서빙에 강점이 있습니다. 모델 평가/오프라인 메트릭 설계 경험이 있으며, 일부
백엔드/웹 연동도 직접 했습니다. 다만 대규모 분산 학습이나 깊은 MLOps(대규모 피처스토어/모델 레지스트리
운영) 경험은 제한적이고, 프론트엔드·모바일·보안은 전문 영역이 아닙니다.

## Skills
- Languages: Python, SQL, 약간의 TypeScript
- ML/DL: PyTorch, Hugging Face Transformers, scikit-learn, ONNX(추론 변환 기초)
- LLM/RAG: LangChain, LlamaIndex, OpenAI/Anthropic API, 프롬프트 설계, 임베딩 기반 검색
- Vector/Datastores: pgvector, FAISS, Pinecone, PostgreSQL, Redis
- Serving/Backend: FastAPI, Uvicorn, Docker, REST API
- Eval/Data: 오프라인 평가 메트릭(recall@k, nDCG), 데이터 라벨링 파이프라인, pandas
- Cloud: AWS(S3, EC2), GPU 인스턴스 운영 경험(소규모)

## Experience
### B2B SaaS 회사 — ML Application Engineer (2022.06 ~ 현재, 2년)
- 사내 문서 QA 시스템을 LlamaIndex + pgvector 기반 RAG로 구축, 답변 정확도(human eval)를 61% → 82%로 향상.
- 검색-생성 단계 분리와 재랭킹(cross-encoder) 도입으로 hallucination 신고 건수를 주당 40건 → 9건으로 감소.
- FastAPI로 추론 API를 서빙하고 Docker로 배포, p95 응답 시간 1.8s → 0.9s로 개선(캐싱 + 배치 임베딩).

### 추천 시스템 외주/계약 — ML Engineer (2021.05 ~ 2022.05, 1년)
- 커머스 상품 랭킹 모델(LightGBM → 간단한 two-tower)을 실험, 오프라인 nDCG@10 기준 7% 개선.
- A/B 테스트 지표 설계에 참여했으나 대규모 온라인 서빙 인프라는 플랫폼 팀이 담당.

## Projects
### LLM 에이전트 프로토타입 (2023)
- LangChain 도구 호출(tool calling)로 사내 위키 검색 + 일정 조회를 수행하는 에이전트 프로토타입 구현.
- 평가 하니스를 직접 작성해 도구 호출 정확도를 측정. 프로덕션 배포 전 단계의 PoC.

### 모델 평가 대시보드 (2022)
- Streamlit + pandas로 모델 버전별 오프라인 메트릭을 비교하는 내부 대시보드 제작.

## Education
- OO대학교 컴퓨터공학 학사 (2016.03 ~ 2021.02)
- 학부 연구생: 자연어처리 연구실 1년(문서 분류 과제)

## Preferences
- 희망 직무: AI Engineer / ML Engineer / LLM·RAG Engineer
- 관심 있음(인접): 데이터 엔지니어, 백엔드 AI 플랫폼, MLOps
- 약함: 프론트엔드, 안드로이드, 순수 보안(security)
- 선호하지 않음: 디자인/기획/마케팅 직무
- 근무 형태: 원격/하이브리드 모두 가능
