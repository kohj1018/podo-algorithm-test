# Job–Resume Fit Ranking Prototype

내 이력서와 **Toss / Daangn 실제 채용 공고**를 입력으로, LLM 기반 파이프라인이
지원자–공고 **적합도(fit)** 를 1~5단계로 평가하는 로컬 CLI 프로토타입입니다.

> **제품 규칙 (중요)**
> - 합격 확률을 예측하지 **않습니다.**
> - `"합격확률 73%"` 같은 퍼센트를 출력하지 **않습니다.**
> - 오직 **적합도(fit 적합도)** 만 평가합니다.
>
> **적합도 레벨**
> - 5 = 매우 높음: 강력 추천
> - 4 = 높음: 추천
> - 3 = 보통: 검토 가능
> - 2 = 낮음: 아쉬움
> - 1 = 매우 낮음: 비추천

> **이 레포를 당신의 서비스로 이식하려면 → [`docs/PORTING_GUIDE.md`](docs/PORTING_GUIDE.md) 부터 읽으세요.**
> (무엇이 핵심 IP라 그대로 옮길지 / 무엇은 개념만 옮겨 재구현할지 / 무엇은 버릴 스캐폴딩인지 모듈 단위 정리.)

## Validated prototype status
**상태: 알고리즘 검증 완료 + 정확도 평가 도입 (2026-06-04, OpenAI / GPT-5.4 mini).**
- **검증(v0):** 단일 실 이력서로 파이프라인 end-to-end 검증.
- **일반화 + 기본 모드:** 4개 합성 페르소나 진단 + 3-모드 ablation → 기본 정렬 `domain_fit_bt` 채택.
- **정확도(최신):** 사람이 라벨링한 **골든 페어 20쌍** 기준 — `domain_fit_bt` **16/20**, `bt_primary` 15/20,
  `fit_primary` 12/20. (실험 스코어링 모드 `dedup_required_preferred`로는 19/20, 회귀 0 — 단 표본 편중으로 **기본값
  미승격, 실험 유지**. → `docs/SCORING_IMPROVEMENT_PROPOSAL.md`)
- 정확도 %는 *평가 내부 지표*(시스템 vs 사람 라벨 일치율)이며 제품 fit/합격확률이 아닙니다.

### 문서 지도 (Doc map)
| 문서 | 내용 |
|---|---|
| [`docs/PORTING_GUIDE.md`](docs/PORTING_GUIDE.md) | **다른 서비스로 이식하는 법** (모듈별 옮김/재구현/버림, 데이터 계약, 아키텍처 매핑) |
| [`STATUS_REPORT.md`](STATUS_REPORT.md) | 전체 현황·과정·실험 결과 종합(특히 `986dd24` 이후) |
| [`docs/PIPELINE_OVERVIEW.md`](docs/PIPELINE_OVERVIEW.md) | 파이프라인 단계 상세 |
| [`docs/ALGORITHM_VALIDATION.md`](docs/ALGORITHM_VALIDATION.md) | v0 알고리즘 검증 근거 |
| [`docs/EVAL_SUITE.md`](docs/EVAL_SUITE.md) | 멀티-페르소나 진단 + 3-모드 ablation |
| [`docs/GOLDEN_PAIR_EVAL.md`](docs/GOLDEN_PAIR_EVAL.md) | 골든 페어(사람 라벨) 정확도 평가 방법론 |
| [`docs/SCORING_IMPROVEMENT_PROPOSAL.md`](docs/SCORING_IMPROVEMENT_PROPOSAL.md) | 스코어링 개선안(A~D) + dedup ablation 결과·승격 기준 |
| [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md) | 다음 단계 |

**회귀(불변식) 검사 실행:**
```bash
python -m src.main regression          # 고정 픽스처에 대한 제품 수준 불변식 검사(캐시 사용)
```

**10-JD 실측 테스트 실행:**
```bash
python -m src.main run --limit 10 --pool-size 50 --refresh-cache
```

**출력 위치:** `outputs/latest/`
- `final_report.md` (사람이 읽는 리포트) · `final_ranking.json` · `matching_tables.json` · `pairwise_comparisons.json`
- `fetch_selection_report.{md,json}` (후보 선택) · `resume_skills_debug.json` · `listwise.json`
- 캐시: `outputs/cache/`

