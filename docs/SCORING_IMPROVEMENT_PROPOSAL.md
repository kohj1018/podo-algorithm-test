# Scoring Improvement Proposal (diagnosis-driven, NOT implemented)

> **Status: proposal only.** Nothing here is implemented. No ranking mode, scoring logic, prompt,
> extraction, matching, or verifier was changed to write this document, and no LLM was called. It is
> derived entirely from the 20-pair human-labeled golden eval and the cached `outputs/eval/`
> artifacts. Treat every change below as a hypothesis to be built behind an experimental flag and
> validated before it touches the default path. See `outputs/eval/golden_pair_error_analysis_20.md`
> for the per-error evidence this proposal is built on.

## 1. Evidence base
First 20-pair human-labeled golden eval:

| mode | pairwise accuracy |
|---|---|
| **domain_fit_bt (default)** | **16/20** |
| bt_primary | 15/20 |
| fit_primary | 12/20 |

- By persona: ai_ml 4/4 · backend 4/4 · devops 5/6 · **junior_frontend 3/6**.
- By category: adjacent_vs_primary 5/5 · seniority_gap 2/2 · domain_transfer 1/1 · **same_domain_close 8/12**.
- **All 4 `domain_fit_bt` errors are `same_domain_close`** (3× junior_frontend, 1× devops). They are
  `prop-junior_frontend-01`, `-04`, `-06`, and `prop-devops_infra_security-04`.

These numbers are an eval-internal agreement metric (system order vs human label) on a small,
concentrated set — **not** a product fit number and **not** a pass probability.

## 2. Root-cause summary
The four misses share one structural cause in `compute_fit` (`src/rank_aggregate.py`), with three
amplifiers:

1. **Critical and required role-defining gaps cap with near-identical severity.** The cap ladder is
   symmetric: `≥2 role-defining gaps → cap 2`, `1 → cap 3`, applied the same way to *critical* and
   *required* gaps. Consequences:
   - A role with **required-only** gaps cannot beat a role with a **critical** gap → `jf-01`, `jf-04`
     (B has all criticals met but 2 required gaps → capped to 2; A has an unmet critical → capped to 3).
   - A role with **many critical** gaps cannot sink **below** a role with **fewer required** gaps →
     `jf-06`, `dev-04` (A has 3–5 critical gaps, B has 2 required / 3 critical, both floored at 2).
2. **Experience-level (seniority) gaps are not weighted by candidate seniority.** An explicit "3년+"
   (`jf-04`) or "5년+" (`dev-04`) requirement vs a ~6-month-intern persona registers only as a
   `weak`/`missing` match → one role-defining critical gap → cap 3, not low enough.
3. **Role-core vs peripheral gaps are not distinguished.** In `dev-04` the candidate matches
   peripheral tooling (K8s/IaC) but misses **all** role-core networking (BGP/OSPF, packet analysis,
   5y); those role-core misses don't outweigh the peripheral matches. (`compute_fit` only de-weights
   *minor tooling* via `MINOR_CATEGORIES`; it has no positive notion of "role-core.")
4. **Duplicate required+preferred rows double-count.** `toss-4076130003` (the B job in *three* of the
   four errors) lists "레거시 코드 개선" as **both** a `required/missing` row **and** a
   `preferred` "…있으면 좋아요" row. The required copy creates a role-defining required gap that caps B
   to 2, even though the JD itself signals the item is optional.

A fifth, mode-level observation: when fit ties, `domain_fit_bt` breaks the tie with **BT**, and BT
rewards absolute match *volume*. In `jf-06`/`dev-04` BT favored the higher-volume role (A) against
human judgment; in `jf-01`/`jf-04` BT actually agreed with the human (B) but was discarded because
fit (3 vs 2) decided first. So **BT is right about half the time on these errors** — it is not a
reliable lever (see Change D).

## 3. Candidate changes (2–4, prioritized)

