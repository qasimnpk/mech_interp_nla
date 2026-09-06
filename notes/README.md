# notes/ — index of reference material

Start here when you need background. Each entry says what the file is and how to use it.
Rule for the large ones: **navigate by index, read by line range, never bulk-load.**

## Project documents (ours)
| File | What it is | Use |
|---|---|---|
| `nla_seed.md` | Everything the previous (tool-conflict) project had already gathered about natural language autoencoders: the Transformer Circuits "misreported tool calls" audit card, the "NLA information gain" fallback design with its blind-describer baseline, the Qwen2.5-7B layer-20 checkpoint pointer, and the CHIVE/RECAP scoop note | Starting point for the NLA brief and lit survey |
| `round1_decisions.md` | Decision log for the round-1 overnight plan: checkpoint choice (hardware-forced), question chosen, reviewer feedback adopted, what the human must verify in the morning | Provenance for the write-up; read before planning round 2 |
| `human_log.md` | Human hours, the verify-by-hand ledger, and the exact `/loop` prompt used per round | Fill in as you go; feeds the "what I verified" section |
| `nla_setup/README.md` | Agent setup log for both NLA checkpoint families: sizes, sidecar values, injection mechanics, the 27B infeasibility, model-card inconsistencies; raw round-trip output alongside | Checkpoint facts; re-derive before quoting |
| `findings_so_far.md` | Agent-drafted running summary of results with file pointers; advisor-facing paragraph at top | Rewrite in own voice for progress updates and the exec summary |
| `nla_paper_card.md` + `nla_paper_2026_text.txt` | The NLA paper: verbatim quotes on claim deletion, recurrence, confabulation, steganography; stripped full text | Primary source for every paper claim in the write-up |
| `progress_vs_advisor.md` | Our results walked through the external advisor's decision tree and proposals; controls run vs not run; unverified citations | Day-2 planning |
| `advisor_nla_strategy_2026-09-06.md` | External advisor report, verbatim, unverified | Reference only |
| `environment.md` | The local MPS environment as built | Setup questions |
| `smoke_test_output.txt` | Correctness-gate output | Sanity reference |

**TODO (human):** add the NLA project brief, literature survey and direction review here as they are written.

## THE RUBRIC — read before anything else
| File | What it is | Use |
|---|---|---|
| `neel_drive/mats12_admissions_procedure_faq.md` | **Neel Nanda MATS 12.0 (Winter 2026-27) — Admissions Procedure + FAQ**, Neel's own doc, archived 2026-09-05 (images stripped, 949 lines). | The application is graded against this. Key lines: deadline & TLDR L1–L35 · what he looks for L112 · how to choose a problem L151 · **Application format + exec-summary format L199–L228** · **20+2 hour rule L230–L248** · research/writing advice L272–L305 · using LLMs L307–L341 · **Sanity-check your agent L343–L354 ("the most important piece of advice in this doc")** · how applications are evaluated L423–L455 · **Common mistakes L477–L505** · past examples with his verdicts L507–L542 · how his interests changed L582 · **suggested problems L602–L776** · past-scholar papers L848 |

## Neel's Drive folder — "Mech Interp Context Docs" (owner neelnanda1011@gmail.com)
`https://drive.google.com/drive/folders/1GfrgKJwndk-twnJ8K7Ba-TE9i_8wBWAU` — 17 files. Archived into `neel_drive/`:
| File | What it is | Use |
|---|---|---|
| `neel_drive/mats12_admissions_procedure_faq.md` | see above | |
| `neel_drive/research_writing_advice_45k.md` | Part I of the 600k file as a standalone: Explore/Understand/Distill, Key Mindsets, Research Taste, Steinhardt, paper-writing advice (~45k tokens) | Small enough to load whole when writing |
| `neel_drive/neel_glossary_60k.md` | Neel's mech-interp explainer & glossary (~60k tokens) | Term lookup; grep it |
| `neel_drive/nnsight_docs_20k.txt` | nnsight docs (docs only, no source) | If we ever switch off raw hooks |
| `neel_drive/transformer_lens_docs_17k.txt` | TransformerLens docs (docs only) | Same |

