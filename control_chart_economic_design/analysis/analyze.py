"""Rebuild all empirical tables, tests, uncertainty, and economic maps.
Run from repository root: python -m control_chart_economic_design.analysis.analyze
"""
from pathlib import Path
import json, itertools, hashlib, sys
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from control_chart_economic_design.data.parse_run import parse_run
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)
RNG=np.random.default_rng(3502026)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':150})

def savefig(name):
    plt.savefig(FIG/(name+'.png'),bbox_inches='tight',dpi=180)
    plt.savefig(FIG/(name+'.svg'),bbox_inches='tight');plt.close()

def arl(n,L,delta):
    return 1/(stats.norm.sf(L-delta*np.sqrt(n))+stats.norm.cdf(-L-delta*np.sqrt(n)))

def baseline():
    groups=[];details=[]
    for p in sorted((ROOT/'runs').glob('Baseline*/observations.json')):
        a=np.array([float(r[1]) for r in json.loads(p.read_text())]).reshape(-1,5)
        groups.append(a);details.append({'run':p.parent.name,'mean':a.mean(),'within_sd':np.sqrt(a.var(axis=1,ddof=1).mean())})
    a=np.concatenate(groups);mu=a.mean();sigma=np.sqrt(a.var(axis=1,ddof=1).mean())
    b=dict(mu=mu,sigma=sigma,range_sigma=np.ptp(a,axis=1).mean()/2.326,
           shapiro_individuals_p=stats.shapiro(a.ravel()).pvalue,shapiro_means_p=stats.shapiro(a.mean(axis=1)).pvalue,
           subgroups=len(a),individuals=a.size,
           lag1_means=np.corrcoef(a.mean(axis=1)[:-1],a.mean(axis=1)[1:])[0,1])
    (OUT/'baseline_diagnostics.json').write_text(json.dumps(b,indent=2));pd.DataFrame(details).to_csv(OUT/'baseline_by_run.csv',index=False)
    fig,ax=plt.subplots(1,2,figsize=(9,3.4));stats.probplot(a.ravel(),plot=ax[0]);stats.probplot(a.mean(axis=1),plot=ax[1]);ax[0].set_title('Individuals: pooled baseline');ax[1].set_title('Subgroup means: n = 5');fig.tight_layout();savefig('baseline_qq')
    return b

def tests(df):
    rows=[];pairs=[]
    for exp,d in df.groupby('experiment'):
        groups=[g.bad_per_day.to_numpy() for _,g in d.groupby('plan')]
        if len(groups)<2 or min(map(len,groups))<2:continue
        f,p=stats.f_oneway(*groups);kw=stats.kruskal(*groups)
        residuals=np.concatenate([g-g.mean() for g in groups])
        rows.append(dict(experiment=exp,n_runs=len(d),F=f,p_anova=p,p_kruskal=kw.pvalue,
                         p_shapiro_residuals=stats.shapiro(residuals).pvalue,p_levene=stats.levene(*groups,center='median').pvalue))
        t=pairwise_tukeyhsd(d.bad_per_day,d.plan)
        pd.DataFrame(t._results_table.data[1:],columns=t._results_table.data[0]).to_csv(OUT/f'tukey_{exp}.csv',index=False)
        for (a,x),(b,y) in itertools.combinations(d.groupby('plan'),2):
            xx=x.bad_per_day.to_numpy();yy=y.bad_per_day.to_numpy();v=xx.var(ddof=1)/len(xx)+yy.var(ddof=1)/len(yy)
            dof=v*v/((xx.var(ddof=1)/len(xx))**2/(len(xx)-1)+(yy.var(ddof=1)/len(yy))**2/(len(yy)-1))
            half=stats.t.ppf(.975,dof)*np.sqrt(v);diff=yy.mean()-xx.mean()
            pairs.append(dict(experiment=exp,plan_a=a,plan_b=b,difference_b_minus_a=diff,ci_low=diff-half,ci_high=diff+half,p_welch=stats.ttest_ind(xx,yy,equal_var=False).pvalue))
    pd.DataFrame(rows).to_csv(OUT/'tests.csv',index=False);pd.DataFrame(pairs).to_csv(OUT/'pairwise_welch.csv',index=False)
    return rows

