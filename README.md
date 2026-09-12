# Can a natural language autoencoder's reconstruction tell true claims from false ones?

An NLA is a pair of models: a **verbalizer (AV)** turns one activation vector into an English explanation, and a
**reconstructor (AR)** turns that text back into an activation. If the AR needs a claim to rebuild the activation,
deleting that claim should cost reconstruction quality — which is why the NLA paper proposes using the AR as a
weak per-claim verifier. This repo tests that on two open NLA pairs, and asks whether paraphrasing works better.

**Measure.** FVE (fraction of variance explained) = 1 − (squared reconstruction error) / (total variance of the
activations), so 0 means no better than guessing the mean activation. A claim's score is the FVE drop when that
claim is removed from the explanation, in percentage points.

## Headline result

Mean FVE drop, all claim types, irrelevant (forecast) claims excluded:

| | deletion: true | false | Δ | paraphrase: true | false | Δ |
|---|---|---|---|---|---|---|
| 27B (`ceselder/qwen3.6-27b-nla-rl`) | 4.15 | 2.66 | +1.49 | 0.09 | 0.20 | −0.11 |
| 7B (`kitft/nla-qwen2.5-7b-L20`) | 1.58 | 0.94 | +0.64 | 17.29 | 17.51 | −0.22 |

Deleting a true claim costs more reconstruction than deleting a false one, in both models, which reproduces the
paper's finding. Heavy paraphrasing does not separate true from false in either model. The deletion gap comes
almost entirely from claims in the explanation's final sentence, the one describing the activation's own token
(27B +24.5 pp there vs −0.75 elsewhere; 7B +2.0 vs +0.03).

## Setup

- **Data:** 100 Re-DocRED Wikipedia introductions (`data/redocred_pilot/`), each cut to end on a word; the
  activation is read at that last token.
- **Claims:** each explanation is split into atomic claims, labelled true / false / irrelevant against the passage
  and its Re-DocRED annotations (`fve_claims/ANNOTATION_GUIDE.md`). Labels are Claude's, spot-checked by hand.
- **Edits:** a deletion removes one claim's exact text spans (`fve_claims/gen_deletions*.py`, no LLM); a heavy
  paraphrase rewords its whole sentence, keeping every proposition (`fve_claims/REWRITE_GUIDE.md`).
- **27B deviation:** the released 27B pair ships no separate target model, so its AV base weights produce the
  activations, and the FVE denominator is computed from the 100 activations rather than a training corpus.

## Reproducing the headline

```sh
uv run python fve_claims/audit/headline_table.py      # the table above, with document-bootstrap intervals
uv run python fve_claims/audit/random_examples.py     # two random documents: explanation, claims, labels, drops
uv run python fve_claims/audit/make_spotcheck.py      # blind label check; score with score_spotcheck.py
```

## Layout

| path | what |
|---|---|
| `fve_claims/` | the experiment: claims, labels, edits, scores, analysis |
| `fve_claims/analysis_27b/` | one script per reported number (see its README) |
| `fve_claims/audit/` | verification: blind label check, re-derivations, random examples |
| `fve_claims/legacy/` | earlier sentence-level protocol, kept for provenance only |
| `overnight/` | rounds 1–5 of earlier controlled experiments on the 7B pair (side material) |
| `notes/` | protocol, comparison with the paper, review sheets, and the human log |
| `notes/human_log.md` | what the human decided, checked and found by hand |
| `src/`, `scripts/` | model loading, MPS workarounds, dataset build, smoke tests |

Agents wrote most of the code and produced the provisional claim labels; the research decisions, the audits and
the conclusions are the human's. `notes/human_log.md` records which is which.