**현재 검증된 동작:**
- 이 이력서에 대해 **frontend 역할이 상위를 지배**하고, adjacent/weak/mismatch 역할은 그 아래로 정렬됩니다.
- **도메인 우선순위 가드:** mismatch 도메인(marketing/design/product) 역할은 비-mismatch(엔지니어링) 역할 위로 올라갈 수 없습니다. 기본 정렬 `domain_fit_bt` 에서는 비-mismatch 파티션 안을 도메인 tier→fit→BT 순으로 정렬합니다(아래 "랭킹 모드" 참고).
- **합격 확률/퍼센트 없음**, fit은 **1~5 레벨만**.
- 살아남은 **모든 evidence 인용은 추출형(extractive)** — 이력서에서 그대로 복사.
- listwise 누락/중복 보정, pairwise A/B·B/A 교차검증, BT 상대 적합도 집계, 캐시 기반 재현성.
- **픽스처 캐시 격리:** `regression` 은 `outputs/cache/fixture/` 네임스페이스를 사용하므로, `run --refresh-cache` 전체 실행이 회귀 골든을 흔들지 않습니다.

**과도하게 해석하지 말 것 (주의):**
- fit 레벨은 **합격 확률이 아니며**, BT 점수는 **비교된 공고 간 상대 적합도 강도**일 뿐입니다.
- 절대 fit 수치는 `--refresh-cache` 재실행 시 LLM 추출 변동으로 **달라질 수 있습니다**(캐시된 동일 실행은 재현됨). 회귀는 정확한 수치가 아니라 **불변식**으로 검증합니다.
- 같은-카테고리 라이브러리 그룹화는 LLM 추출에 따라 가끔 달라질 수 있습니다(알고리즘 결함이 아닌 LLM 비결정성).

## 파이프라인 단계
1. `data/resume.md` 읽기
2. Toss / Daangn 공식 채용 페이지에서 SW 엔지니어링 공고 수집 (JSON API)
3. 각 JD를 요구사항으로 구조화 (중요도는 숫자가 아닌 `critical/required/preferred/optional` 분류)
4. 이력서를 evidence item 으로 구조화
5. 공고별 요구사항–근거 매칭 테이블 생성
6. 모든 매칭 인용이 **이력서에서 그대로 추출(extractive)** 됐는지 검증 + 보수적 LLM verifier
7. 압축된 매칭 테이블로 LLM **listwise 재랭킹**
8. 상위 공고에 대해 **A/B · B/A 순서 교차 pairwise 비교**
9. **Bradley-Terry**(순수 파이썬) 로 상대 적합도 강도 집계
10. **도메인 우선순위 가드 + 랭킹 모드**(기본 `domain_fit_bt`)로 최종 정렬 → **1~5 적합도** 랭킹 출력 (퍼센트 없음)

## 랭킹 모드 (ranking modes)
최종 정렬 방식은 선택 가능합니다. **업스트림 신호(매칭/검증/fit/BT/listwise/pairwise)는 모드와 무관하게 동일**하고,
**최종 순서만** 달라집니다. 모든 모드에서 mismatch(marketing/design/product) 역할은 비-mismatch 위로 올라갈 수 없습니다.

- **`domain_fit_bt`** — **기본값, 권장 제품 정렬.** 도메인 우선순위 가드 → 도메인 tier(strong>adjacent>weak>mismatch)
  → fit_level 내림차순 → BT 점수 → listwise 순위 → 결정적 fallback. 주력 도메인 역할을 항상 위에 두면서,
  **같은 tier 안에서는 fit이 높은 공고가 위**로 와 순위와 fit 숫자가 일치합니다. BT/pairwise 는 같은 tier·같은 fit 의
  타이브레이커로 계속 사용됩니다. (특정 도메인을 강제하지 않으며, 각 후보의 도메인 프로파일을 따릅니다.)
