# B1 blind review sheet — 8 slot_verify items

For each item: does the AV SENTENCE *assert* candidate A, candidate B, or neither (merely mentions a word)?
Fill `human_label:` with exactly `A`, `B` or `neither`; `human_note:` is optional. Do not open b1_review_key.csv until all 8 are filled.
When done, tell Claude and the labels are written back into b1_review_blind.csv.

---

## 1. F2T1f1B_s1

**Passage (source text):**

> The following entry was copied from the archive without changes. It was checked once for completeness and once for accuracy, and nothing in it was altered. The access log records one arrival by Lena and one by Omar. Their arrival times were different. Omar arrived before Lena. The record ends here.

**AV sentence to judge:**

> The phrase "The given sentence says only the first two sentences; story ends here and the rest are irrelevant facts. The complete story falls... The next sentence is finished." implies a closing or summary statement, likely concluding the datum.

- **A:** Lena arrived before Omar.
- **B:** Omar arrived before Lena.

```
human_label: neither
human_note: 
```

---



## 2. F2T1f2A_s1

**Passage (source text):**

> The following entry was copied from the archive without changes. It was checked once for completeness and once for accuracy, and nothing in it was altered. The access log records one arrival by Priya and one by Tomas. Their arrival times were different. Priya arrived before Tomas. The record ends here.

**AV sentence to judge:**

> The phrase "The given knowledge so far is the first sentence of a story ending 'The golden token was empty... The episode ends thus... Then the next sentence is unknown.' The passage ends this." implies a concluding remark or puzzle constraint.

- **A:** Priya arrived before Tomas.
- **B:** Tomas arrived before Priya.

```
human_label: neither
human_note: 
```

---



## 3. F2T2f2A_s1

**Passage (source text):**

> The following entry was copied from the archive without changes. It was checked once for completeness and once for accuracy, and nothing in it was altered. The garage log records one repair and one road test. These events occurred at different times. The repair was completed before the road test began. The record ends here.

**AV sentence to judge:**

> The phrase "He gives the first sentence and the known facts about the callout here...The narrative ends here with no further text. The event now ends. This record ends the thought." implies a concluding clause or instruction, likely a closing remark or metadata element.

- **A:** The repair was completed before the road test began.
- **B:** The road test began before the repair was completed.

```
human_label: neither
human_note: 
```

---



## 4. F3T1f0B_s1

**Passage (source text):**

> The following entry was copied from the archive without changes. It was checked once for completeness and once for accuracy, and nothing in it was altered. The inventory entry describes one sealed box. Its contents were counted twice and the counts agreed. The box contained exactly nine glass vials. The record ends here.

**AV sentence to judge:**

> The phrase "The text has four numbered facts followed by the word 'End of the specimen's description and no further detail follows. The sequence ends here." suggests a concluding or unexplained directive, likely a puzzle or logical closure item.

- **A:** The box contained exactly six glass vials.
- **B:** The box contained exactly nine glass vials.

```
human_label: neither
human_note: 
```

---



## 5. F3T1f2A_s1

**Passage (source text):**

> The following entry was copied from the archive without changes. It was checked once for completeness and once for accuracy, and nothing in it was altered. The inventory entry describes one sealed box. Its contents were counted twice and the counts agreed. The box contained exactly five sealed envelopes. The record ends here.

**AV sentence to judge:**

> The phrase "The text states: 'The preceding four data points about the curve...The statement ends here. There follow no additional facts given.' The sentence appears to be the end of an incomplete record or puzzle context." implies an implied conclusion or constraint about the artifact's remaining data or structure.

- **A:** The box contained exactly five sealed envelopes.
- **B:** The box contained exactly eight sealed envelopes.

```
human_label: neither
human_note: 
```

---



## 6. F3T1f2B_s0

**Passage (source text):**

> The following entry was copied from the archive without changes. It was checked once for completeness and once for accuracy, and nothing in it was altered. The inventory entry describes one sealed box. Its contents were counted twice and the counts agreed. The box contained exactly eight sealed envelopes. The record ends here.

**AV sentence to judge:**

> Mystical/technical format with numbered attributes about an "unknown object" described with features ("Number:1, Shape: circular"), suggesting a puzzle or data record format.

- **A:** The box contained exactly five sealed envelopes.
- **B:** The box contained exactly eight sealed envelopes.

```
human_label: neither
human_note: 
```

---



## 7. F3T2f0A_s1

**Passage (source text):**

> The following entry was copied from the archive without changes. It was checked once for completeness and once for accuracy, and nothing in it was altered. The meeting log records one session. Its duration was measured from the opening statement to the final adjournment. The session lasted exactly twenty minutes. The record ends here.

**AV sentence to judge:**

> The phrase "The stated facts follow: Three incomplete lines...The story ends here. The assertion concludes. The narrative is now finished. This passage concludes." implies a concluding or closing remark, possibly a filler or truncation token signaling the text ends.

- **A:** The session lasted exactly twenty minutes.
- **B:** The session lasted exactly forty minutes.

```
human_label: neither
human_note: 
```

---



## 8. F4T1f1B_s0

**Passage (source text):**

> The following entry was copied from the archive without changes. It was checked once for completeness and once for accuracy, and nothing in it was altered. The tool log records one backup attempt, with no retries. The result was checked after the attempt ended. The backup failed. The record ends here.

**AV sentence to judge:**

> Technical/structured log entry format with informal metadata tags ("#error"), suggesting a software or script context describing an event or failure record.

- **A:** The backup succeeded.
- **B:** The backup failed.

```
human_label: neither
human_note: 
```

