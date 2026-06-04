# 수동 라벨링 패킷 (Top 20) — 골든 페어

> 정확도 평가를 위해 사람이 직접 라벨링할 상위 20개 페어 (가장 어렵고 정보량이 큰 쌍 우선, 4개 페르소나 균형).

> 사람이 직접 라벨링하는 패킷입니다. **expected_winner / label_reason / confidence 는 비어 있으며 직접 채워야 합니다.** 시스템은 라벨을 추론하지 않았습니다. **A/B 규약:** A = 현재 기본 모드(domain_fit_bt)가 더 **높게** 매긴 공고이므로, 시스템에 동의하면 `A_better`, 뒤집어야 하면 `B_better`. 판단 불가는 `unsure`(점수 제외), 진짜 막상막하는 `tie`. fit 은 1~5이며 합격확률이 아닙니다. 발췌(매칭/결손)는 기존 산출물에서 그대로 가져온 추출형 근거입니다.

- 총 20쌍 · 페르소나 분포: {'junior_frontend': 6, 'devops_infra_security': 6, 'ai_ml_application': 4, 'backend_platform': 4} · 카테고리 분포: {'same_domain_close': 12, 'adjacent_vs_primary': 5, 'seniority_gap': 2, 'domain_transfer': 1}
- 난이도 분포: {'hard': 18, 'medium': 2} · 모드 불일치 쌍 수: 9

라벨링 순서 팁: ⚠(모드 불일치)·fit↔BT 불일치 쌍부터 보면 정보량이 큽니다. 각 쌍의 `outputs/eval/<persona>/final_report.md` 에서 두 공고의 매칭/결손을 함께 확인하세요.

---
## 1. prop-junior_frontend-01  ·  [same_domain_close]  ·  난이도 hard (hardness 9)  ·  ⚠ 모드 불일치
- **persona:** `junior_frontend`  ·  résumé: `data/eval/resumes/junior_frontend.md`
- **왜 라벨 가치가 있나:** 두 랭킹 모드(domain_fit_bt vs bt_primary)가 이 쌍을 **반대로** 정렬 → 라벨이 어느 정렬을 지지하는지 가름 · headline **fit과 BT(pairwise) 순서가 불일치** → fit 우선 vs 비교 우선 중 무엇이 맞는지 검증 · 같은 도메인에서 **경력연차(experience_level) 결손**이 순위를 가르는 것이 타당한지 · 같은 직군·티어의 **근소한 fit 차이**가 올바른 순서인지

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Daangn | Toss |
| 포지션 | Software Engineer, Frontend \| 커머스 | Frontend Developer |
| job_id | `daangn-6692173003` | `toss-4076130003` |
| role_family | frontend | frontend |
| domain | strong | strong |
| **fit (1~5)** | **3** | **2** |
| BT score | 0.3367 | 0.841 |
| rank · bt_primary | 5 | 3 |
| rank · fit_primary | 3 | 5 |
| rank · domain_fit_bt ⭐ | 3 | 5 |

**A — Daangn · Software Engineer, Frontend | 커머스**
- 매칭(발췌): TypeScript, React를 활용한 개발 경험이 있으신 분; 복잡한 상태 관리(Recoil, Zustand 등)를 다뤄보신 분
- 결손(발췌): [critical/technical/weak] 프론트엔드 기반 서비스 또는 프로젝트를 주도적으로 개발하고 운영한 경험이 있으신 분; [required/technical/missing] AI 도구(Claude Code, Cursor 등)를 적극 활용해 생산성을 높이고 비즈니스 임팩트에 집중하시는 분
- cap: role-defining critical gap; role-defining required gap
- 시스템 사유: TypeScript/React와 복잡한 상태 관리 경험은 강하게 맞지만, 프론트엔드 서비스를 주도적으로 개발·운영한 prerequisite가 약하고 운영 오너십 증거도 제한적입니다. 핵심 기술은 맞지만 prerequisite gap과 운영 경험 부족이 더 큽니다.

**B — Toss · Frontend Developer**
- 매칭(발췌): React, TypeScript 기반으로 안정적인 서비스를 개발할 수 있는 분
- 결손(발췌): [required/experience_level/missing] 레거시 코드를 최신의 개발 환경에 맞게 개선한 경험; [required/technical/missing] 기존 소스 코드를 새로운 코드 베이스로 점진적으로 이관한 경험
- cap: role-defining required gaps x2
- 시스템 사유: React/TypeScript 기반 안정적 서비스 개발 역량이 직접 매칭되며 도메인 적합성도 높습니다. 그러나 레거시 개선과 점진적 이관 경험이라는 핵심 prerequisite gap이 있어 상위 두 개보다 FIT이 약합니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 2. prop-junior_frontend-02  ·  [same_domain_close]  ·  난이도 hard (hardness 9)  ·  ⚠ 모드 불일치
- **persona:** `junior_frontend`  ·  résumé: `data/eval/resumes/junior_frontend.md`
- **왜 라벨 가치가 있나:** 두 랭킹 모드(domain_fit_bt vs bt_primary)가 이 쌍을 **반대로** 정렬 → 라벨이 어느 정렬을 지지하는지 가름 · headline **fit과 BT(pairwise) 순서가 불일치** → fit 우선 vs 비교 우선 중 무엇이 맞는지 검증 · 같은 도메인에서 **경력연차(experience_level) 결손**이 순위를 가르는 것이 타당한지 · 같은 직군·티어의 **근소한 fit 차이**가 올바른 순서인지

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Daangn | Toss |
| 포지션 | Software Engineer, Frontend \| 커뮤니티 (모임) | Frontend Developer |
| job_id | `daangn-7689088003` | `toss-4076141003` |
| role_family | frontend | frontend |
| domain | strong | strong |
| **fit (1~5)** | **3** | **2** |
| BT score | 0.6765 | 1.0454 |
| rank · bt_primary | 4 | 2 |
| rank · fit_primary | 2 | 4 |
| rank · domain_fit_bt ⭐ | 2 | 4 |

**A — Daangn · Software Engineer, Frontend | 커뮤니티 (모임)**
- 매칭(발췌): JavaScript, TypeScript에 이해가 깊으신 분
- 결손(발췌): [critical/experience_level/weak] 개발 경험 3년 이상 또는 이에 준하는 실력을 가지고 계신 분
- cap: role-defining critical gap
- 시스템 사유: JavaScript/TypeScript 이해가 깊다는 직접 매칭이 있고 frontend 도메인도 일치합니다. 하지만 3년 이상 수준의 경험이 약하게만 충족되며, 모바일 웹뷰와 A/B 테스트 같은 선호 요소는 부족합니다.

