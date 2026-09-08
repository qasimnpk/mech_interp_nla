# N3 summary — what the frozen AR rewards: correct specific / wrong specific / generic / omitted (AR only)

git 321e3df0; settings in n3_settings.json; rows in n3_scores.csv

- accepted deterministic-swap triples 402 → 393 single-token swaps (9 excluded: swap not a single whitespace token); kinds {'name': 304, 'number': 89}; last-claim rows 127
- generic rule: number → `a number`; capitalised name → `a place` (the S3 swap list carries no person marker, so PLAN's else-branch applies to all names); no LLM
- AR forwards 1337 (0.25 s each); errors 0

## Kill N3

- mean [cost(generic) − cost(wrong specific)]: -0.00029 [-0.00087,0.00025] n=393 → **INCONCLUSIVE**

## Four-way table (cost = cos drop relative to the original; CI by explanation)

| subset | n | n_expl | mean cos(original) | cost(wrong specific) | cost(generic) | cost(omitted) | generic − wrong | omitted − wrong | omitted − generic | frac generic>wrong | frac omitted>wrong |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 393 | 158 | 0.8814 | 0.00249 [0.00169,0.00333] | 0.00220 [0.00153,0.00292] | 0.05012 [0.04355,0.05708] | -0.00029 [-0.00087,0.00025] | 0.04763 [0.04108,0.05420] | 0.04792 [0.04154,0.05462] | 0.527 | 0.885 |
| number swaps | 89 | 61 | 0.8747 | 0.00133 [0.00063,0.00214] | 0.00148 [0.00046,0.00270] | 0.07028 [0.05373,0.08812] | 0.00015 [-0.00074,0.00113] | 0.06895 [0.05257,0.08672] | 0.06880 [0.05231,0.08639] | 0.596 | 0.921 |
| name swaps | 304 | 150 | 0.8834 | 0.00283 [0.00189,0.00390] | 0.00241 [0.00161,0.00329] | 0.04422 [0.03740,0.05209] | -0.00041 [-0.00109,0.00019] | 0.04139 [0.03485,0.04880] | 0.04180 [0.03529,0.04925] | 0.507 | 0.875 |
| last claim | 127 | 127 | 0.8810 | 0.00592 [0.00370,0.00840] | 0.00491 [0.00330,0.00662] | 0.12867 [0.11013,0.14785] | -0.00101 [-0.00243,0.00027] | 0.12275 [0.10412,0.14126] | 0.12376 [0.10483,0.14258] | 0.551 | 0.984 |
| not last claim | 266 | 153 | 0.8817 | 0.00085 [0.00051,0.00118] | 0.00091 [0.00038,0.00147] | 0.01262 [0.01095,0.01455] | 0.00006 [-0.00034,0.00048] | 0.01177 [0.01017,0.01354] | 0.01171 [0.01015,0.01340] | 0.515 | 0.838 |

## Five verbatim rows (first five rows; number and name)

### row 154 (stim 45, claim 1/3, number: '2008"' → '2015"')
- original: The sentence structure "The 'Open Source' panel appeared at TED 2008" establishes a date reference ("The conference was held at IFLA 20"), implying a second event date follows about the book's attendance.
- wrong specific: The sentence structure "The 'Open Source' panel appeared at TED 2015" establishes a date reference ("The conference was held at IFLA 20"), implying a second event date follows about the book's attendance.
- generic: The sentence structure "The 'Open Source' panel appeared at TED a number" establishes a date reference ("The conference was held at IFLA 20"), implying a second event date follows about the book's attendance.
- cos original 0.8844; cost wrong +0.00263 generic +0.00666 omitted +0.03699

### row 155 (stim 45, claim 2/3, number: '"20"' → '"27"')
- original: Final token "20" is mid-number in "IFLA 20", part of a date expression ("Symposium 20"), strongly expecting "08" or "09" to complete the year, then "9" or "10, a conference on the findings."
- wrong specific: Final token "27" is mid-number in "IFLA 20", part of a date expression ("Symposium 20"), strongly expecting "08" or "09" to complete the year, then "9" or "10, a conference on the findings."
- generic: Final token "a number" is mid-number in "IFLA 20", part of a date expression ("Symposium 20"), strongly expecting "08" or "09" to complete the year, then "9" or "10, a conference on the findings."
- cos original 0.8844; cost wrong +0.00408 generic -0.00015 omitted +0.08756

### row 178 (stim 52, claim 1/3, number: '1st' → '3st')
- original: The paragraph "During its early formation the 1st Special Unit was organized as the 1st Korean Security Unit" mirrors the pattern of describing unit history and structure, now expected to continue listing subunits or organizational details about the unit's initial formation and designation.
- wrong specific: The paragraph "During its early formation the 3st Special Unit was organized as the 1st Korean Security Unit" mirrors the pattern of describing unit history and structure, now expected to continue listing subunits or organizational details about the unit's initial formation and designation.
- generic: The paragraph "During its early formation the a numberst Special Unit was organized as the 1st Korean Security Unit" mirrors the pattern of describing unit history and structure, now expected to continue listing subunits or organizational details about the unit's initial formation and designation.
- cos original 0.8498; cost wrong -0.00029 generic -0.00078 omitted +0.02152

### row 136 (stim 40, claim 3/4, name: '("Properties' → '("EMI')
- original: Final token "europium" ends mid-sentence ("Properties of europium"), part of a data table or list item ("Some properties of europium"), expecting continuation like "in its solid state are:" or "are:" or "include the following:" or "atoms are given below," completing the atomic data.
- wrong specific: Final token "europium" ends mid-sentence ("EMI of europium"), part of a data table or list item ("Some properties of europium"), expecting continuation like "in its solid state are:" or "are:" or "include the following:" or "atoms are given below," completing the atomic data.
- generic: Final token "europium" ends mid-sentence ("a place of europium"), part of a data table or list item ("Some properties of europium"), expecting continuation like "in its solid state are:" or "are:" or "include the following:" or "atoms are given below," completing the atomic data.
- cos original 0.8783; cost wrong +0.00619 generic +0.00698 omitted +0.06216

### row 137 (stim 41, claim 0/7, name: '"Bulleted' → '"Trek')
- original: Structured wiki format with "Bulleted facts" pattern suggests a machine learning or trivia context about a named entity.
- wrong specific: Structured wiki format with "Trek facts" pattern suggests a machine learning or trivia context about a named entity.
- generic: Structured wiki format with "a place facts" pattern suggests a machine learning or trivia context about a named entity.
- cos original 0.7969; cost wrong -0.00217 generic -0.00154 omitted +0.00323

