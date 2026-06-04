# Porting Guide — 이 레포를 당신의 서비스로 옮기기

> **대상 독자:** 이 프로토타입의 적합도(fit) 랭킹 알고리즘과 플로우를 **다른(실서비스) 코드베이스로
> 이식**하려는 AI/엔지니어. "무엇이 핵심 IP라 반드시 옮겨야 하는가 / 무엇은 개념만 옮기고 프로덕션용으로
> 다시 만들 것인가 / 무엇은 버릴 프로토타입 스캐폴딩인가"를 모듈 단위로 정리합니다.
>
> 함께 읽기: 전체 현황은 [`../STATUS_REPORT.md`](../STATUS_REPORT.md), 파이프라인은
> [`PIPELINE_OVERVIEW.md`](PIPELINE_OVERVIEW.md), 평가 방법론은 [`GOLDEN_PAIR_EVAL.md`](GOLDEN_PAIR_EVAL.md)
> / [`EVAL_SUITE.md`](EVAL_SUITE.md), 스코어링 개선 로드맵은
> [`SCORING_IMPROVEMENT_PROPOSAL.md`](SCORING_IMPROVEMENT_PROPOSAL.md).

---

## 0. 30초 요약
- **이 시스템의 본질:** "이력서 ↔ JD 적합도"를 블랙박스 점수가 아니라, **추출형 근거가 붙고 · 환각이 걸러지고
  · 1~5로 보수적으로 캘리브레이션된 *감사 가능한 랭킹*"** 으로 만든다. **합격확률/퍼센트를 출력하지 않는다.**
- **반드시 옮길 자산 5가지:** (1) 데이터 계약 `models.py`, (2) fit·랭킹 코어 `rank_aggregate.py`,
  (3) 7개 LLM 프롬프트 `prompts/`, (4) 추출형-검증 신뢰 레이어 `verify_matches.py`,
  (5) **골든 페어 평가 프레임워크** `golden_pairs.py`(+ `eval_resumes.py`).
- **다시 만들 것:** 수집·LLM 호출·캐시·저장·CLI·리포트 출력(프로토타입은 로컬 파일/콘솔, 프로덕션은 DB/큐/API).
- **버릴 것:** Toss/Daangn 스크레이퍼, 합성 페르소나(테스트 픽스처), 윈도우 cp949 우회, rich 콘솔 UI.

---

## 1. 멘탈 모델 — 이게 무엇이고 무엇이 아닌지
- **무엇인가:** 한 후보(이력서)에 대해 N개의 JD를 받아 **적합도 순으로 정렬**하고, 각 공고마다
  *왜 그 순위인지*(충족/미충족 요건, 추출형 인용, cap 사유, fit 1~5)를 설명하는 결정적 랭커.
- **무엇이 아닌가:** 합격 예측기가 아니다. fit은 확률이 아니라 **검증된 요구 커버리지 기반의 보수적 레벨**이다.
  Bradley-Terry 점수도 "비교된 공고들 사이의 상대 강도"일 뿐 확률이 아니다.
- **결정성:** 동일 입력 + 동일 캐시 = 동일 출력. LLM 단계는 캐시·재시도·구조화 출력 검증으로 감싼다.

---

## 2. 핵심 IP 4계층 + 평가 하니스 (왜 이게 가치인가)
1. **추출형 근거 + 보수적 verifier (반환각 레이어).** 모든 매칭은 이력서 원문의 **verbatim 인용**으로
   뒷받침되고, verifier가 비추출/과장 매칭을 **강등(낮추기만)** 한다. 채용 도메인에서 신뢰·공정성·설명가능성의 핵심.
   → `verify_matches.py`, `matching.py`, 프롬프트 `match_verifier.md`.
