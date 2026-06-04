# Pipeline Overview (simple terms)

```
JD pool fetch
→ domain-aware candidate selection
→ resume evidence extraction
→ JD requirement extraction
→ requirement–evidence matching
→ match verification
→ fit level calculation
→ listwise reranking
→ pairwise verification
→ BT aggregation
→ markdown/json report
```

## Stage-by-stage (plain language)
1. **JD pool fetch** — pull many engineering JDs from Toss/Daangn (JSON APIs), not just a few.
2. **Domain-aware candidate selection** — cheaply classify each JD's role family from its title and pick a balanced set that prioritizes the candidate's primary domains (frontend/fullstack), with a few contrast roles.
3. **Resume evidence extraction** — turn the résumé into evidence items, and ALWAYS add a guaranteed Skills item so listed tools are never lost.
4. **JD requirement extraction** — turn each JD into requirements, tagging what is a real *prerequisite* vs an on-the-job *duty*, the requirement nature/category, and any interchangeable `alternatives`.
5. **Requirement–evidence matching** — for each requirement, the model selects supporting **evidence IDs** (not free text).
6. **Match verification** — a conservative pass that can only *lower* a match, catching exaggeration and respecting same-category equivalence.
7. **Fit level calculation** — deterministic 1–5 from verified coverage, with prerequisite-only caps and a visible domain-distance cap.
8. **Listwise reranking** — the model orders the jobs by fit; duplicates/omissions are detected and safely repaired.
9. **Pairwise verification** — top candidates are compared head-to-head in both A/B and B/A order to cross-check.
10. **BT aggregation** — Bradley-Terry turns pairwise outcomes into a relative fit-strength order.
11. **Domain-priority guard** — a final, stable partition so a domain-`mismatch` role (marketing/design/product) can never sit above a non-mismatch engineering role. It does not reorder within either group (BT order is kept); it only pushes mismatch roles below all engineering roles. Moves are logged.
12. **Report** — Markdown + JSON written to `outputs/latest/`.

## Important design principles
- **The LLM does not directly produce a final pass/acceptance probability.** Pass probability is intentionally disabled.
- **The LLM does not produce trusted free-form evidence quotes.** It selects evidence by ID.
- **Evidence quotes are copied verbatim from the parsed resume evidence** (extractive by construction). Non-extractive quotes are stripped.
- **Fit and pass probability are separated concepts.** This system measures fit (적합도) only.
- **Pairwise / Bradley-Terry is used for *relative* fit ranking** among compared jobs — it is a strength score, not a probability.
- **Final fit is a 1–5 level, never a percentage.**
- **Domain priority is enforced:** for this candidate, a domain-`mismatch` role (marketing/design/product) can never outrank a non-mismatch engineering role — this is a deterministic guard applied after BT, not a learned signal.

## Reproducibility
- Every LLM call is cached under `outputs/cache/` keyed by (model + rendered prompt + schema version). A cached run is reproducible; `--refresh-cache` forces a fresh (and possibly slightly different) run.
- **Fixture cache isolation:** `python -m src.main regression` uses a separate namespace `outputs/cache/fixture/`, so full `--refresh-cache` runs (normal namespace `outputs/cache/`) never change the fixture's cached artifacts. The regression stays stable unless the fixture data, prompt version, schema version, or model name changes.
