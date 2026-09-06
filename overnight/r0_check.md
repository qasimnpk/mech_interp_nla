# R0 check — artifact counts + cache regeneration

git 893a21df; settings in r0_settings.json

## Artifact counts (expected / found)

- stimuli: expected 200, found 200
- explanations: expected 200, found 200
- claims: expected 671, found 671
- s3_edits: expected 538, found 538
- s3_edit_ok: expected 490, found 490

## Acceptance: mean cos_own on evaluation set (stimuli 40-199)

- round-1 value (S1, s1_recon.csv): 0.8820
- regenerated value: 0.8820 CI95 [0.8753, 0.8886] n=160
- difference: +0.00003; tolerance +-0.002; within tolerance: True
- round-1 eval mean recomputed from s1_recon.csv: 0.8820

## Per-row agreement with round 1 (all 200 stimuli)

- |cos_own − cos_own_round1|: max 0.00000, mean 0.00000, n>0.001: 0
- |act_norm − act_norm_round1|: max 0.0000, mean 0.0000
- |cos_empty − cos_empty_round1|: max 0.00000
- AR errors: 0

## Timings

- target_load_s: 7.94
- acts_regen_s: 226.48
- rss_after_target_free_G: 0.62
- ar_load_s: 4.32
- ar_sec_per_score: 0.28

R0 ACCEPTED: True