2. **prerequisite vs product_duty 구분.** JD 요구를 "입사 전 이미 갖춰야 하는 것(prerequisite, fit을 cap)"과
   "입사 후 할 일(product_duty, cap 금지)"로 분류. *책임(responsibility)으로 후보를 깎지 않는* 것이 정확도의 핵심.
   → `models.py`의 `PREREQ_STATUSES`, 프롬프트 `jd_extract.md`.
3. **`compute_fit`: 확률 아닌 1~5 + caps.** 가중 커버리지 비율 → 레벨, 그 위에 도메인 거리 cap과 role-defining
   갭 cap. → `rank_aggregate.compute_fit`.
4. **도메인 tier → fit → BT → listwise 정렬 + mismatch 하드 가드.** 기본 모드 `domain_fit_bt`.
   → `rank_aggregate.aggregate`, `domain_alignment`, `bradley_terry`.
5. **(과소평가 금물) 평가 하니스.** 불변식 회귀 + 멀티-페르소나 일반화 + 모드 ablation + **골든 페어(사람 라벨)
   정확도**. *스코어링을 안전하게 진화시키는 메커니즘* — 실서비스에서 가장 큰 차별점. → `golden_pairs.py`, `eval_resumes.py`.

---

## 3. 모듈 단위 이식 지도 (`src/`)
범례: **🟢 그대로 옮김(코어 IP)** / **🟡 개념만 옮기고 프로덕션용 재구현** / **🔴 버림(프로토타입 스캐폴딩)**

| 모듈 | 줄수 | 역할 | 이식 | 메모 |
|---|---:|---|:--:|---|
| `models.py` | 315 | Pydantic 스키마(데이터 계약) | 🟢 | **가장 먼저 옮길 것.** 모든 단계가 이 계약 위에 돎 (§4) |
| `rank_aggregate.py` | 467 | `domain_alignment`·`compute_fit`(+dedup)·`bradley_terry`·`aggregate`(3모드)·가드 | 🟢 | **알고리즘 본체.** §5 |
| `verify_matches.py` | 155 | 추출형 검증 + 보수적 verifier | 🟢 | 신뢰 레이어 — 절대 생략 금지 |
| `golden_pairs.py` | 741 | 골든 페어 평가 + `rescore_persona`(저장물로 재채점) | 🟢 | 평가 하니스. `rescore_persona`는 "저장된 산출물로 fit 재계산"의 레퍼런스 |
| `eval_resumes.py` | 533 | 멀티-페르소나 방향성 진단 | 🟢 | 일반화 테스트 방법론 |
| `parse_resume.py` | 148 | 이력서→evidence(+결정적 Skills 항목) | 🟡 | 개념+프롬프트 옮김; PDF/DOCX 파서·실 LLM 인프라로 재구현 |
| `parse_job.py` | 90 | JD→요구사항 구조화 | 🟡 | 개념+프롬프트(`jd_extract`) 옮김 |
| `matching.py` | 184 | 요구↔근거 ID 기반 매칭 + rematch | 🟡 | 개념+프롬프트(`requirement_evidence_match`,`rematch_evidence`) 옮김 |
| `rerank_listwise.py` | 142 | listwise 재랭킹(누락/중복 보정) | 🟡 | 개념+프롬프트(`listwise_rerank`) |
| `compare_pairwise.py` | 65 | A/B·B/A 교차 pairwise | 🟡 | 개념+프롬프트(`pairwise_compare`) |
| `llm.py` | 188 | provider 추상화(OpenAI/Anthropic)·재시도·파라미터 적응 | 🟡 | 프로덕션 LLM 게이트웨이로 교체(개념 유지) |
| `cache.py` | 101 | 파일 캐시 = sha256(model+prompt+SCHEMA_VERSION), 네임스페이스 | 🟡 | **캐시 키 개념은 유지**, 저장소는 Redis/DB로 |
| `config.py` | 107 | 경로·env(provider/model)·도메인 토큰·`SCHEMA_VERSION` | 🟡 | `USER_PRIMARY_DOMAINS` 하드코딩 → 프로덕션은 **후보별** 값으로 |
| `report.py` | 304 | 사람용 리포트 작성기 | 🟡 | 리포트 *필드*(매칭/결손/인용/cap사유/fit)는 유지, 출력은 API/DB로 |
| `main.py` | 1112 | CLI 오케스트레이션 | 🟡 | 단계 시퀀스가 *명세*. 서비스 오케스트레이션으로 재구현 |
| `fetch_jobs.py` | 429 | Toss/Daangn 수집 + 도메인 인지 선택 | 🔴 | 스크레이퍼 버림. ATS/잡보드 연동으로 대체. 선택 휴리스틱은 선택적 |

