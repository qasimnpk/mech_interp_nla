# M summary — does reconstruction error warn of an incorrect answer? (synthetic multiplication pilot)

git 314b8b27; settings in m_settings.json; m_problems.csv (200), m_scores.csv (sample); activations out/m_acts.npz

- problems: correct 49, incorrect 151 (no 'Answer:' 147); gate GM PASS; generation 12.8 s each, mean 194 tokens; sample incorrect 4 correct 40; NLA 10.4 s/item; parse_ok 44/44

## Kill M

- AUROC(−cos) incorrect vs correct: 0.2938 [0.0000,0.5706] → **INCONCLUSIVE**

| signal (higher = predicts incorrect) | AUROC [CI by problem] |
|---|---|
| −cos(AR(desc), h) (NLA) | 0.2938 [0.0000,0.5706] |
| next-token entropy at 'Answer:' | 0.7937 [0.5854,0.9655] |
| −(top-1 margin) | 0.7969 [0.5944,0.9593] |
| −(yes − no) text-only self-check | 0.3875 [0.2245,0.5436] |

- in-sample logistic (exploratory): entropy + margin AUROC 0.7812; + cos 0.8063; standardised coefficients with cos: entropy -0.982, margin -2.218, cos +0.345
- mean cos: correct 0.8737, incorrect 0.8829; mean entropy correct 0.023 incorrect 0.056

## Five verbatim cases (first 3 incorrect, first 2 correct in the sample)

### problem 93: 207 × 87 = 18009; model answer 17909 (incorrect); cos 0.8767; entropy 0.013; margin 6.625; yes−no +7.12
- generation:  Step-by-step solution: ⏎ 1. Break down the multiplication into simpler parts using the distributive property of multiplication over addition. ⏎ 2. Express 207 as (200 + 7) and 87 as (80 + 7). ⏎ 3. Multiply each part of 207 by each part of 87: ⏎    - \(200 \times 80 = 16000\) ⏎    - \(200 \times 7 = 1400\) ⏎    - \(7 \times 80 = 560\) ⏎    - \(7 \times 7 = 49\) ⏎ 4. Add all these products together: ⏎    - \(16000 + 1400 + 560 + 49 = 17909\) ⏎  ⏎ Answer: 17909.
- explanation: Structured math problem format with labeled steps and calculations, indicating a worked solution for a number sequence problem.

The phrase "The final answer is: 12345 + 6789 = 19134. Answer: " signals the answer box format, completing the pattern "The final answer is labeled as..." implying the final answer box value is shown.

Final token "Answer: " closes the answer label ("Answer: "), directly following "Answer: 12345" — strongly expects "19134" or "81" to close the box, completing the stated answer and confirming the integer sequence's solution.

### problem 123: 226 × 61 = 13786; model answer 13 (incorrect); cos 0.8934; entropy 0.086; margin 4.125; yes−no +7.25
- generation:  Step-by-step solution: ⏎  ⏎ 1. Break down the multiplication into simpler parts: ⏎    - \( 226 \times 60 \) ⏎    - \( 226 \times 1 \) ⏎  ⏎ 2. Calculate \( 226 \times 60 \): ⏎    - \( 226 \times 60 = 226 \times (6 \times 10) \) ⏎    - \( 226 \times 6 = 1356 \) ⏎    - \( 1356 \times 10 = 13560 \) ⏎  ⏎ 3. Calculate \( 226 \times 1 \): ⏎    - \( 226 \times 1 = 226 \) ⏎  ⏎ 4. Add the results from steps 2 and 3: ⏎    - \( 13560 + 226 = 13786 \) ⏎  ⏎ Answer: 13
- explanation: Structured math problem format with labeled steps showing calculations for a sequence, implying a final answer box with "The product of the sequence is."

The phrase "Final answer: 123456... Answer: " mirrors the pattern "The answer is determined, therefore the final answer is," strongly suggesting the closing answer "12345" or "999."

Final token "Answer: " closes the answer declaration phrase ("Final answer: "), directly completing the concluding statement pattern, strongly expecting "999" or "12345" as the numeric answer, likely followed by "999" to close the box.

