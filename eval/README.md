# Evaluation Harness (Dev)

## What this checks (rubric-aligned)
- Conditional retrieval:
  - smalltalk/clarify should not cite sources
  - qa/compare/claim_check should cite sources (unless a refusal is expected)
- Conversation behavior:
  - uses session_id per test (isolated)
- Refusal behavior:
  - “no hallucination” expected on some tests

## Run
1) Start backend:
   - uvicorn backend.main:app --reload

2) Run eval:
   - python eval/run_eval.py

Outputs:
- eval/out/results.json (raw responses)
- eval/out/summary.json (scores)

Tip:
- Run this after any code change to confirm you didn’t break routing/citations.
