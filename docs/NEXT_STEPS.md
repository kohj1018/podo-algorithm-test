# Next Steps

The fit-ranking algorithm is validated for prototype v0. These are forward-looking; none are required for the algorithm itself.

## Section A — Product / UI next
- Design the final report UI (web or app surface) on top of the existing JSON outputs.
- Show **top recommendations** (ranked list with fit level 1–5 + label).
- Show **why matched** (strong direct matches per job).
- Show **weak/missing requirements** (prerequisite gaps; device/role-defining gaps).
- Show **evidence quotes** (the extractive quotes backing each match).
- Show **confidence / warnings** (downgrades, invalid matches, listwise notes, domain alignment).
- Keep the product rule visible in the UI: **fit only, no pass probability, no percentages.**

## Section B — Engineering next (not now)
- Later, migrate this Python prototype into a **worker service** (keep the pipeline as-is).
- A **NestJS API** can call the worker **asynchronously** (job queue / task status).
- Store **raw JD/resume** in **S3** later.
- Store **structured outputs** (parsed evidence, matching tables, rankings) in **PostgreSQL** later.
- Add **OpenSearch / pgvector** later for larger-scale JD retrieval.
- (Prototype intentionally has none of these — local files + on-disk cache only.)

## Section C — Future algorithm improvements (after v0)
- **Few-shot examples for same-category library grouping** in `jd_extract` — make grouping fire deterministically so a frontend role's library list doesn't swing between grouped (higher fit) and split (lower fit).
- **Model comparison:** GPT-5.4 mini vs Gemini 2.5 Flash vs Claude Sonnet (extraction recall + matching consistency + cost).
- **Score calibration** — only after **real user outcome data** exists.
- **Learning-to-Rank** — only after enough labeled outcomes are collected.
- **Pass probability must remain DISABLED** until real outcome data exists to calibrate it. Fit (적합도) and pass probability stay separate.
