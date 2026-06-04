# 골든 페어 후보 (UNLABELED) — 사람 라벨링용

> 이 목록은 **라벨이 없는 후보 쌍**입니다. `propose-golden-pairs` 가 기존 `outputs/eval` 산출물만 읽어 '판단이 갈릴 만한' 하드 케이스를 자동 추출한 것입니다. 시스템은 여기서 **어느 쪽이 더 낫다고 라벨하지 않습니다** — 사람이 각 쌍에 `expected_winner`(A_better/B_better/tie/unsure)와 `label_reason`을 채워야 합니다.

- 추출 소스: `outputs\eval` · 최대 50쌍 요청
- 후보 총 44쌍 발견 → 상위 44쌍 반환 (난이도/하드니스 순; 0쌍은 상한으로 생략 — `--max-pairs` 로 더 받기).
- 페르소나별 후보 수: {'ai_ml_application': 12, 'backend_platform': 10, 'devops_infra_security': 12, 'junior_frontend': 10}
- 반환된 쌍의 카테고리 분포: {'same_domain_close': 13, 'adjacent_vs_primary': 10, 'domain_transfer': 8, 'seniority_gap': 6, 'weak_vs_adjacent': 7}

**A/B 정렬 규약:** A = 현재 기본 모드(domain_fit_bt)가 **더 높게** 매긴 공고입니다. 따라서 시스템에 동의하면 `A_better`, 뒤집어야 한다고 보면 `B_better` 입니다.

## junior_frontend (10쌍)

