# STATUS_REPORT — 이력서↔JD 적합도 랭킹 프로토타입

> 이 문서는 다른 AI/엔지니어가 **프로젝트 현황, 그동안의 의사결정 과정, 알고리즘, 실험 결과**를 한 번에
> 파악하도록 작성한 종합 보고서입니다. 특히 **`986dd24` 커밋 이후(= 골든 페어 정확도 평가 + dedup 스코어링
> ablation, 커밋 `61864d2`)** 에 집중합니다. 작성 기준일: 2026-06-04.

---

## 0. TL;DR (한 문단)
로컬에서 도는 "이력서 ↔ 채용공고(JD) 적합도(fit, 1~5) 랭킹" 프로토타입이다. v0(`50c5226`)에서 단일 실 이력서로
검증됐고, `986dd24`에서 멀티-페르소나 진단 + **3개 랭킹 모드 ablation** 끝에 기본 정렬을 `domain_fit_bt`로
바꿨다. 이번 세션(`61864d2`)에서는 **프로젝트 최초의 '정확도' 평가**인 *골든 페어(human-labeled pair)*
프레임워크를 구축했다. 사람이 20쌍을 라벨링한 결과 기본 모드 정확도는 **domain_fit_bt 16/20**(bt 15, fit 12).
오류 4건은 전부 `same_domain_close`였고, 근본 원인은 `compute_fit`의 cap 사다리가 *critical*과 *required* 갭을
거의 동일하게 처리하는 점 + 연차/role-core/중복 미처리였다. 그중 가장 안전한 후보인 **Change B(required/preferred
중복 정리)** 를 **실험 스코어링 모드 `dedup_required_preferred`** 로 구현했고, 같은 20쌍에서 **domain_fit_bt
16→19(+3), 회귀 0건**을 얻었다. 다만 개선 3건이 모두 동일 공고(`toss-4076130003`)에서 나왔고, 캐시된 24개
(persona,job) 중 중복이 탐지되는 공고가 그 1개뿐이라 **기본값으로 승격하지 않고 실험 상태로 유지**한다. 랭킹
로직/프롬프트/기본 스코어링은 변경하지 않았다.

---

## 1. 변하지 않는 제품 규칙 (모든 작업에서 항상 준수)
- **합격확률(pass probability)·퍼센트를 제품 출력으로 내지 않는다.** fit은 **정수 1~5**만.
- NestJS / AWS / DB / mock 모드 추가 금지.
- 프롬프트 / 추출 / 매칭 / 검증 / `compute_fit` **기본** 로직을 (명백한 버그가 아닌 한) 바꾸지 않는다.
- **mismatch 직군(marketing/design/product)은 어떤 엔지니어링 직군보다도 위로 랭크될 수 없다**(하드 가드).
- 살아남는 모든 evidence 인용은 **추출형(extractive)** 이어야 한다(이력서 원문에서 그대로).
- 합성 이력서는 합성임을 명시하고 실제 데이터(`data/resume.md`)를 덮어쓰지 않는다.
- *주: 평가 리포트 내부의 "정확도 %"는 시스템 vs 사람 라벨 일치율(평가 내부 지표)이며 제품 fit/합격확률과 무관.*

---

## 2. 환경 / 스택
- Python 3.10.11 / Windows 11 / PowerShell. 콘솔 cp949 때문에 한글+기호 출력 시
  `$env:PYTHONUTF8="1"; $env:PYTHONIOENCODING="utf-8"` 필요(em-dash 등이 rich 렌더러를 깨뜨림). **로직 버그 아님.**
- 의존성: pydantic 2.x, rich, requests, beautifulsoup4, openai SDK. Bradley-Terry는 순수 파이썬(scipy/playwright 없음).
- LLM: `gpt-5.4-mini` (`OPENAI_MODEL` env). 키는 `.env`(gitignore).
- git 저장소(로컬). 기본 브랜치 `main`. 원격 `origin/main` 존재하나 이번 작업은 **push 안 함**.

---

## 3. 커밋 히스토리
| 커밋 | 내용 |
|---|---|
| `50c5226` | v0: 단일 실 이력서로 파이프라인 end-to-end 검증 |
| `986dd24` | 멀티-페르소나 진단 스위트 + 3-모드 ablation → 기본 정렬을 **domain_fit_bt** 로 전환 |
| **`61864d2`** | **⭐ 이번 세션: 골든 페어 정확도 평가 + dedup 스코어링 ablation(실험)** |