def cost_regions(g):
    breaks=[1.,25.]
    for i,j in itertools.combinations(range(len(g)),2):
        b1,b2=g.iloc[i].bad_per_day,g.iloc[j].bad_per_day
        if b1!=b2:
            x=(g.iloc[j].cost_intercept-g.iloc[i].cost_intercept)/(b1-b2)
            if 1<x<25:breaks.append(float(x))
    breaks=sorted(set(breaks));regions=[]
    for lo,hi in zip(breaks,breaks[1:]):
        k=(g.cost_intercept+(lo+hi)/2*g.bad_per_day).idxmin()
        if regions and regions[-1]['winner']==k:regions[-1]['ratio_high']=hi/.5
        else:regions.append(dict(ratio_low=lo/.5,ratio_high=hi/.5,winner=k))
    return regions

def economics(df):
    # Expected all-in-control false alarms is a transparent conservative exposure
    # approximation, NOT a measured false-alarm count. Sensitivities cover 0 and
    # all observed signals charged as false alarms.
    df['fa_per_day_model']=df.expected_FA_all_in_control/df.days
    df['cost_intercept']=2*df.subgroups_per_day+.5*df.units_per_day+50*df.fa_per_day_model+df.offspec_per_day
    df['cost_day']=df.cost_intercept+5*df.bad_per_day
    df['economic_plan'] = df.apply(lambda r: f'n{r.n:g}-h{r.h:g}-L{r.L:g}-' + ('S' if r.method=='Snapshot' else 'R'), axis=1)
    g=df.groupby('economic_plan').mean(numeric_only=True).sort_index().rename_axis('plan')
    ratios=np.linspace(2,50,481);cost=g.cost_intercept.to_numpy()[:,None]+g.bad_per_day.to_numpy()[:,None]*(.5*ratios)
    winners=cost.argmin(axis=0);names=g.index.to_numpy()
    mp=pd.DataFrame({'ratio_bad_to_unit':ratios,'c_bad':.5*ratios,'winner':names[winners],'cost_per_day':cost.min(axis=0)})
    mp.to_csv(OUT/'cost_map.csv',index=False)
    # Exact lower-envelope segments, including narrow regions grid might miss.
    regions=cost_regions(g)
    pd.DataFrame(regions).to_csv(OUT/'cost_regions_exact.csv',index=False)
    # Run-level resampling respects within-run daily dependence.
    boot=[]
    for plan in names:
        a=df[df.economic_plan==plan][['cost_intercept','bad_per_day']].to_numpy()
        boot.append(a[RNG.integers(len(a),size=(4000,len(a)))].mean(axis=1))
    boot=np.stack(boot);probs=[]
    for ratio in [2,5,10,20,30,40,50]:
        c=boot[:,:,0]+.5*ratio*boot[:,:,1];win=c.argmin(axis=0)
        for i,plan in enumerate(names):probs.append(dict(ratio=ratio,plan=plan,bootstrap_win_probability=np.mean(win==i)))
    pd.DataFrame(probs).to_csv(OUT/'bootstrap_winners.csv',index=False)
    sensitivity=[]
    for label,fa in [('zero_false_alarm_cost',np.zeros(len(df))),('all_signals_charged',df.signals/df.days),('all_in_control_model',df.fa_per_day_model)]:
        c=df.assign(intercept=2*df.subgroups_per_day+.5*df.units_per_day+50*fa+df.offspec_per_day).groupby('economic_plan')[['intercept','bad_per_day']].mean()
        for ratio in [2,10,50]:
            v=c.intercept+.5*ratio*c.bad_per_day
            sensitivity.append(dict(scenario=label,ratio=ratio,winner=v.idxmin(),cost=v.min()))
    pd.DataFrame(sensitivity).to_csv(OUT/'false_alarm_cost_sensitivity.csv',index=False)
    fig,(ax,bar)=plt.subplots(2,1,figsize=(9,5),gridspec_kw={'height_ratios':[4,1]})
    for i,plan in enumerate(names):ax.plot(ratios,cost[i],label=plan,lw=1,alpha=.65)
    ax.plot(ratios,cost.min(axis=0),color='black',lw=2.3,label='Lowest estimated cost')
    ax.set_ylabel('Estimated cost ($/working day)');ax.set_title('Economic design: point estimates, not a proven unique optimum')
    colors=plt.cm.tab20(np.linspace(0,1,len(names)))
    for r in regions:
        i=list(names).index(r['winner']);bar.axvspan(r['ratio_low'],r['ratio_high'],color=colors[i]);bar.text((r['ratio_low']+r['ratio_high'])/2,.5,(str(g.loc[r['winner'],'L'])+' SD\n'+('Random' if r['winner'].endswith('-R') else 'Snapshot')),ha='center',va='center',fontsize=7)
    bar.set(xlim=(2,50),ylim=(0,1),yticks=[],xlabel='Bad-part cost / inspection-unit cost (unit cost held at $0.50)')
    ax.legend(fontsize=6,ncol=4,loc='upper left');fig.tight_layout();savefig('cost_map')
    return g,regions

