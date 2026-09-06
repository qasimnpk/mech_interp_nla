# S4 summary — blind-describer and raw-context baselines (evaluation set)

git fee419a7; settings in s4_settings.json

| column | mean | median | n |
|---|---|---|---|
| cos_AV | 0.8820 | 0.8918 | 160 |
| cos_blind | 0.4286 | 0.4260 | 160 |
| cos_blind_left | 0.4387 | 0.4396 | 100 |
| cos_rawctx | 0.4731 | 0.4661 | 160 |

- mean gap (cos_AV − cos_blind): 0.4534 CI95 [0.4404, 0.4673] n=160
- mean cos_AV − cos_blind_left (first 100 eval positions): 0.4421
- mean cos_AV − cos_rawctx: 0.4089
- fraction blind ≥ AV: 0.0000; fraction rawctx ≥ AV: 0.0000
- blind parse_ok rate: 1.000

| act_norm tercile | range | mean gap | mean cos_AV | mean cos_blind | n |
|---|---|---|---|---|---|
| low | 80.0–109.4 | 0.4348 | 0.8733 | 0.4386 | 54 |
| mid | 109.5–117.8 | 0.4526 | 0.8766 | 0.4240 | 53 |
| high | 117.9–140.2 | 0.4731 | 0.8963 | 0.4232 | 53 |

| pos tercile | range | mean gap | mean cos_AV | mean cos_blind | n |
|---|---|---|---|---|---|
| low | 19.0–218.0 | 0.4405 | 0.8867 | 0.4462 | 55 |
| mid | 219.0–377.0 | 0.4476 | 0.8764 | 0.4288 | 52 |
| high | 379.0–510.0 | 0.4725 | 0.8827 | 0.4102 | 53 |

## Kill test

- 2026-09-06T05:39:29  S4  K4  threshold=CI95 of mean(cos_AV − cos_blind) entirely < 0.05  observed=mean gap=0.4534 CI95=[0.4404,0.4673] n=160; mean cos_AV=0.8820 mean cos_blind=0.4286  NOT MET  a strong blind score shows reconstruction can be achieved from visible context; it does not show the verbalizer ignores the activation

