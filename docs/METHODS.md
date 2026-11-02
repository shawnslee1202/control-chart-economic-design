# Analysis protocol and assumptions

## Evidence and units

A replication is one new simulator login followed by one 15-working-day plant run. Fifteen days within a run are not fifteen independent experimental replications. Raw data are complete visible HTML tables captured as JSON, rather than XLS downloads. Every table is captured in chunks, checked for equal row widths, and checked against all 15 production dates. SHA-256 hashes preserve provenance. Server seeds are unavailable: different output hashes verify distinct output, not mathematical independence.

Baseline: three Phase 1 runs, n=5, m=40; 600 individuals in 120 subgroups. Group adjacent displayed rows in sets of five without sorting the possibly inconsistent timestamps. Pool within-subgroup sums of squares / 480, then take the square root. Cross-check with average range / 2.326. This is pooled s, with its small finite-sample bias left explicit. Check QQ plots, Shapiro tests, and lag-1 correlation; failure to reject is not proof of normality or independence. Fixed limits are mu +/- L*sigma/sqrt(n); baseline parameter uncertainty is a shared source of uncertainty not represented by the run bootstrap.

## Corrected design

The original arithmetic is 27 allocation + 9 width + 6 method = 42 Phase 2 runs, not 45, plus three baseline runs. Add three reference-plan runs to obtain 45 Phase 2 runs and three baselines. Width and method experiments use fresh runs rather than reusing a selected winner's original observations as confirmation.

- A160: n = 2,4,5,8,10; three replications each.
- A80: n = 2,4,5,8; three replications each.
- Reference: n=5, requested wait=960 s, L=3, snapshot, three replications. The historical report does not document a numerical interval, so this is an explicit reference, not a verified exact recreation of Lab 7.
- B: select the allocation minimizing the stated base cost among A plans; L = 2.5,3,3.5, three fresh runs each.
- C: at the selected allocation and selected width, snapshot versus random, three fresh runs each.

The online form has no m field. Stage 0 shows that its requested time is not the realized time between completed subgroups. Target wait = n*(28800/budget - 36), based on approximately 36 seconds per collected unit. Actual effort comes from observed subgroup count*n/15. Report residual budget mismatch explicitly; do not call approximately matched effort exactly fixed. The 200-unit cap is a Phase 1 course constraint, not an independently verified Phase 2 hard limit. All proposed target budgets remain at or below 200. Do not infer a Phase 2 cap from the retrospective form.

Randomize A and reference order using seed 350. Record each actual capture timestamp and plan. Replication order is recorded, not inferred from run IDs. Allow time between blocks; do not run requests concurrently against the teaching server. Selection is exploratory. Additional replications should address uncertainty, not continue until p < .05. If one winner is unstable, report a set of plausible alternatives and expected regret rather than claiming a unique optimum.

## Signals and delays

Cross-check the exact Severity label with subgroup means outside their recorded limits and compare timestamps. Rounded subgroup values may create boundary discrepancies, which must be retained and reported. A signal is not automatically a true detection. Process shift times and ground-truth cause states are not exported.

For each outside point, examine up to 20 preceding subgroup means since the previous signal. Fit a shifted constant suffix of at least two PRE-signal means, excluding the triggering extreme. Accept sustained-shift evidence only if Gaussian SSE improvement, in standardized units, exceeds 2*log(window length)+6. Otherwise label the signal unclassified. This conservative screening is not a validated false-alarm classifier, can miss abrupt one-sample shifts, and must not identify unclassified signals as known false alarms. Report window-truncated episodes as left-censored. Estimate onset at the first shifted subgroup, with one-interval timing uncertainty. Delay bounds use the median regular within-day completion interval, excluding lunch/night gaps; they are approximate working-time bounds, not precise wall-clock onset times. The signal is excluded from shift-size fitting to reduce, not eliminate, selection bias. Sensitivity to window/threshold and unobserved shifts limits inference.

Theoretical alpha=2*Phi(-L); ARL0=1/alpha; ARL1=1/[1-Phi(L-delta*sqrt(n))+Phi(-L-delta*sqrt(n))]. A shift immediately after a sample gives delay h*ARL1; a uniformly positioned shift gives h*(ARL1-1/2). Do not compare an empirical median with the theoretical mean as though they were the same statistic. Plug-in theory on detected episodes is descriptive because of estimated onsets, conditioning on detection, censoring, parameter estimation, changing means and possible variance shifts.