**B — Toss · Frontend Developer**
- 매칭(발췌): React; Next.js
- 결손(발췌): [critical/technical/missing] 웹 기반의 서비스를 운영한 경험이 있으신 분; [critical/technical/missing] 웹소켓, SSE
- cap: role-defining critical gaps x3
- 시스템 사유: Frontend 도메인과 직접 일치하고 React, Next.js, TypeScript 등 핵심 스택 매칭이 매우 강합니다. 다만 웹 기반 서비스 운영, 웹소켓/SSE, GitHub Action 같은 핵심 prerequisite gap이 있어 1위보다는 아래입니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 3. prop-devops_infra_security-01  ·  [adjacent_vs_primary]  ·  난이도 hard (hardness 7)  ·  ⚠ 모드 불일치
- **persona:** `devops_infra_security`  ·  résumé: `data/eval/resumes/devops_infra_security.md`
- **왜 라벨 가치가 있나:** 두 랭킹 모드(domain_fit_bt vs bt_primary)가 이 쌍을 **반대로** 정렬 → 라벨이 어느 정렬을 지지하는지 가름 · headline **fit과 BT(pairwise) 순서가 불일치** → fit 우선 vs 비교 우선 중 무엇이 맞는지 검증 · **주력(strong) 도메인이 인접(adjacent) 도메인보다 fit이 낮음** → 도메인 우선 원칙이 옳은지 검증

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Toss | Toss |
| 포지션 | Cloud Engineer | ML Backend Engineer |
| job_id | `toss-6677722003` | `toss-6600650003` |
| role_family | devops_infra | backend |
| domain | strong | adjacent |
| **fit (1~5)** | **2** | **3** |
| BT score | 0.841 | 0.6765 |
| rank · bt_primary | 3 | 4 |
| rank · fit_primary | 4 | 1 |
| rank · domain_fit_bt ⭐ | 3 | 4 |

**A — Toss · Cloud Engineer**
- 매칭(발췌): Kubernetes를 이용한 서비스 운영 및 배포 경험; 새로운 기술을 배우고, 이를 운영 환경에 적극적으로 적용하는 데 열정적인 분
- 결손(발췌): [critical/technical/missing] Python, Golang, C 중 최소 1개 이상의 숙련된 언어 사용; [critical/technical/missing] Rest API와 Database 트랜잭션에 대한 이해
- cap: role-defining critical gaps x3; role-defining required gap
- 시스템 사유: 주력 도메인과 직접 일치하며 Kubernetes 운영/배포 경험과 인프라 기술 적응성이 확인됩니다. 하지만 숙련 언어, REST API/DB 트랜잭션, OpenStack 핵심 컴포넌트 경험이 빠져 있어 핵심 prerequisite 충족도가 낮습니다.

**B — Toss · ML Backend Engineer**
- 매칭(발췌): 쿠버네티스 환경 위에서 서버를 배포하고 모니터링하며 안정적으로 운영한 경험이 있으면 좋아요.
- 결손(발췌): [critical/technical/weak] Python, Kotlin, Go 등 하나 이상의 언어로 서버를 개발하고 운영해 본 경험이 필요해요.
- cap: role-defining critical gap
- 시스템 사유: Kubernetes 기반 서버 운영 경험은 맞지만 role_family가 adjacent이고, 핵심 prerequisite인 서버 개발·운영 언어 역량이 직접적으로 강하게 확인되지는 않습니다. 도메인 적합성은 있으나 핵심 요구 충족이 제한적입니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 4. prop-devops_infra_security-02  ·  [adjacent_vs_primary]  ·  난이도 hard (hardness 7)  ·  ⚠ 모드 불일치
- **persona:** `devops_infra_security`  ·  résumé: `data/eval/resumes/devops_infra_security.md`
- **왜 라벨 가치가 있나:** 두 랭킹 모드(domain_fit_bt vs bt_primary)가 이 쌍을 **반대로** 정렬 → 라벨이 어느 정렬을 지지하는지 가름 · headline **fit과 BT(pairwise) 순서가 불일치** → fit 우선 vs 비교 우선 중 무엇이 맞는지 검증 · **주력(strong) 도메인이 인접(adjacent) 도메인보다 fit이 낮음** → 도메인 우선 원칙이 옳은지 검증

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Toss | Toss |
| 포지션 | AIOps Platform Engineer | ML Backend Engineer |
| job_id | `toss-7702581003` | `toss-6600650003` |
| role_family | devops_infra | backend |
| domain | strong | adjacent |
| **fit (1~5)** | **2** | **3** |
| BT score | 2.1004 | 0.6765 |
| rank · bt_primary | 1 | 4 |
| rank · fit_primary | 2 | 1 |
| rank · domain_fit_bt ⭐ | 1 | 4 |

**A — Toss · AIOps Platform Engineer**
- 매칭(발췌): 주력 개발 언어 1개 이상; Linux 시스템 관리 역량
- 결손(발췌): [critical/technical/missing] End-to-End 데이터 파이프라인 구축 경험; [critical/technical/missing] 시계열 DB 활용 경험
- cap: role-defining critical gaps x3
- 시스템 사유: 주력 도메인과 직접 일치하는 strong 정렬이고, Linux/인프라 개념/AIOps·모니터링/온콜 경험 등 핵심 직접 매칭이 여러 개 확인됩니다. 다만 데이터 파이프라인, 시계열 DB, 영문 기술문서가 핵심 갭이라 상위권이지만 완전한 적합은 아닙니다.

**B — Toss · ML Backend Engineer**
- 매칭(발췌): 쿠버네티스 환경 위에서 서버를 배포하고 모니터링하며 안정적으로 운영한 경험이 있으면 좋아요.
- 결손(발췌): [critical/technical/weak] Python, Kotlin, Go 등 하나 이상의 언어로 서버를 개발하고 운영해 본 경험이 필요해요.
- cap: role-defining critical gap
- 시스템 사유: Kubernetes 기반 서버 운영 경험은 맞지만 role_family가 adjacent이고, 핵심 prerequisite인 서버 개발·운영 언어 역량이 직접적으로 강하게 확인되지는 않습니다. 도메인 적합성은 있으나 핵심 요구 충족이 제한적입니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 5. prop-ai_ml_application-01  ·  [adjacent_vs_primary]  ·  난이도 hard (hardness 7)  ·  ⚠ 모드 불일치
- **persona:** `ai_ml_application`  ·  résumé: `data/eval/resumes/ai_ml_application.md`
- **왜 라벨 가치가 있나:** 두 랭킹 모드(domain_fit_bt vs bt_primary)가 이 쌍을 **반대로** 정렬 → 라벨이 어느 정렬을 지지하는지 가름 · headline **fit과 BT(pairwise) 순서가 불일치** → fit 우선 vs 비교 우선 중 무엇이 맞는지 검증 · **주력(strong) 도메인이 인접(adjacent) 도메인보다 fit이 낮음** → 도메인 우선 원칙이 옳은지 검증

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Toss | Toss |
| 포지션 | AI Engineer (Brain, AIOC) | Data Analytics Engineer |
| job_id | `toss-7503655003` | `toss-6308074003` |
| role_family | ml_ai | data |
| domain | strong | adjacent |
| **fit (1~5)** | **2** | **3** |
| BT score | 1.2749 | 0.8151 |
| rank · bt_primary | 2 | 3 |
| rank · fit_primary | 3 | 2 |
| rank · domain_fit_bt ⭐ | 2 | 3 |