def empirical_plots(df):
    a=df[df.experiment.isin(['A80','A160'])]
    fig,ax=plt.subplots(figsize=(8,4.5))
    for n,d in a.groupby('n'):
        g=d.groupby('budget_target').agg(x=('units_per_day','mean'),y=('bad_per_day','mean'),s=('bad_per_day','std'),count=('run_id','count'))
        ci=stats.t.ppf(.975,g['count']-1)*g.s/np.sqrt(g['count'])
        ax.errorbar(g.x,g.y,yerr=ci,marker='o',capsize=4,label=f'n = {n}')
    ax.set(xlabel='Actual inspected units / working day',ylabel='Bad parts / working day',title='Allocation and effort: means with 95% run-level t intervals');ax.legend(ncol=5);fig.tight_layout();savefig('quality_effort')
    fig,axes=plt.subplots(1,2,figsize=(10,3.8))
    for ax,exp in zip(axes,['A80','A160']):
        d=a[a.experiment==exp];ax.scatter(d.n,d.bad_per_day,alpha=.7);ax.plot(d.groupby('n').bad_per_day.mean(),color='black');ax.set(title=exp+' allocation',xlabel='Subgroup size n',ylabel='Bad parts / day')
    fig.tight_layout();savefig('allocation')
    b=df[df.experiment=='B']
    if len(b):
        fig,ax=plt.subplots(1,2,figsize=(8,3.4));g=b.groupby('L').mean(numeric_only=True)
        ax[0].plot(g.index,g.signals,'o-');ax[0].plot(g.index,g.expected_FA_all_in_control,'s--',label='All-in-control expectation');ax[0].legend(fontsize=8)
        ax[1].plot(g.index,g.bad_per_day,'o-');ax[0].set(xlabel='Limit width L',ylabel='Signals per 15-day run');ax[1].set(xlabel='Limit width L',ylabel='Bad parts / day');fig.tight_layout();savefig('limit_width')

def renewal_sensitivity():
    candidates=[]
    for n in range(2,11):
        for budget in [40,80,120,160,200]:
            h=28800*n/budget
            for L in [2.5,3.,3.5]:candidates.append((n,budget,h,L))
    renewal=[]
    for delta,lam,excess,ratio in itertools.product([.5,1.,2.],[.1,.5,1.],[10,50,100],[2,10,50]):
        vals=[]
        for n,budget,h,L in candidates:
            hd=h/28800;D=(arl(n,L,delta)-.5)*hd;cycle=1/lam+D
            fa=(2*stats.norm.sf(L)/(lam*hd))/cycle
            C=2/hd+.5*budget+50*fa+(.5*ratio)*excess*D/cycle
            vals.append(C)
        j=int(np.argmin(vals));n,budget,h,L=candidates[j]
        renewal.append(dict(delta=delta,shifts_per_in_control_day=lam,excess_bad_per_out_of_control_day=excess,ratio=ratio,n=n,budget=budget,h=h,L=L,incremental_cost=vals[j]))
    pd.DataFrame(renewal).to_csv(OUT/'renewal_sensitivity.csv',index=False)