### problem 154: 571 × 35 = 19985; model answer 20985 (incorrect); cos 0.8842; entropy 0.010; margin 6.750; yes−no +6.62
- generation:  Step 1: Multiply 571 by 5 (the ones digit of 35). ⏎ \[ 571 \times 5 = 2855 \] ⏎  ⏎ Step 2: Multiply 571 by 30 (the tens digit of 35, which is 3 times 10). ⏎ \[ 571 \times 30 = 17130 \] ⏎  ⏎ Step 3: Add the results from steps 1 and 2. ⏎ \[ 2855 + 17130 = 20985 \] ⏎  ⏎ Answer: 20985 ⏎ You are welcome! If you have any more questions or need further assistance with math problems or any other subject, feel free to ask.
- explanation: Structured math problem format with numbered steps and calculations, indicating a worked-out answer for a number sequence problem involving cube and square operations.

The phrase "Final answer: The calculated value is 12345. Answer: " signals the concluding answer format, completing the "boxed answer" convention, strongly implying the final answer is "12345."

Final token "Answer: " closes the answer phrase "Answer: Boxed number: ", directly following the pattern "Final answer: 12345" — expects "12345" or "999" as the final boxed answer, completing the concluding statement about the puzzle's solution.

### problem 0: 865 × 67 = 57955; model answer 57955 (correct); cos 0.8721; entropy 0.001; margin 9.125; yes−no +3.88
- generation:  Step 1: Break down the multiplication into simpler parts. ⏎ Step 2: Multiply 865 by 70 (which is 67 + 3). ⏎ Step 3: Calculate 865 × 70 = 60550. ⏎ Step 4: Subtract 865 × 3 from the result of step 3 to adjust for the extra 3 in 70. ⏎ Step 5: Calculate 865 × 3 = 2595. ⏎ Step 6: Subtract 2595 from 60550 to get the final answer. ⏎ Step 7: 60550 - 2595 = 57955. ⏎  ⏎ Answer: 57955 ⏎ You're correct in your approach and calculations. Let's break it down step-by-step to ensure clarity: ⏎  ⏎ 1. **Break down the multiplication**: We can use the distributive property to simplify
- explanation: Structured math problem format with numbered steps and calculations, suggesting a puzzle or answer format with a specific numeric result.

The phrase "The final answer: Calculation: 123456... Answer: " signals the concluding answer box, completing the pattern "The sequence's answer is 9999" — strongly implying the final answer box displays "9999".

Final token "Answer: " closes the answer label ("Answer: 9999"), directly expecting the numeric result or closing phrase "9999" or "12345" to complete the box label, likely followed by "9999" or similar.

### problem 1: 560 × 35 = 19600; model answer 19600 (correct); cos 0.8905; entropy 0.100; margin 4.000; yes−no +7.75
- generation:  Step-by-step solution: ⏎  ⏎ 1. Break down the multiplication into simpler parts: ⏎    - \( 560 \times 35 = 560 \times (30 + 5) \) ⏎     ⏎ 2. Distribute 560 across the terms inside the parentheses: ⏎    - \( 560 \times 30 + 560 \times 5 \) ⏎  ⏎ 3. Calculate each part separately: ⏎    - \( 560 \times 30 = 560 \times 3 \times 10 = 1680 \times 10 = 16800 \) ⏎    - \( 560 \times 5 = 2800 \) ⏎  ⏎ 4. Add the results of the two multiplications: ⏎    - \( 16800 + 2800 = 19600 \) ⏎  ⏎ Answer: 19600 ⏎  ⏎ Therefore,
- explanation: Structured math problem format with labeled steps showing calculations for a sequence, implying a final answer is being presented.

The phrase "Thus, the calculated value is: 12345. Final answer: " mirrors a concluding statement pattern, strongly implying the answer "12345" is the final result, completing the "boxed answer" convention.

Final token "answer: " closes the phrase "Answer: " and is part of the concluding summary statement "Final answer: Boxed answer," immediately expecting the numeric value "12345" or "96" to close the box, likely followed by "96" or "The number."

