# T0 check — artifacts, topics, entropy sidecar, measured costs

git 710229a6; settings in t0_settings.json

## Artifact counts (expected / found)

- stimuli: expected 200, found 200
- explanations: expected 200, found 200
- claims: expected 671, found 671
- s3_edits: expected 538, found 538
- s3_edit_ok: expected 490, found 490
- out/acts_L20.npz: {'h20': [200, 3584], 'h19': [200, 3584], 'h21': [200, 3584], 'h20_pos2': [200, 3584], 'stim_idx': [200], 'doc_idx': [200], 'pos': [200], 'pos2': [200]}
- out/recon_L20.npz: {'pred': [200, 3584], 'pred_empty': [3584], 'stim_idx': [200]}

## Topics (t0_topics.csv)

- headings found: 200/200; unique topic_true: 199
- foreign pairing (i+100) mod 200: document collisions 0 (asserted)
- topic_true appears (case-insensitive) in the default explanation: all 6/200; eval 6/160
- topic_true word count: mean 3.97, max 21

## Entropy at pos (t0_entropy.csv; TARGET logits at pos, nats)

- rows OK: 200/200; errors: 0
- entropy all: mean 1.417 median 1.182 min 0.000 max 5.231
- entropy eval: mean 1.411 median 1.182
- top1_prob eval: mean 0.647 median 0.667
- top-1 matches actual next token: all 110/200; eval 86/160

| token_type | n (eval) | mean entropy | median entropy | mean top1_prob |
|---|---|---|---|---|
| punctuation | 24 | 1.728 | 1.645 | 0.589 |
| word_initial | 108 | 1.461 | 1.182 | 0.638 |
| word_piece | 28 | 0.947 | 0.774 | 0.733 |

## Measured per-item costs

- target_load_s: 6.779
- target_fwd_s_per_doc: 0.017
- target_fwd_s_per_doc_median: 0.014
- target_fwd_s_per_short: 0.109
- NOTE target_fwd_s_per_doc above was timed without an MPS sync (dispatch only); wall-clock from the log timestamps is 200 docs in 230 s = 1.15 s/doc, which is the number to budget with. The short-forward and AV/AR figures include the sync (their outputs are read back on the CPU inside the timed region).
- rss_after_target_free_G: 0.571
- av_load_s: 5.788
- av_gen_s_per_expl: 10.566
- av_gen_s_per_token: 0.073
- av_fwd_s_per_prompt: 0.283
- rss_after_av_free_G: 0.516
- ar_load_s: 3.881
- ar_s_per_score: 0.356
- ar_s_per_short_score: 0.073

AV timing generations (pilot stimuli; same_as_round1 = greedy text identical to explanations.jsonl):

- stim 0: 12.1 s, 145 tokens, parse_ok=True, same_as_round1=True
- stim 1: 9.7 s, 143 tokens, parse_ok=True, same_as_round1=True
- stim 2: 9.9 s, 146 tokens, parse_ok=True, same_as_round1=True

AR timing: mean cos_own on pilot 0-9 = 0.8786 (round-1 s1_recon: 0.8786)

## Re-budget from measured costs (item counts from PLAN.md stage specs)

| stage | items | est. compute (min) | + model loads (min) | PLAN estimate |
|---|---|---|---|---|
| C1 | 640 ar | 3.8 | 4.4 | ~10 |
| C2 | 80 target_short, 80 av_gen, 360 ar | 16.4 | 18.1 | ~40 |
| T1 | 1876 ar, 6400 target_short | 22.8 | 23.9 | ~10 |
| T2 | 3380 av_fwd | 16.0 | 16.5 | ~15 |
| T4 | 128 target_short, 360 av_gen, 720 ar | 67.9 | 69.7 | ~30 |
| T3 | 608 av_gen, 480 ar | 109.9 | 111.1 | ~45 |
| total | | | 244 | |

Ten fixed rows (eval 0,16,...,144 = stim 40,56,...,184):

| stim | token | type | entropy | top1_prob | top1 | actual next | topic_true | topic_foreign |
|---|---|---|---|---|---|---|---|---|
| 40 | 'ium' | word_piece | 1.453 | 0.513 | ' are' | ' are' | Europium | The Litigators |
| 56 | " '" | punctuation | 0.005 | 1.000 | 's' | 's' | Andrew Johnston ( singer ) | President Evil |
| 72 | ' spinner' | word_initial | 4.831 | 0.064 | ' Jack' | ' Max' | No result , Pts | Blackburn Firecrest |
| 88 | ' .' | punctuation | 4.085 | 0.191 | ' The' | ' Those' | Draining and development of the Everglades | Battle of Binh Gia |
| 104 | ' characters' | word_initial | 1.563 | 0.689 | ' ,' | ' who' | Martin Keamy | Pokiri |
| 120 | ' promised' | word_initial | 1.482 | 0.614 | ' to' | ' to' | Chapter 1 ( House of Cards ) | Battle of Hubbardton |
| 136 | ' =' | punctuation | 0.107 | 0.983 | ' =' | ' =' | Hurricane Omar ( 2008 ) | Saint Leonard Catholic Church ( Madison , Nebraska ) |
| 152 | ' condemned' | word_initial | 0.268 | 0.950 | ' to' | ' to' | Ulysses ( poem ) | 766th Independent Infantry Regiment ( North Korea ) |
| 168 | ' a' | word_initial | 3.283 | 0.270 | ' consistent' | ' weekly' | Stop ! ! Hibari @-@ kun ! | Texas A & M Singing Cadets |
| 184 | ' directly' | word_initial | 1.834 | 0.410 | ' .' | ' .' | Florida State Road 878 | Central Area Command ( RAAF ) |