**A — Toss · AI Engineer (Brain, AIOC)**
- 매칭(발췌): 데이터셋/지표/가드레일을 기반으로 품질을 체계적으로 끌어올릴 수 있는 능력; Multi-Agent, LLM, RAG, 멀티모달 모델 등 최신 AI 기술을 활용해 복잡한 비즈니스 문제를 해결한 경험
- 결손(발췌): [critical/technical/missing] 불확실성을 정량화하는 데 능숙한 역량; [critical/technical/missing] 다양한 모달의 데이터(텍스트, 이미지, 구조화 데이터)를 통합적으로 활용해 모델을 설계하고 실험해 본 경험
- cap: role-defining critical gaps x2
- 시스템 사유: ML/AI 도메인 정합성은 매우 강하고, 품질 개선 체계와 최신 AI 기술 활용 경험도 잘 맞습니다. 다만 불확실성 정량화와 멀티모달 통합 경험이 핵심 갭으로 남아 있어 같은 계열의 다른 Toss AI 역할보다 한 단계 아래입니다.

**B — Toss · Data Analytics Engineer**
- 매칭(발췌): SQL(상); Python(중) 정도의 기술 역량
- 결손(발췌): [critical/technical/missing] 데이터마트를 주도적으로 설계, 구축하고 운영한 경험
- cap: role-defining critical gap
- 시스템 사유: SQL과 Python 역량은 직접 맞지만, 데이터마트를 주도적으로 설계·구축·운영한 핵심 전제는 충족되지 않습니다. 인접 도메인이고 핵심 prerequisite 갭이 있어 상위 AI 역할들보다 확실히 뒤입니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 6. prop-junior_frontend-03  ·  [same_domain_close]  ·  난이도 hard (hardness 7)  ·  ⚠ 모드 불일치
- **persona:** `junior_frontend`  ·  résumé: `data/eval/resumes/junior_frontend.md`
- **왜 라벨 가치가 있나:** 두 랭킹 모드(domain_fit_bt vs bt_primary)가 이 쌍을 **반대로** 정렬 → 라벨이 어느 정렬을 지지하는지 가름 · headline **fit과 BT(pairwise) 순서가 불일치** → fit 우선 vs 비교 우선 중 무엇이 맞는지 검증 · 같은 직군·티어의 **근소한 fit 차이**가 올바른 순서인지

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Daangn | Toss |
| 포지션 | Software Engineer, Frontend \| 커머스 | Frontend Developer |
| job_id | `daangn-6692173003` | `toss-4076141003` |
| role_family | frontend | frontend |
| domain | strong | strong |
| **fit (1~5)** | **3** | **2** |
| BT score | 0.3367 | 1.0454 |
| rank · bt_primary | 5 | 2 |
| rank · fit_primary | 3 | 4 |
| rank · domain_fit_bt ⭐ | 3 | 4 |

**A — Daangn · Software Engineer, Frontend | 커머스**
- 매칭(발췌): TypeScript, React를 활용한 개발 경험이 있으신 분; 복잡한 상태 관리(Recoil, Zustand 등)를 다뤄보신 분
- 결손(발췌): [critical/technical/weak] 프론트엔드 기반 서비스 또는 프로젝트를 주도적으로 개발하고 운영한 경험이 있으신 분; [required/technical/missing] AI 도구(Claude Code, Cursor 등)를 적극 활용해 생산성을 높이고 비즈니스 임팩트에 집중하시는 분
- cap: role-defining critical gap; role-defining required gap
- 시스템 사유: TypeScript/React와 복잡한 상태 관리 경험은 강하게 맞지만, 프론트엔드 서비스를 주도적으로 개발·운영한 prerequisite가 약하고 운영 오너십 증거도 제한적입니다. 핵심 기술은 맞지만 prerequisite gap과 운영 경험 부족이 더 큽니다.

**B — Toss · Frontend Developer**
- 매칭(발췌): React; Next.js
- 결손(발췌): [critical/technical/missing] 웹 기반의 서비스를 운영한 경험이 있으신 분; [critical/technical/missing] 웹소켓, SSE
- cap: role-defining critical gaps x3
- 시스템 사유: Frontend 도메인과 직접 일치하고 React, Next.js, TypeScript 등 핵심 스택 매칭이 매우 강합니다. 다만 웹 기반 서비스 운영, 웹소켓/SSE, GitHub Action 같은 핵심 prerequisite gap이 있어 1위보다는 아래입니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 7. prop-junior_frontend-04  ·  [same_domain_close]  ·  난이도 hard (hardness 7)  ·  ⚠ 모드 불일치
- **persona:** `junior_frontend`  ·  résumé: `data/eval/resumes/junior_frontend.md`
- **왜 라벨 가치가 있나:** 두 랭킹 모드(domain_fit_bt vs bt_primary)가 이 쌍을 **반대로** 정렬 → 라벨이 어느 정렬을 지지하는지 가름 · headline **fit과 BT(pairwise) 순서가 불일치** → fit 우선 vs 비교 우선 중 무엇이 맞는지 검증 · 같은 직군·티어의 **근소한 fit 차이**가 올바른 순서인지

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Daangn | Toss |
| 포지션 | Software Engineer, Frontend \| 커뮤니티 (모임) | Frontend Developer |
| job_id | `daangn-7689088003` | `toss-4076130003` |
| role_family | frontend | frontend |
| domain | strong | strong |
| **fit (1~5)** | **3** | **2** |
| BT score | 0.6765 | 0.841 |
| rank · bt_primary | 4 | 3 |
| rank · fit_primary | 2 | 5 |
| rank · domain_fit_bt ⭐ | 2 | 5 |

**A — Daangn · Software Engineer, Frontend | 커뮤니티 (모임)**
- 매칭(발췌): JavaScript, TypeScript에 이해가 깊으신 분
- 결손(발췌): [critical/experience_level/weak] 개발 경험 3년 이상 또는 이에 준하는 실력을 가지고 계신 분
- cap: role-defining critical gap
- 시스템 사유: JavaScript/TypeScript 이해가 깊다는 직접 매칭이 있고 frontend 도메인도 일치합니다. 하지만 3년 이상 수준의 경험이 약하게만 충족되며, 모바일 웹뷰와 A/B 테스트 같은 선호 요소는 부족합니다.

