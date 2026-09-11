# Round 4 — experiment setup (for advisor review)

Written 2026-09-09 from the committed artifacts (`overnight/*_settings.json`, `overnight/MORNING4.md`, `overnight/DISCONFIRMATION.md`). Every number below traces to those files. Results are quoted only where needed to describe what the setup produced; the labels are provisional (agent-judged) until the blind review sheets are checked.

## 0. Common setup (all round-4 stages)

- **Models.** TARGET = Qwen/Qwen2.5-7B-Instruct, used only to produce activations (never as an LLM in round 4). AV = `kitft/nla-qwen2.5-7b-L20-av` (verbalizer: the activation is injected at the prompt's marker token, rescaled to norm 150, and the model writes an `<explanation>`). AR = `kitft/nla-qwen2.5-7b-L20-ar` (reconstructor: 21-layer backbone + linear value head that maps an explanation back to a 3584-d vector).
- **Activation.** Output of transformer block 20 (`hidden_states[21]`) at one token position, batch 1, bf16 on MPS, raw text without a chat template.
- **Score.** `s(h, z) = cos(h, AR(z))`, cosine between the true activation and the reconstruction from text `z`. Reconstruction movement `V(z, z0) = 1 − cos(AR(z), AR(z0))`.
- **Decoding.** B1 and A1 verbalize with sampling (temperature 1.0, top-p 1, top-k off) and a recorded seed, one explanation per activation; D1 uses greedy decoding; K1 generates nothing new.
- **Editor / judge.** Every language judgement (entailment label, single-fact correction, fact swap, corruption, edit check, paraphrase, paraphrase-equivalence) was made by the orchestrating agent (Claude Fable 5.1) through a task-file protocol: the script writes tasks without any score, the agent answers, the script validates. Labels carry `label_source=claude` and are provisional; each stage wrote a blind review sheet (no scores, no labels) and a separate key for the human.
- **Truth.** Defined narrowly for the whole round: a sentence is *entailed* or *contradicted* by the visible prefix (tokens 0..t) alone, never by world knowledge; *undetermined* covers format/genre/"what comes next" claims. Each label quotes a verbatim evidence span from the prefix (found verbatim in 98 % of A1 originals).
- **Statistics.** 95 % CIs from a cluster bootstrap (1000 draws, seed 0) by the stage's cluster unit; three-way outcome MET / NOT MET / INCONCLUSIVE, INCONCLUSIVE also when n is below the stage minimum.
- **Cut rules** applied at V0 from measured costs: A1 paraphrases 2+2 → 1+1 (light1, aggr1), A1 negation candidate dropped, A1 contexts 60 → 40; B1 fillings 5 → 4 (64 contexts). No threshold changed.

## 1. B1 — controlled paired contexts (human-designed; primary controlled test)

**Question.** Does the reconstructor's preference between two competing meanings A and B reverse when the source fact changes?

- **Data (synthetic, frozen in PLAN.md).** 4 families × 2 templates × 4 fillings = 32 pairs = 64 contexts. Each context = a fixed two-sentence preamble ("The following entry was copied from the archive without changes. It was checked once for completeness and once for accuracy, and nothing in it was altered.") + a family background + one fact sentence (version A or B) + "The record ends here." A and B differ only in the fact.
  - F1 entity (slot type *entity*): who received the parcel / which technician calibrated the sensor (names swapped).
  - F2 relation/order (*detail*): who arrived before whom; which of two events came first.
  - F3 number (*detail*): "exactly six/nine glass vials"; "lasted exactly twenty/forty minutes".
  - F4 outcome/polarity (*detail*): upload succeeded/failed; application approved/rejected.
  - dev = filling 0 (16 contexts, 8 pairs); eval = fillings 1–3 (48 contexts, 24 pairs).
- **Position.** The final "." of "The record ends here.", t = 55–67 tokens (all ≥ 50, the released pair's training minimum); the token id at t is identical within every pair; cos(h_A, h_B) mean 0.993 (min 0.968).
- **Generation.** One sampled explanation per context (seed 5000 + 2·pair + {0,1}); 64/64 parsed, 0 CJK.
- **Slot detection.** Split each explanation into sentences (quote-aware); drop "final token / expecting / continu…" snippet sentences; any remaining sentence containing a family keyword (the two names; before/after/earlier/later/first + the event nouns; digits, number words, the item noun, "minutes"; the polarity words and stems) is a candidate slot and gets a `slot_verify` judgement (asserts A / B / neither). Eligible carrier = exactly one asserting sentence.
- **Planned downstream (pre-registered, not reached).** `fact_swap` of the asserting sentence to the other meaning (accepted only if an edit check finds exactly one fact changed and a second `slot_verify` returns the other meaning); 4 paraphrases per meaning (two light, two aggressive) with equivalence judged in a shuffled batch; a deletion baseline; 11 texts per carrier substituted at the sentence's character span and scored against both h_A and h_B; statistic D = [μ_A(h_A) − μ_B(h_A)] − [μ_A(h_B) − μ_B(h_B)], cluster by pair, minimum 32 eligible eval carriers.
- **What happened.** 192 sentences, 8 keyword hits, 0 assertions: every explanation described the closing sentence or the record format, so 64/64 carriers were omissions (no insertion arm by design). Only the unedited explanations were scored: s(h_own) mean 0.839, s(h_other) 0.837. **B1 INCONCLUSIVE by n (0 < 32).**
- **Breakdowns available.** By family, and entity (F1) vs detail (F2–F4); all empty here.

## 2. A1 — natural AV claims (human-designed; primary natural test)

**Question.** Can paraphrase-averaged reconstruction scores identify factual errors the verbalizer actually makes?

- **Data (fresh; chosen before any AV output was seen).** wikitext-2 train documents (`EleutherAI/wikitext_document_level`, `wikitext-2-raw-v1`) not among the round-1 stimuli and ≥ 256 TARGET tokens (410 candidates), permuted with seed 4; for each document the largest t in [127, 255] whose token is a sentence-final ".", "!" or "?" followed by whitespace or a capital; context = tokens 0..t (198–256 tokens), raw text. First 40 passing documents: dev = contexts 0–9, eval = 10–39. 0 documents skipped.
- **Generation.** One sampled explanation per context (seed 4000 + id); 40/40 parsed, 5 contained CJK characters.
- **Slots (rule-located, then verified).** Drop snippet sentences and sentences under 6 words. *Entity slot* = first sentence with a capitalised non-initial token outside a stoplist (Wikipedia, Wiki, English, The, This, A, An, In, It, Its, I, Final, months, weekdays); focus word = that token. *Detail slot* = first other sentence with a digit or English number word, else with a relation word (before, after, first, last, earlier, later, during, until, since, succeeded, failed, won, lost, born, died, founded, released, defeated, elected, became, moved, married). At most two slots per context → 54 slots (37 entity, 17 detail); 3 contexts had no slot.
- **Verification.** `slot_verify`: does the sentence make a checkable claim involving the focus word? 50 yes, 4 no (focus words "Wikipedia-style" ×2, "On", "UK"). A repeated-fact check for the 2 slots whose focus word recurred in another sentence found the same fact asserted → `fact_repeated`, ineligible.
- **Truth labels of the originals** (label task with the full prefix): 51 contradicted, 2 entailed, 1 undetermined (entity 35 / 2 / 0; detail 16 / 0 / 1). Eligible slots 47 (31 entity, 16 detail).
- **Correct meaning per slot.** The original if entailed (1 slot), otherwise a single-fact correction (task with the passage: "change only the incorrect fact to the value the passage supports"), accepted only if an edit check confirms exactly one fact changed *and* a fresh label returns entailed: 46 correction tasks → 19 "no single-fact correction exists" (NONE), 27 candidates → 11 passed the one-fact check, 20 labelled entailed → **7 valid corrections**. Slots with a correct meaning: 8 (4 dev, 4 eval), all entity slots.
- **False meanings (corruptions of the original sentence), each passed through an edit check and a truth label.**
  - `entity_sub` (entity slots): deterministic swap of the focus word for a name drawn (seed 7000 + slot) from the round-1 pool of capitalised tokens, excluding words in the context or explanation: 31 → 14 accepted, 16 rejected at edit check (the pool contains non-name tokens such as "When", "Is", "Unlike"), 1 labelled undetermined.
  - `detail_sub` (agent: change exactly one non-name detail — number, quantity, event, attribute, date, outcome): 47/47 accepted.
  - `relation_rev` (agent: exchange an ordered two-party relation, else NONE): 9 non-NONE, 8 accepted, 38 NONE.
  - `negation`: dropped by cut rule A1(b).
  - Result: 69 contradicted false meanings in play (47 detail_sub, 14 entity_sub, 8 relation_rev).
- **Realizations.** For each meaning in play (8 correct, 69 false, 46 contradicted originals; 124 meanings): the original wording plus two paraphrases, `light1` (wording/word order only) and `aggr1` (different syntax and vocabulary, same proposition). The agent wrote one light and one aggressive paraphrase template per slot and applied each candidate's exact word substitution to it, so the rewording is identical across the meanings of a slot; every pair was then judged for exact propositional equivalence in a shuffled batch (248/248 Yes). Plus a deletion baseline per eligible slot (47).
- **Scoring.** Each realization substituted at the sentence's span in the explanation; 459 texts (40 unedited, 372 realizations, 47 deletions) → one AR forward each → cosine with the context's own activation.
- **Statistics.** μ_m = mean score over the valid paraphrases of meaning m (original excluded). Primary G = μ_correct − mean over false meanings of μ_m, per eligible slot, cluster by context, minimum 30 eval slots. Natural-error test: μ_correction − μ_original on slots with a contradicted original and a valid correction, minimum 15. Also reported: correct-ranks-first rate, by corruption category, paraphrase sensitivity (|Δ| vs original by light/aggressive and by truth), 2×2 blocks truth (entailed/contradicted) × slot type (entity/detail), deletion Δ, reconstruction movement V.
- **What happened.** In-primary eval slots 4 (< 30) → **A1 INCONCLUSIVE**; natural-error eval slots 4 (< 15) → **A1-nat INCONCLUSIVE**. Descriptively G = 0.0032 [−0.0004, 0.0067] on those 4; paraphrase sensitivity |Δ| 0.0013 (light) and 0.0043 (aggressive), i.e. larger than G.

## 3. K1 — K-way alternative ranking (desk-designed; reuses round-1/3 artifacts)

**Question.** With paraphrase noise held at zero by construction, does the reconstructor prefer the word the verbalizer originally wrote over matched one-word alternatives, and does that depend on whether the word occurs in the prefix?

- **Inherited data (rounds 1–3b).**
  - Stimuli: 200 wikitext-2 train documents (≥ 300 TARGET tokens, shuffle seed 0, truncated to 512 tokens), one random position per document (pos uniform in 16..L−1; observed 18–510); block-20 activation at pos.
  - Explanations: one greedy AV explanation per stimulus (200 tokens max).
  - Claims: sentence-level split of each explanation (≥ 3 words) → 671 claims, 538 in the evaluation stimuli (40–199).
  - Deterministic one-word corruption of each evaluation claim (round 1, S3): the first number n → n + 7 (n × 3 if n < 3); otherwise the first capitalised non-sentence-initial token → a capitalised non-initial token from another evaluation explanation's claims. The 393 corruptions that change exactly one word (equal word count) are the `corrupt_det` rows of `t2b_claims.csv`, with `word_orig`, `word_corrupt` and `is_last` (the claim is the explanation's last sentence, typically the "Final token … expecting …" snippet).
  - `in_full_prefix` (desk-computed, lexical): whether `word_orig` occurs as a whole word in the full prefix (tokens 0..pos). It is a string proxy for grounding, not a truth label; 107 of the 266 non-last rows are in-prefix.
- **Rows and strata.** 393 rows: non-last in-prefix 107 (99 entity / 8 detail), non-last not-in-prefix 159 (136 / 23), last 127 (positive control; 95 / 32). Slot type: `word_orig` a pure number → detail, else entity.
- **Alternatives.** 7 per row (seed 6000 + row). Names: distinct draws from the pool of 200 distinct entity `word_orig` cores of *other* explanations, excluding words in this row's prefix or explanation and `word_corrupt` (6 rows had fewer than 7 available). Numbers: {n+1, n+7, n+13, 2n, 3n, n+100, n−1} in the same digit format. `word_orig` is replaced at its first whole-word occurrence in the claim and the claim is substituted at its span in the explanation; asserted: any two of the 8 texts differ in exactly one word.
- **Scoring.** 8 texts per row against the row's own activation: 2,751 new AR forwards; the originals' scores were reused from round 1 after 20 recomputed rows agreed to 1e-16.
- **Statistics.** Rank of the original among 8; kill statistic = top-1 rate − 0.125 (chance) on the non-last in-prefix rows, cluster by explanation, minimum 80 rows; also MRR, gap = cos(orig) − mean cos(alternatives), 2×2 in-prefix × entity/detail, positive control.
- **What happened.** **NOT MET**: in-prefix top-1 0.308 (excess 0.183 [0.096, 0.265], 89 explanations); not-in-prefix 0.252 (0.127 [0.061, 0.190]); positive control 0.449 (0.324 [0.237, 0.410]); mean gap 0.00125 / 0.00044 / 0.0108. 2×2 top-1: in-prefix entity 0.293 (n 99), in-prefix detail 0.500 (n 8), not-in-prefix entity 0.272 (n 136), not-in-prefix detail 0.130 (n 23).
- **No truth labels in K1.** It measures preference for the verbalizer's own word.

## 4. D1 — claim-direction ablation with the reconstructor as encoder (desk-designed; same rows)

**Question.** If the direction the reconstructor attributes to one claim is subtracted from the activation, does the verbalizer stop asserting that claim, compared with subtracting another row's direction?

- **Rows.** Seed-8000 sample of the K1 rows: 60 non-last in-prefix, 60 non-last not-in-prefix, 20 last (positive control), processed round-robin across strata; 111 completed at the 60-minute cap (46 / 45 / 20; entity/detail 43/3, 36/9, 18/2), 29 not generated.
- **Direction.** z = the explanation; z∖c = the explanation with claim c removed (round-1 split rule); d_c = AR(z) − AR(z∖c) in fp32; d̂ = d_c/‖d_c‖. Own ablation h' = h − 0.3‖h‖·d̂ (single strength). Random control: d̂ of a different row from a different explanation in the same stratum (fixed derangement, seed 8001).
- **Re-verbalization.** Greedy, 200 tokens, for h' and h'_rand (222 generations), each re-scored against the original h. Reference = the round-1 greedy explanation of the unablated h.
- **Measures.** `persist_word` (the corrupted-word position's original word still present, whole word), `persist_claim` (max token-Jaccard between the original claim and any sentence of the new explanation), whole-explanation Jaccard, parse/CJK format break, cos(h, AR(new)); positive control: the explanation's quoted final token equals the true token.
- **Kill statistic.** persist_word(random) − persist_word(own) on non-last rows, cluster by explanation, minimum 60 rows.
- **What happened.** **NOT MET**: own 0.495 vs random 0.703 (difference 0.209 [0.111, 0.311], n 91, 73 explanations); persist_claim 0.236 vs 0.345 (0.109 [0.081, 0.138]); in-prefix 0.152 [0.022, 0.289], not-in-prefix 0.267 [0.130, 0.422]; positive control 0.250 [0.050, 0.450]; format break 0/222; cos(h, AR(new)) own 0.856 vs random 0.873. Concerns the verbalizer's output only; no target-model behaviour was tested.

## 5. Breakdowns that exist, and what does not

- **Entity vs detail** everywhere: B1 by family (F1 entity; F2–F4 detail), A1 by slot type (entity = proper-name focus word; detail = number or relation word), K1/D1 by whether the swapped word is numeric.
- **Truth**: A1 only (entailed / contradicted / undetermined, per original and per candidate, with evidence quotes); B1 would have used version A/B as truth; K1 and D1 have no truth label (`in_full_prefix` is lexical).
- **Corruption category**: A1 (entity_sub / detail_sub / relation_rev).
- **No theme or topic breakdown** in round 4 (round-3 topic readouts are separate, not reused here).
- **Provisional**: all A1/B1 labels; the human's re-run with `--labels` recomputes every table from the raw scores.