> **랭킹 로직(`aggregate`의 정렬)·프롬프트·기본 `compute_fit`은 이번 평가/dedup 작업에서 일절 바뀌지 않았다.**
> dedup은 실험 플래그(§6)일 뿐 기본 경로가 아니다.

---

## 4. 데이터 계약 (`models.py`) — 반드시 보존할 스키마
이식의 출발점. 핵심 enum(이 분류가 알고리즘 정확도를 만든다):

- **`Requirement` / `MatchRow`** 의 4대 필드:
  - `requirement_type`: `critical | required | preferred | optional` (가중치 3/2/1/0.5)
  - `requirement_nature`: `technical | domain | experience_level | behavioral | language | location | employment | other`
    (`CORE_NATURES = {technical, domain, experience_level, language}` 만 fit을 gate)
  - `prerequisite_status`: `prerequisite | product_duty | context | behavioral_preference`
    (**오직 prerequisite만 강하게 cap**; 가중치 1 / 0.15 / 0.1 / 0.4)
  - `match_level`: `direct | adjacent | weak | missing` (credit 1 / .6 / .3 / 0)
  - 보조: `requirement_category`(같은-카테고리 툴 그룹: state_management/styling/data_fetching/build_tooling/testing/
    framework/language/other — `MINOR_CATEGORIES`는 갭이어도 "마이너/툴링"으로 덜 cap), `alternatives`(OR 그룹).
- **`FitResult`**: 최종 출력 계약 — `fit_level`(1~5), `fit_label`, `bt_score`, `coverage`(cap 사유 포함),
  `strong_matches` / `weak_or_missing` / `preferred_gaps` / `product_duties` / `invalid_matches` / `risk_notes`.
- **`ROLE_FAMILY_TO_DOMAINS`**: role_family → 도메인 토큰 매핑(예: `fullstack → {fullstack,frontend,backend,web}`).
  도메인 tier 산출의 근거. 당신 도메인 분류 체계에 맞게 재작성하되 *tier 4단계(strong/adjacent/weak/mismatch)는 유지*.

---

## 5. 알고리즘 상세 (충실히 재구현할 부분)
**`compute_fit(table, alignment)` (`rank_aggregate.py`):**
1. 각 행 가중치 = `type가중 × prerequisite_status가중 × match_level credit`(confidence=low면 ×0.7). 합산 → `earned/total`.
2. 비율 → 레벨: ≥0.80→5, ≥0.62→4, ≥0.42→3, ≥0.22→2, 그 외 1.
3. **cap 사다리:** role-defining(=마이너 아님) critical 미충족 ≥2→cap2 / =1→cap3; required도 동일; 마이너 critical만
   남고 crit_ratio≥0.8이면 cap4. *(주의: 이 critical/required 동급 처리가 골든 페어가 드러낸 캘리브레이션 약점 — §7.)*
4. **도메인 거리 cap:** strong 5 / adjacent 4 / weak 3 / mismatch 2(증거 없으면 1).

