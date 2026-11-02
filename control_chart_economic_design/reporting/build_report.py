"""Create the two-page brief from validated result tables."""
from pathlib import Path
import json
import pandas as pd
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
ROOT=Path(__file__).resolve().parents[2]

def build():
    summary=json.loads((ROOT/'results/summary.json').read_text())
    base=json.loads((ROOT/'results/baseline_diagnostics.json').read_text())
    runs=pd.read_csv(ROOT/'results/run_table.csv');g=pd.read_csv(ROOT/'results/plan_summary.csv').set_index('plan')
    best=summary['best_base_cost'];r=g.loc[best]
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyCompact',fontName='Helvetica',fontSize=9,leading=12,spaceAfter=5,textColor=colors.HexColor('#253347')))
    styles.add(ParagraphStyle(name='TitleCustom',fontName='Helvetica-Bold',fontSize=22,leading=25,spaceAfter=8,textColor=colors.HexColor('#17364d')))
    styles.add(ParagraphStyle(name='SubCustom',fontName='Helvetica-Bold',fontSize=11,leading=14,spaceBefore=7,spaceAfter=4,textColor=colors.HexColor('#087e8b')))
    body=[]
    def p(t):body.append(Paragraph(t,styles['BodyCompact']))
    def h(t):body.append(Paragraph(t,styles['SubCustom']))
    def pic(name,w=480,h=220):body.append(Image(str(ROOT/'figures'/name),width=w,height=h,kind='proportional'))
    body.append(Paragraph('How much sampling is worth paying for?',styles['TitleCustom']))
    access=', '.join(sorted(runs.access.unique()))
    p(f'<b>Economic design of an X-bar chart | Mouse Factory | {access} access</b><br/>{summary["runs"]} experimental runs x 15 working days; three pooled Phase 1 baselines. Registered login was unavailable; these results do not reproduce the original registered plant. Base-Snap Point Opening. Collection date: October 26, 2026.')
    h('Decision under stated costs')
    p(f'The lowest estimated base cost among tested plans is <b>n={r.n:g}, random sampling</b>: requested wait {r.h:g} seconds, L={r.L:g}, and {r.units_per_day:.1f} inspected units/day in the observed schedule. Estimated daily cost is <b>${r.cost_day:,.2f}</b>. The point-estimate choice switches from 3.5-sigma snapshot to 2.5-sigma random near a bad-part/inspection cost ratio of 4.73. At the base ratio of 10, random wins 88.8% of run-level bootstrap resamples; its $10.64/day lead over 3.5-sigma snapshot has a 95% Welch interval of -$9.76 to $31.04. Treat both as plausible choices.')
    pic('cost_map.png',480,240)
    p('Cost assumptions: $2/subgroup; $0.50/inspected unit; $50/false alarm; $5/bad unit at the base case; $1/off-spec unit. The map varies bad-part cost from $1 to $25, holding all other costs fixed. False-alarm cost uses the all-in-control expectation; zero-charge and all-signals-charged sensitivities are supplied.')
    h('Experiment and baseline')
    p(f'Allocation compares n=2,4,5,8,10 near 160 units/day and n=2,4,5,8 near 80. Sampling time is included when setting the requested wait; costs use actual recorded counts. Allocation has three runs/cell; width and method have five after a fixed precision extension. Identical physical plans are pooled for economics. Pooled baseline: mean {base["mu"]:.8f}, within-subgroup SD {base["sigma"]:.8f}; range estimate {base["range_sigma"]:.8f}. Limits are mean +/- L*SD/sqrt(n).')
    p('Allocation ANOVA p=.176 (high budget) and .053 (low budget); width p=.072; method p=.066. No omnibus comparison crosses .05. Doubling effort does not establish a consistent bad-part reduction; two budgets cannot locate a flattening point. The statistical unit is a 15-day run. All 55 runs passed horizon and signal checks.')
    body.append(PageBreak())
    body.append(Paragraph('Quality, detection, and what the evidence supports',styles['TitleCustom']))
    pic('quality_effort.png',480,220)
    h('Detection and theory')
    p(f'The experiment recorded {summary["signals"]} chart signals; {summary["sustained_shift_signals"]} had sustained pre-signal shift evidence under the documented screening rule. All 52 remain unclassified: empirical shift size and detection delay cannot be estimated defensibly. This does not prove that shifts never occurred. ARL1 = 1/[1-Phi(L-delta*sqrt(n))+Phi(-L-delta*sqrt(n))]. A uniformly placed shift gives expected delay h*(ARL1-0.5); a shift just after sampling gives h*ARL1. The renewal-model sensitivity is explicitly assumption-based because true cause rates, repair durations, and state-specific losses are unavailable.')
    h('Corrected historical Lab 7 result')
    p('Using the supplied reports, bad parts fell from 147.267 to 121.333/day: -25.934 (17.6%), Welch 95% CI [-33.76,-18.11], p=2.28e-7. Good parts increased by 32.133/day, CI [11.33,52.94], p=.00404. Total and off-spec means did not show clear changes. Target defect records fell 760 to 270 (64.5%). These tests assume independent days and use rounded reported summaries. Improvement is consistent with the simulator\'s built-in corrective action; it does not establish optimal sampling.')
    h('Limitations and interpretation')
    p('The simulator is a teaching model with corrective-only actions. Guest and registered plant profiles must not be pooled. Every new login produces distinct data, but hidden seeds prevent verification of independence. Actual subgroup intervals vary and timestamp labels have calendar/DST inconsistencies. Onset estimates can miss short shifts and are censored; empirical false alarms are not identifiable. Costs are assumptions. Shared baseline uncertainty and sequential selection are not fully included in the bootstrap. Fifteen-day runs and three-to-five replications per cell can leave close alternatives unresolved. No real-plant savings are claimed.')
    p('Historical audit: the visible Phase 1 chart limits differ from the Lab 7 text; its off-spec comparison table duplicates bad-parts statistics. The 150 appendix values reproduce the text limits, so the figure is inconsistent with those values; actual online inputs remain unverified.')
    p('<font size="7.5">Sources: user-supplied ISEN 350 Lab 6 and Lab 7 reports/instructions; UTRGV Mouse Factory course and simulator pages; NIST/SEMATECH, Cusum Average Run Length (Shewhart ARL calculation); Montgomery (1982), Journal of Quality Technology 14(1), 40-43, doi:10.1080/00224065.1982.11978782 (abstract). Full links and methods are in docs/METHODS.md.</font>')
    def footer(c,doc):
        c.setStrokeColor(colors.HexColor('#d8e1e8'));c.line(42,36,570,36);c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#65758b'));c.drawString(42,24,'Simulator evidence | Reproducible economic-design study');c.drawRightString(570,24,str(doc.page))
    doc=SimpleDocTemplate(str(ROOT/'project_brief.pdf'),pagesize=(612,792),rightMargin=54,leftMargin=54,topMargin=40,bottomMargin=46)
    doc.title='Economic design of an X-bar chart'
    doc.author='Shawn Lee | reproducible simulator study'
    doc.build(body,onFirstPage=footer,onLaterPages=footer)

if __name__=='__main__':build()