def theory(df,events):
    rows=[]
    for _,r in df.groupby('plan').mean(numeric_only=True).iterrows():
        for delta in [.25,.5,1.,1.5,2.,3.]:
            a=arl(r.n,r.L,delta)
            rows.append(dict(n=r.n,L=r.L,h_effective=r.effective_h_seconds,delta=delta,ARL1=a,delay_uniform_minutes=(a-.5)*r.effective_h_seconds/60,delay_after_sample_minutes=a*r.effective_h_seconds/60))
    pd.DataFrame(rows).to_csv(OUT/'arl_sensitivity.csv',index=False)
    fig,ax=plt.subplots(figsize=(8,4))
    delta=np.linspace(.2,3,120)
    for n in [2,4,5,8,10]:ax.plot(delta,(arl(n,3,delta)-.5)*(28800*n/160)/60,label=f'n = {n}')
    ax.set(yscale='log',xlabel='Persistent mean shift (individual standard deviations)',ylabel='Expected delay (working minutes)',title='ARL prediction at exactly 160 inspected units/day');ax.legend(ncol=5);fig.tight_layout();savefig('arl_theory')
    # Explicit reduced Duncan-style renewal model, not the full textbook model.
    # In-control duration Exp(lambda); instantaneous correction; uniform onset.
    # Cycle = 1/lambda + D; expected FA/cycle = alpha/(lambda*h).
    renewal_sensitivity()
    if len(events):
        e=events[events.classification=='sustained-shift evidence'].copy()
        if len(e):
            e=e.merge(df[['run_id','n','L']],on='run_id');e['ARL1_plugin']=arl(e.n,e.L,e.delta_hat.abs());e['theory_delay_minutes']=(e.ARL1_plugin-.5)*e.effective_h_seconds/60
            e.to_csv(OUT/'estimated_delay_theory_comparison.csv',index=False)
            fig,ax=plt.subplots(figsize=(8,4));ax.scatter(e.n,e.delay_lower_seconds/60,alpha=.65);ax.set(xlabel='Subgroup size n',ylabel='Estimated delay lower bound (working minutes)',title='Detected sustained episodes only; short shifts can be missed');fig.tight_layout();savefig('estimated_delays')

def original_audit():
    rows=[]
    for label,m0,s0,m1,s1 in [('total',804.2,22.345,811.8,26.296),('good',599.2,19.774,631.333,33.519),('bad',147.267,10.727,121.333,10.189),('offspec',57.733,8.948,59.133,6.610)]:
        v=s0*s0/15+s1*s1/15;df=v*v/((s0*s0/15)**2/14+(s1*s1/15)**2/14);d=m1-m0;ci=stats.t.ppf(.975,df)*np.sqrt(v)
        rows.append(dict(metric=label,lab6_mean=m0,lab7_mean=m1,difference=d,ci_low=d-ci,ci_high=d+ci,p=2*stats.t.sf(abs(d)/np.sqrt(v),df),df=df,source='reported summary statistics; independent-day assumption'))
    pd.DataFrame(rows).to_csv(OUT/'original_lab_welch.csv',index=False)

def main():
    baseline();rows=[];events=[];checks=[]
    for p in sorted((ROOT/'runs').glob('*/metadata.json')):
        meta=json.loads(p.read_text())
        if meta['experiment']=='stage0':continue
        row,ev,prod,quality,obs=parse_run(p.parent);rows.append(row);events.extend(ev)
        checks.append(dict(run_id=row['run_id'],production_days=len(prod),quality_rows=len(quality),chart_rows=len(obs),signal_difference=row['signal_count_difference'],timestamp_mismatch=row['unmatched_signal_timestamps']))
    if not rows:raise ValueError('No completed experiment runs')
    df=pd.DataFrame(rows);ev=pd.DataFrame(events)
    result_tests=tests(df);g,regions=economics(df)
    df.to_csv(OUT/'run_table.csv',index=False);g.to_csv(OUT/'plan_summary.csv');ev.to_csv(OUT/'signal_events.csv',index=False);pd.DataFrame(checks).to_csv(OUT/'validation.csv',index=False)
    empirical_plots(df);theory(df,ev);original_audit()
    summary=dict(runs=len(df),plans=df.plan.nunique(),best_base_cost=g.cost_day.idxmin(),cost_regions=regions,tests=result_tests,
                 signals=int(df.signals.sum()),sustained_shift_signals=int(df.sustained_shift_signals.sum()))
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,default=float));print(json.dumps(summary,indent=2,default=float))
    checksums={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'runs').glob('*/*.json'))}
    (OUT/'raw_sha256.json').write_text(json.dumps(checksums,indent=2))

if __name__=='__main__':main()
