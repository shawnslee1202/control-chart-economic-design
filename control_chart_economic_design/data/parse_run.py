"""Parse complete visible simulator tables. Raw JSON retains original row order.
Usage: python -m control_chart_economic_design.data.parse_run runs/RUN_ID
"""
from pathlib import Path
import json, re, argparse
from datetime import datetime
import numpy as np
import pandas as pd
from scipy.stats import norm
TARGET = 'Base-Snap Point Opening'

def read_table(folder, name):
    p=Path(folder)/(name+'.json')
    if p.exists():
        rows=json.loads(p.read_text())
        if not rows or any(len(r)!=len(rows[0]) for r in rows):
            raise ValueError(f'Incomplete/ragged table: {p}')
        return pd.DataFrame(rows[1:],columns=rows[0])
    return pd.read_csv(Path(folder)/(name+'.csv'))

def timestamp(s):
    s=re.sub(r'\s+C[DS]T\s+',' ',s)
    s=re.sub(r'^[A-Za-z]{3}\s+','',s)
    for fmt in ('%b %d %H:%M:%S %Y','%m-%d-%Y %H:%M:%S','%b %d, %Y'):
        try:return datetime.strptime(s,fmt)
        except ValueError:pass
    raise ValueError(f'Unknown timestamp: {s}')

def operating_gaps(times):
    gaps=times.diff().dt.total_seconds()
    same=times.dt.date.eq(times.shift().dt.date)
    lunch = times.shift().dt.hour.between(11,12) & times.dt.hour.ge(13)
    ordinary=gaps[same & ~lunch & (gaps>0)]
    med=ordinary.median()
    return ordinary[ordinary < max(1800,2.5*med)]

def estimate_events(obs,meta):
    # Signal values are excluded from the shift fit to reduce selection bias.
    # Isolated extremes remain unclassified, not automatically false alarms.
    mu,sig,n=meta['mu'],meta['sigma'],meta['n']
    z=(obs.iloc[:,1].astype(float).to_numpy()-mu)/(sig/np.sqrt(n))
    hit=np.flatnonzero((obs.iloc[:,1].astype(float)<obs.iloc[:,2].astype(float)) |
                      (obs.iloc[:,1].astype(float)>obs.iloc[:,3].astype(float)))
    times=obs.iloc[:,0].map(timestamp)
    effective_h=float(operating_gaps(times).median())
    events=[];previous=-1
    for j in hit:
        start=max(previous+1,j-20); w=z[start:j];best=(0,None,None)
        for k in range(2,len(w)+1):
            a=w[-k:];score=k*float(a.mean())**2
            if score>best[0]:best=(score,k,float(a.mean()/np.sqrt(n)))
        evidence=best[1] is not None and best[0]>2*np.log(max(len(w),2))+6
        k=best[1] if evidence else None
        events.append(dict(run_id=meta['run_id'],signal_index=int(j),signal_time=str(times.iloc[j]),
            classification='sustained-shift evidence' if evidence else 'unclassified',
            pre_signal_points=len(w),score=best[0],delta_hat=best[2] if evidence else np.nan,
            onset_index=int(j-k) if evidence else np.nan,
            delay_lower_seconds=k*effective_h if evidence else np.nan,
            delay_upper_seconds=(k+1)*effective_h if evidence else np.nan,
            window_left_censored=bool(evidence and k==len(w)),effective_h_seconds=effective_h))
        previous=int(j)
    return events

def parse_run(folder):
    folder=Path(folder);meta=json.loads((folder/'metadata.json').read_text())
    p=read_table(folder,'production');q=read_table(folder,'quality');o=read_table(folder,'observations')
    if len(p)!=meta['days']:raise ValueError(f'{folder}: incomplete production horizon')
    dates=p.iloc[:,0].map(timestamp).dt.date
    ot=o.iloc[:,0].map(timestamp);qt=q.iloc[:,0].map(timestamp)
    if dates.nunique()!=meta['days'] or set(ot.dt.date)!=set(dates) or set(qt.dt.date)!=set(dates):
        raise ValueError(f'{folder}: incomplete/incorrect table horizon')
    values=o.iloc[:,1:].apply(pd.to_numeric)
    if not np.isfinite(values.to_numpy()).all():raise ValueError('Nonfinite chart values')
    expected=(meta['mu']-meta['L']*meta['sigma']/np.sqrt(meta['n']),meta['mu']+meta['L']*meta['sigma']/np.sqrt(meta['n']))
    if not (np.allclose(values.iloc[:,1],expected[0],rtol=0,atol=1e-12) and np.allclose(values.iloc[:,2],expected[1],rtol=0,atol=1e-12)):
        raise ValueError('Limits do not match plan')
    sig=q.iloc[:,2].str.strip().eq('Xbar control chart signaled')
    outside=(values.iloc[:,0]<values.iloc[:,1])|(values.iloc[:,0]>values.iloc[:,2])
    signal_times=set(qt[sig].astype(str));outside_times=set(ot[outside].astype(str))
    row={**meta,'observations':len(o),'subgroups_per_day':len(o)/len(p),
         'units_per_day':meta['n']*len(o)/len(p),'effective_h_seconds':float(operating_gaps(ot).median()),
         'signals':int(sig.sum()),'outside_points':int(outside.sum()),
         'signal_count_difference':int(sig.sum()-outside.sum()),
         'unmatched_signal_timestamps':len(signal_times.symmetric_difference(outside_times)),
         'target_defect_records':int((q.iloc[:,1].eq(TARGET)&~sig).sum()),
         'expected_FA_all_in_control':len(o)*2*norm.sf(meta['L'])}
    for col,key in [('Good Parts','good'),('Bad Parts','bad'),('Offspec Parts','offspec')]:
        p[col]=pd.to_numeric(p[col]);row[key+'_per_day']=float(p[col].mean())
    row['total_per_day']=sum(row[x+'_per_day'] for x in ['good','bad','offspec'])
    events=estimate_events(o,meta)
    row['sustained_shift_signals']=sum(x['classification']=='sustained-shift evidence' for x in events)
    row['unclassified_signals']=int(outside.sum())-row['sustained_shift_signals']
    return row,events,p,q,o

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('folder');args=ap.parse_args()
    row,*_=parse_run(args.folder);print(json.dumps(row,indent=2,default=str))