**B — Toss · Frontend Developer**
- 매칭(발췌): React, TypeScript 기반으로 안정적인 서비스를 개발할 수 있는 분
- 결손(발췌): [required/experience_level/missing] 레거시 코드를 최신의 개발 환경에 맞게 개선한 경험; [required/technical/missing] 기존 소스 코드를 새로운 코드 베이스로 점진적으로 이관한 경험
- cap: role-defining required gaps x2
- 시스템 사유: React/TypeScript 기반 안정적 서비스 개발 역량이 직접 매칭되며 도메인 적합성도 높습니다. 그러나 레거시 개선과 점진적 이관 경험이라는 핵심 prerequisite gap이 있어 상위 두 개보다 FIT이 약합니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 8. prop-devops_infra_security-03  ·  [adjacent_vs_primary]  ·  난이도 hard (hardness 6)  ·  ⚠ 모드 불일치
- **persona:** `devops_infra_security`  ·  résumé: `data/eval/resumes/devops_infra_security.md`
- **왜 라벨 가치가 있나:** 두 랭킹 모드(domain_fit_bt vs bt_primary)가 이 쌍을 **반대로** 정렬 → 라벨이 어느 정렬을 지지하는지 가름 · headline **fit과 BT(pairwise) 순서가 불일치** → fit 우선 vs 비교 우선 중 무엇이 맞는지 검증 · **주력(strong) 도메인이 인접(adjacent) 도메인보다 fit이 낮음** → 도메인 우선 원칙이 옳은지 검증

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Daangn | Toss |
| 포지션 | Network Engineer \| 인프라 (네트워크, Cloud) | ML Backend Engineer |
| job_id | `daangn-5004587003` | `toss-6600650003` |
| role_family | devops_infra | backend |
| domain | strong | adjacent |
| **fit (1~5)** | **2** | **3** |
| BT score | 1.0454 | 0.6765 |
| rank · bt_primary | 2 | 4 |
| rank · fit_primary | 3 | 1 |
| rank · domain_fit_bt ⭐ | 2 | 4 |

**A — Daangn · Network Engineer | 인프라 (네트워크, Cloud)**
- 매칭(발췌): Kubernetes 환경에 대한 이해가 깊으신 분; 네트워크 모니터링 플랫폼 개발이나 자동화에 관심이 많으신 분(Go, Python 등)
- 결손(발췌): [critical/experience_level/missing] Network Engineering 실무 경험이 5년 이상이신 분; [critical/technical/weak] OSPF, BGP 등 Dynamic Routing Protocol에 대한 이해와 운영 경험이 있으신 분
- cap: role-defining critical gaps x5
- 시스템 사유: 주력 도메인과 직접 일치하고 Kubernetes, 네트워크 모니터링 자동화, IaC는 강하게 맞습니다. 그러나 5년 이상 실무, 라우팅 프로토콜, 고급 클라우드 네트워크, 패킷 분석이 핵심 갭/미충족이라 Toss AIOps보다 아래입니다.

**B — Toss · ML Backend Engineer**
- 매칭(발췌): 쿠버네티스 환경 위에서 서버를 배포하고 모니터링하며 안정적으로 운영한 경험이 있으면 좋아요.
- 결손(발췌): [critical/technical/weak] Python, Kotlin, Go 등 하나 이상의 언어로 서버를 개발하고 운영해 본 경험이 필요해요.
- cap: role-defining critical gap
- 시스템 사유: Kubernetes 기반 서버 운영 경험은 맞지만 role_family가 adjacent이고, 핵심 prerequisite인 서버 개발·운영 언어 역량이 직접적으로 강하게 확인되지는 않습니다. 도메인 적합성은 있으나 핵심 요구 충족이 제한적입니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 9. prop-junior_frontend-05  ·  [same_domain_close]  ·  난이도 hard (hardness 5)
- **persona:** `junior_frontend`  ·  résumé: `data/eval/resumes/junior_frontend.md`
- **왜 라벨 가치가 있나:** 같은 도메인에서 **경력연차(experience_level) 결손**이 순위를 가르는 것이 타당한지 · 같은 직군·티어의 **근소한 fit 차이**가 올바른 순서인지

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Daangn | Daangn |
| 포지션 | Software Engineer, Frontend \| 커뮤니티 (모임) | Software Engineer, Frontend \| 커머스 |
| job_id | `daangn-7689088003` | `daangn-6692173003` |
| role_family | frontend | frontend |
| domain | strong | strong |
| **fit (1~5)** | **3** | **3** |
| BT score | 0.6765 | 0.3367 |
| rank · bt_primary | 4 | 5 |
| rank · fit_primary | 2 | 3 |
| rank · domain_fit_bt ⭐ | 2 | 3 |

**A — Daangn · Software Engineer, Frontend | 커뮤니티 (모임)**
- 매칭(발췌): JavaScript, TypeScript에 이해가 깊으신 분
- 결손(발췌): [critical/experience_level/weak] 개발 경험 3년 이상 또는 이에 준하는 실력을 가지고 계신 분
- cap: role-defining critical gap
- 시스템 사유: JavaScript/TypeScript 이해가 깊다는 직접 매칭이 있고 frontend 도메인도 일치합니다. 하지만 3년 이상 수준의 경험이 약하게만 충족되며, 모바일 웹뷰와 A/B 테스트 같은 선호 요소는 부족합니다.

**B — Daangn · Software Engineer, Frontend | 커머스**
- 매칭(발췌): TypeScript, React를 활용한 개발 경험이 있으신 분; 복잡한 상태 관리(Recoil, Zustand 등)를 다뤄보신 분
- 결손(발췌): [critical/technical/weak] 프론트엔드 기반 서비스 또는 프로젝트를 주도적으로 개발하고 운영한 경험이 있으신 분; [required/technical/missing] AI 도구(Claude Code, Cursor 등)를 적극 활용해 생산성을 높이고 비즈니스 임팩트에 집중하시는 분
- cap: role-defining critical gap; role-defining required gap
- 시스템 사유: TypeScript/React와 복잡한 상태 관리 경험은 강하게 맞지만, 프론트엔드 서비스를 주도적으로 개발·운영한 prerequisite가 약하고 운영 오너십 증거도 제한적입니다. 핵심 기술은 맞지만 prerequisite gap과 운영 경험 부족이 더 큽니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 10. prop-junior_frontend-06  ·  [same_domain_close]  ·  난이도 hard (hardness 5)
- **persona:** `junior_frontend`  ·  résumé: `data/eval/resumes/junior_frontend.md`
- **왜 라벨 가치가 있나:** 같은 도메인에서 **경력연차(experience_level) 결손**이 순위를 가르는 것이 타당한지 · 같은 직군·티어의 **근소한 fit 차이**가 올바른 순서인지

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Toss | Toss |
| 포지션 | Frontend Developer | Frontend Developer |
| job_id | `toss-4076141003` | `toss-4076130003` |
| role_family | frontend | frontend |
| domain | strong | strong |
| **fit (1~5)** | **2** | **2** |
| BT score | 1.0454 | 0.841 |
| rank · bt_primary | 2 | 3 |
| rank · fit_primary | 4 | 5 |
| rank · domain_fit_bt ⭐ | 4 | 5 |