### prop-junior_frontend-01  ·  [same_domain_close] / 난이도 힌트: hard  ·  ⚠ 모드 불일치
- **A** `daangn-6692173003` — Daangn · Software Engineer, Frontend | 커머스  (role=frontend, domain=strong, fit=3, BT=0.3367)
- **B** `toss-4076130003` — Toss · Frontend Developer  (role=frontend, domain=strong, fit=2, BT=0.841)
- 추출 사유: 같은 role_family(frontend) · 같은 도메인 tier(strong) · 근접 fit(Δ1); 같은 도메인 tier인데 한쪽만 경력연차(experience_level) prerequisite 결손; domain_fit_bt 와 bt_primary 가 이 쌍을 서로 반대로 정렬; headline fit 과 Bradley-Terry 순서가 불일치 (fit 3/2, BT 0.34/0.84)
- 모드별 순위: bt_primary: A#5/B#3 · fit_primary: A#3/B#5 · domain_fit_bt: A#3/B#5
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-junior_frontend-02  ·  [same_domain_close] / 난이도 힌트: hard  ·  ⚠ 모드 불일치
- **A** `daangn-7689088003` — Daangn · Software Engineer, Frontend | 커뮤니티 (모임)  (role=frontend, domain=strong, fit=3, BT=0.6765)
- **B** `toss-4076141003` — Toss · Frontend Developer  (role=frontend, domain=strong, fit=2, BT=1.0454)
- 추출 사유: 같은 role_family(frontend) · 같은 도메인 tier(strong) · 근접 fit(Δ1); 같은 도메인 tier인데 한쪽만 경력연차(experience_level) prerequisite 결손; domain_fit_bt 와 bt_primary 가 이 쌍을 서로 반대로 정렬; headline fit 과 Bradley-Terry 순서가 불일치 (fit 3/2, BT 0.68/1.05)
- 모드별 순위: bt_primary: A#4/B#2 · fit_primary: A#2/B#4 · domain_fit_bt: A#2/B#4
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-junior_frontend-03  ·  [same_domain_close] / 난이도 힌트: hard  ·  ⚠ 모드 불일치
- **A** `daangn-6692173003` — Daangn · Software Engineer, Frontend | 커머스  (role=frontend, domain=strong, fit=3, BT=0.3367)
- **B** `toss-4076141003` — Toss · Frontend Developer  (role=frontend, domain=strong, fit=2, BT=1.0454)
- 추출 사유: 같은 role_family(frontend) · 같은 도메인 tier(strong) · 근접 fit(Δ1); domain_fit_bt 와 bt_primary 가 이 쌍을 서로 반대로 정렬; headline fit 과 Bradley-Terry 순서가 불일치 (fit 3/2, BT 0.34/1.05)
- 모드별 순위: bt_primary: A#5/B#2 · fit_primary: A#3/B#4 · domain_fit_bt: A#3/B#4
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-junior_frontend-04  ·  [same_domain_close] / 난이도 힌트: hard  ·  ⚠ 모드 불일치
- **A** `daangn-7689088003` — Daangn · Software Engineer, Frontend | 커뮤니티 (모임)  (role=frontend, domain=strong, fit=3, BT=0.6765)
- **B** `toss-4076130003` — Toss · Frontend Developer  (role=frontend, domain=strong, fit=2, BT=0.841)
- 추출 사유: 같은 role_family(frontend) · 같은 도메인 tier(strong) · 근접 fit(Δ1); domain_fit_bt 와 bt_primary 가 이 쌍을 서로 반대로 정렬; headline fit 과 Bradley-Terry 순서가 불일치 (fit 3/2, BT 0.68/0.84)
- 모드별 순위: bt_primary: A#4/B#3 · fit_primary: A#2/B#5 · domain_fit_bt: A#2/B#5
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-junior_frontend-05  ·  [same_domain_close] / 난이도 힌트: hard
- **A** `daangn-7689088003` — Daangn · Software Engineer, Frontend | 커뮤니티 (모임)  (role=frontend, domain=strong, fit=3, BT=0.6765)
- **B** `daangn-6692173003` — Daangn · Software Engineer, Frontend | 커머스  (role=frontend, domain=strong, fit=3, BT=0.3367)
- 추출 사유: 같은 role_family(frontend) · 같은 도메인 tier(strong) · 근접 fit(Δ0); 같은 도메인 tier인데 한쪽만 경력연차(experience_level) prerequisite 결손; 동일 회사(Daangn) 같은 직군 비교
- 모드별 순위: bt_primary: A#4/B#5 · fit_primary: A#2/B#3 · domain_fit_bt: A#2/B#3
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-junior_frontend-06  ·  [same_domain_close] / 난이도 힌트: hard
- **A** `toss-4076141003` — Toss · Frontend Developer  (role=frontend, domain=strong, fit=2, BT=1.0454)
- **B** `toss-4076130003` — Toss · Frontend Developer  (role=frontend, domain=strong, fit=2, BT=0.841)
- 추출 사유: 같은 role_family(frontend) · 같은 도메인 tier(strong) · 근접 fit(Δ0); 같은 도메인 tier인데 한쪽만 경력연차(experience_level) prerequisite 결손; 동일 회사(Toss) 같은 직군 비교
- 모드별 순위: bt_primary: A#2/B#3 · fit_primary: A#4/B#5 · domain_fit_bt: A#4/B#5
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-junior_frontend-07  ·  [seniority_gap] / 난이도 힌트: medium
- **A** `toss-5311744003` — Toss · Frontend Developer  (role=frontend, domain=strong, fit=5, BT=2.1004)
- **B** `daangn-7689088003` — Daangn · Software Engineer, Frontend | 커뮤니티 (모임)  (role=frontend, domain=strong, fit=3, BT=0.6765)
- 추출 사유: 같은 도메인 tier인데 한쪽만 경력연차(experience_level) prerequisite 결손
- 모드별 순위: bt_primary: A#1/B#4 · fit_primary: A#1/B#2 · domain_fit_bt: A#1/B#2
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-junior_frontend-08  ·  [seniority_gap] / 난이도 힌트: medium
- **A** `toss-5311744003` — Toss · Frontend Developer  (role=frontend, domain=strong, fit=5, BT=2.1004)
- **B** `toss-4076130003` — Toss · Frontend Developer  (role=frontend, domain=strong, fit=2, BT=0.841)
- 추출 사유: 같은 도메인 tier인데 한쪽만 경력연차(experience_level) prerequisite 결손
- 모드별 순위: bt_primary: A#1/B#3 · fit_primary: A#1/B#5 · domain_fit_bt: A#1/B#5
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-junior_frontend-09  ·  [domain_transfer] / 난이도 힌트: easy
- **A** `toss-4076130003` — Toss · Frontend Developer  (role=frontend, domain=strong, fit=2, BT=0.841)
- **B** `toss-7503655003` — Toss · AI Engineer (Brain, AIOC)  (role=ml_ai, domain=weak, fit=1, BT=0.0)
- 추출 사유: 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#3/B#6 · fit_primary: A#5/B#6 · domain_fit_bt: A#5/B#6
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-junior_frontend-10  ·  [domain_transfer] / 난이도 힌트: easy
- **A** `toss-4076141003` — Toss · Frontend Developer  (role=frontend, domain=strong, fit=2, BT=1.0454)
- **B** `toss-7503655003` — Toss · AI Engineer (Brain, AIOC)  (role=ml_ai, domain=weak, fit=1, BT=0.0)
- 추출 사유: 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#2/B#6 · fit_primary: A#4/B#6 · domain_fit_bt: A#4/B#6
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

