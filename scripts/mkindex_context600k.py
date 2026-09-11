import os, re, sys
NOTES=os.path.expanduser('~/repos/mech_interp/notes')  # the context file moved out of this repo 2026-09-11
src=f'{NOTES}/context_600k.md'; out=f'{NOTES}/context_600k_index.md'
lines=open(src,encoding='utf-8').read().split('\n')
# curated TOC = everything before the first real post heading "# [" (line 85)
first=next(i for i,l in enumerate(lines) if l.startswith('# ['))
toc='\n'.join(lines[:first]).rstrip()
# outline: H1-H3, skipping fenced code and ARENA notebook cell markers
entries=[]; fence=False
skip=re.compile(r'^#\s*(!|HIDE\b|%)')
for i,l in enumerate(lines,1):
    if l.startswith('```'): fence=not fence; continue
    if fence: continue
    m=re.match(r'^(#{1,3}) (.+)$',l)
    if not m or skip.match(l): continue
    lvl=len(m.group(1)); txt=m.group(2).strip()
    txt=re.sub(r'\]\(https?://[^)]+\)',']',txt)          # drop URLs, keep [title]
    txt=re.sub(r'\*\*','',txt)
    if len(txt)>110: txt=txt[:107]+'...'
    entries.append((i,lvl,txt))
n1=sum(1 for e in entries if e[1]==1); n2=sum(1 for e in entries if e[1]==2); n3=sum(1 for e in entries if e[1]==3)
body=[]
for i,lvl,txt in entries:
    body.append(f"{'  '*(lvl-1)}- L{i}: {txt}")
hdr=f"""# Index — ~/repos/mech_interp/notes/context_600k.md

Curated mech-interp context file (≈600k tokens, {len(lines):,} lines, 2.2 MB). Three parts:
research philosophy (Neel Nanda's Explore/Understand/Distill sequence, Steinhardt, paper-writing
advice) · foundations (glossary, annotated paper list, Ferrando primer, Sharkey open problems) ·
tooling (TransformerLens, NNsight, ARENA tutorials as raw notebook source).

**How to use.** Do not load the whole file. Find the section here, then read by line range
(`Read` with `offset`/`limit`, or `sed -n 'A,Bp'`), or grep:
`grep -n "term" ~/repos/mech_interp/notes/context_600k.md`. Line numbers below are 1-based and current as of the
file's 2026-09-05 copy; regenerate with `python3 scratchpad/mkindex.py` after any edit.

**What the outline filters out.** Part III contains ARENA notebook source, whose cell markers
(`# ! CELL TYPE`, `# ! TAGS`, `# ! FILTERS`, `# HIDE`) look like ~4,150 H1 headings. They are
excluded. Real headings kept: {n1} H1 · {n2} H2 · {n3} H3.

---

## 1. Curated table of contents (verbatim from the file head, lines 1–{first})

{toc}

---

## 2. Line-numbered outline (H1–H3, code blocks and cell markers skipped)

"""
open(out,'w',encoding='utf-8').write(hdr+'\n'.join(body)+'\n')
print(f"index written: {len(body)} outline entries (H1 {n1}, H2 {n2}, H3 {n3}); first real post at L{first+1}")