Not archived (fetch on demand with `curl -sL "https://drive.google.com/uc?export=download&id=<ID>"`):
`default_600k.md` (id `18cF3lkU17_elUSv0zk8KSVejM1jGfNnz`) — **byte-identical to our `context_600k.md`** ·
`arena_all_650k.txt` (`1MiZaXDL1gQZcyB3bWVIommQb7eTf1qx6`) · `arena_short_320k.txt` (`1XPUjZQk8EffFAvjU1U373YJK-NodVldz`) ·
`ferrando_technique_primer_15k.pdf` (`14e1IdzFLrGjPtB6LLl33mHg1DfoW-iaG`) · `sharkey_lit_review_22k.pdf` (`1UkVyEgR4a3oR9X9EXaBnK1Z7L63znpA-`) — text of both is in the 600k file ·
`huggingface_transformers_short_170k.txt` (`1O6HZTiKbBgvqCJPJmLaBIgnJMoD3HdtT`) ·
`nnsight_all_270k.txt` (`1lKZ3jGvTF6OdZcYqAxEizTb9EHSRnjGN`) · `nnsight_docs+code_120k.txt` (`1iSUsTXNzL-WqO7mhX83mNMaPiSGgop1C`) · `nnsight_notebooks_150k.md` (`1lNIng6KttmI0vHoYNqf0aYwNt4jToBZD`) ·
`transformer_lens_all_400k.txt` (`1RoDjJWnZc6IH6pr65QvM7l4307p17Xpa`) · `transformer_lens_docs+code_325k.txt` (`1qbUWdtQaetsz5sUPy1f-H7IwPyOn4wfQ`) · `transformer_lens_notebooks_72k.md` (`1kMQra78CmcraRddDhTJgm4WVlYsCmyvq`).
(The Drive MCP cannot list this folder; the public embed view `embeddedfolderview?id=…` can.)

## Neel Nanda / GDM source texts (archived verbatim)
| File | What it is | Use |
|---|---|---|
| `neel_pragmatic_vision_interpretability.md` | *A Pragmatic Vision for Interpretability* — Nanda, Engels, Conmy, Rajamanoharan, Chughtai, McDougall, Kramár, Smith; AF, 2025-12-01; 8.1k words. Contents block with line numbers at top. | The framing the application is scored against: North Star → proxy task → cheapest method first, method minimalism |
| `neel_how_interp_researchers_help_agi_go_well.md` | *How Can Interpretability Researchers Help AGI Go Well?* — the companion piece: which research areas/problems they think matter. Contents block at top. | Which problem classes are considered high-value; where our North Star sits |
| `context_600k.md` | Neel's curated ~600k-token context file: his Explore/Understand/Distill research-process sequence, Steinhardt, paper-writing advice, glossary, annotated paper list, Ferrando primer, Sharkey open problems, TransformerLens/NNsight/ARENA source. 2.2 MB. | **Never load whole.** Use the index below. |
| `context_600k_index.md` | Curated TOC + line-numbered H1–H3 outline of the file above (ARENA cell markers filtered). Regenerate: `python3 scripts/mkindex_context600k.py` | Find the section, then `Read` by `offset`/`limit` or `grep -n` |
| `mats_paper_index.md` | Synthesized index of all 48 papers on Neel's MATS scholar list, each read in full: taste tag (CURRENT/COOLED against his stated interests), baselines/controls (WEAK flagged), open threads. ~185 KB. | Read whole for ideation/positioning; grep otherwise |

## Quick pointers into `context_600k.md` (line numbers from the index)
- Research process — Explore/Understand/Distill: L85; Key mindsets (truth-seeking, prioritisation, moving fast, **fail fast**): L189; Research taste: L330
- Distillation stage (compress → refine → communicate; publish negatives; discuss limitations): L168–L187
- Steinhardt, research as a stochastic decision process: L437
- Paper-writing advice: L647; *The Essence of a Paper* L685; *Rigorous Supporting Evidence* L798; *Common Pitfalls* L1117

## Archiving another Alignment Forum / LessWrong post
`scripts/af_post_to_md.py <graphql.json> <url> <out.md>` — fetch `htmlBody` via the AF GraphQL API
(`post(input:{selector:{_id:"<id from the URL>"}})`), convert with the stdlib parser, then add a
contents block. See the two `neel_*.md` files for the output format.