## Inference

Primary outcome: bad parts/day averaged over each 15-day run. For each experiment, report one-way ANOVA, residual Shapiro and Brown-Forsythe/median-centered Levene diagnostics, and Kruskal-Wallis as a robustness analysis. Tukey intervals apply to the normal equal-variance ANOVA model. Pairwise Welch differences and 95% intervals are unadjusted descriptive sensitivity results, not multiplicity-controlled confirmations. With three runs/cell, diagnostics have little power. For a two-method experiment, use a direct Welch comparison as well. Days are never pooled as independent replicates.

## Costs and decision uncertainty

Daily cost = 2*actual subgroups + 0.50*actual inspected units + 50*FA + c_bad*bad units + 1*offspec units. Costs are illustrative USD assumptions, not plant accounting. Bad and off-spec are separate production categories according to the supplied instructions; do not add defect-record counts as additional bad units. Total units = good+bad+offspec.

Ground-truth FA is unavailable. Primary model uses actual subgroup exposure*alpha/15, the expectation if all exposure were in control. It generally overstates expected FA when time is spent out of control; estimated baseline parameters may also change actual alpha. Sensitivities charge no false alarms or charge every observed signal. The latter brackets classification cost for the observed signals, not future stochastic outcomes. Sampling costs accrue on every observed subgroup.

Sweep c_bad/c_unit from 2 to 50 while holding c_unit=.50, c_sub=2, c_fa=50 and c_off=1 fixed. Ratios alone do not determine an optimum when the other absolute costs change. Compute exact intersections of affine plan costs, not just grid winners. A single-color cost map is a valid finding. Bootstrap entire runs within plan (4000 draws; seed 3502026); bootstrap win frequencies are descriptive resampling frequencies, not Bayesian posterior probabilities. They omit baseline uncertainty and sequential-selection bias.

## Duncan-style comparison

Use a clearly labeled reduced renewal model with exponential in-control lifetime 1/lambda, a persistent fixed mean shift, instantaneous correction, and negligible search/repair downtime. D = h*(ARL1-.5); cycle duration = 1/lambda + D. Fraction out of control = D/cycle. Expected false alarms per cycle = alpha/(lambda*h). Sampling cost accrues continuously. Sweep shift size, shift arrival rate and excess bad production, and optimize n, budget and L over an explicit grid. These missing rates cannot be reliably inferred from unclassified chart signals. The sensitivity output is not a fitted full Duncan-model optimum and cannot validate the empirical winner under unknown dynamics. A complete textbook calibration additionally needs search/repair times, true cause incidence and out-of-control loss rates.

## References

1. UTRGV Mouse Factory course page: https://qualityengineering.utrgv.edu/ccli/AggieMouseFactory/
2. Simulator: https://qualityengineering.utrgv.edu/SPCLabTwo_2023
3. NIST/SEMATECH, ARL definition and Shewhart calculation: https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc3131.htm
4. Montgomery (1982), Economic Design of an X-bar Control Chart, Journal of Quality Technology 14(1), 40-43: https://doi.org/10.1080/00224065.1982.11978782 (abstract consulted, not full text).
5. User-supplied original reports and instructions: see original_lab_audit.md.


## Final execution amendments

Registered access could not be established with the supplied identifier or the assignment-documented prefix. After the user asked to continue and finish, the empirical study used guest access. Credentials are not stored. The guest results are not pooled with the historical registered plant.

The initial 45 Phase 2 runs were completed, followed by a fixed addition of two runs per B and C cell because initial width costs were close relative to variability. Final totals: A160 15, A80 12, reference 3, B 15, C 10 = 55 experimental runs; three pooled Phase 1 baselines; separate Stage 0/pilot captures. The added schedule was fixed before viewing its results. Exploratory sequential selection remains a limitation. B selected the A80/n8 allocation using base cost; C selected L=2.5 from the initial B sample. Later results do not retroactively change that selection.

Economic maps pool identical physical plans across stages using n, requested wait, L and method, while experiment-specific tests retain their original groups. Consequently, A80/n8/L3 snapshot has eight runs and n8/L2.5 snapshot has ten runs in the final pooled economic comparison. Method comparisons use only the five fresh runs per method in C. Results are conditional on this selection and do not exhaust the n/h/L design space.
