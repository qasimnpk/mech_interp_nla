# RT summary — gates FAILED; routes not run

git 7e948de8; settings in rt_settings.json; rows in rt_gates.csv

- G0 16/16 (need ≥14); G1 16/16 (need 16); G2 11/16 (need ≥12)

| ctx | text | correct | m_native | top1 | self-patch max|Δlogit| | m_twin_patch | Δm | cos(h,h_twin) |
|---|---|---|---|---|---|---|---|---|
| 0 | 'Anna received the key. Tom received the book.\nQuestion: Who received the key?\nAnswer:' | Anna | +8.875 | ' Anna' | 0.00e+00 | +6.625 | -2.250 | 0.9883 |
| 1 | 'Tom received the key. Anna received the book.\nQuestion: Who received the key?\nAnswer:' | Tom | +13.625 | ' Tom' | 0.00e+00 | +11.375 | -2.250 | 0.9883 |
| 2 | 'Anna received the coin. Tom received the letter.\nQuestion: Who received the coin?\nAnswer:' | Anna | +11.750 | ' Anna' | 0.00e+00 | +9.250 | -2.500 | 0.9909 |
| 3 | 'Tom received the coin. Anna received the letter.\nQuestion: Who received the coin?\nAnswer:' | Tom | +12.375 | ' Tom' | 0.00e+00 | +12.938 | +0.562 | 0.9909 |
| 4 | 'Anna received the cup. Tom received the hat.\nQuestion: Who received the cup?\nAnswer:' | Anna | +12.062 | ' Anna' | 0.00e+00 | +9.625 | -2.438 | 0.9922 |
| 5 | 'Tom received the cup. Anna received the hat.\nQuestion: Who received the cup?\nAnswer:' | Tom | +15.000 | ' Tom' | 0.00e+00 | +13.250 | -1.750 | 0.9922 |
| 6 | 'Anna received the map. Tom received the pen.\nQuestion: Who received the map?\nAnswer:' | Anna | +10.688 | ' Anna' | 0.00e+00 | +10.875 | +0.188 | 0.9931 |
| 7 | 'Tom received the map. Anna received the pen.\nQuestion: Who received the map?\nAnswer:' | Tom | +11.250 | ' Tom' | 0.00e+00 | +10.562 | -0.688 | 0.9931 |
| 8 | 'Sara received the key. Ben received the book.\nQuestion: Who received the key?\nAnswer:' | Sara | +13.625 | ' Sara' | 0.00e+00 | +13.875 | +0.250 | 0.9879 |
| 9 | 'Ben received the key. Sara received the book.\nQuestion: Who received the key?\nAnswer:' | Ben | +15.375 | ' Ben' | 0.00e+00 | +12.500 | -2.875 | 0.9879 |
| 10 | 'Sara received the coin. Ben received the letter.\nQuestion: Who received the coin?\nAnswer:' | Sara | +11.375 | ' Sara' | 0.00e+00 | +11.125 | -0.250 | 0.9891 |
| 11 | 'Ben received the coin. Sara received the letter.\nQuestion: Who received the coin?\nAnswer:' | Ben | +15.875 | ' Ben' | 0.00e+00 | +13.625 | -2.250 | 0.9891 |
| 12 | 'Sara received the cup. Ben received the hat.\nQuestion: Who received the cup?\nAnswer:' | Sara | +15.500 | ' Sara' | 0.00e+00 | +12.500 | -3.000 | 0.9872 |
| 13 | 'Ben received the cup. Sara received the hat.\nQuestion: Who received the cup?\nAnswer:' | Ben | +11.500 | ' Ben' | 0.00e+00 | +12.312 | +0.812 | 0.9872 |
| 14 | 'Sara received the map. Ben received the pen.\nQuestion: Who received the map?\nAnswer:' | Sara | +13.938 | ' Sara' | 0.00e+00 | +14.188 | +0.250 | 0.9912 |
| 15 | 'Ben received the map. Sara received the pen.\nQuestion: Who received the map?\nAnswer:' | Ben | +13.625 | ' Ben' | 0.00e+00 | +11.938 | -1.688 | 0.9912 |