**A — Toss · Frontend Developer**
- 매칭(발췌): React; Next.js
- 결손(발췌): [critical/technical/missing] 웹 기반의 서비스를 운영한 경험이 있으신 분; [critical/technical/missing] 웹소켓, SSE
- cap: role-defining critical gaps x3
- 시스템 사유: Frontend 도메인과 직접 일치하고 React, Next.js, TypeScript 등 핵심 스택 매칭이 매우 강합니다. 다만 웹 기반 서비스 운영, 웹소켓/SSE, GitHub Action 같은 핵심 prerequisite gap이 있어 1위보다는 아래입니다.

**B — Toss · Frontend Developer**
- 매칭(발췌): React, TypeScript 기반으로 안정적인 서비스를 개발할 수 있는 분
- 결손(발췌): [required/experience_level/missing] 레거시 코드를 최신의 개발 환경에 맞게 개선한 경험; [required/technical/missing] 기존 소스 코드를 새로운 코드 베이스로 점진적으로 이관한 경험
- cap: role-defining required gaps x2
- 시스템 사유: React/TypeScript 기반 안정적 서비스 개발 역량이 직접 매칭되며 도메인 적합성도 높습니다. 그러나 레거시 개선과 점진적 이관 경험이라는 핵심 prerequisite gap이 있어 상위 두 개보다 FIT이 약합니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 11. prop-ai_ml_application-02  ·  [domain_transfer]  ·  난이도 hard (hardness 4)  ·  ⚠ 모드 불일치
- **persona:** `ai_ml_application`  ·  résumé: `data/eval/resumes/ai_ml_application.md`
- **왜 라벨 가치가 있나:** 두 랭킹 모드(domain_fit_bt vs bt_primary)가 이 쌍을 **반대로** 정렬 → 라벨이 어느 정렬을 지지하는지 가름 · 서로 다른 엔지니어링 직군 간 비교(도메인 전이)

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Daangn | Toss |
| 포지션 | Data Analytics Engineer \| 테크코어 (데이터 가치화) | AIOps Platform Engineer |
| job_id | `daangn-7507320003` | `toss-7702581003` |
| role_family | data | devops_infra |
| domain | adjacent | weak |
| **fit (1~5)** | **2** | **2** |
| BT score | 0.3213 | 0.5211 |
| rank · bt_primary | 5 | 4 |
| rank · fit_primary | 4 | 5 |
| rank · domain_fit_bt ⭐ | 4 | 5 |

**A — Daangn · Data Analytics Engineer | 테크코어 (데이터 가치화)**
- 매칭(발췌): SQL, Python을 활용해 데이터를 분석하고 처리할 수 있으신 분
- 결손(발췌): [critical/technical/missing] 데이터 모델링/ETL/데이터 마트 구축 경험이 있으신 분; [critical/technical/missing] 단일 모델 수준이 아닌, 데이터 파이프라인 전반의 데이터 품질 관리, 정합성 검증 경험이 있으신 분
- cap: role-defining critical gaps x2
- 시스템 사유: SQL/Python 기반 데이터 처리 역량은 맞지만, 데이터 모델링·ETL·데이터마트·품질관리 같은 핵심 요구가 여러 개 비어 있습니다. 협업 요구까지 포함해 prerequisite 갭이 커서 Toss 데이터 역할보다도 약합니다.

**B — Toss · AIOps Platform Engineer**
- 매칭(발췌): 주력 개발 언어 1개 이상; 검색 엔진 활용 경험
- 결손(발췌): [critical/experience_level/missing] 데이터 파이프라인/플랫폼 엔지니어링/SRE/인프라 엔지니어링 경력 3년 이상; [critical/technical/weak] 대규모 메트릭·로그 처리 경험
- cap: role-defining critical gaps x4
- 시스템 사유: 주력 언어, 검색 엔진 활용, 영문 기술 문서 적용, 프롬프트 엔지니어링은 맞지만, 3년 이상 플랫폼/SRE 경력과 Linux, 대규모 운영 경험이 핵심 갭입니다. 약한 도메인 정합성에 비해 필수 인프라 prerequisite 부족이 큽니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 12. prop-devops_infra_security-04  ·  [same_domain_close]  ·  난이도 hard (hardness 4)
- **persona:** `devops_infra_security`  ·  résumé: `data/eval/resumes/devops_infra_security.md`
- **왜 라벨 가치가 있나:** 같은 도메인에서 **경력연차(experience_level) 결손**이 순위를 가르는 것이 타당한지 · 같은 직군·티어의 **근소한 fit 차이**가 올바른 순서인지

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Daangn | Toss |
| 포지션 | Network Engineer \| 인프라 (네트워크, Cloud) | Cloud Engineer |
| job_id | `daangn-5004587003` | `toss-6677722003` |
| role_family | devops_infra | devops_infra |
| domain | strong | strong |
| **fit (1~5)** | **2** | **2** |
| BT score | 1.0454 | 0.841 |
| rank · bt_primary | 2 | 3 |
| rank · fit_primary | 3 | 4 |
| rank · domain_fit_bt ⭐ | 2 | 3 |

**A — Daangn · Network Engineer | 인프라 (네트워크, Cloud)**
- 매칭(발췌): Kubernetes 환경에 대한 이해가 깊으신 분; 네트워크 모니터링 플랫폼 개발이나 자동화에 관심이 많으신 분(Go, Python 등)
- 결손(발췌): [critical/experience_level/missing] Network Engineering 실무 경험이 5년 이상이신 분; [critical/technical/weak] OSPF, BGP 등 Dynamic Routing Protocol에 대한 이해와 운영 경험이 있으신 분
- cap: role-defining critical gaps x5
- 시스템 사유: 주력 도메인과 직접 일치하고 Kubernetes, 네트워크 모니터링 자동화, IaC는 강하게 맞습니다. 그러나 5년 이상 실무, 라우팅 프로토콜, 고급 클라우드 네트워크, 패킷 분석이 핵심 갭/미충족이라 Toss AIOps보다 아래입니다.

