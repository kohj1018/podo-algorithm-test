# Multi-Resume Eval Suite (Generalization Diagnostic)

## Why this suite exists
The prototype was validated end-to-end against **one real résumé** — a frontend/fullstack
profile (see `docs/ALGORITHM_VALIDATION.md`). A single profile is enough to prove the pipeline
*works*, but not that it *generalizes*. With N=1 it is impossible to tell whether the ranking
logic encodes real fit signal or is quietly **overfit** to one candidate's domain, vocabulary,
and skill list. This suite adds 4 synthetic personas so another engineer can ask: *does the same
algorithm behave sensibly for a backend engineer, a junior frontend, an AI/ML engineer, and a
DevOps/infra engineer — without any algorithm changes?*

## Why N=1 was not enough
- **Domain bias is invisible at N=1.** If every test résumé is frontend, a frontend-favoring bug
  looks like correct behavior.
- **The domain cap, prerequisite-vs-duty, and same-category grouping logic are all domain-relative.**
  They must be exercised from *different* primary domains to confirm they are symmetric.
- **The mismatch guard** (marketing/design/product can never outrank engineering) must hold for
  *every* candidate domain, not just frontend.

This suite does **not** change the algorithm. It only feeds different résumés + per-persona domain
profiles into the existing pipeline and checks coarse, direction-level invariants.

## The 4 personas (all synthetic)
See [`data/eval/personas.md`](../data/eval/personas.md) for full descriptions and
[`data/eval/expected_behavior.json`](../data/eval/expected_behavior.json) for machine-readable
expectations.

| persona | primary domains | tests that… |
|---|---|---|
| `backend_platform` | backend | backend/server roles top a backend résumé; frontend/ML/security stay weak |
| `junior_frontend` | frontend, web | junior frontend ranks frontend top, but **senior (3–5y) frontend roles get a lower fit_level** via experience_level capping (domain stays strong) |
| `ai_ml_application` | ml_ai, ai | AI/ML/RAG roles top; data/backend adjacent; frontend/android weak |
| `devops_infra_security` | devops, cloud, infra | infra/SRE/cloud roles top; security/backend adjacent; frontend/ML weak |

All four also test the universal rule: **marketing/design/product (mismatch) must never outrank a
non-mismatch engineering role.**

> The résumés are SYNTHETIC and marked as such at the top of each file. Unlike `data/resume.md`
> (real, PII, git-ignored), `data/eval/**` contains no personal data and **is** committed.

## How per-persona domains drive the pipeline
`domain_alignment` (`src/rank_aggregate.py`) expands each JD's `role_family` to domain tokens via
`ROLE_FAMILY_TO_DOMAINS`, then compares against the candidate's `primary_domains` /
`secondary_domains`. The eval temporarily sets `config.USER_PRIMARY_DOMAINS` /
`USER_SECONDARY_DOMAINS` from each persona's `expected_behavior.json` entry (and redirects
`config.LATEST_DIR` to `outputs/eval/<persona>/`). Those domain tokens steer **both**:
1. **JD selection tiers** — the domain-aware fetch prioritizes the persona's primary-domain roles.
2. **The fit domain cap** — strong ≤5, adjacent ≤4, weak ≤3, mismatch ≤2.

Because `fullstack` expands to `{fullstack, frontend, backend, web}`, a fullstack JD can resolve to
**strong** (not adjacent) for a frontend or backend persona. The eval treats strong and adjacent
both as non-mismatch, so this is fine.

## How to run

### 0) Cheap check first (no LLM, no cost)
```bash
python -m src.main eval-resumes --dry-run
```
Validates that each résumé has the required sections (Summary / Skills / Experience / Projects /
Education / Preferences) and that every persona has a domain profile, then prints the plan. Use
this to confirm the suite is wired up before spending tokens.

### 1) Full eval (uses real LLM calls — see cost note)
```bash
python -m src.main eval-resumes --resume-dir data/eval/resumes --pool-size 50 --limit 10
```
Runs the **same** pipeline for each persona with per-persona domain-aware JD selection. Outputs:
```
outputs/eval/<persona>/   final_ranking.json, matching_tables.json, pairwise_comparisons.json,
                          final_report.md, fetch_selection_report.md, resume_parsed.json, …
outputs/eval/summary.md   human-readable diagnostic table + per-persona detail
outputs/eval/summary.json machine-readable results (label, invariants, top5, counts)
```

### Useful flags
- `--only backend_platform` — run a single persona (cheapest way to spot-check).
- `--fixture <path.json>` — evaluate every persona against ONE shared, fixed JD set instead of a
  live per-persona fetch (more reproducible, lets you compare personas on identical JDs).
- `--limit N` / `--pool-size P` — JDs evaluated per persona / candidate pool before selection.
- `--refresh-cache` — ignore cached LLM parses (eval uses an isolated `outputs/cache/eval/`
  namespace, so this never touches the normal or fixture caches).

### ⚠️ Cost note
A full 4-persona live run does, per persona: 1 résumé extraction + (≈`limit`) JD structurings +
(≈`limit`) matching calls + (≈`limit`) verifier calls + 1 listwise + several pairwise + (rematch
retries). With `--limit 10` that is on the order of **~150–200 LLM calls across all 4 personas**
on the first (uncached) run. Subsequent runs are mostly cache hits. Prefer `--only` or a small
`--limit` while iterating; run the full suite deliberately.

