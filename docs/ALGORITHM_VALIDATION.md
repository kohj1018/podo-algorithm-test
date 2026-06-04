# Algorithm Validation — Resume↔JD Fit Ranking (Prototype v0)

- **Validation date:** 2026-06-04
- **Model used:** OpenAI / **GPT-5.4 mini** (`OPENAI_MODEL=gpt-5.4-mini`; selected via env, not hardcoded)
- **Goal:** evaluate **resume–JD fit 적합도 only**. It does **NOT** predict pass/acceptance probability.
- **Fit scale:** **1–5 only** (no percentages, no probability)
  - 5 매우 높음: 강력 추천 · 4 높음: 추천 · 3 보통: 검토 가능 · 2 낮음: 아쉬움 · 1 매우 낮음: 비추천

## Final validated pipeline
1. **Fetch a larger JD pool** from Toss/Daangn (`--pool-size`, default 50; engineering-keyword filtered).
2. **Domain-aware candidate selection** — heuristic `role_family` per title, balanced pick (~5 primary / 3 adjacent / 2 weak-contrast); primary (frontend/fullstack) prioritized.
3. **Resume extraction with a guaranteed Skills evidence item** — LLM evidence **plus** a deterministic, code-first Skills item per Skills bullet (verbatim `exact_quote`), so explicitly-listed tools are never dropped.
4. **JD prerequisite-vs-duty extraction** — each requirement carries `requirement_type`, `requirement_nature`, `prerequisite_status` (prerequisite | product_duty | context | behavioral_preference), `requirement_category`, and `alternatives`. Only prerequisites can cap fit.
5. **Requirement–evidence matching by `evidence_id`** — the LLM selects evidence IDs only; it does **not** write quotes.
6. **Extractive quote filling from evidence IDs** — the code copies each selected evidence item's `exact_quote` verbatim, so every quote is extractive by construction. One targeted re-match retry recovers `missing`/`weak` critical/required same-category groups.
7. **Verifier** — conservative; may only lower match levels; understands same-category equivalence and old/student-project evidence.
8. **Listwise reranking** — with duplicate/omission detection, one stricter re-ask, and fit/domain-aware safe placement.
9. **Pairwise A/B and B/A comparison** — order-swap cross-check on a bounded candidate set (listwise top-K + fit≥4 + strong-domain rescue; comparison-only, never a forced rank).
10. **Bradley-Terry aggregation** — pure-python relative fit-strength among compared jobs (NOT a probability). Tie-breakers: fit_level → domain_alignment → listwise rank.
11. **Domain-priority guard** — a thin, stable final-order partition so a `mismatch`-domain role (marketing/design/product) can never outrank a non-mismatch (engineering) role. BT/pairwise order is preserved **within** each partition; the guard only moves mismatch roles below all non-mismatch roles. Any moved job is logged (`domain_priority_guard_moves`).
12. **Invariant regression** (`python -m src.main regression`) — asserts product-level invariants, not exact fit levels. Runs in an **isolated fixture cache namespace** (`outputs/cache/fixture/`) so full `--refresh-cache` runs never drift the golden.

## What was validated
- **Frontend roles dominate the top rankings** for this resume (frontend/web/fullstack is the candidate's primary domain).
- **Adjacent/weak roles rank below strong frontend roles** (android/devops/data/ml/security do not outrank a strong frontend fit).
- **No pass probabilities and no percentages** anywhere in the output.
- **All surviving evidence quotes are extractive** (verbatim from `data/resume.md` / parsed evidence; non-extractive quotes are stripped/invalidated).
- **Listwise duplicate/omission handling exists** (re-ask + fit-aware placement; observed handling a real duplicate).
- **Cache-based reproducibility works** — a given cached run is byte-reproducible (`outputs/cache/`).

### Regression invariants (current)
- Frontend ranks #1; Frontend fit ≥ 4
- Android ranks below Frontend; Android fit ≤ 3; Android fit < Frontend fit
- Marketing ranks last; Marketing fit ≤ 2
- **A mismatch-domain role must not rank above any non-mismatch role** (enforced by the domain-priority guard)
- All surviving evidence quotes are extractive
- Pairwise A/B vs B/A disagreements are reported and do not change the top ranking

## Current known limitations (acceptable for prototype v0)
- **Cross-run fit-level variance** can occur after `--refresh-cache` (LLM extraction/matching is non-deterministic even at temperature 0). A given cached run is reproducible.
- **Same-category library grouping may still vary by LLM extraction** — e.g. a frontend role's library list (Recoil/Emotion/Vitest…) is sometimes grouped (→ higher fit) and sometimes split (→ lower fit). The grouping logic is correct; the LLM applies it inconsistently.
- Within an all-same-domain top cluster, fit labels need not be strictly monotonic with rank, because pairwise/BT (relative strength) is the primary order key by design.
- These are LLM-determinism properties for a prototype; the **ranking direction and frontend dominance are stable**.

### Resolved (previously open) robustness items
- **Domain priority is now deterministically enforced** by the domain-priority guard (step 11): a `mismatch`-domain role can no longer outrank a non-mismatch engineering role, so "Marketing ranks last" holds on every parse. BT is **not** replaced — it still orders within each partition.
- **Cache coupling is resolved** via fixture cache isolation: the regression uses `outputs/cache/fixture/`, so full `--refresh-cache` runs (normal namespace `outputs/cache/`) never drift the golden.

## Bottom line
The fit-ranking algorithm is **validated and frozen for prototype v0**. It produces stable, product-sensible, extractive, reproducible (per cached run) fit rankings on the 1–5 scale; pass-probability prediction is intentionally **disabled**; domain priority is deterministically enforced; and the invariant regression is isolated and green. Remaining variance (cross-run absolute fit levels, occasional same-category grouping differences) is inherent LLM non-determinism, acceptable for v0, and does not affect ranking direction or the invariants.
