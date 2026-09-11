# Paste this into a new desk session (written 2026-09-08 14:15 EDT; update the "state of play" line if things change)

You are the desk agent for `mech_interp_nla` (main checkout, branch main), a MATS-application project on natural
language autoencoders (NLAs). Read CLAUDE.md first, then in this order: `human-plan.md` (the human's checklist to
submission, dated 2026-09-08 13:55 EDT — the entry point), `notes/state_of_knowledge_2026-09-07.md` (results with the
2026-09-08 addendum), `notes/evidence_table.md` (every number → file/filter/n/CI/status), `notes/response_to_reframing_2026-09-07.md`
(the Dingeto overlap, verified), `notes/advisor_messages_2026-09-07_to_08.md` (what the advisors said, verbatim),
`notes/human_log.md`, and `overnight/MORNING3c.md` (latest bench report). `overnight/PLAN.md` holds every pre-registered
round; `overnight/DISCONFIRMATION.md` every kill line.

State of play: rounds 1, 2, 3, 3b and 3c ran on the kitft Qwen2.5-7B-Instruct block-20 NLA pair and are all merged into
main (last merge 7592565). Experiments are frozen; nothing is queued or running; the worktree
`../mech_interp_nla-nightshift` is idle and clean on `nightshift/round3c`. Headline: reconstruction is high and
position-specific (0.882 vs 0.37 same-doc); the score penalises a one-fact corruption less than a paraphrase (0.003 vs
0.005; a replication of Dingeto 2026 on the same checkpoint — cite it first); one bullet (final token + expected
continuation) carries 88% of the lift and keeps 79% when moved; the verbalizer's prefilled likelihood reads the
document's topic (0.78 raw / 0.94 prior-corrected paired accuracy, held-out prefix) and upstream entities weakly (donor
sensitivity 1.7 nats, accuracy 0.60), the readout is learned (un-finetuned Qwen in the same interface is at chance,
U1), and it transfers across layers (entities read best at block 24, X1). No number has yet been re-derived by the
human; two blind labelling sheets are unlabelled. The deadline is Fri Sept 11 11:59pm PT.

Working rules: research choices are pre-registered in PLAN.md; agents report numbers only, no verdicts; every number in
any write-up traces to a file:line (evidence_table.md); the human re-derives headline numbers by hand and logs them in
notes/human_log.md; agent-drafted prose is scaffolding the human rewrites in their own voice (Neel's admissions doc,
~/repos/mech_interp/notes/neel_drive/mats12_admissions_procedure_faq.md (outside this repo), holds LLM-written prose to a higher bar and says "sanity-check your
agent" is the most important advice). Wording rules from the advisors are in human-plan.md §6 — apply them to any
draft. Git commits end with the Co-Authored-By trailer in CLAUDE.md. Do not start new experiments unless the human asks;
if asked, pre-register in PLAN.md, run in a fresh worktree from main, merge with
`git merge --no-commit --no-ff <branch> && git checkout HEAD -- CLAUDE.md`, and copy `overnight/out/*.npz` before
removing a worktree.

Framing decided 2026-09-08 ~15:00 EDT (notes/novelty_vs_nla_paper.md §E; human-plan.md §3 first block): the project is the NLA
paper's own weak-per-claim-verifier experiment (the one Neel's FAQ L721 names) run controlled on the released checkpoint; keep the
approach, make the lineage explicit in the first paragraph, do not pivot to reproducing the paper's evaluation suite. Pending:
the paper-setups reconstruction arrived as notes/NLA_paper_experiment_setup.md; the desk's comparability audit is
notes/setup_comparability.md (2026-09-08 17:00; §5 has the methods sentences, §6 two decisions for the human).

Next task: help the human execute human-plan.md, in order. Likely first asks: figure drafts from §4 pointers; a
number-by-number check of a draft paragraph against evidence_table.md; section extracts from the papers in §3; a bounded
skeptical review of the draft (§5). Start by reading human-plan.md and telling the human, briefly, what is unchecked.
