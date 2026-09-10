"""Step 5 (atomic-v1, truth v2): join per-claim deletion scores (04_scores_7b.csv) with atom labels (tasks/02_atoms_v2_7b_doc*.jsonl
for relabelled docs, else tasks/02_atoms_7b_doc*.jsonl if already v2) and produce the paper-layout numbers:
mean FVE drop (pp) by type × truth (true / false) for theme, entity, detail; false related vs unrelated overall; irrelevant
reported separately; cluster-bootstrap CIs by document (1000, seed 0). Figure in the paper's two-panel layout."""
import argparse, glob, json
import numpy as np, pandas as pd
from common import *

TYPES = ["theme", "entity", "detail"]

def load_atoms():
    recs = {}
    for f in sorted(glob.glob(str(HERE / "tasks/02_atoms_7b_doc*.jsonl"))):
        for l in open(f):
            r = json.loads(l); recs[(r["pilot_id"], r["claim_id"])] = r
    for f in sorted(glob.glob(str(HERE / "tasks/02_atoms_v2_7b_doc*.jsonl"))):  # v2 relabels override
        for l in open(f):
            r = json.loads(l); recs[(r["pilot_id"], r["claim_id"])] = r
    df = pd.DataFrame(recs.values())
    df["v2"] = df.truth.isin(["true", "false", "irrelevant"]) & ((df.truth != "false") | df.get("related", pd.Series(dtype=str)).isin(["related", "unrelated"]))
    df["cls"] = np.where(df.truth == "false", "false_" + df.get("related", "NA").astype(str), df.truth)
    return df

def ci(vals, clusters, n_boot=1000, seed=0, method="sem"):
    """method='sem': mean +/- 1.96*std/sqrt(n) over individual claims (independence assumed; matches the paper's
    stated method for its one error-barred figure). method='bootstrap': cluster bootstrap by document (pilot_id),
    kept for comparison since pilot_id/claim_id stay on every row and either can be recomputed from 04_scores_7b.csv."""
    vals = np.asarray(vals, float); clusters = np.asarray(clusters)
    if len(vals) == 0: return dict(mean=np.nan, lo=np.nan, hi=np.nan, n=0, k=0)
    k = int(len(np.unique(clusters)))
    if method == "sem":
        m, se = float(vals.mean()), float(vals.std(ddof=1) / np.sqrt(len(vals))) if len(vals) > 1 else 0.0
        return dict(mean=m, lo=m - 1.96 * se, hi=m + 1.96 * se, n=int(len(vals)), k=k, se=se)
    uniq, inv = np.unique(clusters, return_inverse=True); rng = np.random.default_rng(seed); boots = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(uniq), len(uniq)); m_ = np.concatenate([np.flatnonzero(inv == p) for p in pick]); boots.append(vals[m_].mean())
    return dict(mean=float(vals.mean()), lo=float(np.percentile(boots, 2.5)), hi=float(np.percentile(boots, 97.5)), n=int(len(vals)), k=k)