**랭킹 (`aggregate`, `DOM_RANK = strong3/adjacent2/weak1/mismatch0`):**
- `domain_fit_bt`(기본): `(-domrank, -fit, -bt, listwise_idx, jid)`
- `fit_primary`: `(-fit, -domrank, -bt, listwise_idx, jid)`
- `bt_primary`: 비교집합 `(-bt, -fit, -domrank, lw, jid)` + 나머지 `(-fit, -domrank, lw, jid)`
- 마지막 **도메인 우선순위 가드**: mismatch를 모든 non-mismatch 아래로(안정 분할). **하드 규칙 — 반드시 이식.**

**Bradley-Terry (`bradley_terry`):** 순수 파이썬 MM 반복(scipy 불필요). pairwise A/B·B/A 결과로 상대 강도 추정.

---

## 6. 평가 하니스 — 이것도 함께 옮겨라 (실서비스의 안전장치)
스코어링을 바꿀 때마다 "정확도가 올랐나/회귀 없나"를 자동으로 확인하는 게이트다.

- **불변식 회귀** (`main._check_invariants`): 고정 픽스처에서 제품 규칙(프론트 #1, mismatch 최하위, 추출형 등) 검사.
- **멀티-페르소나 진단** (`eval_resumes.py`): 여러 도메인 합성 이력서로 *방향성* 일반화 점검.
- **골든 페어 정확도** (`golden_pairs.py`): 사람이 라벨링한 A/B 쌍과 시스템 순위 일치율 — **유일한 외부 정답 기반 정확도**.
  - 핵심 함수: `load_pairs`(라벨 검증, 빈 라벨=미라벨 분리), `evaluate_pairs`, `aggregate_metrics`(pairwise/tie-aware,
    페르소나·난이도·카테고리별, 모드 불일치, 시스템≠사람), `rescore_persona`(저장 산출물만으로 fit 재계산 + 실제
    `aggregate` 재사용 → **LLM 없이 스코어링 변경을 ablation**).
  - 후보 자동 추출: `propose_pairs` (라벨은 안 달고 하드 케이스만 제안).
- **프로덕션 적용:** 도메인별 골든셋을 만들고 **CI 게이트**로 건다("정확도 보존/개선 + 회귀 0"이 아니면 스코어링 변경 차단).

---

## 7. 옮기기 *전에* 반드시 보완할 것 (골든 페어가 드러낸 약점)
20쌍 골든 평가: `domain_fit_bt` **16/20**(baseline). 오류 4건 **전부 same_domain_close**. 근본 원인:
1. **cap 대칭 결함:** critical 갭과 required 갭을 동급으로 cap → 크리티컬을 다 채운 공고가 required-only 갭 공고에
   밀리거나, critical 다수 갭이 required 소수 갭 아래로 못 내려감.
2. **후보 연차(seniority) 미모델링:** "3년+/5년+" 요구 vs 주니어를 제대로 못 깎음. 프로덕션이라면 **후보 경력 추정**이
   1급 피처여야 함.
3. **role-core vs 주변 도구 갭 미구분:** 네트워크 BGP/OSPF, 클라우드 K8s/IaC 같은 *역할 본질* 갭의 가중 부족.
4. **required/preferred 중복 이중 계산** → 이게 가장 안전한 부분 수정(아래 dedup).

**dedup (Change B) = 실험 스코어링 모드:** `compute_fit(dedup_required_preferred=True)` + `eval-golden-pairs
--scoring-mode dedup_required_preferred`. 같은 20쌍에서 **16→19, 회귀 0**. 단 개선 3건이 모두 한 공고에서 나와
**기본값 승격 보류, 실험 유지**. 승격 4조건: (a) 정확도 개선/보존, (b) 비-프론트엔드 회귀 0, (c) 진짜 필수 요구를
약화 안 함, (d) 탐지가 계속 보수적. 자세한 내용·후보 A/C/D는 [`SCORING_IMPROVEMENT_PROPOSAL.md`](SCORING_IMPROVEMENT_PROPOSAL.md).

> **권고:** 코어 알고리즘은 그대로 옮기되, *프로덕션 스코어링을 신뢰하기 전에* 위 1·2번을 당신 도메인의 골든셋으로
> 검증·보완하라. dedup은 실험 플래그로만 들여오고, 기본화는 골든셋 확장 후 4조건 충족 시에만.

---

## 8. 프로덕션 아키텍처 매핑
```
[Ingest]  이력서 PDF/DOCX→텍스트 · JD(ATS/Greenhouse/Lever API)        ← fetch_jobs 대체
   → [Extract] 이력서 evidence + JD 요구 구조화(prereq vs duty)         ← parse_resume/parse_job + 프롬프트
   → [Match]   요구↔근거 ID 매칭 + rematch                              ← matching + 프롬프트
   → [Verify]  보수적 verifier(비추출 인용 제거)                         ← verify_matches  (신뢰 레이어, 필수)
   → [Score]   compute_fit (1~5 + caps)                                ← rank_aggregate  (코어)
   → [Rank]    listwise + pairwise(BT) + domain_fit_bt + 가드            ← rank_aggregate  (코어)
   → [Serve]   랭킹 API + 리포트(매칭/결손/추출 인용/cap 사유/fit 1~5)    ← report 필드 유지
   → [Eval]    골든 페어 정확도 + 불변식 회귀를 CI 게이트로               ← golden_pairs/eval_resumes
```
**횡단 관심사:** 구조화 출력 검증(Pydantic), 캐시(Redis/DB, 키=model+prompt+schema_version), 작업 큐,
관측(비용/지연/정확도 대시보드), PII 처리, 감사 로그(dedup_audit/cap_reason 포함).

---

## 9. 두 가지 이식 체크리스트
**(A) 최소 이식 — "코어 랭킹만"**
- [ ] `models.py` 스키마 이식(또는 동등 계약)
- [ ] 7개 프롬프트(`prompts/`) 이식
- [ ] `parse_resume`/`parse_job`/`matching`/`verify_matches`/`rerank_listwise`/`compare_pairwise` 개념 재구현
- [ ] `rank_aggregate`(domain_alignment·compute_fit·bradley_terry·aggregate·가드) **그대로 이식**
- [ ] LLM 게이트웨이 + 구조화 출력 검증 + 캐시

**(B) 신뢰 가능한 프로덕션 — 추가로**
- [ ] 골든 페어 평가 + 불변식 회귀를 **CI 게이트**로
- [ ] 후보 연차(seniority) 추정 피처 추가(§7-2)
- [ ] cap 캘리브레이션을 도메인 골든셋으로 재검증(§7-1)
- [ ] 공정성/편향 점검·설명가능성(채용 규제 대응) — "fit은 합격확률 아님"·추출형 근거·감사 로그가 *제품 요건*
- [ ] PII 처리·접근통제·데이터 보존 정책

---

## 10. 용어집 (빠른 참조)
- **fit (적합도):** 1~5 정수. 합격확률 아님.
- **prerequisite vs product_duty:** 입사 전 보유 vs 입사 후 수행. 전자만 cap.
- **role-defining gap:** 마이너/툴링이 아닌 핵심 미충족 — cap을 크게 떨어뜨림.
- **domain tier:** strong/adjacent/weak/mismatch (JD role_family vs 후보 도메인).
- **BT (Bradley-Terry):** pairwise 비교 기반 상대 강도. 동점 타이브레이크.
- **domain-priority guard:** mismatch는 비-mismatch 위로 못 옴(하드 규칙).
- **golden pair:** 사람이 라벨한 A/B 적합도 비교 = 외부 정답. 정확도 측정 단위.
- **dedup_required_preferred:** required/preferred 중복을 cap에서만 제외하는 **실험** 스코어링 모드.
- **SCHEMA_VERSION:** 캐시 무효화 키의 일부(프롬프트/스키마 변경 시 캐시 자동 폐기).
