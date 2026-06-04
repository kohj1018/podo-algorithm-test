# dedup 검증용 타깃 페어 세트 (experimental dedup_required_preferred)

> 실제 캐시 공고만 사용했고 **새 쌍을 만들지 않았습니다**. LLM 미호출·신규 수집 없음. expected_winner/label_reason/confidence 는 **비어 있으며 직접 채워야** 합니다. dedup은 여전히 **실험 플래그**이며 기본값이 아닙니다. fit은 1~5이며 합격확률/퍼센트가 아닙니다.

## 데이터 한계 (중요)
- 현재 캐시 산출물 24개 (persona,job) 인스턴스 중 required/preferred 중복이 탐지되는 공고는 toss-4076130003(junior_frontend) **단 1개**뿐입니다. backend·devops·ai_ml·기타 frontend 공고에는 탐지되는 중복이 없습니다. 따라서 dedup의 '이득'은 이 한 공고로만 검증 가능하며, 다른 페르소나 쌍은 dedup이 **무해(no-op)** 함을 확인하는 통제(control) 역할만 합니다. 새 중복 사례를 만들려면 더 많은 공고를 수집/구조화해야 하나, 이는 LLM 호출이 필요하므로 이번 범위에서 제외했습니다(가짜 쌍 생성 금지).
- 검증 쌍 11개 중 **실제 중복 탐지에 걸리는 쌍은 5개**(모두 toss-4076130003). 나머지는 통제(무해성) 쌍입니다.
- 페르소나 분포: {'junior_frontend': 5, 'backend_platform': 2, 'devops_infra_security': 2, 'ai_ml_application': 2}
- 검증 역할 분포: {'control_no_dups': 6, 'winner_change': 3, 'fit_change_no_winner': 2}

## 검증 역할(validation_role) 의미
- **winner_change**: dedup이 domain_fit_bt 승자를 바꿈 → 그 변화가 옳은지 사람이 검증.
- **fit_change_no_winner**: dedup이 fit은 바꾸지만 승자는 유지 → 순위 안정성 검증.
- **detected_no_effect**: 중복이 탐지됐으나 cap/순위 영향 없음 → '탐지=무해' 검증.
- **control_no_dups**: 중복 전혀 없음 → dedup이 baseline과 동일해야 함(무해성 통제).

---
## dval-junior_frontend-01  ·  [same_domain_close]  ·  역할: **winner_change**
- persona: `junior_frontend`  ·  중복 탐지 포함: 예
- baseline 승자: **A**  ·  dedup 승자(다를 때만): **B**
- (참고) golden_pairs_20 기존 라벨: B_better
- 왜 검증에 유용한가: dedup이 이 쌍의 domain_fit_bt 승자를 바꿈 — 사람 라벨로 그 변화가 옳은지 검증.

| 항목 | **A** (baseline 상위) | **B** |
|---|---|---|
| 회사·포지션 | Daangn · Software Engineer, Frontend \| 커머스 | Toss · Frontend Developer |
| job_id | `daangn-6692173003` | `toss-4076130003` |
| role_family / domain | frontend / strong | frontend / strong |
| fit baseline→dedup | 3→3 | 2→3 |
| rank baseline→dedup (domain_fit_bt) | 3→4 | 5→2 |
- **B 탐지 중복:** required(required/missing) `레거시 코드를 최신의 개발 환경에 맞게 개선한 경험…` ↔ preferred `…있으면 좋아요` · downgraded_required_for_cap (preferred twin exists) · cap 제외=True
- **B 탐지 중복:** required(required/adjacent) `잘 모르던 기술 스택을 빠르게 학습해서 개발해나간 경험…` ↔ preferred `…있으면 좋아요` · downgraded_required_for_cap (preferred twin exists) · cap 제외=True

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## dval-junior_frontend-02  ·  [same_domain_close]  ·  역할: **winner_change**
- persona: `junior_frontend`  ·  중복 탐지 포함: 예
- baseline 승자: **A**  ·  dedup 승자(다를 때만): **B**
- (참고) golden_pairs_20 기존 라벨: B_better
- 왜 검증에 유용한가: dedup이 이 쌍의 domain_fit_bt 승자를 바꿈 — 사람 라벨로 그 변화가 옳은지 검증.

| 항목 | **A** (baseline 상위) | **B** |
|---|---|---|
| 회사·포지션 | Daangn · Software Engineer, Frontend \| 커뮤니티 (모임) | Toss · Frontend Developer |
| job_id | `daangn-7689088003` | `toss-4076130003` |
| role_family / domain | frontend / strong | frontend / strong |
| fit baseline→dedup | 3→3 | 2→3 |
| rank baseline→dedup (domain_fit_bt) | 2→3 | 5→2 |
- **B 탐지 중복:** required(required/missing) `레거시 코드를 최신의 개발 환경에 맞게 개선한 경험…` ↔ preferred `…있으면 좋아요` · downgraded_required_for_cap (preferred twin exists) · cap 제외=True
- **B 탐지 중복:** required(required/adjacent) `잘 모르던 기술 스택을 빠르게 학습해서 개발해나간 경험…` ↔ preferred `…있으면 좋아요` · downgraded_required_for_cap (preferred twin exists) · cap 제외=True

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## dval-junior_frontend-03  ·  [same_domain_close]  ·  역할: **winner_change**
- persona: `junior_frontend`  ·  중복 탐지 포함: 예
- baseline 승자: **A**  ·  dedup 승자(다를 때만): **B**
- (참고) golden_pairs_20 기존 라벨: B_better
- 왜 검증에 유용한가: dedup이 이 쌍의 domain_fit_bt 승자를 바꿈 — 사람 라벨로 그 변화가 옳은지 검증.