def fmt(c): return f"{c['mean']*100:.3f} +/- {(c['hi']-c['mean'])*100:.3f} (n={c['n']}, docs={c['k']})" if c["n"] else "n=0"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--split", default="all", choices=["all", "dev", "eval"]); ap.add_argument("--denom", default="released", choices=["released", "local"])
    ap.add_argument("--stat", default="sem", choices=["sem", "bootstrap"]); ap.add_argument("--scores", default=None, help="path to a 04_scores_7b*.csv batch file; default merges every batch file found")
    a = ap.parse_args()
    score_files = [Path(a.scores)] if a.scores else sorted(HERE.glob("04_scores_7b*.csv"))
    sc = pd.concat([pd.read_csv(f) for f in score_files], ignore_index=True) if score_files else pd.DataFrame()
    atoms = load_atoms()
    df = sc.merge(atoms[["pilot_id", "claim_id", "type", "subtype", "truth", "related", "cls", "v2", "review_flag"]], on=["pilot_id", "claim_id"], how="inner")
    if a.split != "all": df = df[df.split == a.split]
    n_not_v2 = int((~df.v2).sum()); df = df[df.v2]
    col = f"fve_drop_{a.denom}"
    A = np.load(OUT / "acts_7b.npz")["h20"].astype(np.float64)
    An = A / np.linalg.norm(A, axis=1, keepdims=True) * np.sqrt(A.shape[1])
    D_local = float(((An - An.mean(0)) ** 2).sum(1).mean() / A.shape[1])
    D = {"released": FVE_DENOM_RELEASED_7B, "local": D_local}[a.denom]
    S = settings("05", split=a.split, denom=a.denom, n_scored=len(sc), n_atoms=len(atoms), n_joined=len(df), n_not_v2=n_not_v2)
    rel = df[df.truth != "irrelevant"]
    L_ = [f"# fve_claims baseline — FVE drop when one atomic claim is removed (7B, DocRED pilot, {a.split}, D_{a.denom} = {D:.4f})", "",
          f"Claims scored {len(sc)}; atoms labelled {len(atoms)} ({atoms.pilot_id.nunique()} docs); joined {len(df)} over {df.pilot_id.nunique()} docs ({n_not_v2} dropped: not yet relabelled to v2). FVE drop in percentage points; error = {'+/-1.96*SEM over individual claims (independence assumed)' if a.stat=='sem' else 'cluster bootstrap 95% CI by document (1000 draws, seed 0)'}. Labels provisional (agents).", "",
          "Counts by type × class: " + json.dumps({t: df[df.type == t].cls.value_counts().to_dict() for t in TYPES + ["forecast"]}), "",
          "## Type × truth (irrelevant excluded)", "", "| type | true | false | true − false |", "|---|---|---|---|"]
    for t in TYPES:
        s = rel[rel.type == t]; ct, cf = ci(s[s.truth == "true"][col], s[s.truth == "true"].pilot_id, method=a.stat), ci(s[s.truth == "false"][col], s[s.truth == "false"].pilot_id, method=a.stat)
        L_.append(f"| {t} | {fmt(ct)} | {fmt(cf)} | {(ct['mean']-cf['mean'])*100:.3f} |" if ct["n"] and cf["n"] else f"| {t} | {fmt(ct)} | {fmt(cf)} | — |")
    ct, cf = ci(rel[rel.truth == "true"][col], rel[rel.truth == "true"].pilot_id, method=a.stat), ci(rel[rel.truth == "false"][col], rel[rel.truth == "false"].pilot_id, method=a.stat)
    L_.append(f"| **all** | {fmt(ct)} | {fmt(cf)} | {(ct['mean']-cf['mean'])*100:.3f} |")
    # companion table: mean raw FVE (not the drop) per class, both fve_z (full explanation) and fve_del (claim removed)
    col_z, col_del = f"fve_z_{a.denom}", f"fve_del_{a.denom}"
    L_ += ["", "## Mean raw FVE per class (not the drop): fve_z = FVE of the full explanation containing the claim; fve_del = FVE with that claim removed", "",
           "| type | truth | mean fve_z | mean fve_del | n |", "|---|---|---|---|---|"]
    for t in TYPES:
        for tr in ("true", "false"):
            s_ = rel[(rel.type == t) & (rel.truth == tr)]
            if len(s_): L_.append(f"| {t} | {tr} | {s_[col_z].mean()*100:.3f} | {s_[col_del].mean()*100:.3f} | {len(s_)} |")
    L_.append(f"| **all** | true | {rel[rel.truth=='true'][col_z].mean()*100:.3f} | {rel[rel.truth=='true'][col_del].mean()*100:.3f} | {len(rel[rel.truth=='true'])} |")
    L_.append(f"| **all** | false | {rel[rel.truth=='false'][col_z].mean()*100:.3f} | {rel[rel.truth=='false'][col_del].mean()*100:.3f} | {len(rel[rel.truth=='false'])} |")
    fa = rel[rel.truth == "false"]
    L_ += ["", "## False claims by relatedness (all types)", "", "| related | unrelated |", "|---|---|", f"| {fmt(ci(fa[fa.related=='related'][col], fa[fa.related=='related'].pilot_id, method=a.stat))} | {fmt(ci(fa[fa.related=='unrelated'][col], fa[fa.related=='unrelated'].pilot_id, method=a.stat))} |"]
    ir = df[df.truth == "irrelevant"]
    L_ += ["", f"Irrelevant (forecast / model_output) claims, reported separately: {fmt(ci(ir[col], ir.pilot_id, method=a.stat))}", "",
           "Paper (Claude NLAs): theme 0.25 / 0.09; entity 0.37 / 0.12; detail 0.35 / 0.16; related 0.14, unrelated 0.06 (percent FVE, true / false).", "",
           "## Percentiles of the drop (pp) by class: 10 / 25 / 50 / 75 / 90", ""]
    for c in ["true", "false_related", "false_unrelated", "irrelevant"]:
        v = df[df.cls == c][col] * 100
        if len(v): L_.append(f"- {c}: " + " / ".join(f"{np.percentile(v, p):.3f}" for p in (10, 25, 50, 75, 90)) + f"  (n={len(v)}, negative {int((v<0).sum())})")
    L_ += ["", f"Deletions with preserves_other_propositions=false: {int((df.preserves_other == False).sum())} (kept in the tables; listed in 04_scores_7b.csv)."]
    (HERE / f"05_summary_{a.split}_{a.denom}.md").write_text("\n".join(L_))
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    (HERE / "fig").mkdir(exist_ok=True); fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.3, 1]}); x = np.arange(3); wb = 0.38
    for j, (tr, colr) in enumerate((("true", "#3b7dd8"), ("false", "#c0504d"))):
        cs = [ci(rel[(rel.type == t) & (rel.truth == tr)][col], rel[(rel.type == t) & (rel.truth == tr)].pilot_id) for t in TYPES]
        m = [c["mean"] * 100 for c in cs]; err = [[c["mean"] * 100 - c["lo"] * 100 for c in cs], [c["hi"] * 100 - c["mean"] * 100 for c in cs]]
        ax[0].bar(x + (j - 0.5) * wb, m, wb, yerr=err, capsize=3, color=colr, label=f"{tr.capitalize()} claims")
        for xi, c in zip(x + (j - 0.5) * wb, cs): ax[0].text(xi, (c["hi"] * 100 if c["n"] else 0) + 0.02, f"{c['mean']*100:.2f}% (n={c['n']})", ha="center", fontsize=7)
    ax[0].set_xticks(x); ax[0].set_xticklabels([t.capitalize() for t in TYPES]); ax[0].set_ylabel("FVE drop when removed (pp)"); ax[0].set_xlabel("Type of claim removed"); ax[0].legend(); ax[0].set_title("Removing true vs false claims — 7B, DocRED pilot", fontsize=10)
    cs = [ci(fa[fa.related == r][col], fa[fa.related == r].pilot_id, method=a.stat) for r in ("related", "unrelated")]
    ax[1].bar([0, 1], [c["mean"] * 100 for c in cs], 0.6, yerr=[[c["mean"] * 100 - c["lo"] * 100 for c in cs], [c["hi"] * 100 - c["mean"] * 100 for c in cs]], capsize=3, color=["#e8cdbf", "#a0522d"])
    for xi, c in zip([0, 1], cs): ax[1].text(xi, (c["hi"] * 100 if c["n"] else 0) + 0.02, f"{c['mean']*100:.2f}% (n={c['n']})", ha="center", fontsize=7)
    ax[1].set_xticks([0, 1]); ax[1].set_xticklabels(["Related", "Unrelated"]); ax[1].set_xlabel("How related the false claim is"); ax[1].set_title("Related vs unrelated false claims", fontsize=10)
    for axx in ax: axx.axhline(0, color="k", lw=0.8)
    fig.tight_layout(); fig.savefig(HERE / "fig" / f"fve_drop_7b_{a.split}_{a.denom}.png", dpi=160)
    finish("05", S); print("\n".join(L_[:16]))

if __name__ == "__main__":
    main()