`main`은 현재 `origin/main`보다 **2 커밋 앞섬**(`986dd24`, `61864d2` 미push) — 이후 문서 커밋이 추가될 수 있음.

---

## 4. `986dd24` 시점 베이스라인 (이미 있던 것 — 이번에 미변경)
이번 세션은 아래를 **건드리지 않았다**. 정확도 평가의 대상일 뿐이다.

**파이프라인(단계별):**
1. fetch (Toss/Daangn JSON API) → 2. 도메인 인지 선택(pool→tier 균형) → 3. 이력서 evidence 추출(+결정적
Skills 항목) → 4. JD 요구사항 구조화(**prerequisite vs product_duty** 구분) → 5. ID 기반 추출형 매칭 + rematch →
6. 보수적 verifier(비추출 인용 제거) → 7. **`compute_fit`(1~5, caps)** → 8. listwise 재랭킹 → 9. pairwise A/B·B/A
교차 비교 → 10. **Bradley-Terry** 집계 → 11. **도메인 우선순위 가드** → 12. 최종 랭킹.

**3개 랭킹 모드(최종 정렬만 다름, 업스트림 신호는 동일):**
- **`domain_fit_bt` (기본값/권장):** 도메인 tier(strong>adjacent>weak>mismatch) → fit_level → BT → listwise → 결정적.
- `bt_primary` (BT 우선/디버그용): BT가 1차 키, fit/도메인은 동점 타이브레이크. (v0 원래 기본값)
- `fit_primary` (fit 정렬 UI 옵션): fit_level 1차, 그다음 도메인·BT. (인접이 strong을 추월할 수 있음)

**진단 스위트(미변경):** fixture 회귀(불변식 10개), 멀티-페르소나(backend/junior_frontend/ai_ml/devops 4개 합성
이력서)의 **방향성** 검사. → 이들은 *일관성*만 보고 *정확도*는 못 본다 (그래서 이번에 골든 페어 도입).

---

## 5. ⭐ `986dd24` 이후 변경사항 (이번 세션 = 커밋 `61864d2`)

### 5.1 왜 골든 페어인가 — "최초의 진짜 정확도 평가"
기존 3종 평가(불변식 회귀 / 멀티-페르소나 / 모드 ablation)는 전부 **자기 일관성(self-consistency)** 검사다:
규칙을 지키는지만 보므로 "규칙은 지키지만 틀린" 랭킹을 잡지 못한다. **외부 정답(사람 판단)** 이 없었다.
**골든 페어**는 그 정답을 도입한다: 한 페르소나의 두 공고 A/B를 사람이 `A_better / B_better / tie / unsure`로
라벨링하고, 시스템 순위가 사람과 얼마나 일치하는지 측정한다. 이것이 프로젝트에서 처음으로 *내려갈 수 있는*
(랭킹이 나빠지면 떨어지는) 숫자다. **랭킹 로직 변경 없음, LLM 호출 없음** — `outputs/eval/<persona>/`의 기존
산출물(`final_ranking_*.json`, `pairwise_comparisons.json`, `matching_tables.json`)만 읽는다.

### 5.2 후보 추출(`propose-golden-pairs`) + 라벨링 패킷
- `propose-golden-pairs --from outputs/eval --max-pairs N`: 기존 산출물에서 **하드 케이스**(같은 직군·근접 fit,
  모드 불일치, fit↔BT 불일치, 주력 vs 인접 fit 역전, 연차 갭, 동일 회사 유사 직군 등)를 자동 추출. **라벨은 절대
  안 단다**(`expected_winner` 공백). → `proposed_pairs.{md,json}` (44쌍 추출됨).
- 사람 라벨링용 패킷 생성: `manual_labeling_packet.{md,json}`(상위 20), `manual_labeling_packet_10.{md,json}`
  (빠른 시작 10), `manual_labeling_remaining_10.{md,json}`(나머지 10), 병합 타깃 `golden_pairs_20.json`.
- 각 쌍에 A/B 회사·직군·도메인·fit·BT·모드별 순위 + 추출형 매칭/결손 근거 + 빈 라벨 필드 포함.

### 5.3 사람 라벨 결과 (10쌍 → 20쌍)
사용자가 직접 라벨링. **A/B 규약: A = 기본 모드(domain_fit_bt)가 더 높게 매긴 공고** → `A_better`=시스템 동의,
`B_better`=뒤집어야 함. 라벨 분포(20쌍): **A_better 16, B_better 4**.

