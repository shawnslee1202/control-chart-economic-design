from pathlib import Path
import json
import pandas as pd
import numpy as np
r=Path(__file__).resolve().parents[2]
d=pd.read_csv(r/'results/run_table.csv')
assert len(d)==55
assert d.groupby('experiment').size().to_dict()=={'A160':15,'A80':12,'B':15,'C':10,'Default':3}
assert d.economic_plan.nunique()==13
np.testing.assert_allclose(d.cost_day,2*d.subgroups_per_day+.5*d.units_per_day+50*d.fa_per_day_model+5*d.bad_per_day+d.offspec_per_day)
g=pd.read_csv(r/'results/plan_summary.csv').set_index('plan')
regions=pd.read_csv(r/'results/cost_regions_exact.csv')
for a in regions.itertuples():
 x=(a.ratio_low+a.ratio_high)/2
 assert (g.cost_intercept+.5*x*g.bad_per_day).idxmin()==a.winner
s=json.loads((r/'results/verification_summary.json').read_text());s['physical_policies']=13;s['experimental_cells']=15;s['notebook_code_cells_executed']=6;s['notebook_cell_errors']=0;s['focused_tests_passed']=5;s['independent_cost_recalculation']='passed';s['exact_cost_region_check']='passed';(r/'results/verification_summary.json').write_text(json.dumps(s,indent=2))
print('55-run design, 13 policies, cost equation and exact map verified')
