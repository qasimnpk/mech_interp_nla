# DISCONFIRMATION — kill tests
# One line per pre-registered kill test, appended the moment it is computed. MET = the
# disconfirming condition occurred. Report flatly; never soften, re-run, or skip because of it.
# <ISO time>  <stage>  <K-id>  threshold=<...>  observed=<...>  MET|NOT MET  <one line: what it means for the framing>
2026-09-06T02:27:06  S0  K0  threshold=cjk_rate>0.25  observed=cjk_rate=0.062 (1/16), parse_ok=1.000  NOT MET  injection on raw-text activations: MET would mean the AV is describing the marker glyph
2026-09-06T02:59:26  S1  K1a  threshold=mean cos_own<0.5 (eval n>=160)  observed=mean cos_own=0.8820 CI95=[0.8753,0.8886] n=160  NOT MET  pipeline fidelity on wikitext stimuli vs published 0.752 FVE on WildChat+FineWeb
2026-09-06T02:59:26  S1  K1b  threshold=mean cos_shuffled_samedoc >= mean cos_own-0.05  observed=mean cos_own=0.8820 mean cos_shuffled_samedoc=0.3664 paired diff=0.5156 CI95=[0.4987,0.5331] n=160; cross-doc: mean cos_shuffled_doc=0.3198 diff=0.5622 CI95=[0.5455,0.5779]  NOT MET  position specificity: MET would mean explanations reconstruct another position of the same context about as well as their own
2026-09-06T03:14:37  S2  K2  threshold=CI95 of mean(|Δcos_claim| − mean|Δcos_randspan|) ≤ 0  observed=mean D=0.00578 CI95=[0.00224,0.00964] n_claims=538 n_expl=160; mean|Δcos_all|=0.5349 vs 5×median|Δcos_i|=0.0821 (>=: True)  NOT MET  MET would mean deleting a whole claim is indistinguishable from deleting a random equal-length span