**B — Toss · Cloud Engineer**
- 매칭(발췌): Kubernetes를 이용한 서비스 운영 및 배포 경험; 새로운 기술을 배우고, 이를 운영 환경에 적극적으로 적용하는 데 열정적인 분
- 결손(발췌): [critical/technical/missing] Python, Golang, C 중 최소 1개 이상의 숙련된 언어 사용; [critical/technical/missing] Rest API와 Database 트랜잭션에 대한 이해
- cap: role-defining critical gaps x3; role-defining required gap
- 시스템 사유: 주력 도메인과 직접 일치하며 Kubernetes 운영/배포 경험과 인프라 기술 적응성이 확인됩니다. 하지만 숙련 언어, REST API/DB 트랜잭션, OpenStack 핵심 컴포넌트 경험이 빠져 있어 핵심 prerequisite 충족도가 낮습니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 13. prop-devops_infra_security-05  ·  [same_domain_close]  ·  난이도 hard (hardness 4)
- **persona:** `devops_infra_security`  ·  résumé: `data/eval/resumes/devops_infra_security.md`
- **왜 라벨 가치가 있나:** 같은 도메인에서 **경력연차(experience_level) 결손**이 순위를 가르는 것이 타당한지 · 같은 직군·티어의 **근소한 fit 차이**가 올바른 순서인지

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Toss | Daangn |
| 포지션 | AIOps Platform Engineer | Network Engineer \| 인프라 (네트워크, Cloud) |
| job_id | `toss-7702581003` | `daangn-5004587003` |
| role_family | devops_infra | devops_infra |
| domain | strong | strong |
| **fit (1~5)** | **2** | **2** |
| BT score | 2.1004 | 1.0454 |
| rank · bt_primary | 1 | 2 |
| rank · fit_primary | 2 | 3 |
| rank · domain_fit_bt ⭐ | 1 | 2 |

**A — Toss · AIOps Platform Engineer**
- 매칭(발췌): 주력 개발 언어 1개 이상; Linux 시스템 관리 역량
- 결손(발췌): [critical/technical/missing] End-to-End 데이터 파이프라인 구축 경험; [critical/technical/missing] 시계열 DB 활용 경험
- cap: role-defining critical gaps x3
- 시스템 사유: 주력 도메인과 직접 일치하는 strong 정렬이고, Linux/인프라 개념/AIOps·모니터링/온콜 경험 등 핵심 직접 매칭이 여러 개 확인됩니다. 다만 데이터 파이프라인, 시계열 DB, 영문 기술문서가 핵심 갭이라 상위권이지만 완전한 적합은 아닙니다.

**B — Daangn · Network Engineer | 인프라 (네트워크, Cloud)**
- 매칭(발췌): Kubernetes 환경에 대한 이해가 깊으신 분; 네트워크 모니터링 플랫폼 개발이나 자동화에 관심이 많으신 분(Go, Python 등)
- 결손(발췌): [critical/experience_level/missing] Network Engineering 실무 경험이 5년 이상이신 분; [critical/technical/weak] OSPF, BGP 등 Dynamic Routing Protocol에 대한 이해와 운영 경험이 있으신 분
- cap: role-defining critical gaps x5
- 시스템 사유: 주력 도메인과 직접 일치하고 Kubernetes, 네트워크 모니터링 자동화, IaC는 강하게 맞습니다. 그러나 5년 이상 실무, 라우팅 프로토콜, 고급 클라우드 네트워크, 패킷 분석이 핵심 갭/미충족이라 Toss AIOps보다 아래입니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 14. prop-backend_platform-01  ·  [same_domain_close]  ·  난이도 hard (hardness 4)
- **persona:** `backend_platform`  ·  résumé: `data/eval/resumes/backend_platform.md`
- **왜 라벨 가치가 있나:** 같은 도메인에서 **경력연차(experience_level) 결손**이 순위를 가르는 것이 타당한지 · 같은 직군·티어의 **근소한 fit 차이**가 올바른 순서인지

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Daangn | Toss |
| 포지션 | Software Engineer, Backend \| 광고 | ML Backend Engineer |
| job_id | `daangn-6640363003` | `toss-6600650003` |
| role_family | backend | backend |
| domain | strong | strong |
| **fit (1~5)** | **3** | **3** |
| BT score | 1.2749 | 0.8151 |
| rank · bt_primary | 2 | 3 |
| rank · fit_primary | 2 | 3 |
| rank · domain_fit_bt ⭐ | 2 | 3 |

**A — Daangn · Software Engineer, Backend | 광고**
- 매칭(발췌): 하나 이상의 프로그래밍 언어에 능숙하신 분; 스스로 데이터베이스를 설계하고 개발/운영해 본 경험이 있으신 분
- 결손(발췌): [critical/experience_level/weak] 5년 이상의 서버 개발 경험, 혹은 이에 준하는 역량을 보유하신 분
- cap: role-defining critical gap
- 시스템 사유: 백엔드 도메인 정합성이 높고, 언어 숙련·DB 설계/운영·마이크로서비스/REST/gRPC·클라우드 운영이 직접 맞습니다. 다만 5년 이상 서버 개발 경력이라는 핵심 prerequisite가 약하게만 남아 있어 1위보다는 아래입니다.

**B — Toss · ML Backend Engineer**
- 매칭(발췌): Python, Kotlin, Go 등 하나 이상의 언어로 서버를 개발하고 운영해 본 경험이 필요해요.; 크고 복잡한 문제를 소프트웨어 기술로 해결하거나, 혹은 서비스나 제품으로 비즈니스 임팩트를 낸 경험이 있으면 좋아요.
- 결손(발췌): [critical/technical/weak] 견고한 서비스 아키텍처를 설계하고 안정적인 구조의 코드를 구현할 수 있는 역량이 필요해요.
- cap: role-defining critical gap
- 시스템 사유: 백엔드 도메인과 직접 일치하고 서버 개발 운영 경험, 복잡한 문제 해결/비즈니스 임팩트 경험이 맞습니다. 그러나 견고한 서비스 아키텍처 설계 역량이 core prerequisite gap으로 남아 있어 상위 두 개보다 약합니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 15. prop-ai_ml_application-03  ·  [adjacent_vs_primary]  ·  난이도 hard (hardness 3)
- **persona:** `ai_ml_application`  ·  résumé: `data/eval/resumes/ai_ml_application.md`
- **왜 라벨 가치가 있나:** **주력(strong) 도메인이 인접(adjacent) 도메인보다 fit이 낮음** → 도메인 우선 원칙이 옳은지 검증

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Toss | Toss |
| 포지션 | AI Engineer (Commerce) | Data Analytics Engineer |
| job_id | `toss-6545457003` | `toss-6308074003` |
| role_family | ml_ai | data |
| domain | strong | adjacent |
| **fit (1~5)** | **3** | **3** |
| BT score | 2.0676 | 0.8151 |
| rank · bt_primary | 1 | 3 |
| rank · fit_primary | 1 | 2 |
| rank · domain_fit_bt ⭐ | 1 | 3 |

