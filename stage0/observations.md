# Stage 0: observed simulator behavior

Checked through the public UTRGV SPC Lab Two interface on October 26, 2026.

| Check | Observed result | Consequence |
|---|---|---|
| Registered access | Neither supplied course-prefix form nor assignment-prefix form opened the registered main page; an intervening stale session produced a ViewExpiredException and was refreshed. | Guest-mode experiment; do not call this an expired-account diagnosis or a registered-plant reproduction. No credentials retained. |
| Guest access | Blank optional guest information was accepted; no personal information was sent. | All new experimental data are guest mode. |
| Inspection point | Base-Snap Point Opening is selectable in both phases. | Matches the characteristic in the original project, but not its registered defect prevalence. |
| Phase 1 versus Phase 2 | Phase 1 n=5/m=40 followed by Phase 2 n=2 was accepted. | New designs can use one common pooled baseline. |
| Phase 2 m field | No subgroup-count field exists in Phase 2. | Use observed subgroup counts to calculate actual effort. |
| Time field | n=2 with requested 360 s produced typical completed-subgroup gaps near 425 s. | Requested waiting/collection setting is not the effective interval; calibration uses collection time. |
| Day structure | Production spans roughly 08:00-17:00, with a lunch gap around noon; the Nov 2 records contain an additional apparent DST/calendar discontinuity. | Use 28,800 working seconds as a planning approximation. Exclude lunch/night gaps for regular-interval summaries. Preserve raw timestamp labels. |
| Baseline timestamp labels | Weekday and timezone labels do not consistently match the calendar dates. | Parse month/day/year and local clock, not the printed weekday. Do not infer exact wall-clock causality from labels. |
| Snapshot versus random | Snapshot baseline units are often ~36 s apart; the separate random baseline starts 08:02:59, 08:04:47, 08:06:35, 08:08:23, 08:10:11. | The methods differ in within-subgroup timing. Random spacing is not independent random selection of an instantaneous subgroup. |
| Exports | Production contains daily good/bad/offspec counts; quality contains defect and signal timestamps; chart table contains subgroup mean and both limits. | Capture complete visible tables in chunks; retain raw text and source row order. |
| Signals | Across 55 analyzed runs, all 52 exact signal labels match chart-limit exceedances by count and timestamp. | Observed signal rule is consistent with a simple outside-limit rule; additional hidden rules cannot be ruled out from source code. |
| Login replication | Distinct production+chart hashes for all 55 experimental runs. | Confirms different outputs; hidden random seeds mean independence is assumed, not proven. |

A first incomplete extraction and three 2,000-row-truncated quality captures were quarantined and excluded. The corrected collector waits for the final export control and reads all rows in 400-row chunks, verifying captured row count against the visible table count. These files are table transcriptions, not original Excel downloads.
