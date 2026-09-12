"""Full descriptive baseline report, with shared document-bootstrap contrasts and coverage.
Run after atomic annotation, reviewed deletion scoring, and 05_analyze.py.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from claim_stats import bootstrap_weights, summarize, contrast

HERE=Path(__file__).resolve().parent
TYPES=['entity','detail','theme','forecast']
TRUTHS=['true','false','unsupported']


def main():
    atoms=pd.read_json(HERE/'02_atoms_7b.jsonl',lines=True)
    scores=pd.read_csv(HERE/'04_atomic_scores_7b.csv')
    originals=pd.read_csv(HERE/'04_atomic_expl_7b.csv')
    keys=['pilot_id','claim_id']
    if atoms.duplicated(keys).any() or scores.duplicated(keys).any(): raise ValueError('Duplicate keys')
    joined=scores.merge(atoms,on=keys,validate='one_to_one',suffixes=('','_label'),how='left',indicator=True)
    if not joined['_merge'].eq('both').all(): raise ValueError('Unlabelled scores')
    if not joined.proposition.eq(joined.proposition_label).all(): raise ValueError('Stale propositions')
    if not scores.protocol.eq('atomic-v1').all(): raise ValueError('Legacy scores')
    summary_rows=[]; comparisons=[]; coverage_rows=[]; baseline_rows=[]
    for split, ids in [('all',originals.pilot_id.tolist()),('dev',list(range(20))),('eval',list(range(20,100))),('first10',list(range(10)))]:
        base=originals[originals.pilot_id.isin(ids)]
        if base.empty: continue
        docs,w=bootstrap_weights(base.pilot_id,draws=1000,seed=0)
        frame=joined[joined.pilot_id.isin(docs)]
        labels=atoms[atoms.pilot_id.isin(docs)]
        for kind in TYPES:
            for truth in TRUTHS:
                labelcell=labels[(labels.type==kind)&(labels.truth==truth)]
                scorecell=frame[(frame.type==kind)&(frame.truth==truth)]
                coverage_rows.append(dict(split=split,type=kind,truth=truth,annotated=len(labelcell),scored=len(scorecell),
                                          fraction_scored=len(scorecell)/len(labelcell) if len(labelcell) else None,
                                          annotated_documents=int(labelcell.pilot_id.nunique()),scored_documents=int(scorecell.pilot_id.nunique())))
        for denom in ['released','local']:
            value=f'fve_drop_{denom}'
            for group,cell in [('overall',frame)]+[(f'type={t};truth={tr}',frame[(frame.type==t)&(frame.truth==tr)]) for t in TYPES for tr in TRUTHS]+[(f'truth={tr}',frame[frame.truth==tr]) for tr in TRUTHS]+[(f'subtype={st};truth={tr}',frame[(frame.subtype==st)&(frame.truth==tr)]) for st in sorted(frame.subtype.unique()) for tr in TRUTHS]+[(f'review_flag={flag}',frame[frame.review_flag==flag]) for flag in [False,True]]:
                summary_rows.append(dict(split=split,denominator=denom,group=group,**summarize(cell,docs,w,value=value)))
            for kind,cell in [('all',frame)]+[(t,frame[frame.type==t]) for t in TYPES]:
                for positive,negative in [('true','false'),('true','unsupported'),('false','unsupported')]:
                    comparisons.append(dict(split=split,denominator=denom,type=kind,**contrast(cell,docs,w,positive,negative,value)))
            baseline_rows.append(dict(split=split,denominator=denom,**summarize(base,docs,w,value=f'fve_z_{denom}')))
    tables={'cells':pd.DataFrame(summary_rows),'contrasts':pd.DataFrame(comparisons),'coverage':pd.DataFrame(coverage_rows),'original_fve':pd.DataFrame(baseline_rows)}
    for name,table in tables.items(): table.to_csv(HERE/f'06_{name}.csv',index=False)
    lines=['# Atomic claim deletion baseline — full statistical report','',
           f'Original explanations: {len(originals)} documents. Annotated: {len(atoms)} atoms in {atoms.pilot_id.nunique()} documents. Scored: {len(scores)} reviewed deletions in {scores.pilot_id.nunique()} documents.',
           '', 'Labels and deletion reviews are provisional agent judgments. FVE measures reconstruction utility, not factual truth. Atoms that could not be independently removed are excluded from deletion statistics; coverage is reported explicitly.',
           '', 'Means weight claims equally. Document-weighted means are provided alongside them. 95% percentile confidence intervals use 1,000 shared document-bootstrap draws, seed 0. True–false contrasts use the same draws for both classes. Sparse cells can have empty bootstrap replicates; the valid count is recorded. One-document cells do not support population uncertainty.',
           '', 'AUROC is the probability that a randomly chosen true (positive) claim has a greater deletion drop than a false (negative) claim, with half credit for ties. Standardized differences use the square root of the average class variance. These are descriptive exploratory comparisons; no significance claims or multiple-testing-adjusted tests are made.',
           '', 'The released denominator is a 7B training reference; the local denominator is estimated on this pilot and held fixed during bootstrap. The two scales rescale drops and confidence limits, not ranks or AUROC. The dev split informed protocol development; eval is shown separately. Provisional review flags are also broken out.', '']
    def val(x): return 'NA' if x is None or not np.isfinite(x) else f'{100*x:.3f}'
    for split in ['all','dev','eval','first10']:
        if not any(r['split']==split for r in baseline_rows): continue
        lines += [f'## {split}: original-explanation FVE','', '| Denominator | Mean % FVE | 95% CI | Median | Documents |','|---|---:|---|---:|---:|']
        for row in baseline_rows:
            if row['split']==split:
                lines.append(f"| {row['denominator']} | {val(row['mean'])} | [{val(row['lo'])}, {val(row['hi'])}] | {val(row.get('median'))} | {row['documents']} |")
        for denom in ['released','local']:
            lines += ['', f'### {denom}: mean deletion drop, percentage points', '', '| Type | Truth | Annotated | Scored | Documents | Mean [95% CI] | Median | Negative drops |','|---|---|---:|---:|---:|---|---:|---:|']
            for t in TYPES:
                for tr in TRUTHS:
                    row=next(r for r in summary_rows if r['split']==split and r['denominator']==denom and r['group']==f'type={t};truth={tr}')
                    cover=next(r for r in coverage_rows if r['split']==split and r['type']==t and r['truth']==tr)
                    lines.append(f"| {t} | {tr} | {cover['annotated']} | {row['n']} | {row['documents']} | {val(row['mean'])} [{val(row['lo'])}, {val(row['hi'])}] | {val(row.get('median'))} | {val(row.get('negative_fraction'))}% |")
            lines += ['', '| Type | True − false mean (pp) | 95% CI | AUROC |','|---|---:|---|---:|']
            for row in comparisons:
                if row['split']==split and row['denominator']==denom and row['positive']=='true' and row['negative']=='false':
                    auc='NA' if row.get('auc') is None else f"{row['auc']:.3f}"
                    lines.append(f"| {row['type']} | {val(row['mean_difference'])} | [{val(row.get('lo'))}, {val(row.get('hi'))}] | {auc} |")
    lines += ['', '## Machine-readable detail', '', '- `06_cells.csv`: type/truth, subtype/truth, review flags, percentiles, SD, negative-drop fractions, and document-weighted means.', '- `06_contrasts.csv`: pairwise truth contrasts, shared-bootstrap CIs, AUROC and standardized differences.', '- `06_coverage.csv`: annotated versus independently scored claims per cell.', '- `06_original_fve.csv`: absolute reconstruction FVE of original explanations. CSV FVE values are fractions; multiply by 100 for percentages or percentage-point drops.', '']
    (HERE/'06_baseline_report.md').write_text('\n'.join(lines))
    print(f'Wrote report and four statistical tables for {len(scores)} reviewed deletions.')


if __name__=='__main__': main()