**A — Toss · AI Engineer (Commerce)**
- 매칭(발췌): 비즈니스 요구사항을 이해하고, 최신 AI 기술(LLM/RAG, LMM 등)을 포함한 ML 기술로 문제를 해결한 경험; PyTorch, Hugging Face Transformers, LangChain 등 최신 AI 생태계에 익숙해야 해요.
- 결손(발췌): [critical/technical/missing] 다양한 형태의 데이터 (텍스트, 이미지, 음성, 구조화 데이터)를 통합적으로 활용해 모델을 설계하고 빠르게 응용해본 …
- cap: role-defining critical gap
- 시스템 사유: 가장 강한 도메인 정합성과 함께 핵심 요구사항 다수가 직접 충족되어 있습니다. 다중 데이터 통합 경험이라는 핵심 갭은 있지만, LLM/RAG·PyTorch·Transformers·LangChain 기반의 문제 해결과 전체 주도 경험이 명확해 전체적으로 가장 잘 맞습니다.

**B — Toss · Data Analytics Engineer**
- 매칭(발췌): SQL(상); Python(중) 정도의 기술 역량
- 결손(발췌): [critical/technical/missing] 데이터마트를 주도적으로 설계, 구축하고 운영한 경험
- cap: role-defining critical gap
- 시스템 사유: SQL과 Python 역량은 직접 맞지만, 데이터마트를 주도적으로 설계·구축·운영한 핵심 전제는 충족되지 않습니다. 인접 도메인이고 핵심 prerequisite 갭이 있어 상위 AI 역할들보다 확실히 뒤입니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 16. prop-backend_platform-02  ·  [seniority_gap]  ·  난이도 hard (hardness 3)
- **persona:** `backend_platform`  ·  résumé: `data/eval/resumes/backend_platform.md`
- **왜 라벨 가치가 있나:** 같은 도메인에서 **경력연차(experience_level) 결손**이 순위를 가르는 것이 타당한지

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Toss | Daangn |
| 포지션 | Server Developer (수신) | Software Engineer, Backend \| 광고 |
| job_id | `toss-6613962003` | `daangn-6640363003` |
| role_family | backend | backend |
| domain | strong | strong |
| **fit (1~5)** | **4** | **3** |
| BT score | 2.0676 | 1.2749 |
| rank · bt_primary | 1 | 2 |
| rank · fit_primary | 1 | 2 |
| rank · domain_fit_bt ⭐ | 1 | 2 |

**A — Toss · Server Developer (수신)**
- 매칭(발췌): Kotlin과 Spring 기반의 MSA 환경; 트랜잭션 안정성
- 결손(발췌): _(핵심 결손 없음)_
- cap: no cap
- 시스템 사유: 가장 많은 핵심 요건이 직접 일치하고 core_prerequisite_gaps가 없어 FIT가 가장 좋습니다. Kotlin/Spring, 트랜잭션 안정성, RDB 설계·운영, 운영 관점 품질 개선이 모두 강하게 맞습니다.

**B — Daangn · Software Engineer, Backend | 광고**
- 매칭(발췌): 하나 이상의 프로그래밍 언어에 능숙하신 분; 스스로 데이터베이스를 설계하고 개발/운영해 본 경험이 있으신 분
- 결손(발췌): [critical/experience_level/weak] 5년 이상의 서버 개발 경험, 혹은 이에 준하는 역량을 보유하신 분
- cap: role-defining critical gap
- 시스템 사유: 백엔드 도메인 정합성이 높고, 언어 숙련·DB 설계/운영·마이크로서비스/REST/gRPC·클라우드 운영이 직접 맞습니다. 다만 5년 이상 서버 개발 경력이라는 핵심 prerequisite가 약하게만 남아 있어 1위보다는 아래입니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 17. prop-backend_platform-03  ·  [seniority_gap]  ·  난이도 hard (hardness 3)
- **persona:** `backend_platform`  ·  résumé: `data/eval/resumes/backend_platform.md`
- **왜 라벨 가치가 있나:** 같은 도메인에서 **경력연차(experience_level) 결손**이 순위를 가르는 것이 타당한지

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Toss | Daangn |
| 포지션 | AIOps Platform Engineer | Network Engineer \| 인프라 (네트워크, Cloud) |
| job_id | `toss-7702581003` | `daangn-5004587003` |
| role_family | devops_infra | devops_infra |
| domain | adjacent | adjacent |
| **fit (1~5)** | **2** | **1** |
| BT score | 0.5211 | 0.3213 |
| rank · bt_primary | 4 | 5 |
| rank · fit_primary | 4 | 5 |
| rank · domain_fit_bt ⭐ | 4 | 5 |

**A — Toss · AIOps Platform Engineer**
- 매칭(발췌): 주력 개발 언어 1개 이상
- 결손(발췌): [critical/technical/missing] 오픈소스 기반 수집·분석 플랫폼을 직접 설계·구축·운영한 경험; [critical/technical/missing] 시계열 DB 활용 경험
- cap: role-defining critical gaps x5
- 시스템 사유: 주력 언어 경험은 맞지만, 오픈소스 수집·분석 플랫폼 설계/운영, 시계열 DB, 검색 엔진, 영문 기술문서 적용 등 핵심 prerequisite가 다수 비어 있습니다. 인접 도메인이라도 핵심 결손이 커서 하위입니다.

**B — Daangn · Network Engineer | 인프라 (네트워크, Cloud)**
- 매칭(발췌): _(강한 직접 매칭 없음)_
- 결손(발췌): [critical/experience_level/missing] Network Engineering 실무 경험이 5년 이상이신 분; [critical/technical/missing] OSPF, BGP 등 Dynamic Routing Protocol에 대한 이해와 운영 경험이 있으신 분
- cap: role-defining critical gaps x4
- 시스템 사유: 네트워크 엔지니어 실무, 라우팅 프로토콜, 방화벽/SASE, 패킷 분석 등 핵심 prerequisite가 대부분 미충족입니다. 인프라 인접성만 있고 직접적인 네트워크 운영 증거가 없어 낮은 적합도입니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 18. prop-devops_infra_security-06  ·  [same_domain_close]  ·  난이도 hard (hardness 3)
- **persona:** `devops_infra_security`  ·  résumé: `data/eval/resumes/devops_infra_security.md`
- **왜 라벨 가치가 있나:** 같은 직군·티어의 **근소한 fit 차이**가 올바른 순서인지

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Toss | Toss |
| 포지션 | AIOps Platform Engineer | Cloud Engineer |
| job_id | `toss-7702581003` | `toss-6677722003` |
| role_family | devops_infra | devops_infra |
| domain | strong | strong |
| **fit (1~5)** | **2** | **2** |
| BT score | 2.1004 | 0.841 |
| rank · bt_primary | 1 | 3 |
| rank · fit_primary | 2 | 4 |
| rank · domain_fit_bt ⭐ | 1 | 3 |