### Change B — Required/preferred duplicate cleanup *(highest leverage, lowest risk)*
**What:** In `compute_fit`, before applying caps, detect when the *same capability* appears as both a
`required`/`critical` row and a `preferred`/`optional` row (high text overlap). Collapse the pair:
keep the stricter row only if the wording is unambiguously mandatory; otherwise treat the duplicated
requirement as preferred (so it no longer creates a role-defining *required* gap). Pure scoring-side
dedup — **no prompt/extraction change.**
- **Addresses:** `jf-01`, `jf-04`, `jf-06` (all hinge on `toss-4076130003`'s duplicated "레거시 개선").
- **Expected benefit:** B's cap lifts from 2 toward 3–4 → B passes the fit-3 A roles in `jf-01`/`jf-04`
  and is no longer artificially tied-down in `jf-06`. Potentially +2 to +3 corrected pairs.
- **Overfitting risk:** *Medium.* "Same capability" is a fuzzy text match; an over-eager matcher
  could downgrade a genuinely-required item that merely shares wording with a preferred line. Mitigate
  with a conservative overlap threshold and only downgrade when a preferred twin clearly exists.
- **Metric to improve:** `same_domain_close` accuracy (8/12) and `junior_frontend` persona (3/6).
- **Validate on golden_pairs_20:** re-run `eval-golden-pairs`; expect `jf-01`/`jf-04` → B, `jf-06`
  improved; **require zero regression** on the 16 currently-correct pairs (esp. adjacent_vs_primary
  5/5, seniority_gap 2/2, and all `A_better` pairs).
- **Experimental flag first:** **Yes.**

### Change A — Seniority-gap handling
**What:** Detect explicit years-of-experience requirements ("N년 이상" / "N+ years") in JD rows; compare
against a per-persona estimated experience level; when the candidate is clearly junior and the JD
demands 3+/5+ years, cap more strongly (e.g., an unmet experience-level critical → cap 2 instead of 3).
Do **not** add penalty when the years requirement is `preferred`/`optional`.
- **Addresses:** `jf-04` (3년 vs junior), `dev-04` (5년 network).
- **Expected benefit:** A roles with a hard seniority bar drop below no-bar peers for junior personas
  → fixes `jf-04`, contributes to `dev-04`. +1 to +2 pairs.
- **Overfitting risk:** *Medium–high.* Requires a candidate-experience estimate the pipeline doesn't
  model today; "N년" parsing is brittle (ranges, "이에 준하는", English/Korean). A bad estimate could
  wrongly penalize roles the candidate actually qualifies for. Keep the cap conditional on a
  *confident* junior signal.
- **Metric to improve:** `junior_frontend` persona, `same_domain_close`; watch that `seniority_gap`
  category stays 2/2.
- **Validate on golden_pairs_20:** `jf-04` → B and `dev-04` → B without regressing the 2/2
  seniority_gap pairs or any `A_better` pair.
- **Experimental flag first:** **Yes.**

### Change C — Role-core gap weighting
**What:** Give missing **role-core** requirements more weight than peripheral tool gaps. Maintain a
small per-role-family notion of "core": e.g., network → BGP/OSPF/packet analysis; cloud → cloud
platform/K8s/IaC/operations; for junior frontend, production-ownership / years-of-experience are
treated differently from basic React/TS. A role-core miss caps harder (and/or counts more) than a
peripheral miss.
- **Addresses:** `dev-04` (role-core networking all missing), `jf-06` (operational critical gaps:
  web-service operation, WebSocket/SSE).
- **Expected benefit:** A roles whose *core* is unmet sink below better-core-matched peers → fixes
  `dev-04`, contributes to `jf-06`. +1 to +2 pairs.
- **Overfitting risk:** *High.* A hand-maintained role-core taxonomy is exactly the kind of thing that
  overfits to these JDs and rots as new role families appear. Strongest only if derived from
  requirement metadata already present (e.g., `requirement_nature`/`requirement_category`) rather than
  keyword lists.
- **Metric to improve:** `devops_infra_security` persona, `same_domain_close`.
- **Validate on golden_pairs_20:** `dev-04`/`jf-06` flip; no regression elsewhere. **N for devops is
  only 1**, so confirm with more devops pairs before trusting.
- **Experimental flag first:** **Yes** (and keep it off by default until the taxonomy is validated on a
  larger set).

### Change D — Fit/BT reconciliation for same-domain close pairs *(NOT recommended as an accuracy lever)*
**What considered:** When two roles are in the same domain tier and fit is tied/close, lean on BT more
heavily; or alternatively keep `domain_fit_bt` and merely **flag close-pair uncertainty**.
- **Why not (accuracy):** BT agreed with the human in `jf-01`/`jf-04` (B) but **disagreed** in
  `jf-06`/`dev-04` (A). Using BT more would fix two and break two, and risks regressing currently-correct
  pairs where fit is the better signal. `bt_primary` is already the weaker mode overall (15/20).
- **What is safe:** the **uncertainty-flag** variant — when fit ties within a tier and BT disagrees
  with fit ordering, surface "low confidence / close pair" rather than changing the order. No accuracy
  change, better calibration/UX.
- **Overfitting risk:** *High* for the "use BT more" form; *low* for the flag-only form.
- **Metric:** none directly (flag form); watch overall accuracy doesn't drop if BT-weighting is tried.
- **Validate:** any BT-weighting experiment must show net gain on all 20 (expect mixed). The flag form
  needs only a sanity check that flags land on the genuinely-close pairs.
- **Experimental flag first:** **Yes**; prefer shipping only the flag form, not BT re-weighting.

## 4. Recommended sequencing & guardrails
1. **B first** (single duplicate drives 3/4 errors; scoring-side, no prompt change, lowest risk).
2. **A next** (closes `jf-04`, helps `dev-04`).
3. **C** only if B+A don't resolve `dev-04`/`jf-06`, and only after more devops/role-core pairs exist.
4. **D**: ship the uncertainty-flag form at most; do **not** re-weight BT as an accuracy fix.

**Guardrails for any experiment:**
- Build behind an off-by-default experimental flag; the default path stays `domain_fit_bt` + current
  `compute_fit`.
- Acceptance bar: **strictly improve `same_domain_close` (8/12) with zero regression** on the other 16
  correct pairs, and keep the fixture invariant regression green.
- **Sample caution:** 4 errors, 3 of which share one job (`toss-4076130003`) and one persona; devops is
  N=1. This is enough to *propose* but not to *confirm* — expand the labeled set (more junior_frontend,
  more devops, more `same_domain_close`) so fixes aren't overfit to these four pairs. Treat
  golden_pairs_20 as a guardrail, not a target to maximize.

## 5. Decisions
- **Do not implement now** — diagnosis/proposal only.
- **Keep `domain_fit_bt` as the default.** It is the best of the three modes (16/20), and every error
  is a `compute_fit` calibration issue inside a single tier, not a mode-ordering issue; switching modes
  would lower accuracy (bt_primary 15, fit_primary 12).

## 6. Change B — built as an experiment (ablation result + validation plan)
Change B is now implemented **behind the experimental flag only** (`compute_fit(dedup_required_preferred=…)`
+ `eval-golden-pairs --scoring-mode dedup_required_preferred`). The default scoring path is unchanged.

**Ablation result on `golden_pairs_20`** (re-scored from cached artifacts, no LLM):

| mode | baseline | dedup_required_preferred |
|---|---|---|
| **domain_fit_bt** | **16/20** | **19/20** |
| bt_primary | 15/20 | 15/20 |
| fit_primary | 12/20 | 15/20 |

- **No regressions:** `domain_fit_bt` 16 → 19 with **zero** correct→wrong flips; fixed exactly
  `prop-junior_frontend-01/-04/-06`. `same_domain_close` 8/12 → 11/12; `adjacent_vs_primary` 5/5,
  `seniority_gap` 2/2, `domain_transfer` 1/1 all unchanged. The **only** fit-level change anywhere was
  `toss-4076130003` (2 → 3). Fixture regression stayed green (10/10).
- **Limitation (decisive):** all three improvements come from **one job** (`toss-4076130003`). A scan of
  all 24 cached (persona, job) instances finds **that is the only job with any detected required/preferred
  duplicate** — no backend, devops, ai_ml, or other frontend job currently exercises the dedup path.

**Next validation target:** `data/eval/golden_pairs/dedup_validation_pairs.{json,md}` — a real-data-only
set (no invented pairs) that mixes: dedup winner-change pairs, dedup fit-change-but-not-winner pairs, and
cross-persona **control** pairs (backend/devops/ai_ml) where no duplicate exists and dedup must be a
no-op. Because the artifacts contain only one duplicate job, this set proves *harmlessness* broadly but
can confirm *benefit* only on `toss-4076130003`; confirming benefit elsewhere requires more JDs (a future
collection/structuring pass — out of scope here, as it needs the LLM).

**Promotion criteria (all must hold before `dedup_required_preferred` becomes default):**
1. **Improves or preserves accuracy** on `golden_pairs_20` and the validation set (never lowers it).
2. **No regressions on non-frontend personas** — backend/devops/ai_ml control pairs stay identical to
   baseline (winner and fit unchanged).
3. **Does not weaken truly mandatory requirements** — rows with clearly mandatory wording
   (필수/반드시/must) are kept; only genuinely duplicated, ambiguously-required rows are downgraded.
4. **Duplicate detection stays conservative** — it must keep firing on real duplicates only (no spurious
   groups on unrelated requirements; verified here as 1/24 jobs), with threshold sensitivity checked.

Until then, **`dedup_required_preferred` remains experimental** and is not wired into `run`/`rank`/
`regression`.
