# Golden pairs — human-labeled accuracy set

This folder holds the **first real accuracy eval** for the ranking prototype. Everything else in
the repo checks *direction* and *legibility* (does a mismatch role stay below engineering roles? is
fit monotonic within a tier?). None of it can say whether the system puts the **better-fit** job on
top of a genuinely close pair, because there was no ground truth. A *golden pair* is that ground
truth: two jobs (for one persona) plus a **human judgment** of which is the better fit.

> All résumés/personas here are **synthetic** (see `../personas.md`). The labels are a human's
> product judgment over the *synthetic* profiles — not real hiring outcomes.

## Files
| file | what it is |
|---|---|
| `golden_pairs.template.json` | the schema + 3 illustrative labeled examples (copy this to start) |
| `golden_pairs.json` | **you create this** — your labeled pairs (this is what the evaluator reads) |
| `proposed_pairs.json` / `.md` | auto-suggested **unlabeled** hard candidates (from `propose-golden-pairs`) |
| `../../../docs/GOLDEN_PAIR_EVAL.md` | full rationale, run guide, and how to read the results |

## The label set
| label | meaning | scoring |
|---|---|---|
| `A_better` | job A is the better-fit role; system should rank A above B | counted (strict + tie-aware) |
| `B_better` | job B is the better-fit role; system should rank B above A | counted (strict + tie-aware) |
| `tie` | genuinely too close to call | counted in **tie-aware** only; "correct" iff the system shows a near-tie (same fit_level) |
| `unsure` | you can't decide | **excluded** from scoring (reported only) |

## Each pair's fields
See `golden_pairs.template.json` `_schema`. The required ones are `pair_id`, `persona`,
`job_a_id`, `job_b_id`, `expected_winner`. The rest (`*_title`, `*_company`, `label_reason`,
`difficulty`, `category`) are for human readability and per-slice accuracy breakdowns.

`difficulty`: `easy | medium | hard`. `category` is one of:

| category | the pair tests… |
|---|---|
| `same_domain_close` | two roles in the same family/tier with near-identical fit — which fit really wins |
| `adjacent_vs_primary` | an adjacent-domain role vs a primary-domain role (does primary win even at equal/higher adjacent fit?) |
| `seniority_gap` | same domain, one role has an unmet `experience_level` prerequisite |
| `domain_transfer` | different engineering families (e.g. backend vs ml_ai) |
| `tool_stack_gap` | same role, differs mainly by tool/framework coverage |
| `product_duty_vs_prerequisite` | a gap that is a product duty vs one that is a true prerequisite |
| `weak_vs_adjacent` | a weak-domain role vs an adjacent-domain role |
| `mismatch_guard` | a mismatch role (marketing/design/product) vs an engineering role (guard sanity) |

## How to label (workflow)
1. Generate candidates from the existing eval artifacts (no LLM, no labels):
   ```bash
   python -m src.main propose-golden-pairs --from outputs/eval --max-pairs 50
   ```
   This writes `proposed_pairs.json` (+ a readable `proposed_pairs.md`). Every candidate has
   `expected_winner: ""` — **the system does not label them**.
2. For each pair, open the persona's `outputs/eval/<persona>/final_report.md` and read the two
   jobs' matched/unmet requirements. Decide `A_better` / `B_better` / `tie` / `unsure` and write a
   short, extractive `label_reason`. (A = the job the default mode ranks higher, so `A_better` =
   you agree with the system, `B_better` = you would flip it.)
3. Save your labeled file as `golden_pairs.json` and run the evaluator:
   ```bash
   python -m src.main eval-golden-pairs --pairs data/eval/golden_pairs/golden_pairs.json
   ```
   It writes `outputs/eval/golden_pair_report.{md,json}` with pairwise / tie-aware accuracy per
   ranking mode and breakdowns by persona / difficulty / category, plus the **system≠human** list
   (the pairs to investigate).

## Guardrails when labeling
- Judge **fit to the JD's requirements**, not company prestige or guessed hiring bar.
- Base `label_reason` on what the résumé actually contains vs what the JD requires (extractive).
- Use `tie` honestly — a system that refuses to invent a distinction on a true tie should score
  *well*, not be punished.
- fit is on the **1–5** scale only; there is no pass probability anywhere. The accuracy `%` the
  evaluator prints is an eval-internal agreement metric, not a product number.