| 항목 | **A** (baseline 상위) | **B** |
|---|---|---|
| 회사·포지션 | Toss · Frontend Developer | Toss · Frontend Developer |
| job_id | `toss-4076141003` | `toss-4076130003` |
| role_family / domain | frontend / strong | frontend / strong |
| fit baseline→dedup | 2→2 | 2→3 |
| rank baseline→dedup (domain_fit_bt) | 4→5 | 5→2 |
- **B 탐지 중복:** required(required/missing) `레거시 코드를 최신의 개발 환경에 맞게 개선한 경험…` ↔ preferred `…있으면 좋아요` · downgraded_required_for_cap (preferred twin exists) · cap 제외=True
- **B 탐지 중복:** required(required/adjacent) `잘 모르던 기술 스택을 빠르게 학습해서 개발해나간 경험…` ↔ preferred `…있으면 좋아요` · downgraded_required_for_cap (preferred twin exists) · cap 제외=True

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## dval-junior_frontend-04  ·  [same_domain_close]  ·  역할: **fit_change_no_winner**
- persona: `junior_frontend`  ·  중복 탐지 포함: 예
- baseline 승자: **A**  ·  dedup 승자(다를 때만): **동일**
- 왜 검증에 유용한가: dedup이 한 공고의 fit을 바꾸지만 승자는 불변 — fit 상향이 순위 안정성을 깨지 않는지 검증.

| 항목 | **A** (baseline 상위) | **B** |
|---|---|---|
| 회사·포지션 | Toss · Frontend Developer | Toss · Frontend Developer |
| job_id | `toss-5311744003` | `toss-4076130003` |
| role_family / domain | frontend / strong | frontend / strong |
| fit baseline→dedup | 5→5 | 2→3 |
| rank baseline→dedup (domain_fit_bt) | 1→1 | 5→2 |
- **B 탐지 중복:** required(required/missing) `레거시 코드를 최신의 개발 환경에 맞게 개선한 경험…` ↔ preferred `…있으면 좋아요` · downgraded_required_for_cap (preferred twin exists) · cap 제외=True
- **B 탐지 중복:** required(required/adjacent) `잘 모르던 기술 스택을 빠르게 학습해서 개발해나간 경험…` ↔ preferred `…있으면 좋아요` · downgraded_required_for_cap (preferred twin exists) · cap 제외=True

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## dval-junior_frontend-05  ·  [domain_transfer]  ·  역할: **fit_change_no_winner**
- persona: `junior_frontend`  ·  중복 탐지 포함: 예
- baseline 승자: **A**  ·  dedup 승자(다를 때만): **동일**
- 왜 검증에 유용한가: dedup이 한 공고의 fit을 바꾸지만 승자는 불변 — fit 상향이 순위 안정성을 깨지 않는지 검증.

| 항목 | **A** (baseline 상위) | **B** |
|---|---|---|
| 회사·포지션 | Toss · Frontend Developer | Toss · AI Engineer (Brain, AIOC) |
| job_id | `toss-4076130003` | `toss-7503655003` |
| role_family / domain | frontend / strong | ml_ai / weak |
| fit baseline→dedup | 2→3 | 1→1 |
| rank baseline→dedup (domain_fit_bt) | 5→2 | 6→6 |
- **A 탐지 중복:** required(required/missing) `레거시 코드를 최신의 개발 환경에 맞게 개선한 경험…` ↔ preferred `…있으면 좋아요` · downgraded_required_for_cap (preferred twin exists) · cap 제외=True
- **A 탐지 중복:** required(required/adjacent) `잘 모르던 기술 스택을 빠르게 학습해서 개발해나간 경험…` ↔ preferred `…있으면 좋아요` · downgraded_required_for_cap (preferred twin exists) · cap 제외=True

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## dval-backend_platform-01  ·  [same_domain_close]  ·  역할: **control_no_dups**
- persona: `backend_platform`  ·  중복 탐지 포함: 아니오
- baseline 승자: **A**  ·  dedup 승자(다를 때만): **동일**
- (참고) golden_pairs_20 기존 라벨: A_better
- 왜 검증에 유용한가: 중복 그룹이 전혀 없는 통제 쌍 — dedup이 baseline과 동일(무해)해야 함을 확인.