- **`bt_primary`** — pairwise/BT 중심의 연구·디버그용 정렬(v0 원래 기본값). BT가 1차 키, fit/도메인은 동점 타이브레이커.
- **`fit_primary`** — 순수 fit 레벨 정렬("fit 기준 정렬" UI 옵션으로 유용). fit이 1차 키지만, adjacent 역할이
  strong 주력 도메인 역할 위로 올라갈 수 있어 기본값으로는 권장하지 않습니다.

3개 모드의 ablation 비교 근거는 `docs/EVAL_SUITE.md` 와 `outputs/eval/ranking_mode_comparison.md` 참고.
`eval-resumes` 에서 `--ranking-mode <mode>` 로 선택하거나 `--compare-ranking-modes` 로 세 모드를 한 번에 비교할 수 있습니다.

## 요구 사항
- Python 3.10+ (3.11+ 권장)
- LLM API 키 1개: `ANTHROPIC_API_KEY` (우선) 또는 `OPENAI_API_KEY`

## 설치 & 실행
```bash
# 1) 이력서 준비: data/resume.md 를 본인 이력서로 채웁니다.
#    (플레이스홀더로 생성된 경우, 내용 교체 후 맨 위 <!-- RESUME_PLACEHOLDER --> 줄 삭제)

# 2) 환경 변수
cp .env.example .env          # Windows PowerShell: Copy-Item .env.example .env

# 3) .env 에 API 키 + 모델 추가 (모델은 env 로 선택, 코드에 하드코딩하지 않음)
#    OPENAI_API_KEY=sk-...
#    OPENAI_MODEL=gpt-5.4-mini
#    (Anthropic 사용 시: ANTHROPIC_API_KEY=sk-ant-...  /  ANTHROPIC_MODEL=...)

# 4) 의존성 설치
pip install -r requirements.txt
#    (uv 사용 시: uv pip install -r requirements.txt)

# 5) 준비 점검 (provider/model/resume/prompts + 실제 LLM 핑)
python -m src.main doctor

# 6) 전체 파이프라인 실행
python -m src.main run

# 7) 결과 확인
#    outputs/latest/final_report.md
```

## 개별 명령
```bash
python -m src.main doctor          # 프리플라이트: 설정 + 실제 LLM 연결 핑
python -m src.main fetch-jobs      # 공고만 수집 (LLM 키 불필요) → data/raw/jobs/
python -m src.main parse-resume    # 이력서 evidence 추출
python -m src.main rank            # 이미 수집된 공고로 랭킹만 수행
python -m src.main run             # 전체 (수집 → 랭킹 → 리포트)
python -m src.main regression      # 픽스처 불변식(invariant) 회귀 검사

# 평가 (LLM 키 필요: eval-resumes / 불필요: propose·eval-golden-pairs는 캐시 산출물만 읽음)
python -m src.main eval-resumes --pool-size 50 --limit 6 [--compare-ranking-modes]   # 멀티-페르소나 진단
python -m src.main propose-golden-pairs --from outputs/eval --max-pairs 50            # 골든 페어 후보 추출(라벨 안 함)
python -m src.main eval-golden-pairs --pairs data/eval/golden_pairs/golden_pairs_20.json                                 # 정확도(기본=baseline)
python -m src.main eval-golden-pairs --pairs data/eval/golden_pairs/golden_pairs_20.json --scoring-mode dedup_required_preferred   # 실험 스코어링 ablation

# 도메인 인지 선택: 큰 후보 풀에서 사용자 도메인 기준으로 균형 선택
python -m src.main run --limit 10 --pool-size 50 --refresh-cache
python -m src.main fetch-jobs --pool-size 50 --selection-report   # LLM 없이 선택 미리보기

# 고정 3-JD 회귀 테스트(픽스처)
python -m src.main regression                                     # 불변식 검사(권장)
python -m src.main run --fixture data/fixtures/original_3_jds.json --refresh-cache
```

