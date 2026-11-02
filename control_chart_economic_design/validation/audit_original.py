"""Recompute original Phase 1 limits from the user-supplied Lab 7 PDF.
Example: python -m control_chart_economic_design.validation.audit_original "path/to/ISEN 350 Lab 7 Report-1.pdf"
"""
from pathlib import Path
import argparse,re,json
import numpy as np
from pypdf import PdfReader
ap=argparse.ArgumentParser();ap.add_argument('pdf');args=ap.parse_args()
s='\n'.join(p.extract_text() or '' for p in PdfReader(args.pdf).pages)
s=s.split('APPENDIX A: Phase 1 Raw Subgroup Data')[-1]
rows=re.findall(r'([A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d\d:\d\d:\d\d C[DS]T 2026)\s+(0\.\d+)',s)
if len(rows)!=150:raise ValueError(f'Expected 150 appendix measurements; found {len(rows)}')
g=np.array([float(v) for _,v in rows]).reshape(30,5)
mu=g.mean();r=np.ptp(g,axis=1).mean();sigma=r/2.326
result=dict(n=5,m=30,mean=mu,Rbar=r,sigma_Rbar_d2=sigma,UCL=mu+3*sigma/np.sqrt(5),LCL=mu-3*sigma/np.sqrt(5))
out=Path(__file__).resolve().parents[2]/'results';out.mkdir(exist_ok=True)
(out/'original_phase1_recalculation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