| 단계 | domain_fit_bt | bt_primary | fit_primary |
|---|---|---|---|
| 10쌍 | 8/10 | 7/10 | 4/10 |
| **20쌍 (현재 기준선)** | **16/20** | **15/20** | **12/20** |

**카테고리별(20쌍, 헤드라인 domain_fit_bt):** adjacent_vs_primary 5/5 · seniority_gap 2/2 · domain_transfer 1/1 ·
**same_domain_close 8/12 (유일하게 100% 미만)**. → **오류 4건이 전부 same_domain_close**.
**페르소나별:** ai_ml 4/4 · backend 4/4 · devops 5/6 · **junior_frontend 3/6(최저)**.

### 5.4 오류 분석 (4개, 전부 same_domain_close)
`outputs/eval/golden_pair_error_analysis_20.{md,json}` 참조.

| pair_id | persona | A(시스템 상위) | B(사람 선택) | 사람 | 모드별(bt/fit/dfb) | 1차 root cause |
|---|---|---|---|---|---|---|
| jf-01 | junior_frontend | 당근 커머스 FE (fit3) | 토스 FE `toss-4076130003` (fit2) | B | B/A/A | required_gap_overweighted (+중복) |
| jf-04 | junior_frontend | 당근 모임 FE (fit3, **3년+ 요구**) | 토스 FE `toss-4076130003` (fit2) | B | B/A/A | seniority_gap_underweighted |
| jf-06 | junior_frontend | 토스 증권 FE (fit2, critical 3건 미충족) | 토스 FE `toss-4076130003` (fit2) | B | A/A/A | role_core_gap_underweighted |
| dev-04 | devops_infra_security | 당근 Network Eng (fit2, **role-core 5건 미충족**) | 토스 Cloud Eng (fit2) | B | A/A/A | role_core_gap_underweighted (+domain_tier_too_strong, 연차) |

**통합 근본 원인:** `compute_fit`의 cap 사다리가 role-defining **critical** 갭과 **required** 갭을 거의 동일
강도로 처리한다(둘 다 1건→cap3, 2건+→cap2). 그래서 (a) required-only 갭 공고가 critical 갭 공고를 못 이기고
(jf-01/04), (b) critical 다수 갭 공고가 required 소수 갭 공고 **아래로 못 내려간다**(jf-06/dev-04). 여기에
experience_level 갭을 후보 연차로 가중하지 않고, role-core vs 주변 도구 갭을 구분하지 않으며, 동일 역량의
required/preferred **중복을 이중 계산**하는 점이 겹친다. 동점이면 BT가 매칭 '물량'으로 깨면서 주니어/도메인
적합 관점과 어긋난다. (참고: jf-01/04는 `bt_primary`가 사람과 일치했으나 domain_fit_bt가 같은 tier에서
fit_level로 정렬하며 BT 신호를 버림.)

### 5.5 스코어링 개선 제안 (미구현 → docs/SCORING_IMPROVEMENT_PROPOSAL.md)
| 후보 | 내용 | 해결 오류 | 위험 |
|---|---|---|---|
| **B (선택)** | required/preferred **중복 정리**(scoring단, 프롬프트 아님) | jf-01/04/06 | 낮음~중간 |
| A | 연차 가중(3년+/5년+ vs 주니어면 더 강하게 cap, preferred는 제외) | jf-04, dev-04 | 중간~높음 |
| C | role-core 갭 가중(네트워크 BGP/OSPF, 클라우드 K8s/IaC 등) | dev-04, jf-06 | 높음(분류표 유지비) |
| D | same-domain close에서 BT 더 쓰기 | — | **비권장**(BT가 절반에서 틀림); 대신 close-pair 불확실성 '플래그'만 |

→ **B를 가장 안전·고레버리지로 판단**(단일 중복이 4오류 중 3개에 관여, 프롬프트 변경 아님). C/A는 후순위.

### 5.6 Change B 구현 — 실험 스코어링 모드 `dedup_required_preferred`
**기본 스코어링은 그대로 두고**, 플래그 뒤에서만 동작:
- `rank_aggregate.compute_fit(table, alignment, dedup_required_preferred=False)` — 기본 OFF = baseline과
  **바이트 단위 동일**. ON이면 동일 역량이 required/critical 행과 preferred/optional 행에 **중복** 등장할 때,
  더 센 쪽(required) 행을 **cap 계산에서만 제외**한다. 행은 리포트에 그대로 남고, 처리 내역은 `dedup_audit`
  (duplicate_group_id / duplicate_resolution / excluded_from_fit_cap / dedup_reason)로 감사 가능. **증거 삭제 없음.**