## How to interpret results
Each persona gets a coarse label:

- **pass** — all invariants hold (or are n/a).
- **warning** — a *direction* invariant bent (e.g. an expected-top family not in top 3, or some
  strong/adjacent role ranked below a weak one). LLM non-determinism can legitimately cause these;
  investigate, but it is not a hard failure.
- **fail** — a **hard product rule** broke. The CLI exits non-zero if any persona fails.

| invariant | severity | meaning |
|---|---|---|
| `extractive` | fail | every surviving evidence quote is verbatim-extractive from the résumé |
| `fit_scale` | fail | every fit value is an integer 1–5 (no percentage / pass-probability fields) |
| `mismatch_priority` | fail | no mismatch (marketing/design/product) role ranks above any engineering role |
| `expected_top_in_top3` | warning | an expected-top role_family appears in top 3 — **n/a** if none was selected |
| `domain_order` | warning | strong/adjacent roles generally outrank weak/mismatch (reports inversion count) |
| `primary_domain_available` | warning | a primary-domain JD was actually present in the live pool |

`n/a` means the live JD pool did not contain the role family needed to test that invariant — itself
a useful signal (e.g. Toss/Daangn rarely list pure `ml_ai` or `security` roles, so the AI persona's
top-family check may be n/a). Use `--fixture` with a hand-built JD set to force coverage.

The summary also reports, per persona: selected role_family distribution, top-5 jobs with fit
levels, whether expected-top families landed in top 3/5, whether any domain inversion occurred,
how many non-extractive matches were removed, and the pairwise disagreement count.

## Ranking-mode ablation (why the default is `domain_fit_bt`)
This eval suite was also used to choose the final-order **ranking mode**. Only the final ordering
changes between modes — every upstream signal (matching/verify/fits/BT/listwise/pairwise) is
identical, and the mismatch-below-non-mismatch guard holds in all of them. Run the comparison with:

```bash
python -m src.main eval-resumes --pool-size 50 --limit 6 --compare-ranking-modes
```

It writes `outputs/eval/ranking_mode_comparison.{md,json}` plus per-persona
`final_ranking_{bt_primary,fit_primary,domain_fit_bt}.json`, reporting for each persona the top 6
under all three modes, **fit-vs-rank inversions** (lower-fit ranked above higher-fit, same
mismatch-partition), **tier inversions** (lower domain tier ranked above higher tier — catches an
adjacent role jumping above a strong primary-domain role), domain inversions, mismatch violations,
and which jobs moved.

The 3-mode comparison found:

| mode | sorting | result across the 4 personas |
|---|---|---|
| `bt_primary` | BT primary, fit/domain as tiebreak | most fit-vs-rank inversions (e.g. junior 4, devops 3); rank often disagrees with the headline fit |
| `fit_primary` | fit_level primary | fit-monotonic (0 fit-rank inversions) **but** introduced a tier inversion — an adjacent backend role outranked the candidate's strong infra roles (devops) |
| **`domain_fit_bt`** | **domain tier → fit → BT** | **0 tier inversions and 0 mismatch violations everywhere**; keeps the legibility win wherever it's free (junior 4→0); equals `bt_primary` where domain order already matters (devops/backend); neutralized the `ai_ml` domain-inversion warning |

**`domain_fit_bt` was selected as the default** because it preserves domain priority (primary-domain
roles stay on top), removes the within-tier fit-vs-rank legibility problem, avoids `fit_primary`'s
strong-role demotion, keeps BT/pairwise as the same-tier/same-fit tiebreaker, and is regression-safe
on the fixture (its three roles sit in distinct tiers, so the order matches the existing invariants).

- **`fit_primary`** remains useful as an optional **"sort by fit"** UI mode.
- **`bt_primary`** remains useful for **debugging/researching pairwise (BT) behavior**.

Both stay selectable via `--ranking-mode`; neither was removed.

## What this eval does NOT prove
- **Not absolute accuracy.** It checks *direction* (which family ranks above which), not whether
  fit 4 vs 5 is "correct."
- **Not pass/acceptance probability.** That is intentionally disabled everywhere; this suite would
  fail (`fit_scale`) if a percentage ever leaked out.
- **Not real hiring outcomes.** Personas are synthetic; expectations are the author's product
  judgment, not ground-truth labels.
- **Not statistical significance.** N=4 synthetic profiles is a smoke/diagnostic suite, not a
  benchmark. Treat `warning`/`fail` as "look here," not as a metric to optimize.

## Next steps after running it
1. Read `outputs/eval/summary.md`; triage any `fail` first (hard rules), then `warning`s.
2. For `warning`s, open that persona's `outputs/eval/<persona>/final_report.md` and check the
   `cap_reason` / pairwise rows to see whether the inversion is a real bug or LLM variance.
3. If a real cross-domain bug appears, add a minimal fixture under `data/fixtures/` that reproduces
   it and (only then) consider an algorithm change — keeping the v0 invariant regression green.
4. Grow the suite: add more personas / edge cases (e.g. career-changer, security specialist) and,
   if you want hard gates, promote stable expectations into the fixture regression.
