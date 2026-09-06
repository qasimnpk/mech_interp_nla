# R3 summary — truncation curve (first k / last k claims), AR only, evaluation explanations

git 8d7030d9; settings in r3_settings.json; AR forwards 916

- explanations: 160; claims: 538; n_claims histogram: 3:123, 4:23, 5:9, 6:3, 7:2
- cos_z mean 0.8820; cos_empty mean 0.3471; errors 0

## Mean cos and lift vs k (explanations with n_claims >= k; cluster-bootstrap CI95 by explanation)

| k | n_expl | first-k mean cos | first-k mean lift | first-k median lift | last-k mean cos | last-k mean lift | last-k median lift |
|---|---|---|---|---|---|---|---|
| 1 | 160 | 0.4673 [0.4528, 0.4814] | 0.2270 [0.2080, 0.2460] | 0.2251 | 0.8217 [0.8060, 0.8349] | 0.8837 [0.8574, 0.9044] | 0.9253 |
| 2 | 160 | 0.7115 [0.6917, 0.7320] | 0.6766 [0.6395, 0.7143] | 0.7240 | 0.8635 [0.8551, 0.8724] | 0.9640 [0.9533, 0.9730] | 0.9791 |
| 3 | 160 | 0.8533 [0.8384, 0.8669] | 0.9427 [0.9206, 0.9624] | 0.9982 | 0.8768 [0.8689, 0.8847] | 0.9885 [0.9809, 0.9949] | 0.9985 |
| 4 | 37 | 0.8657 [0.8465, 0.8830] | 0.9728 [0.9443, 0.9910] | 0.9979 | 0.8702 [0.8536, 0.8855] | 0.9853 [0.9715, 0.9950] | 0.9975 |
| 5 | 14 | 0.8534 [0.8211, 0.8827] | 0.9539 [0.8894, 1.0009] | 0.9993 | 0.8598 [0.8349, 0.8830] | 0.9742 [0.9402, 0.9988] | 0.9983 |
| 6 | 5 | 0.8281 [0.7818, 0.8711] | 0.9072 [0.8285, 0.9858] | 0.9412 | 0.8365 [0.7892, 0.8795] | 0.9277 [0.8495, 0.9973] | 0.9949 |
| 7 | 2 | 0.8391 [0.7969, 0.8813] | 0.9252 [0.8553, 0.9950] | 0.9252 | 0.8391 [0.7969, 0.8813] | 0.9252 [0.8553, 0.9950] | 0.9252 |

- k at which the median first-k lift first exceeds 0.9: 3; last-k: 1
- all claims joined (k = n) minus cos_z: -0.00089 [-0.00188, -0.00005] n=160

## Per-explanation smallest k with lift > 0.9

| direction | n_expl | never reached | k*=1 | k*=2 | k*=3 | k*>=4 | mean k*/n |
|---|---|---|---|---|---|---|---|
| first | 160 | 2 | 0 | 33 | 102 | 23 | 0.897 |
| last | 160 | 1 | 103 | 44 | 10 | 2 | 0.430 |

## First k vs last k, paired within explanation (same k)

| k | n_expl | mean cos(first k) − cos(last k) | CI95 |
|---|---|---|---|
| 1 | 160 | -0.35444 | [-0.37379, -0.33391] |
| 2 | 160 | -0.15206 | [-0.17204, -0.13159] |
| 3 | 37 | -0.10149 | [-0.14181, -0.06278] |
| 4 | 14 | -0.01194 | [-0.02873, 0.00135] |
| 5 | 5 | -0.01802 | [-0.03935, 0.00231] |
| 6 | 2 | -0.02108 | [-0.02667, -0.01550] |

## Single claims alone (S2 cos_alone)

- cos_alone: mean 0.6603, median 0.6924, p10 0.4171, p90 0.8705 (n=538)
- lift_alone: mean 0.5808, median 0.6418
- Spearman(claim word count, cos_alone): rho=0.7024 p=3.45e-81 (n=538)
- Spearman(claim word count, lift_alone): rho=0.7339 p=4.2e-92
- Spearman(relative claim position, cos_alone): rho=0.7638 p=5.5e-104

| claim position | n | mean cos_alone | mean n_words |
|---|---|---|---|
| first | 160 | 0.4673 | 20.3 |
| middle | 218 | 0.6835 | 30.5 |
| last | 160 | 0.8217 | 39.4 |

## Timings

- ar_load_s: 2.94
- ar_forward_s: 163.33
- ar_n_forward: 916