## ai_ml_application (12쌍)

### prop-ai_ml_application-01  ·  [adjacent_vs_primary] / 난이도 힌트: hard  ·  ⚠ 모드 불일치
- **A** `toss-7503655003` — Toss · AI Engineer (Brain, AIOC)  (role=ml_ai, domain=strong, fit=2, BT=1.2749)
- **B** `toss-6308074003` — Toss · Data Analytics Engineer  (role=data, domain=adjacent, fit=3, BT=0.8151)
- 추출 사유: 주력(strong, fit2) vs 인접(adjacent, fit3) — 주력 도메인이 그래도 위여야 하나?; headline fit 과 Bradley-Terry 순서가 불일치 (fit 2/3, BT 1.27/0.82); 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#2/B#3 · fit_primary: A#3/B#2 · domain_fit_bt: A#2/B#3
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-ai_ml_application-02  ·  [domain_transfer] / 난이도 힌트: hard  ·  ⚠ 모드 불일치
- **A** `daangn-7507320003` — Daangn · Data Analytics Engineer | 테크코어 (데이터 가치화)  (role=data, domain=adjacent, fit=2, BT=0.3213)
- **B** `toss-7702581003` — Toss · AIOps Platform Engineer  (role=devops_infra, domain=weak, fit=2, BT=0.5211)
- 추출 사유: weak 도메인 vs 인접(adjacent) 도메인 — 도메인 거리 판단; domain_fit_bt 와 bt_primary 가 이 쌍을 서로 반대로 정렬
- 모드별 순위: bt_primary: A#5/B#4 · fit_primary: A#4/B#5 · domain_fit_bt: A#4/B#5
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-ai_ml_application-03  ·  [adjacent_vs_primary] / 난이도 힌트: hard
- **A** `toss-6545457003` — Toss · AI Engineer (Commerce)  (role=ml_ai, domain=strong, fit=3, BT=2.0676)
- **B** `toss-6308074003` — Toss · Data Analytics Engineer  (role=data, domain=adjacent, fit=3, BT=0.8151)
- 추출 사유: 주력(strong, fit3) vs 인접(adjacent, fit3) — 주력 도메인이 그래도 위여야 하나?; 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#1/B#3 · fit_primary: A#1/B#2 · domain_fit_bt: A#1/B#3
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-ai_ml_application-04  ·  [weak_vs_adjacent] / 난이도 힌트: medium
- **A** `daangn-7507320003` — Daangn · Data Analytics Engineer | 테크코어 (데이터 가치화)  (role=data, domain=adjacent, fit=2, BT=0.3213)
- **B** `daangn-7655325003` — Daangn · Security Engineer | 인프라 (보안, AI Security)  (role=security, domain=weak, fit=2, BT=0.0)
- 추출 사유: weak 도메인 vs 인접(adjacent) 도메인 — 도메인 거리 판단; 동일 회사(Daangn) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#5/B#6 · fit_primary: A#4/B#6 · domain_fit_bt: A#4/B#6
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-ai_ml_application-05  ·  [weak_vs_adjacent] / 난이도 힌트: medium
- **A** `toss-6308074003` — Toss · Data Analytics Engineer  (role=data, domain=adjacent, fit=3, BT=0.8151)
- **B** `toss-7702581003` — Toss · AIOps Platform Engineer  (role=devops_infra, domain=weak, fit=2, BT=0.5211)
- 추출 사유: weak 도메인 vs 인접(adjacent) 도메인 — 도메인 거리 판단; 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#3/B#4 · fit_primary: A#2/B#5 · domain_fit_bt: A#3/B#5
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-ai_ml_application-06  ·  [same_domain_close] / 난이도 힌트: medium
- **A** `toss-6545457003` — Toss · AI Engineer (Commerce)  (role=ml_ai, domain=strong, fit=3, BT=2.0676)
- **B** `toss-7503655003` — Toss · AI Engineer (Brain, AIOC)  (role=ml_ai, domain=strong, fit=2, BT=1.2749)
- 추출 사유: 같은 role_family(ml_ai) · 같은 도메인 tier(strong) · 근접 fit(Δ1); 동일 회사(Toss) 같은 직군 비교
- 모드별 순위: bt_primary: A#1/B#2 · fit_primary: A#1/B#3 · domain_fit_bt: A#1/B#2
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-ai_ml_application-07  ·  [adjacent_vs_primary] / 난이도 힌트: medium
- **A** `toss-7503655003` — Toss · AI Engineer (Brain, AIOC)  (role=ml_ai, domain=strong, fit=2, BT=1.2749)
- **B** `daangn-7507320003` — Daangn · Data Analytics Engineer | 테크코어 (데이터 가치화)  (role=data, domain=adjacent, fit=2, BT=0.3213)
- 추출 사유: 주력(strong, fit2) vs 인접(adjacent, fit2) — 주력 도메인이 그래도 위여야 하나?
- 모드별 순위: bt_primary: A#2/B#5 · fit_primary: A#3/B#4 · domain_fit_bt: A#2/B#4
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-ai_ml_application-08  ·  [seniority_gap] / 난이도 힌트: medium
- **A** `toss-7702581003` — Toss · AIOps Platform Engineer  (role=devops_infra, domain=weak, fit=2, BT=0.5211)
- **B** `daangn-7655325003` — Daangn · Security Engineer | 인프라 (보안, AI Security)  (role=security, domain=weak, fit=2, BT=0.0)
- 추출 사유: 같은 도메인 tier인데 한쪽만 경력연차(experience_level) prerequisite 결손
- 모드별 순위: bt_primary: A#4/B#6 · fit_primary: A#5/B#6 · domain_fit_bt: A#5/B#6
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-ai_ml_application-09  ·  [same_domain_close] / 난이도 힌트: easy
- **A** `toss-6308074003` — Toss · Data Analytics Engineer  (role=data, domain=adjacent, fit=3, BT=0.8151)
- **B** `daangn-7507320003` — Daangn · Data Analytics Engineer | 테크코어 (데이터 가치화)  (role=data, domain=adjacent, fit=2, BT=0.3213)
- 추출 사유: 같은 role_family(data) · 같은 도메인 tier(adjacent) · 근접 fit(Δ1)
- 모드별 순위: bt_primary: A#3/B#5 · fit_primary: A#2/B#4 · domain_fit_bt: A#3/B#4
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-ai_ml_application-10  ·  [weak_vs_adjacent] / 난이도 힌트: easy
- **A** `toss-6308074003` — Toss · Data Analytics Engineer  (role=data, domain=adjacent, fit=3, BT=0.8151)
- **B** `daangn-7655325003` — Daangn · Security Engineer | 인프라 (보안, AI Security)  (role=security, domain=weak, fit=2, BT=0.0)
- 추출 사유: weak 도메인 vs 인접(adjacent) 도메인 — 도메인 거리 판단
- 모드별 순위: bt_primary: A#3/B#6 · fit_primary: A#2/B#6 · domain_fit_bt: A#3/B#6
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-ai_ml_application-11  ·  [domain_transfer] / 난이도 힌트: easy
- **A** `toss-6545457003` — Toss · AI Engineer (Commerce)  (role=ml_ai, domain=strong, fit=3, BT=2.0676)
- **B** `toss-7702581003` — Toss · AIOps Platform Engineer  (role=devops_infra, domain=weak, fit=2, BT=0.5211)
- 추출 사유: 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#1/B#4 · fit_primary: A#1/B#5 · domain_fit_bt: A#1/B#5
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-ai_ml_application-12  ·  [domain_transfer] / 난이도 힌트: easy
- **A** `toss-7503655003` — Toss · AI Engineer (Brain, AIOC)  (role=ml_ai, domain=strong, fit=2, BT=1.2749)
- **B** `toss-7702581003` — Toss · AIOps Platform Engineer  (role=devops_infra, domain=weak, fit=2, BT=0.5211)
- 추출 사유: 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#2/B#4 · fit_primary: A#3/B#5 · domain_fit_bt: A#2/B#5
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

