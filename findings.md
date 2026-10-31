# Findings and decision rationale

## 1. Allocation at approximately fixed inspection budgets

At the 160-unit target, mean bad parts/day ranged from 134.11 (n=5) to 139.62 (n=8). At the 80-unit target, they ranged from 134.91 (n=2) to 139.58 (n=4). These sample differences do not establish an allocation effect: ANOVA p=.1755 and .0532 respectively; Kruskal-Wallis p=.2038 and .0922. Tukey intervals and run-level data are provided. Failure to reject does not establish equivalence. Actual effort, not nominal m*n, is plotted and costed; the largest target deviation was 2.67%.

The quality-minimizing sample mean and the cost-minimizing plan need not coincide. A subgroup setup costs $2 in the assumed model. At roughly 80 units/day, n=8 uses about ten subgroups/day instead of about 41 for n=2. The setup-cost difference alone is about $62/day. With weak evidence of a quality response, that difference matters economically.

## 2. Inspection budget and the tradeoff curve

Doubling effort does not consistently reduce bad parts in the observed guest plant. For n=2,4,5,8, the high-minus-low differences are +1.76, -2.98, -4.11 and +3.62 bad parts/day; all four unadjusted Welch 95% intervals include zero. The evidence does not locate a flattening point or prove that lower inspection is safe at every possible budget. There are only two common budget levels; n=10 was tested only at the higher budget. A no-chart plan and budgets below 80 were not tested. The recommendation is restricted to tested candidates.

The two main figures are figures/quality_effort.png and figures/cost_map.png. Straight segments in the quality plot connect tested means; they are not fitted dose-response functions or evidence of monotonicity.

## 3. Limit width and sampling method

B tested n=8, requested wait=2592 seconds and snapshot sampling with L=2.5,3,3.5, five runs each. Mean bad parts/day are 134.41, 138.97 and 136.93 respectively. Omnibus ANOVA p=.0715; Kruskal-Wallis p=.1142. No Tukey pair crosses .05 (the closest adjusted p=.0594). One unadjusted Welch pair is below .05, but that does not override multiplicity or the exploratory design.

C compared five fresh random and five fresh snapshot runs at L=2.5. Snapshot minus random is +3.19 bad parts/day, 95% Welch interval [-0.27,6.64], p=.0663. The result does not establish a method effect. Random sampling actually inspected about 82.03 units/day; snapshot at these settings was near 80.4. Method and actual effort are therefore not perfectly isolated. Phase 1 confirms that random spreads individuals across the collection interval while snapshot takes consecutive units.

## 4. Economic recommendation and its uncertainty

Costs are assumptions: $2/subgroup, $.50/inspected unit, $50/false alarm, $5/bad unit, $1/off-spec unit. Bad and off-spec production counts are separate categories; defect records are not charged again. True false alarms are not observed, so the primary model uses all-in-control expectation alpha*observed subgroup exposure. Alternative false-alarm charging rules are shown separately.

The estimated base-cost winner is n=8, requested wait=2592 s, L=2.5, random: $795.65/day. Its actual median regular subgroup interval is about 2794 seconds (46.6 working minutes); the requested wait is not the completed-subgroup interval. The nearby n=8/L=3.5 snapshot plan costs $806.29/day. Their estimated cost difference is $10.64/day with a 95% Welch interval [-9.76,31.04]. The bootstrap assigns the random plan a winning frequency of .888 at ratio 10 and the 3.5 snapshot plan .0863. These are conditional resampling frequencies, not probabilities of a universal optimum. Baseline estimation and adaptive selection uncertainty are not fully represented.

The exact lower cost envelope switches at c_bad/c_unit=4.7330, with c_unit fixed at $.50: 3.5 snapshot wins below, 2.5 random above. Setting false-alarm cost to zero makes random the winner even at ratio 2; charging all observed signals preserves the 3.5 snapshot winner at ratio 2. At ratios 10 and 50, random wins under all three false-alarm scenarios. The low-cost threshold is thus sensitive to the false-alarm assumption.

Against the explicit n=5/h=960/L=3 snapshot reference, the base estimate is $68.01/day lower (7.9%), with an unadjusted Welch interval of $34.78 to $101.23/day. This is modeled simulator cost, not actual savings and not a verified comparison against the historical Lab 7 plan. The historical report never states a numerical interval. All cost comparisons are selected/exploratory, not prospective confirmatory estimates.

## 5. ARL and Duncan-style theory check

ARL0 equals approximately 80.52, 370.40 and 2149.34 for L=2.5,3,3.5. ARL1 depends on the individual-standard-deviation shift delta and n. The script evaluates delta=.25,.5,1,1.5,2,3 and plots the entire allocation tradeoff at 160 units/day. Expected working delay is h*(ARL1-.5) for a uniform onset within the sampling interval, and h*ARL1 for onset immediately after sampling. The original proposal's latter expression is a special timing convention, not the general continuous-onset average.

All 52 recorded signals match the observed outside points, but none have sufficient sustained pre-signal evidence under the prespecified screen. They cannot be counted as known false alarms or known true detections. An estimated delay distribution, a measured representative delta, and empirical ARL1 agreement are not identifiable. Signal counts are compared descriptively against the all-in-control reference in signal_reference.csv; that is not a validated false-alarm test.

The reduced renewal model explicitly assumes exponential time to a fixed persistent shift, instantaneous correction, and no search/repair downtime. It sweeps delta=.5,1,2, cause rate=.1,.5,1 per in-control day, excess bad output=10,50,100 per out-of-control day, and ratios=2,10,50. For each scenario it optimizes n=2..10, budgets=40,80,120,160,200 and L=2.5,3,3.5. Its incremental-loss objective uses the same sampling and false-alarm unit costs; baseline quality cost is common and omitted, and incremental off-spec loss is assumed zero. These explicit scenarios are not estimates of this simulator and do not constitute a fitted full Duncan optimum. Calibrating one would require true cause incidence, shift magnitude, state-specific losses and repair/search durations.

## Original lab correction

See original_lab_audit.md for the corrected paragraph and tests. The 150 Phase 1 appendix values reproduce the TEXT limits (0.051128 / 0.049783); the plotted Figure 1 uses different limits (0.051231 / 0.049869). The raw appendix therefore supports the text rather than the figure. The original online limit input remains unverifiable. Table 9 erroneously repeats bad-parts statistics as off-spec statistics.

## Scope and remaining information limits

The guest study is complete under the available access. It does not recreate the registered-account plant. No source data or empirical statistics were fabricated. Ground-truth onset/delay/FA analysis, a full fitted Duncan model, and an original-account recommendation remain unsupported by the accessible evidence; these cannot be resolved by additional arithmetic. A future registered rerun can use the same pipeline after a new baseline. Resume wording must preserve the guest-simulator and illustrative-cost qualifications.
