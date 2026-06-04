# 평가용 합성 페르소나 (Synthetic Evaluation Personas)

> 이 디렉터리의 모든 이력서는 **합성(synthetic) 데이터**이며 실존 인물이 아닙니다.
> 단일 실제 이력서(프론트엔드/풀스택)로만 검증된 v0 알고리즘이 **다른 후보 프로파일에도
> 일반화되는지**를 진단하기 위한 4개 페르소나입니다. 기계가 읽는 기대값은
> [`expected_behavior.json`](./expected_behavior.json) 에 있습니다.

## 도메인 정렬(domain_alignment)이 동작하는 방식 (중요)
- 알고리즘은 각 JD의 `role_family`를 `ROLE_FAMILY_TO_DOMAINS`로 도메인 토큰 집합으로 확장한 뒤,
  페르소나의 `primary_domains` / `secondary_domains` 와 비교해
  **strong / adjacent / weak / mismatch** 를 결정합니다(`src/rank_aggregate.py:domain_alignment`).
- 페르소나별 `primary_domains` / `secondary_domains` 토큰이 **JD 선택(tier)** 과 **fit 상한(domain cap)** 을 함께 좌우합니다.
- `fullstack` 은 `{fullstack, frontend, backend, web}` 으로 확장되므로, primary 가 frontend 이거나 backend 인
  페르소나에서는 fullstack JD가 **strong** 으로 분류될 수 있습니다(= adjacent 기대였더라도 더 높게 나옴).
  평가에서는 strong/adjacent 를 모두 "non-mismatch(양호)"로 취급하므로 문제되지 않습니다.
- `marketing / design / product` 는 항상 **mismatch** 이며, 도메인 우선순위 가드에 의해
  어떤 비-mismatch(엔지니어링) 역할보다도 위로 랭크될 수 없습니다.

---

## 1. Backend / Platform Engineer — `backend_platform.md`
- **프로파일:** 2.5년차 서버 엔지니어. Java/Kotlin, Spring Boot, JPA, PostgreSQL/MySQL, Redis, Kafka/SQS, REST/gRPC, AWS.
  API 설계·DB 모델링·트랜잭션·비동기 처리·모니터링 강점. 프론트는 일부 어드민 수정 수준, ML 경험 거의 없음.
- **primary_domains:** `backend`
- **secondary_domains:** `fullstack, devops, cloud, infra`
- **strong-fit 기대:** backend / server / platform backend
- **adjacent 기대:** devops_infra, (백엔드 비중 큰) fullstack
- **weak 기대:** frontend 전담, ml_ai, data, security, android/ios
- **mismatch 기대:** marketing / design / product
- **실패의 모습:** 프론트엔드/ML/보안 역할이 backend 역할보다 위로 올라가거나, 마케팅이 엔지니어링 역할 위로 랭크됨.

## 2. Junior Frontend Engineer — `junior_frontend.md`
- **프로파일:** 신입/주니어. React, TypeScript, Next.js, Tailwind, Zustand/React Query, 기본 테스트.
  프로젝트 다수 + 인턴 1회, 그러나 대규모 프로덕션 오너십은 부족. 시니어(3~5년) 아키텍처 주도 경험 없음.
- **primary_domains:** `frontend, web`
- **secondary_domains:** `fullstack`
- **strong-fit 기대:** frontend 인턴 / 주니어 frontend / web frontend
- **moderate 기대:** 일반 frontend 포지션
- **weak 기대:** 3~5년 요구 시니어 frontend(도메인은 frontend지만 experience_level prerequisite 갭으로 fit↓),
  backend, infra, android
- **mismatch 기대:** marketing / design / product
- **실패의 모습:** backend/android 가 frontend 위로 랭크되거나, 시니어 frontend 가 신입에게 fit 5로 과대평가되거나,
  마케팅이 엔지니어링 위로 랭크됨.

## 3. AI / ML Application Engineer — `ai_ml_application.md`
- **프로파일:** 3년차 AI 애플리케이션/ML 엔지니어. Python, PyTorch, Hugging Face, LangChain/LlamaIndex, RAG,
  벡터 DB, FastAPI, PostgreSQL, Docker. 문서 QA·추천/랭킹·모델 평가·LLM 에이전트 PoC. 일부 백엔드/웹 연동.
  대규모 분산 학습/깊은 MLOps는 제한적.
- **primary_domains:** `ml_ai, ai`
- **secondary_domains:** `data, backend`
- **strong-fit 기대:** AI Engineer / ML Engineer / LLM·RAG Engineer
- **adjacent 기대:** data engineer, backend AI 플랫폼, MLOps
- **weak 기대:** frontend, android, 순수 security, devops_infra
- **mismatch 기대:** marketing / design / product
- **실패의 모습:** frontend/android 가 ML 역할 위로 랭크됨, 또는 마케팅이 엔지니어링 위로 랭크됨.
- **데이터 주의:** 라이브 JD 풀(Toss/Daangn)에 ml_ai 공고가 적을 수 있음 → ml_ai JD가 선택되지 않으면
  관련 불변식은 `n/a`로 보고됩니다(일반화 진단의 핵심 신호).

## 4. DevOps / Infra / Security-adjacent Engineer — `devops_infra_security.md`
- **프로파일:** 4년차 클라우드 인프라/플랫폼. AWS, Linux, Docker, Kubernetes, Terraform, GitHub Actions,
  관측성, 장애 대응. 보안 운영/취약점 관리 일부 관여(깊은 모의해킹은 아님). 앱 기능 개발 비중 낮음.
- **primary_domains:** `devops, cloud, infra`
- **secondary_domains:** `security, backend`
- **strong-fit 기대:** devops_infra / platform / SRE / AIOps / cloud infra
- **adjacent 기대:** security 탐지·대응, backend 플랫폼
- **weak 기대:** frontend, ml_ai, data 분석
- **mismatch 기대:** marketing / design / product
- **실패의 모습:** frontend/ML 이 infra 역할 위로 랭크됨, 또는 마케팅이 엔지니어링 위로 랭크됨.

---

## 공통 실패 신호 (모든 페르소나)
1. **mismatch(marketing/design/product) 가 비-mismatch 역할보다 위로** 랭크됨 → 도메인 우선순위 가드 위반(FAIL).
2. 페르소나의 **expected_top_role_family 가 선택된 JD에 존재함에도 Top 3에 하나도 없음** → WARNING.
3. **strong/adjacent 역할이 weak/mismatch 역할보다 광범위하게 아래로** 뒤집힘(domain inversion 다수) → WARNING.
4. **비추출(non-extractive) 인용이 최종 산출물에 살아남음** → FAIL(추출형 불변식 위반).
5. **합격 확률/퍼센트 수치 출력** 또는 fit 이 1~5 정수 레벨이 아님 → FAIL.

> 이 진단은 정확도 벤치마크가 아니라 **방향성(direction) 진단**입니다. 각 페르소나 결과는
> `pass` / `warning` / `fail` 로만 라벨링되며, 자세한 해석은 `docs/EVAL_SUITE.md` 를 참고하세요.