## devops_infra_security (12쌍)

### prop-devops_infra_security-01  ·  [adjacent_vs_primary] / 난이도 힌트: hard  ·  ⚠ 모드 불일치
- **A** `toss-6677722003` — Toss · Cloud Engineer  (role=devops_infra, domain=strong, fit=2, BT=0.841)
- **B** `toss-6600650003` — Toss · ML Backend Engineer  (role=backend, domain=adjacent, fit=3, BT=0.6765)
- 추출 사유: 주력(strong, fit2) vs 인접(adjacent, fit3) — 주력 도메인이 그래도 위여야 하나?; headline fit 과 Bradley-Terry 순서가 불일치 (fit 2/3, BT 0.84/0.68); 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#3/B#4 · fit_primary: A#4/B#1 · domain_fit_bt: A#3/B#4
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-devops_infra_security-02  ·  [adjacent_vs_primary] / 난이도 힌트: hard  ·  ⚠ 모드 불일치
- **A** `toss-7702581003` — Toss · AIOps Platform Engineer  (role=devops_infra, domain=strong, fit=2, BT=2.1004)
- **B** `toss-6600650003` — Toss · ML Backend Engineer  (role=backend, domain=adjacent, fit=3, BT=0.6765)
- 추출 사유: 주력(strong, fit2) vs 인접(adjacent, fit3) — 주력 도메인이 그래도 위여야 하나?; headline fit 과 Bradley-Terry 순서가 불일치 (fit 2/3, BT 2.10/0.68); 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#1/B#4 · fit_primary: A#2/B#1 · domain_fit_bt: A#1/B#4
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-devops_infra_security-03  ·  [adjacent_vs_primary] / 난이도 힌트: hard  ·  ⚠ 모드 불일치
- **A** `daangn-5004587003` — Daangn · Network Engineer | 인프라 (네트워크, Cloud)  (role=devops_infra, domain=strong, fit=2, BT=1.0454)
- **B** `toss-6600650003` — Toss · ML Backend Engineer  (role=backend, domain=adjacent, fit=3, BT=0.6765)
- 추출 사유: 주력(strong, fit2) vs 인접(adjacent, fit3) — 주력 도메인이 그래도 위여야 하나?; headline fit 과 Bradley-Terry 순서가 불일치 (fit 2/3, BT 1.05/0.68)
- 모드별 순위: bt_primary: A#2/B#4 · fit_primary: A#3/B#1 · domain_fit_bt: A#2/B#4
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-devops_infra_security-04  ·  [same_domain_close] / 난이도 힌트: hard
- **A** `daangn-5004587003` — Daangn · Network Engineer | 인프라 (네트워크, Cloud)  (role=devops_infra, domain=strong, fit=2, BT=1.0454)
- **B** `toss-6677722003` — Toss · Cloud Engineer  (role=devops_infra, domain=strong, fit=2, BT=0.841)
- 추출 사유: 같은 role_family(devops_infra) · 같은 도메인 tier(strong) · 근접 fit(Δ0); 같은 도메인 tier인데 한쪽만 경력연차(experience_level) prerequisite 결손
- 모드별 순위: bt_primary: A#2/B#3 · fit_primary: A#3/B#4 · domain_fit_bt: A#2/B#3
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-devops_infra_security-05  ·  [same_domain_close] / 난이도 힌트: hard
- **A** `toss-7702581003` — Toss · AIOps Platform Engineer  (role=devops_infra, domain=strong, fit=2, BT=2.1004)
- **B** `daangn-5004587003` — Daangn · Network Engineer | 인프라 (네트워크, Cloud)  (role=devops_infra, domain=strong, fit=2, BT=1.0454)
- 추출 사유: 같은 role_family(devops_infra) · 같은 도메인 tier(strong) · 근접 fit(Δ0); 같은 도메인 tier인데 한쪽만 경력연차(experience_level) prerequisite 결손
- 모드별 순위: bt_primary: A#1/B#2 · fit_primary: A#2/B#3 · domain_fit_bt: A#1/B#2
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-devops_infra_security-06  ·  [same_domain_close] / 난이도 힌트: hard
- **A** `toss-7702581003` — Toss · AIOps Platform Engineer  (role=devops_infra, domain=strong, fit=2, BT=2.1004)
- **B** `toss-6677722003` — Toss · Cloud Engineer  (role=devops_infra, domain=strong, fit=2, BT=0.841)
- 추출 사유: 같은 role_family(devops_infra) · 같은 도메인 tier(strong) · 근접 fit(Δ0); 동일 회사(Toss) 같은 직군 비교
- 모드별 순위: bt_primary: A#1/B#3 · fit_primary: A#2/B#4 · domain_fit_bt: A#1/B#3
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-devops_infra_security-07  ·  [seniority_gap] / 난이도 힌트: medium
- **A** `toss-6600650003` — Toss · ML Backend Engineer  (role=backend, domain=adjacent, fit=3, BT=0.6765)
- **B** `daangn-6045408003` — Daangn · Security Engineer | 인프라 (보안, 모의해킹)  (role=security, domain=adjacent, fit=1, BT=0.3367)
- 추출 사유: 같은 도메인 tier인데 한쪽만 경력연차(experience_level) prerequisite 결손
- 모드별 순위: bt_primary: A#4/B#5 · fit_primary: A#1/B#5 · domain_fit_bt: A#4/B#5
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-devops_infra_security-08  ·  [weak_vs_adjacent] / 난이도 힌트: medium
- **A** `toss-6600650003` — Toss · ML Backend Engineer  (role=backend, domain=adjacent, fit=3, BT=0.6765)
- **B** `toss-7503655003` — Toss · AI Engineer (Brain, AIOC)  (role=ml_ai, domain=weak, fit=1, BT=0.0)
- 추출 사유: weak 도메인 vs 인접(adjacent) 도메인 — 도메인 거리 판단; 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#4/B#6 · fit_primary: A#1/B#6 · domain_fit_bt: A#4/B#6
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-devops_infra_security-09  ·  [adjacent_vs_primary] / 난이도 힌트: easy
- **A** `daangn-5004587003` — Daangn · Network Engineer | 인프라 (네트워크, Cloud)  (role=devops_infra, domain=strong, fit=2, BT=1.0454)
- **B** `daangn-6045408003` — Daangn · Security Engineer | 인프라 (보안, 모의해킹)  (role=security, domain=adjacent, fit=1, BT=0.3367)
- 추출 사유: 동일 회사(Daangn) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#2/B#5 · fit_primary: A#3/B#5 · domain_fit_bt: A#2/B#5
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-devops_infra_security-10  ·  [weak_vs_adjacent] / 난이도 힌트: easy
- **A** `daangn-6045408003` — Daangn · Security Engineer | 인프라 (보안, 모의해킹)  (role=security, domain=adjacent, fit=1, BT=0.3367)
- **B** `toss-7503655003` — Toss · AI Engineer (Brain, AIOC)  (role=ml_ai, domain=weak, fit=1, BT=0.0)
- 추출 사유: weak 도메인 vs 인접(adjacent) 도메인 — 도메인 거리 판단
- 모드별 순위: bt_primary: A#5/B#6 · fit_primary: A#5/B#6 · domain_fit_bt: A#5/B#6
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-devops_infra_security-11  ·  [domain_transfer] / 난이도 힌트: easy
- **A** `toss-6677722003` — Toss · Cloud Engineer  (role=devops_infra, domain=strong, fit=2, BT=0.841)
- **B** `toss-7503655003` — Toss · AI Engineer (Brain, AIOC)  (role=ml_ai, domain=weak, fit=1, BT=0.0)
- 추출 사유: 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#3/B#6 · fit_primary: A#4/B#6 · domain_fit_bt: A#3/B#6
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-devops_infra_security-12  ·  [domain_transfer] / 난이도 힌트: easy
- **A** `toss-7702581003` — Toss · AIOps Platform Engineer  (role=devops_infra, domain=strong, fit=2, BT=2.1004)
- **B** `toss-7503655003` — Toss · AI Engineer (Brain, AIOC)  (role=ml_ai, domain=weak, fit=1, BT=0.0)
- 추출 사유: 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#1/B#6 · fit_primary: A#2/B#6 · domain_fit_bt: A#1/B#6
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

