# Entity-claim audit changelog (2026-09-10)

Scope: all 231 entity-type atoms (identity/identification/relationship) across the 100 authoritative task files
(v2 file where present), checked against prefix_text and the Re-DocRED entity/relation lists with the rule that a name
must fill the same role in the claim as in the text. 230 labels confirmed; 1 changed.

10/8: truth true->false; related NA->related; prefix_evidence [span]->[]; review_flag true (unchanged)  reason: the prefix names the "Lower Canada Rebellion" undated; 1837 is the year the Russell Resolutions reached Canada and agitation began, so "the rebellion of 1837" is an identity the prefix does not supply (absent -> false/related).

# Detail-claim audit changelog (2026-09-10)

Scope: all 790 detail-type atoms across the 100 authoritative task files, reviewed blind to AR scores.
Truth rule: true only if the prefix states or entails the whole proposition with subject, role, value, negation and qualifiers preserved; false otherwise, with `false_basis` contradicted|absent.
Final-token claims were checked literally against the Qwen2.5-7B-Instruct tokenizer (the NLA's backbone): the last token of each prefix was decoded and compared with the claimed token. Years tokenise digit-by-digit and rare words split, so 22 claims whose token matched the final WORD but not the final TOKEN moved true->false/related (contradicted). The final word remains recorded in each rationale.

## Label corrections
7/14: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is '1'; final word is '1971'; claimed '1971'
11/11: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is 'ley'; final word is 'Presley'; claimed 'Presley'
15/13: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is '9'; final word is '1959'; claimed '1959'
24/12: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is '5'; final word is '75'; claimed '75'
28/18: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is 'ém'; final word is 'Belém'; claimed 'Belém'
30/15: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is '4'; final word is '1974'; claimed '1974'
31/15: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is 'man'; final word is 'Paperman'; claimed 'Paperman'
32/12: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is '4'; final word is '2014'; claimed '2014'
37/10: review_flag False->True; reason: audit: type check — the nickname meaning lies after the cut, forecast-like; type left as detail, flagged
38/15: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is '3'; final word is '1993'; claimed '1993'
39/12: review_flag False->True; reason: audit: type check — 'how-to guides' completes the cut word, forecast-like; type left as detail, flagged
40/14: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is '0'; final word is '70'; claimed '70'
41/12: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is 'ours'; final word is 'harbours'; claimed 'harbours'
43/10: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is 'on'; final word is 'Luzon'; claimed 'Luzon'
47/7: truth true->false; related NA->related; false_basis ->absent; reason: audit: the prefix says the species 'is now considered critically endangered' with no regional qualifier; the added qualifier 'in some regions' is not stated or entailed
48/13: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is 'erra'; final word is 'Guerra'; claimed 'Guerra'
51/15: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is 'ife'; final word is 'Recife'; claimed 'Recife'
54/10: review_flag False->True; reason: audit: type check — the chapter title lies after the cut; forecast-like; type left as detail, flagged
60/12: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is '1'; final word is '1941'; claimed '1941'
65/10: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is 'PM'; final word is 'DPM'; claimed 'DPM'
66/12: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is '7'; final word is '2017'; claimed '2017'
70/13: truth true->false; related NA->related; false_basis ->contradicted; reason: audit: the final clause 'in which the party lost its representation...' is a relative clause, not a parenthetical; consistent with other parenthetical claims labelled false
71/1: truth true->false; related NA->related; false_basis ->absent; reason: audit: the prefix gives 'Professor of Commercial Law' and 'economic and empirical studies'; 'economic law' as his field is not stated or entailed
72/15: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is 'avor'; final word is 'Endeavor'; claimed 'Endeavor'
73/14: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is ' States'; final word is 'States'; claimed 'United States'
76/8: truth true->false; related NA->related; false_basis ->absent; reason: audit: the prefix states the book is published with nihil obstat and imprimatur; that this is a 'standard' credential phrase is world knowledge, not stated
76/11: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is 'atur'; final word is 'imprimatur'; claimed 'imprimatur'
82/8: truth true->false; related NA->related; false_basis ->absent; reason: audit: only '"It seems," she said' is visible; the quotation's content is cut, so what it is about is not stated (the preceding paraphrase is not the quotation)
87/11: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is '4'; final word is '1984'; claimed '1984'
88/8: truth true->false; related NA->related; false_basis ->contradicted; reason: audit (tokenizer check, Qwen2.5-7B-Instruct): actual final token is 'a'; final word is 'Sousa'; claimed 'Sousa'
89/7: review_flag False->True; reason: audit: 'popular' vs prefix 'classic astrology textbook'; kept true as a near-paraphrase, judgement call

## Routine tagging (no label change)
- `detail_scope` added to all 790: substantive 468, syntax_structure 117, local_token 111, mixed_unclear 94 (final_token->local_token; exact_words <=4 quoted words->local_token else mixed_unclear; local_text purely structural->syntax_structure, structural+content->mixed_unclear, content-only->substantive; date/quantity/event/attribute/cause->substantive).
- `false_basis` added to all false atoms: contradicted where the prefix fills the same slot with a different value or the quoted string/structure is checkably not there (all false exact_words treated as contradicted); absent where the rationale records the specific as unsupported/not entailed. 9 heuristic assignments hand-overridden to absent (36/5, 37/10, 39/10, 39/12, 47/6, 49/4, 54/10, 56/6, 78/11).
- `audit`='detail-audit-2026-09-10' stamped; 41 atoms had review_flag set for bundled disjunctions ('X or Y') or ambiguous subject bindings ('the AV's male subject'), noted in rationale, propositions not rewritten.
- Forecast-like detail atoms flagged (type not changed): 37/10, 39/10, 39/12, 54/10.
- Unresolved: 87/9 ('since 1984' attachment ambiguous; kept true, flagged).