**A — Toss · AIOps Platform Engineer**
- 매칭(발췌): 주력 개발 언어 1개 이상; Linux 시스템 관리 역량
- 결손(발췌): [critical/technical/missing] End-to-End 데이터 파이프라인 구축 경험; [critical/technical/missing] 시계열 DB 활용 경험
- cap: role-defining critical gaps x3
- 시스템 사유: 주력 도메인과 직접 일치하는 strong 정렬이고, Linux/인프라 개념/AIOps·모니터링/온콜 경험 등 핵심 직접 매칭이 여러 개 확인됩니다. 다만 데이터 파이프라인, 시계열 DB, 영문 기술문서가 핵심 갭이라 상위권이지만 완전한 적합은 아닙니다.

**B — Toss · Cloud Engineer**
- 매칭(발췌): Kubernetes를 이용한 서비스 운영 및 배포 경험; 새로운 기술을 배우고, 이를 운영 환경에 적극적으로 적용하는 데 열정적인 분
- 결손(발췌): [critical/technical/missing] Python, Golang, C 중 최소 1개 이상의 숙련된 언어 사용; [critical/technical/missing] Rest API와 Database 트랜잭션에 대한 이해
- cap: role-defining critical gaps x3; role-defining required gap
- 시스템 사유: 주력 도메인과 직접 일치하며 Kubernetes 운영/배포 경험과 인프라 기술 적응성이 확인됩니다. 하지만 숙련 언어, REST API/DB 트랜잭션, OpenStack 핵심 컴포넌트 경험이 빠져 있어 핵심 prerequisite 충족도가 낮습니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 19. prop-ai_ml_application-06  ·  [same_domain_close]  ·  난이도 medium (hardness 2)
- **persona:** `ai_ml_application`  ·  résumé: `data/eval/resumes/ai_ml_application.md`
- **왜 라벨 가치가 있나:** 같은 직군·티어의 **근소한 fit 차이**가 올바른 순서인지

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Toss | Toss |
| 포지션 | AI Engineer (Commerce) | AI Engineer (Brain, AIOC) |
| job_id | `toss-6545457003` | `toss-7503655003` |
| role_family | ml_ai | ml_ai |
| domain | strong | strong |
| **fit (1~5)** | **3** | **2** |
| BT score | 2.0676 | 1.2749 |
| rank · bt_primary | 1 | 2 |
| rank · fit_primary | 1 | 3 |
| rank · domain_fit_bt ⭐ | 1 | 2 |

**A — Toss · AI Engineer (Commerce)**
- 매칭(발췌): 비즈니스 요구사항을 이해하고, 최신 AI 기술(LLM/RAG, LMM 등)을 포함한 ML 기술로 문제를 해결한 경험; PyTorch, Hugging Face Transformers, LangChain 등 최신 AI 생태계에 익숙해야 해요.
- 결손(발췌): [critical/technical/missing] 다양한 형태의 데이터 (텍스트, 이미지, 음성, 구조화 데이터)를 통합적으로 활용해 모델을 설계하고 빠르게 응용해본 …
- cap: role-defining critical gap
- 시스템 사유: 가장 강한 도메인 정합성과 함께 핵심 요구사항 다수가 직접 충족되어 있습니다. 다중 데이터 통합 경험이라는 핵심 갭은 있지만, LLM/RAG·PyTorch·Transformers·LangChain 기반의 문제 해결과 전체 주도 경험이 명확해 전체적으로 가장 잘 맞습니다.

**B — Toss · AI Engineer (Brain, AIOC)**
- 매칭(발췌): 데이터셋/지표/가드레일을 기반으로 품질을 체계적으로 끌어올릴 수 있는 능력; Multi-Agent, LLM, RAG, 멀티모달 모델 등 최신 AI 기술을 활용해 복잡한 비즈니스 문제를 해결한 경험
- 결손(발췌): [critical/technical/missing] 불확실성을 정량화하는 데 능숙한 역량; [critical/technical/missing] 다양한 모달의 데이터(텍스트, 이미지, 구조화 데이터)를 통합적으로 활용해 모델을 설계하고 실험해 본 경험
- cap: role-defining critical gaps x2
- 시스템 사유: ML/AI 도메인 정합성은 매우 강하고, 품질 개선 체계와 최신 AI 기술 활용 경험도 잘 맞습니다. 다만 불확실성 정량화와 멀티모달 통합 경험이 핵심 갭으로 남아 있어 같은 계열의 다른 Toss AI 역할보다 한 단계 아래입니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## 20. prop-backend_platform-04  ·  [same_domain_close]  ·  난이도 medium (hardness 2)
- **persona:** `backend_platform`  ·  résumé: `data/eval/resumes/backend_platform.md`
- **왜 라벨 가치가 있나:** 같은 직군·티어의 **근소한 fit 차이**가 올바른 순서인지

| 항목 | **A** (시스템이 위에 둔 쪽) | **B** |
|---|---|---|
| 회사 | Toss | Toss |
| 포지션 | Server Developer (수신) | ML Backend Engineer |
| job_id | `toss-6613962003` | `toss-6600650003` |
| role_family | backend | backend |
| domain | strong | strong |
| **fit (1~5)** | **4** | **3** |
| BT score | 2.0676 | 0.8151 |
| rank · bt_primary | 1 | 3 |
| rank · fit_primary | 1 | 3 |
| rank · domain_fit_bt ⭐ | 1 | 3 |

**A — Toss · Server Developer (수신)**
- 매칭(발췌): Kotlin과 Spring 기반의 MSA 환경; 트랜잭션 안정성
- 결손(발췌): _(핵심 결손 없음)_
- cap: no cap
- 시스템 사유: 가장 많은 핵심 요건이 직접 일치하고 core_prerequisite_gaps가 없어 FIT가 가장 좋습니다. Kotlin/Spring, 트랜잭션 안정성, RDB 설계·운영, 운영 관점 품질 개선이 모두 강하게 맞습니다.

**B — Toss · ML Backend Engineer**
- 매칭(발췌): Python, Kotlin, Go 등 하나 이상의 언어로 서버를 개발하고 운영해 본 경험이 필요해요.; 크고 복잡한 문제를 소프트웨어 기술로 해결하거나, 혹은 서비스나 제품으로 비즈니스 임팩트를 낸 경험이 있으면 좋아요.
- 결손(발췌): [critical/technical/weak] 견고한 서비스 아키텍처를 설계하고 안정적인 구조의 코드를 구현할 수 있는 역량이 필요해요.
- cap: role-defining critical gap
- 시스템 사유: 백엔드 도메인과 직접 일치하고 서버 개발 운영 경험, 복잡한 문제 해결/비즈니스 임팩트 경험이 맞습니다. 그러나 견고한 서비스 아키텍처 설계 역량이 core prerequisite gap으로 남아 있어 상위 두 개보다 약합니다.

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)