## backend_platform (10쌍)

### prop-backend_platform-01  ·  [same_domain_close] / 난이도 힌트: hard
- **A** `daangn-6640363003` — Daangn · Software Engineer, Backend | 광고  (role=backend, domain=strong, fit=3, BT=1.2749)
- **B** `toss-6600650003` — Toss · ML Backend Engineer  (role=backend, domain=strong, fit=3, BT=0.8151)
- 추출 사유: 같은 role_family(backend) · 같은 도메인 tier(strong) · 근접 fit(Δ0); 같은 도메인 tier인데 한쪽만 경력연차(experience_level) prerequisite 결손
- 모드별 순위: bt_primary: A#2/B#3 · fit_primary: A#2/B#3 · domain_fit_bt: A#2/B#3
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-backend_platform-02  ·  [seniority_gap] / 난이도 힌트: hard
- **A** `toss-6613962003` — Toss · Server Developer (수신)  (role=backend, domain=strong, fit=4, BT=2.0676)
- **B** `daangn-6640363003` — Daangn · Software Engineer, Backend | 광고  (role=backend, domain=strong, fit=3, BT=1.2749)
- 추출 사유: 같은 role_family(backend) · 같은 도메인 tier(strong) · 근접 fit(Δ1); 같은 도메인 tier인데 한쪽만 경력연차(experience_level) prerequisite 결손
- 모드별 순위: bt_primary: A#1/B#2 · fit_primary: A#1/B#2 · domain_fit_bt: A#1/B#2
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-backend_platform-03  ·  [seniority_gap] / 난이도 힌트: hard
- **A** `toss-7702581003` — Toss · AIOps Platform Engineer  (role=devops_infra, domain=adjacent, fit=2, BT=0.5211)
- **B** `daangn-5004587003` — Daangn · Network Engineer | 인프라 (네트워크, Cloud)  (role=devops_infra, domain=adjacent, fit=1, BT=0.3213)
- 추출 사유: 같은 role_family(devops_infra) · 같은 도메인 tier(adjacent) · 근접 fit(Δ1); 같은 도메인 tier인데 한쪽만 경력연차(experience_level) prerequisite 결손
- 모드별 순위: bt_primary: A#4/B#5 · fit_primary: A#4/B#5 · domain_fit_bt: A#4/B#5
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-backend_platform-04  ·  [same_domain_close] / 난이도 힌트: medium
- **A** `toss-6613962003` — Toss · Server Developer (수신)  (role=backend, domain=strong, fit=4, BT=2.0676)
- **B** `toss-6600650003` — Toss · ML Backend Engineer  (role=backend, domain=strong, fit=3, BT=0.8151)
- 추출 사유: 같은 role_family(backend) · 같은 도메인 tier(strong) · 근접 fit(Δ1); 동일 회사(Toss) 같은 직군 비교
- 모드별 순위: bt_primary: A#1/B#3 · fit_primary: A#1/B#3 · domain_fit_bt: A#1/B#3
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-backend_platform-05  ·  [weak_vs_adjacent] / 난이도 힌트: medium
- **A** `toss-7702581003` — Toss · AIOps Platform Engineer  (role=devops_infra, domain=adjacent, fit=2, BT=0.5211)
- **B** `toss-7503655003` — Toss · AI Engineer (Brain, AIOC)  (role=ml_ai, domain=weak, fit=1, BT=0.0)
- 추출 사유: weak 도메인 vs 인접(adjacent) 도메인 — 도메인 거리 판단; 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#4/B#6 · fit_primary: A#4/B#6 · domain_fit_bt: A#4/B#6
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-backend_platform-06  ·  [weak_vs_adjacent] / 난이도 힌트: easy
- **A** `daangn-5004587003` — Daangn · Network Engineer | 인프라 (네트워크, Cloud)  (role=devops_infra, domain=adjacent, fit=1, BT=0.3213)
- **B** `toss-7503655003` — Toss · AI Engineer (Brain, AIOC)  (role=ml_ai, domain=weak, fit=1, BT=0.0)
- 추출 사유: weak 도메인 vs 인접(adjacent) 도메인 — 도메인 거리 판단
- 모드별 순위: bt_primary: A#5/B#6 · fit_primary: A#5/B#6 · domain_fit_bt: A#5/B#6
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-backend_platform-07  ·  [adjacent_vs_primary] / 난이도 힌트: easy
- **A** `daangn-6640363003` — Daangn · Software Engineer, Backend | 광고  (role=backend, domain=strong, fit=3, BT=1.2749)
- **B** `daangn-5004587003` — Daangn · Network Engineer | 인프라 (네트워크, Cloud)  (role=devops_infra, domain=adjacent, fit=1, BT=0.3213)
- 추출 사유: 동일 회사(Daangn) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#2/B#5 · fit_primary: A#2/B#5 · domain_fit_bt: A#2/B#5
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-backend_platform-08  ·  [domain_transfer] / 난이도 힌트: easy
- **A** `toss-6600650003` — Toss · ML Backend Engineer  (role=backend, domain=strong, fit=3, BT=0.8151)
- **B** `toss-7503655003` — Toss · AI Engineer (Brain, AIOC)  (role=ml_ai, domain=weak, fit=1, BT=0.0)
- 추출 사유: 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#3/B#6 · fit_primary: A#3/B#6 · domain_fit_bt: A#3/B#6
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-backend_platform-09  ·  [adjacent_vs_primary] / 난이도 힌트: easy
- **A** `toss-6600650003` — Toss · ML Backend Engineer  (role=backend, domain=strong, fit=3, BT=0.8151)
- **B** `toss-7702581003` — Toss · AIOps Platform Engineer  (role=devops_infra, domain=adjacent, fit=2, BT=0.5211)
- 추출 사유: 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#3/B#4 · fit_primary: A#3/B#4 · domain_fit_bt: A#3/B#4
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

### prop-backend_platform-10  ·  [adjacent_vs_primary] / 난이도 힌트: easy
- **A** `toss-6613962003` — Toss · Server Developer (수신)  (role=backend, domain=strong, fit=4, BT=2.0676)
- **B** `toss-7702581003` — Toss · AIOps Platform Engineer  (role=devops_infra, domain=adjacent, fit=2, BT=0.5211)
- 추출 사유: 동일 회사(Toss) 유사/인접 직군 비교
- 모드별 순위: bt_primary: A#1/B#4 · fit_primary: A#1/B#4 · domain_fit_bt: A#1/B#4
- ✍️ 라벨링: `expected_winner` = ____ (A_better/B_better/tie/unsure), `label_reason` = ____

---
## 라벨링 후 다음 단계
1. `proposed_pairs.json` 의 각 쌍에 `expected_winner` 와 `label_reason` 을 채웁니다 (unsure 는 자유롭게 사용 — 점수에서 제외됩니다).
2. 라벨링한 파일을 `data/eval/golden_pairs/golden_pairs.json` 으로 저장합니다.
3. `python -m src.main eval-golden-pairs --pairs data/eval/golden_pairs/golden_pairs.json` 로 정확도를 측정합니다 (LLM 호출 없음).