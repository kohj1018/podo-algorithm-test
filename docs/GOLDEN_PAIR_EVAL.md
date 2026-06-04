# Golden-Pair Evaluation (the first real ranking-accuracy eval)

## Why this exists
The prototype already has three checks, and **none of them measures accuracy**:

| existing check | what it measures | what it canNOT tell you |
|---|---|---|
| fixture regression (`_check_invariants`) | coarse invariants on one fixed 3-JD set (frontend #1, mismatch last, quotes extractive…) | whether *close* pairs are ordered correctly |
| multi-resume suite (`eval_resumes.py`) | direction invariants across 4 personas (domain priority, extractive, 1–5 scale) | whether the better-fit job actually wins |
| ranking-mode ablation | *legibility* (fit-vs-rank inversions, tier inversions) between `bt_primary`/`fit_primary`/`domain_fit_bt` | whether the chosen order matches human judgment |

All of those are **self-consistency** checks: they assert the system obeys its own rules. They have
no external ground truth, so a confidently-wrong ranking that still obeys the rules passes every
one of them. The golden-pair eval adds the missing piece: **human labels**. A human looks at two
jobs for a persona and says which is the better fit (or that it's a tie / unclear). We then measure
how often the system's order agrees with the human. That agreement rate is the first number in this
project that means "accuracy," not "consistency."

It changes **no ranking logic** and makes **no LLM calls** — it only reads the artifacts the
pipeline already wrote under `outputs/eval/<persona>/`.

## Why the synthetic-persona invariants are not enough
The multi-resume suite was built to answer "does the algorithm *generalize* across domains?" and it
does that well. But its invariants are deliberately **coarse and directional**:

- *"mismatch never outranks engineering"* — a hard rule, but it says nothing about two engineering
  roles in the *same* domain.
- *"an expected-top family appears in top-3"* — checks a family is near the top, not that the
  **specific** better role beat the **specific** worse one.
- *"strong/adjacent generally outrank weak/mismatch"* — a tier-direction check; within a tier it is
  silent.

The hard cases in real ranking are exactly the ones these invariants don't touch:
two backend roles where one has a seniority gap; a strong-domain role with a weak fit vs an
adjacent-domain role with a strong fit; the same company's frontend vs backend opening. The only
way to know if the system gets those right is to **label them and check**. Synthetic invariants
prove the system is *reasonable*; golden pairs test whether it is *right* on the close calls.

## The label set
`A_better`, `B_better`, `tie`, `unsure` (see `data/eval/golden_pairs/golden_pairs.md` for the full
table). Two accuracy numbers come out of this:

- **pairwise accuracy (strict)** — denominator is the decisive pairs (`A_better`/`B_better`) where
  both jobs exist in the artifacts. A pair is correct when the mode ranks the human-preferred job
  higher. This is the headline accuracy.
- **tie-aware accuracy** — also includes `tie` pairs. A `tie` counts as correct when the system
  shows a **near-tie** (the two jobs share the same `fit_level`), i.e. it did *not* fabricate a
  strong distinction the human doesn't see. This rewards calibrated humility on genuine ties.

`unsure` pairs are never scored — they're listed in the report so you can revisit them.

## How to label pairs
1. **Generate candidates (no LLM, no labels):**
   ```bash
   python -m src.main propose-golden-pairs --from outputs/eval --max-pairs 50
   ```
   Reads `outputs/eval/<persona>/` and surfaces the *hard* pairs worth a human's time (see the
   heuristics below). It writes `data/eval/golden_pairs/proposed_pairs.json` and a readable
   `proposed_pairs.md`. Every candidate has `expected_winner: ""` — **the tool never labels.**

2. **Label each pair.** Open the persona's `outputs/eval/<persona>/final_report.md`, read the two
   jobs' matched/unmet requirements, and fill in `expected_winner` + a short, extractive
   `label_reason`. By convention **A = the job the default mode ranks higher**, so `A_better` means
   you agree with the system and `B_better` means you'd flip it. Adjust `difficulty`/`category` if
   the auto-suggested values are off.

3. **Save & run.** Save your labeled file as `data/eval/golden_pairs/golden_pairs.json` and run:
   ```bash
   python -m src.main eval-golden-pairs --pairs data/eval/golden_pairs/golden_pairs.json
   ```

You can also hand-write pairs from scratch — copy `golden_pairs.template.json` (it has 3
illustrative labeled examples that run as-is against the `backend_platform` artifacts) and edit.

### What `propose-golden-pairs` looks for (hard-pair heuristics)
Each candidate fires one or more of these (all read only from cached artifacts):

- **same role_family + same tier + close fit** (`|Δfit| ≤ 1`) → `same_domain_close`
- **adjacent-domain fit ≥ primary(strong)-domain fit** (does primary still win?) → `adjacent_vs_primary`
- **same tier, exactly one has an `experience_level` prerequisite gap** → `seniority_gap`
- **`domain_fit_bt` and `bt_primary` order the pair in opposite directions** (modes disagree)
- **headline `fit_level` and the pairwise Bradley-Terry order disagree** (both pairwise-compared)
- **same company, similar/cross-discipline roles** → `same_domain_close` / `domain_transfer`
- **mismatch vs a weak engineering role** → `mismatch_guard` (low-priority sanity pair)

Candidates are ranked by a "hardness" score (mode/BT disagreements and adjacent-over-primary rank
highest) and capped at `--max-pairs`; the report states how many were dropped so the cap is never
silent.

## How to run the evaluator
```bash
python -m src.main eval-golden-pairs --pairs data/eval/golden_pairs/golden_pairs.json
# optional: --eval-dir <root>   (default outputs/eval)
```
- **No LLM, no fetching.** It reads `outputs/eval/<persona>/final_ranking_{bt_primary,fit_primary,
  domain_fit_bt}.json` (falling back to `final_ranking.json` for the default mode) and
  `pairwise_comparisons.json`.
- **Missing data is reported, never re-fetched.** If a persona has no artifacts, or a labeled
  `job_*_id` isn't in that persona's ranking, the pair is marked **unavailable** and excluded from
  accuracy (listed in the report). Run `eval-resumes` first to (re)generate the artifacts.

Outputs: `outputs/eval/golden_pair_report.md` and `…report.json`.

## How to interpret the results
The report has these sections:

1. **Accuracy by mode** — pairwise(strict) and tie-aware for `bt_primary` / `fit_primary` /
   `domain_fit_bt` (the ⭐ headline). Compare modes here: if `domain_fit_bt` matches human labels
   more often than the others, that's empirical support for it being the default.
2. **By persona / by difficulty / by category** — where the system is strong or weak. Expect
   `hard` and `same_domain_close`/`adjacent_vs_primary` to be the lowest; that's where ranking is
   genuinely difficult.
3. **Mode disagreements** — pairs the three modes order differently. These are the highest-signal
   pairs for choosing/justifying the default.
4. **System ≠ human** — decisive pairs the headline mode got wrong. **This is the to-do list.**
   Each row shows the human label, the system's pick, both fits, and the per-mode winners, so you
   can tell whether it's a real ranking bug or a defensible close call.
5. **unsure / unavailable** — excluded pairs, for follow-up.

Reading guidance:
- **Look at fractions, not just %.** With a small set, one pair swings the percentage a lot — the
  report always prints `correct/total`.
- **A `tie` you got "wrong"** means the system made a hard distinction (different `fit_level`) where
  you saw a tie. That's a *calibration* signal, not necessarily a misorder.
- **`unavailable` is a data problem, not an accuracy problem** — regenerate artifacts and re-run.
- The accuracy `%` is an **eval-internal agreement metric** (system order vs your labels). It is
  **not** a fit score and **not** a pass/acceptance probability; fit stays on the 1–5 scale.

## Why this is the first *real* accuracy eval
Up to now, "good" meant "obeys our invariants." That can be satisfied by a system that is
internally consistent and externally wrong. Golden pairs introduce an **external oracle** (human
judgment) and a **metric of agreement** with it. For the first time the question is not "did we
break a rule?" but "**did we rank the better job higher?**" — measured, sliced by difficulty and
category, and compared across ranking modes. It starts tiny (that's fine — it's a seed set), but it
is the first eval whose number can go *down* when the ranking gets *worse* on real judgment, which
is exactly what an accuracy benchmark must do.

## What it still does NOT prove
- **Not statistical significance** — a seed set of hand-labeled synthetic pairs, not a benchmark.
  Grow it before trusting small differences.
- **Not real hiring outcomes** — personas and labels are synthetic product judgment.
- **Not absolute fit calibration** — it tests *relative* order within a pair, not whether "fit 4"
  is objectively right.
- **Label quality is the ceiling.** Garbage labels → meaningless accuracy. Keep `label_reason`
  extractive and JD-relative, and prefer `unsure` over a coin-flip.
