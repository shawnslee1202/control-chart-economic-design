"""Additional reporting: budget effects, costs, validation and evidence gaps."""
from pathlib import Path
import json,itertools
import numpy as np
import pandas as pd
from scipy import stats
from parse_run import read_table,estimate_events
ROOT=Path(__file__).resolve().parent

def welch(x,y):
    x=np.asarray(x);y=np.asarray(y);v=x.var(ddof=1)/len(x)+y.var(ddof=1)/len(y)
    if v==0:return (float(y.mean()-x.mean()),0,0,1)
    dof=v*v/((x.var(ddof=1)/len(x))**2/(len(x)-1)+(y.var(ddof=1)/len(y))**2/(len(y)-1))
    d=y.mean()-x.mean();half=stats.t.ppf(.975,dof)*np.sqrt(v)
    return float(d),float(d-half),float(d+half),float(stats.ttest_ind(x,y,equal_var=False).pvalue)

def main():
    out=ROOT/'results';df=pd.read_csv(out/'run_table.csv');rows=[]
    for n in [2,4,5,8]:
        a=df[(df.experiment=='A80')&(df.n==n)];b=df[(df.experiment=='A160')&(df.n==n)]
        d,lo,hi,p=welch(a.bad_per_day,b.bad_per_day)
        rows.append(dict(n=n,difference_160_minus_80=d,ci_low=lo,ci_high=hi,p_unadjusted=p,
                         effort80=a.units_per_day.mean(),effort160=b.units_per_day.mean()))
    pd.DataFrame(rows).to_csv(out/'budget_effects.csv',index=False)
    # Compare physical policies, pooling independently collected identical plans.
    g=df.groupby('economic_plan');winner=g.cost_day.mean().idxmin();a=g.get_group(winner)
    rows=[]
    for name,b in g:
        if name==winner:continue
        d,lo,hi,p=welch(a.cost_day,b.cost_day)
        rows.append(dict(recommended=winner,alternative=name,cost_alternative_minus_recommended=d,ci_low=lo,ci_high=hi,p_unadjusted=p,n_recommended=len(a),n_alternative=len(b)))
    pd.DataFrame(rows).to_csv(out/'cost_differences.csv',index=False)
    # Signal comparison cannot identify true FA; preserve the distinction.
    rows=[]
    for name,b in df.groupby('economic_plan'):
        total=int(b.signals.sum());e=float(b.expected_FA_all_in_control.sum())
        rows.append(dict(plan=name,signals=total,expected_if_always_in_control=e,
                         poisson_95_low=stats.poisson.ppf(.025,e),poisson_95_high=stats.poisson.ppf(.975,e),
                         interpretation='reference only; true in-control exposure unknown'))
    pd.DataFrame(rows).to_csv(out/'signal_reference.csv',index=False)
    # Preserve normalized daily records; defect occurrences remain distinct.
    days=[];defects=[]
    for run in df.run_id:
        p=read_table(ROOT/'runs'/run,'production');p['run_id']=run;days.append(p)
        q=read_table(ROOT/'runs'/run,'quality');q=q[q.iloc[:,2]!='Xbar control chart signaled']
        defects.extend(q.iloc[:,1].tolist())
    pd.concat(days).to_csv(out/'daily_production.csv',index=False)
    pd.Series(defects).value_counts().rename_axis('defect').rename('records').to_csv(out/'defect_pareto.csv')
    # Distinct-data audit excludes metadata hashes (timestamps alone differ).
    import hashlib
    hashes={r:hashlib.sha256((ROOT/'runs'/r/'production.json').read_bytes()+(ROOT/'runs'/r/'observations.json').read_bytes()).hexdigest() for r in df.run_id}
    duplicates=len(hashes)-len(set(hashes.values()))
    validation=pd.read_csv(out/'validation.csv')
    audit=dict(experiment_runs=len(df),production_days=int(validation.production_days.sum()),
               chart_subgroups=int(validation.chart_rows.sum()),quality_records=int(validation.quality_rows.sum()),
               baseline_individuals=600,duplicate_output_pairs=duplicates,
               signal_count_mismatches=int((validation.signal_difference!=0).sum()),
               timestamp_mismatches=int(validation.timestamp_mismatch.sum()),
               max_budget_deviation_percent=float(((df[df.experiment.isin(['A80','A160'])].units_per_day/df[df.experiment.isin(['A80','A160'])].budget_target-1).abs()*100).max()))
    (out/'verification_summary.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
    # Explicit absence is preferable to inventing shift-size/delay estimates.
    events=pd.read_csv(out/'signal_events.csv');est=events[events.classification=='sustained-shift evidence']
    if len(est)==0:
        (out/'detection_identifiability.md').write_text('No signal had sustained pre-signal shift evidence under the prespecified rule. Empirical shift size, detection-delay distribution, true false-alarm count and a fitted Duncan optimum are not identifiable from this experiment. This is not proof that no special causes occurred: rapid detections can leave too little pre-signal evidence. See signal_events.csv for every unclassified event and arl_sensitivity.csv / renewal_sensitivity.csv for explicitly theoretical scenarios.\n')

if __name__=='__main__':main()
