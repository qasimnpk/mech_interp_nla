# overnight/ — nightshift rounds 1-5 (side material)

Pre-registered plans (`PLAN.md`), kill-test log (`DISCONFIRMATION.md`), per-round reports (`MORNING*.md`),
per-stage summaries (`*_summary.md`) and the human review sheets (`*_review_blind.csv` with their keys).
The main experiment of the application is in `fve_claims/`.

Three raw generation dumps were removed before sharing to keep the repo small: `k1_texts.jsonl`,
`t3_outputs.jsonl`, `t4_outputs.jsonl`. Every number computed from them is in the matching `*_summary.md`
and `MORNING*.md`; the scripts that produced them are still here (`k1_kway.py`, `t3_steer.py`, `t4_concept.py`).
