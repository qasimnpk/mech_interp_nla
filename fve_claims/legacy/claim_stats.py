"""Document-cluster uncertainty for claim-level descriptive statistics (no model imports)."""
import numpy as np
import pandas as pd


def bootstrap_weights(documents, draws=1000, seed=0):
    ids = np.asarray(sorted(set(documents)))
    if not len(ids): raise ValueError('No documents')
    rng = np.random.default_rng(seed)
    weights = rng.multinomial(len(ids), np.full(len(ids), 1 / len(ids)), size=draws)
    return ids, weights


def summarize(frame, ids, weights, value='fve_drop_released'):
    """Claim-weighted mean, resampling whole documents from the selected population."""
    x = frame[value].to_numpy(float)
    if not len(x): return dict(n=0, documents=0, mean=None, lo=None, hi=None)
    grouped = frame.groupby('pilot_id')[value].agg(['sum', 'count']).reindex(ids, fill_value=0)
    numer = weights @ grouped['sum'].to_numpy()
    denom = weights @ grouped['count'].to_numpy()
    boot = np.divide(numer, denom, out=np.full(len(denom), np.nan), where=denom > 0)
    q = np.quantile(x, [0, .1, .25, .5, .75, .9, 1])
    return dict(n=len(x), documents=int(frame.pilot_id.nunique()), mean=float(x.mean()),
                lo=float(np.nanquantile(boot, .025)), hi=float(np.nanquantile(boot, .975)),
                sd=float(x.std(ddof=1)) if len(x)>1 else None,
                minimum=q[0], p10=q[1], p25=q[2], median=q[3], p75=q[4], p90=q[5], maximum=q[6],
                negative_fraction=float((x<0).mean()), zero_fraction=float((x==0).mean()),
                document_weighted_mean=float(frame.groupby('pilot_id')[value].mean().mean()),
                valid_bootstrap_draws=int(np.isfinite(boot).sum()))


def mean_bootstrap(frame, ids, weights, value):
    groups = frame.groupby('pilot_id')[value].agg(['sum','count']).reindex(ids,fill_value=0)
    count=weights @ groups['count'].to_numpy()
    return np.divide(weights @ groups['sum'].to_numpy(), count, out=np.full(len(count),np.nan), where=count>0)


def contrast(frame, ids, weights, positive='true', negative='false', value='fve_drop_released'):
    a,b=frame[frame.truth==positive],frame[frame.truth==negative]
    if a.empty or b.empty: return dict(positive=positive, negative=negative, n_positive=len(a), n_negative=len(b), mean_difference=None)
    av,bv=a[value].to_numpy(),b[value].to_numpy()
    boots=mean_bootstrap(a,ids,weights,value)-mean_bootstrap(b,ids,weights,value)
    # AUROC = probability a randomly selected positive has a larger drop; ties receive half credit.
    ranks=pd.Series(np.r_[av,bv]).rank(method='average').to_numpy()
    auc=(ranks[:len(av)].sum()-len(av)*(len(av)+1)/2)/(len(av)*len(bv))
    pooled=np.sqrt((av.var(ddof=1)+bv.var(ddof=1))/2) if min(len(av),len(bv))>1 else np.nan
    return dict(positive=positive,negative=negative,n_positive=len(a),n_negative=len(b),
                mean_difference=float(av.mean()-bv.mean()),lo=float(np.nanquantile(boots,.025)),hi=float(np.nanquantile(boots,.975)),
                auc=float(auc),standardized_difference=float((av.mean()-bv.mean())/pooled) if pooled>0 else None,
                valid_bootstrap_draws=int(np.isfinite(boots).sum()))