## 도메인 인지 후보 선택 (domain-aware selection)
- `--pool-size`(기본 50)로 더 큰 후보 풀을 먼저 수집한 뒤, `--limit` 만큼 **균형 선택**합니다(비싼 LLM 단계 전에 값싼 휴리스틱으로 선별).
- 제목 기반 휴리스틱으로 `role_family`를 임시 분류(LLM 파싱 role_family가 최종 권위).
- 사용자 도메인 기준 tier: primary(frontend/fullstack) · adjacent(backend/devops_infra/android/ios) · weak(ml_ai/data/security) · mismatch(marketing/design/product).
- 약 5 primary + 3 adjacent + 1~2 weak(대조군)으로 선택. 주력 도메인 직무가 없으면 리포트에 명시.
- 선택 내역: `outputs/latest/fetch_selection_report.{md,json}`.

## 재현성(캐시) & 회귀 픽스처(불변식 기반)
- 모든 LLM 파싱 결과(이력서·JD·매칭·검증·listwise·pairwise)는 `outputs/cache/` 에 캐시됩니다. 키 = (모델 + 렌더된 프롬프트 + SCHEMA_VERSION). 프롬프트/이력서/JD/모델/스키마가 바뀌면 자동 무효화됩니다.
- 기본 동작: 캐시가 있으면 재사용(재현 가능). `--refresh-cache` 로 강제 재파싱.
- `data/fixtures/original_3_jds.json` = 고정 3-JD(Android 디바이스 SWE / Frontend / Content Marketer 인턴) 회귀 픽스처.
- **회귀는 정확한 fit 수치(예: 5/2/1)를 요구하지 않고 제품 수준 불변식으로 검사**합니다 (`python -m src.main regression`):
  - Frontend 가 #1, Frontend fit ≥ 4
  - Android 가 Frontend 보다 아래(rank), Android fit ≤ 3, 그리고 Android fit < Frontend fit
  - Marketing 이 최하위, Marketing fit ≤ 2
  - **mismatch 도메인 역할은 어떤 비-mismatch 역할보다도 위에 올 수 없음** (domain-priority guard)
  - 살아남은 모든 evidence 인용은 추출형(extractive)
  - pairwise A/B vs B/A 불일치는 보고되어야 하며 최상위 랭킹을 바꾸지 않아야 함

### 회귀 검사 철학 (중요)
- 회귀는 **정확한 fit 레벨이 아니라 제품 수준 불변식**(순위 관계, 도메인 우선순위, 추출형 인용 등)을 검증합니다.
- **프롬프트/스키마가 개선되면 절대 fit 수치는 정당하게 변동**될 수 있습니다 (예: Skills evidence recall 개선으로 이력서의 실제 Android/Kotlin/모바일 근거가 드러남).
- **근거 recall 개선은 인접 도메인(adjacent) 역할의 fit를 합당하게 올릴 수 있습니다** — 예: Android가 fit 2 → fit 3("검토 가능")로 상승. 이는 버그가 아니라 더 정확해진 결과이며, Frontend보다 낮게 유지되는 한 허용됩니다. 따라서 Android 불변식을 `≤ 2`에서 `≤ 3`(+ `< Frontend fit`)로 재설정했습니다.

## 요구사항 분류: prerequisite vs product duty
- JD의 각 요구사항은 `prerequisite_status`(prerequisite | product_duty | context | behavioral_preference)와 `requirement_origin`을 가집니다.
- **입사 전 보유해야 하는 사전 역량(prerequisite)** 만 적합도를 강하게 제한(cap)합니다.
- **입사 후 수행할 업무(product_duty, 예: "POS 제품 개발")** 와 도메인 배경(context), 일반 성향(behavioral_preference)은 랭킹을 깎지 않습니다(설명에만 사용).

## 모델 선택 (LLM)
- provider 는 `.env` 의 키로 자동 선택됩니다(둘 다 있으면 Anthropic 우선). `LLM_PROVIDER` 로 강제 지정 가능.
- 모델은 **환경변수로만** 지정합니다: `OPENAI_MODEL`, `ANTHROPIC_MODEL`. 비즈니스 로직에는 모델명을 하드코딩하지 않습니다.
- OpenAI 호출은 모델 계열별 파라미터 차이(`max_tokens` ↔ `max_completion_tokens`, 고정 temperature 등)를 자동 감지·적응합니다.

