# Audit of the original Lab 6 and Lab 7 reports

This audit distinguishes reported historical results from newly collected simulator data. It does not rewrite or alter the submitted reports. The historical calculations below use rounded descriptive statistics in the reports, not reconstructed daily observations.

## Corrected Lab 7 summary

In the reported 15-day periods, mean bad parts fell from 147.267 to 121.333 per day, a decrease of 25.934 (17.6%), and mean good parts rose from 599.200 to 631.333 per day. Independent-samples Welch tests calculated from the reported sample sizes and standard deviations give a 95% confidence interval of -33.76 to -18.11 bad parts/day (p = 2.28e-7) and +11.33 to +52.94 good parts/day (p = .00404). Total production (+7.60/day, p = .401) and off-spec production (+1.40/day, p = .630) did not show clear changes in their means. Base-Snap Point Opening defect records fell from 760 to 270, a descriptive reduction of 64.5%. These results are consistent with the simulator's built-in corrective action after a chart signal; they establish neither an economically optimal sampling plan nor real-world causal effectiveness. The tests assume independent daily observations, an assumption that cannot be checked from summary statistics alone.

## Corrections supported by the supplied files

| Location | Finding | Correction |
|---|---|---|
| Lab 7 report, page 14, Figure 1 | Visible chart: UCL 0.051231, CL 0.050550, LCL 0.049869. Caption and text: UCL 0.051128, LCL 0.049783. | The two sets disagree. The report does not establish which set was actually entered online. New runs use recorded analytic limits from an independent pooled baseline. |
| Lab 7 report, page 39, Table 9 | Off-spec table duplicates the bad-parts means and standard deviations. | Off-spec: Lab 6 mean 57.733, SD 8.948; Lab 7 mean 59.133, SD 6.610, n = 15 each, as reported in the surrounding text and benchmark sections. |
| Lab 7 report, pages 35-40 | CI overlap/non-overlap is described as the hypothesis test. | Replace with direct tests and confidence intervals for differences. See results/original_lab_welch.csv. |
| Lab 7 report, confidence-interval calculations | Several mean intervals use 1.96 with estimated SD and only 15 days. | Use the t distribution for small-sample intervals; do not confuse confidence and prediction intervals. |
| Lab 7 report, pages 39-40 | Losing a significant run-chart pattern is described as proof that a trend was eliminated and the process became stable. | A non-significant result does not establish absence of a pattern. Establish stability using an explicit monitoring protocol and more data. |
| Lab 7 report, sampling description | Snapshot is described as all observations collected at a single instant. | The simulator's form defines snapshot as consecutive units. Collection takes time. |
| Lab 7 report, page 44 onward | Phase 1 appendix dates/weekday labels and chart dates are inconsistent; the narrative date also postdates the report cover date. | Preserve timestamps as supplied, do not silently infer accurate calendar chronology, and distinguish simulation dates from collection dates. |
| Lab 7 report, recommendations | Dimensional X-bar monitoring is suggested for defect categories such as Sink Spot and Burn Spot. | An X-bar chart needs an associated measurable variable; an attribute chart or process-variable study may be more appropriate. |

Multiplicity: the four historical Welch p-values are unadjusted. A Holm correction preserves the significant good- and bad-parts conclusions. Serial dependence and non-random assignment remain unresolved. Defect records are occurrences, not necessarily distinct units; the 64.5% record reduction must not be called a 64.5% reduction in all bad parts.

## Source ledger

- `ISEN 350 Lab 6 Report.pdf`, supplied by the user; 36 pages, dated April 7, 2026.
- `ISEN 350 Lab 7 Report-1.pdf`, supplied by the user; 47 pages, dated April 22, 2026. Figure 1 on page 14 was visually checked.
- `Lab_6_Mouse Factory I.pdf`, supplied instructions, pages 1-2: definitions of bad versus off-spec parts.
- `Lab_7_Mouse Factory II.pdf`, supplied instructions, pages 1-2: corrective-only response and 15-day run requirement.
- `Lab 7- Mouse Factory II slides.pdf`, supplied slides, pages 6-9: Phase 1 cap and sampling procedure. The slide login prefix differs from the assignment; use the user's confirmed identifier, not an inferred one.

Original PDFs are not redistributed in the project bundle. They remain at the user-supplied paths.

## Recalculation from the original raw appendix

All 150 Phase 1 individual measurements were recoverable from Lab 7 Appendix A (pages 44-47). Grouping adjacent rows into 30 subgroups of five gives mean = 0.0504554000 and average range = 0.0011653333. With d2 = 2.326, sigma = 0.0005010032; mean +/- 3*sigma/sqrt(5) gives UCL = 0.0511275663 and LCL = 0.0497832337. These round to the report's TEXT limits (0.051128 / 0.049783), not the visible Figure 1 limits. Thus the text is supported by the appended numbers; Figure 1 appears inconsistent with those data. Actual online inputs remain unverified without the original observation export. The earlier warning about inconsistency does not imply that the text limits were mathematically wrong.

The recalculation is saved in results/original_phase1_recalculation.json. It is separate from the fresh pooled baseline and is not used to set new experimental limits.