- `golden_pairs.rescore_persona(eval_root, persona, scoring_mode)` — 캐시 산출물만으로 fit을 재계산하고
  **실제 `aggregate()` 를 재사용**해 모드별 순위를 다시 만든다(LLM 없음 → 랭킹 로직과 100% 동일, fit만 다름).
- CLI: `eval-golden-pairs --pairs ... --scoring-mode {baseline|dedup_required_preferred}` (비-baseline은
  리포트 파일명에 접미사).

**ablation 결과(`golden_pairs_20`, `outputs/eval/scoring_ablation_required_preferred_dedup.{md,json}`):**

| 모드 | baseline | dedup |
|---|---|---|
| **domain_fit_bt** | **16/20** | **19/20 (+3)** |
| bt_primary | 15/20 | 15/20 |
| fit_primary | 12/20 | 15/20 (+3) |

- **회귀 0건.** 고친 쌍은 정확히 jf-01/04/06. **유일하게 바뀐 fit은 `toss-4076130003` 2→3.** 카테고리:
  same_domain_close 8/12→11/12, 나머지(adjacent_vs_primary 5/5·seniority_gap 2/2·domain_transfer 1/1) 전부 불변.
- fixture 회귀 10/10 유지(baseline 경로 불변). recompute-baseline이 cached-baseline(16/15/12)과 일치 → 재계산 경로 충실.

### 5.7 dedup 검증 세트 + 결정적 한계
`data/eval/golden_pairs/dedup_validation_pairs.{md,json}` — 실제 캐시 공고만으로 11쌍(가짜 생성 없음):
- 3 `winner_change` + 2 `fit_change_no_winner`(모두 `toss-4076130003`) + 6 `control_no_dups`(backend/devops/ai_ml).
- **한계(중요):** 캐시된 **24개 (persona,job) 중 required/preferred 중복이 탐지되는 공고는 `toss-4076130003`
  단 1개**뿐. 그래서 dedup의 *이득*은 이 한 공고로만 입증되고, 다른 페르소나 쌍은 dedup이 **무해(no-op)** 함을
  확인하는 통제 역할만 한다. 새 중복 사례를 만들려면 더 많은 JD 수집/구조화(LLM 필요)가 있어야 하므로 이번
  범위 밖. → **그래서 dedup은 기본값으로 승격하지 않고 실험 유지.**

---

## 6. 알고리즘 상세

### 6.1 `compute_fit` 1~5 산출 + cap (이번에 dedup 플래그만 추가, 기본 로직 불변)
- 가중 비율 `earned/total` → 레벨: ≥0.80→5, ≥0.62→4, ≥0.42→3, ≥0.22→2, 그 외 1.
- 가중치: type(critical 3 / required 2 / preferred 1 / optional 0.5) × prerequisite_status(prerequisite 1 /
  behavioral_preference 0.4 / product_duty 0.15 / context 0.1) × match_level credit(direct 1 / adjacent .6 / weak .3 / missing 0).
- **cap 사다리(근본 결함 위치):** role-defining critical 미충족 ≥2→cap2, =1→cap3 / required도 동일 / 마이너(툴링)
  critical은 crit_ratio≥0.8이면 cap4. → **critical과 required가 사실상 동급으로 cap** (= §5.4 통합 원인).
- 도메인 거리 cap: strong 5 / adjacent 4 / weak 3 / mismatch 2(증거 없으면 1).

### 6.2 랭킹 모드 정렬 키 (`aggregate`, 미변경)
- `DOM_RANK = strong3/adjacent2/weak1/mismatch0`.
- `domain_fit_bt`: `(-domrank, -fit, -bt, listwise_idx, jid)`
- `fit_primary`: `(-fit, -domrank, -bt, listwise_idx, jid)`
- `bt_primary`: 비교집합은 `(-bt, -fit, -domrank, lw, jid)`, 나머지는 `(-fit, -domrank, lw, jid)`.
- 마지막에 **도메인 우선순위 가드**: mismatch를 모든 non-mismatch 아래로(안정 분할).