| 항목 | **A** (baseline 상위) | **B** |
|---|---|---|
| 회사·포지션 | Daangn · Software Engineer, Backend \| 광고 | Toss · ML Backend Engineer |
| job_id | `daangn-6640363003` | `toss-6600650003` |
| role_family / domain | backend / strong | backend / strong |
| fit baseline→dedup | 3→3 | 3→3 |
| rank baseline→dedup (domain_fit_bt) | 2→2 | 3→3 |

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## dval-backend_platform-02  ·  [same_domain_close]  ·  역할: **control_no_dups**
- persona: `backend_platform`  ·  중복 탐지 포함: 아니오
- baseline 승자: **A**  ·  dedup 승자(다를 때만): **동일**
- (참고) golden_pairs_20 기존 라벨: A_better
- 왜 검증에 유용한가: 중복 그룹이 전혀 없는 통제 쌍 — dedup이 baseline과 동일(무해)해야 함을 확인.

| 항목 | **A** (baseline 상위) | **B** |
|---|---|---|
| 회사·포지션 | Toss · Server Developer (수신) | Toss · ML Backend Engineer |
| job_id | `toss-6613962003` | `toss-6600650003` |
| role_family / domain | backend / strong | backend / strong |
| fit baseline→dedup | 4→4 | 3→3 |
| rank baseline→dedup (domain_fit_bt) | 1→1 | 3→3 |

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## dval-devops_infra_security-01  ·  [same_domain_close]  ·  역할: **control_no_dups**
- persona: `devops_infra_security`  ·  중복 탐지 포함: 아니오
- baseline 승자: **A**  ·  dedup 승자(다를 때만): **동일**
- (참고) golden_pairs_20 기존 라벨: B_better
- 왜 검증에 유용한가: 중복 그룹이 전혀 없는 통제 쌍 — dedup이 baseline과 동일(무해)해야 함을 확인.

| 항목 | **A** (baseline 상위) | **B** |
|---|---|---|
| 회사·포지션 | Daangn · Network Engineer \| 인프라 (네트워크, Cloud) | Toss · Cloud Engineer |
| job_id | `daangn-5004587003` | `toss-6677722003` |
| role_family / domain | devops_infra / strong | devops_infra / strong |
| fit baseline→dedup | 2→2 | 2→2 |
| rank baseline→dedup (domain_fit_bt) | 2→2 | 3→3 |

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## dval-devops_infra_security-02  ·  [same_domain_close]  ·  역할: **control_no_dups**
- persona: `devops_infra_security`  ·  중복 탐지 포함: 아니오
- baseline 승자: **A**  ·  dedup 승자(다를 때만): **동일**
- (참고) golden_pairs_20 기존 라벨: A_better
- 왜 검증에 유용한가: 중복 그룹이 전혀 없는 통제 쌍 — dedup이 baseline과 동일(무해)해야 함을 확인.

| 항목 | **A** (baseline 상위) | **B** |
|---|---|---|
| 회사·포지션 | Toss · AIOps Platform Engineer | Toss · Cloud Engineer |
| job_id | `toss-7702581003` | `toss-6677722003` |
| role_family / domain | devops_infra / strong | devops_infra / strong |
| fit baseline→dedup | 2→2 | 2→2 |
| rank baseline→dedup (domain_fit_bt) | 1→1 | 3→3 |

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## dval-ai_ml_application-01  ·  [adjacent_vs_primary]  ·  역할: **control_no_dups**
- persona: `ai_ml_application`  ·  중복 탐지 포함: 아니오
- baseline 승자: **A**  ·  dedup 승자(다를 때만): **동일**
- (참고) golden_pairs_20 기존 라벨: A_better
- 왜 검증에 유용한가: 중복 그룹이 전혀 없는 통제 쌍 — dedup이 baseline과 동일(무해)해야 함을 확인.

| 항목 | **A** (baseline 상위) | **B** |
|---|---|---|
| 회사·포지션 | Toss · AI Engineer (Brain, AIOC) | Toss · Data Analytics Engineer |
| job_id | `toss-7503655003` | `toss-6308074003` |
| role_family / domain | ml_ai / strong | data / adjacent |
| fit baseline→dedup | 2→2 | 3→3 |
| rank baseline→dedup (domain_fit_bt) | 2→2 | 3→3 |

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)

---
## dval-ai_ml_application-02  ·  [adjacent_vs_primary]  ·  역할: **control_no_dups**
- persona: `ai_ml_application`  ·  중복 탐지 포함: 아니오
- baseline 승자: **A**  ·  dedup 승자(다를 때만): **동일**
- (참고) golden_pairs_20 기존 라벨: A_better
- 왜 검증에 유용한가: 중복 그룹이 전혀 없는 통제 쌍 — dedup이 baseline과 동일(무해)해야 함을 확인.

| 항목 | **A** (baseline 상위) | **B** |
|---|---|---|
| 회사·포지션 | Toss · AI Engineer (Commerce) | Toss · Data Analytics Engineer |
| job_id | `toss-6545457003` | `toss-6308074003` |
| role_family / domain | ml_ai / strong | data / adjacent |
| fit baseline→dedup | 3→3 | 3→3 |
| rank baseline→dedup (domain_fit_bt) | 1→1 | 3→3 |

**✍️ 라벨 입력 (직접 작성):**
- `expected_winner`: ______  (A_better / B_better / tie / unsure)
- `label_reason`: ______
- `confidence`: ______  (high / medium / low)