## 출력물 (`outputs/latest/`)
| 파일 | 설명 |
|---|---|
| `final_report.md` | 사람이 읽는 최종 리포트 (랭킹/사유/강점/약점/리스크/pairwise/수집 이슈) |
| `final_ranking.json` | 최종 적합도 랭킹 (구조화) |
| `matching_tables.json` | 검증까지 끝난 요구사항-근거 매칭 테이블 |
| `pairwise_comparisons.json` | pairwise 결과 + Bradley-Terry 점수 |
| `resume_parsed.json`, `jobs_parsed.json`, `matching_tables_raw.json`, `listwise.json` | 단계별 중간 산출물(검수용) |

## 공고 수집 동작
- Toss: `api-public.toss.im` 채용 API, Daangn: Greenhouse Board API 에서 JSON 으로 가져옵니다(둘 다 Greenhouse 기반). **Playwright 불필요.**
- 제목이 타깃 키워드(software engineer, frontend, backend, fullstack, web, intern, 인턴, 프론트엔드, 백엔드, 소프트웨어 엔지니어, 웹)에 매칭되는 공고만, 두 회사에서 균형 있게 **최대 10건** 수집합니다.
  - 키워드는 `.env` 의 `TARGET_KEYWORDS`(쉼표 구분)로 덮어쓸 수 있습니다.
- 원본은 `data/raw/jobs/<job_id>.{json,html}` 로 저장됩니다.
- 수집이 실패하면 `data/jobs_manual.md` 에 JD를 직접 붙여넣어 동일 파이프라인을 돌릴 수 있습니다.

## 설계 메모
- 구조화 출력은 모두 **Pydantic** 모델로 검증하며, LLM이 잘못된 JSON을 주면 **1회 재시도**합니다.
- 모든 매칭 인용은 **추출형(extractive)** 강제: 이력서 텍스트(또는 파싱된 evidence)에 실제로 존재하지 않는 인용은 제거되고 해당 매칭은 강등됩니다.
- verifier 는 **보수적**입니다(개인 프로젝트 배포 ≠ 대규모 프로덕션 운영, 학교 과제 ≠ 실무 경험 등). 매칭 수준을 **올리지 않고 낮추기만** 합니다.
- Bradley-Terry 점수는 비교된 공고들 사이의 **상대 적합도 강도**일 뿐, **합격 확률이 아닙니다.** (scipy 불필요 — 순수 파이썬 MM 반복, Elo 대체 구현도 포함)

## 디렉터리 구조
```
.
├── README.md / .env.example / requirements.txt
├── STATUS_REPORT.md                  # 전체 현황 종합 보고서
├── data/
│   ├── resume.md (PII, gitignore) / jobs_manual.md / raw/jobs/ (gitignore)
│   ├── fixtures/                     # 회귀 픽스처 (original_3_jds.json)
│   └── eval/                         # 평가용 (모두 합성/공개 데이터)
│       ├── resumes/ · personas.md · expected_behavior.json   # 멀티-페르소나 진단
│       └── golden_pairs/             # 골든 페어 정확도 평가(라벨/후보/검증 세트)
├── outputs/                          # 생성물 (gitignore: latest/ cache/ eval/)
├── prompts/  (resume_extract, jd_extract, requirement_evidence_match,
│              rematch_evidence, match_verifier, listwise_rerank, pairwise_compare)
├── docs/     (PORTING_GUIDE, PIPELINE_OVERVIEW, ALGORITHM_VALIDATION, EVAL_SUITE,
│              GOLDEN_PAIR_EVAL, SCORING_IMPROVEMENT_PROPOSAL, NEXT_STEPS)
└── src/  (config, llm, cache, fetch_jobs, parse_resume, parse_job, matching,
           verify_matches, rerank_listwise, compare_pairwise, rank_aggregate,
           report, main, models, eval_resumes, golden_pairs)
```
> 참고: 공유 Pydantic 스키마는 `src/models.py` 에 모았습니다(순환 import 방지). 평가 모듈(`eval_resumes`,
> `golden_pairs`)은 `main` 을 import 하지 않는 순수 함수라 import 사이클이 없습니다. 이식 시 모듈별 우선순위는
> [`docs/PORTING_GUIDE.md`](docs/PORTING_GUIDE.md) §3 표를 참고하세요.