### 6.3 골든 페어 평가 지표
- **pairwise(strict):** 분모 = `A_better`/`B_better` 라벨. 시스템이 사람이 고른 쪽을 더 위에 두면 정답.
- **tie-aware:** `tie`도 포함. tie는 시스템이 둘을 near-tie(같은 fit_level)로 보면 정답. `unsure`는 점수 제외.
- 부가: 페르소나/난이도/카테고리별 정확도, 모드 간 불일치 목록, **시스템≠사람**(개선 후보) 목록, unavailable/unsure.
- 데이터 없으면 **재수집하지 않고** unavailable로 보고. 빈 라벨은 "미라벨"로 분리해 graceful skip(전부 미라벨이면 friendly fail).

### 6.4 dedup 탐지 휴리스틱(`detect_required_preferred_dups`, 보수적)
- **교차 타입만**(required/critical ↔ preferred/optional). 텍스트 정규화 후 **containment**(한쪽 핵심 substring) 또는
  **token Jaccard ≥0.6**, 또는 (같은 requirement_category & Jaccard ≥0.4)이면 중복으로 판정.
- 짧은/일반 텍스트(<6자) 스킵. **명백한 필수 표현(필수/반드시/must)이 있으면 유지**(강등 안 함).
- 강등 대상은 **cap 계산에서만 제외**(가중 비율·리포트 행은 그대로). 미충족(missing/weak)인 required 행만 cap에 영향.
- 24개 중 1개 공고에서만 발화(과발화 없음) — `toss-4076130003`의 "레거시 개선"(required/missing) ↔
  "…레거시 개선…있으면 좋아요"(preferred) 중복이 fit 2→3을 만든 핵심.

---

## 7. 최종 실험 결과 (요약 표)
**기준선(baseline) vs dedup, `golden_pairs_20`:**

| 지표 | baseline | dedup_required_preferred |
|---|---|---|
| domain_fit_bt (기본) | 16/20 | **19/20** |
| bt_primary | 15/20 | 15/20 |
| fit_primary | 12/20 | 15/20 |
| 오류 수(헤드라인) | 4 | 1 (dev-04) |
| 회귀 | — | **0** |
| fit 변동 공고 | — | toss-4076130003 (2→3)만 |
| fixture 회귀 | 10/10 | 10/10(불변) |

**남은 오류 1건:** `dev-04`(Network vs Cloud) — 중복 없음 → dedup 무관, **Change C(role-core)** 영역.

---

## 8. 파일 구조

### 8.1 커밋 `61864d2`에 포함된 18개
- **코드:** `src/golden_pairs.py`(신규, ~741줄), `src/rank_aggregate.py`(dedup만 추가, `aggregate` 불변),
  `src/main.py`(golden-pair 커맨드 2개 + `--scoring-mode`).
- **문서:** `docs/GOLDEN_PAIR_EVAL.md`, `docs/SCORING_IMPROVEMENT_PROPOSAL.md`(§6에 ablation 결과·승격 기준).
- **데이터(`data/eval/golden_pairs/`, 13개):** `golden_pairs.template.json`, `golden_pairs.md`,
  `proposed_pairs.{md,json}`, `manual_labeling_packet.{md,json}`, `manual_labeling_packet_10.{md,json}`,
  `manual_labeling_remaining_10.{md,json}`, `golden_pairs_20.json`(사람 라벨), `dedup_validation_pairs.{md,json}`.
- *(이식/문서: `docs/PORTING_GUIDE.md` 와 본 `STATUS_REPORT.md` 는 별도 문서 커밋으로 추가.)*

### 8.2 생성물(gitignore, `outputs/eval/`)
`golden_pair_report.{md,json}`(baseline), `golden_pair_report_dedup_required_preferred.{md,json}`,
`golden_pair_error_analysis.{md,json}`(10쌍), `golden_pair_error_analysis_20.{md,json}`,
`scoring_ablation_required_preferred_dedup.{md,json}`, 그리고 페르소나별 `outputs/eval/<persona>/...`.

### 8.3 절대 커밋 안 함(gitignore 확인됨)
`.env`, `data/resume.md`(PII), `outputs/cache/`·`outputs/latest/`·`outputs/eval/`·`outputs/*.log`, `data/raw/`.

---

## 9. CLI 사용법 (핵심)
```bash
# 회귀(불변식) — 캐시 웜이면 LLM 0회
python -m src.main regression

# 멀티-페르소나 진단(방향성)
python -m src.main eval-resumes --pool-size 50 --limit 6 [--compare-ranking-modes]

# 골든 페어 후보 추출(라벨 안 함)
python -m src.main propose-golden-pairs --from outputs/eval --max-pairs 50

# 골든 페어 정확도 — baseline(기본) / dedup(실험)
python -m src.main eval-golden-pairs --pairs data/eval/golden_pairs/golden_pairs_20.json
python -m src.main eval-golden-pairs --pairs data/eval/golden_pairs/golden_pairs_20.json --scoring-mode dedup_required_preferred
```
> `eval-golden-pairs`/`propose-golden-pairs`는 **LLM을 호출하지 않고** 캐시 산출물만 읽는다. 공고가 산출물에
> 없으면 재수집 없이 unavailable 처리.

---

## 10. 현재 상태(스냅샷)
- **기본 랭킹 모드:** `domain_fit_bt` (불변).
- **기본 스코어링 모드:** `baseline` (`compute_fit` dedup OFF).
- **실험 스코어링 모드:** `dedup_required_preferred` — `eval-golden-pairs --scoring-mode`로만 접근. `run`/`rank`/
  `regression`에는 미연결.
- **HEAD:** `61864d2` (main, origin보다 앞섬, **미push**). 이후 문서 커밋이 추가될 수 있음.
- 검증 수치 재확인: regression 10/10, baseline 16/15/12, dedup 19/15/15.

---

## 11. 알려진 한계 & 다음 단계
1. **표본이 작고 편중:** 골든 20쌍, 오류 4건 중 3건이 동일 공고(`toss-4076130003`)·동일 페르소나.
   dedup 개선도 그 1개 공고에서만. devops role-core는 N=1.
2. **dedup 승격 기준(4개 모두 충족해야 기본화):** (a) 정확도 개선/보존, (b) 비-프론트엔드 페르소나 회귀 0,
   (c) 진짜 필수 요구를 약화시키지 않음, (d) 중복 탐지가 계속 보수적. → 충족 전까지 **실험 유지**.
3. **다음 실험 순서:** 라벨 셋 확장(특히 junior_frontend·devops·same_domain_close, dedup이 다른 공고에서도 이득/
   무해인지 확인) → 그 후 **Change A(연차 가중)** → 필요 시 **Change C(role-core)** 로 `dev-04` 처리.
4. **D(BT 더 쓰기)는 비권장**(BT가 오류의 절반에서 사람과 불일치). 필요하면 close-pair 불확실성 '플래그'만.
5. **dedup 검증 세트 라벨링:** `dedup_validation_pairs.json`의 빈 라벨을 채운 뒤 baseline vs dedup 재비교.

---

## 12. 다른 AI를 위한 빠른 참조
- **무엇이 바뀌었나(이번 세션):** 정확도 평가 인프라(골든 페어) + 실험 스코어링 모드(dedup). **랭킹 sort
  로직·프롬프트·기본 스코어링은 불변.** `aggregate()`는 손대지 않았다.
- **이식하려면:** [`docs/PORTING_GUIDE.md`](docs/PORTING_GUIDE.md) 부터. (옮길 코어 IP / 재구현 / 버릴 것 모듈별 정리)
- **어디를 볼까:**
  - 정확도 수치/오류 목록 → `outputs/eval/golden_pair_report*.{md,json}` (생성물).
  - 오류 근본 원인 → `outputs/eval/golden_pair_error_analysis_20.md`.
  - 개선안·승격 기준 → `docs/SCORING_IMPROVEMENT_PROPOSAL.md`(§6).
  - 평가 방법론 → `docs/GOLDEN_PAIR_EVAL.md`.
  - dedup 안전성 검증 → `data/eval/golden_pairs/dedup_validation_pairs.md` + `outputs/eval/scoring_ablation_*`.
  - 코어 로직 → `src/rank_aggregate.py`(`compute_fit`, cap 사다리, `detect_required_preferred_dups`, `aggregate`),
    `src/golden_pairs.py`(평가/재채점), `src/main.py`(CLI).
- **핵심 한 줄:** "domain_fit_bt 기본값 유지가 맞다(16/20로 3모드 중 최고). 4개 오류는 모두 same_domain_close의
  `compute_fit` 캘리브레이션 문제이지 모드 문제가 아니며, 가장 안전한 부분 수정(dedup)을 실험 플래그로만 넣어
  16→19를 확인했지만 표본 편중 때문에 아직 기본화하지 않는다."
- **하지 말 것:** dedup을 기본으로 승격, 랭킹 sort/프롬프트/기본 compute_fit 변경, LLM 임의 호출, 합격확률/퍼센트
  제품 출력, fit을 1~5 밖으로.
