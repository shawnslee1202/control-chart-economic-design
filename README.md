# Economic design of an X-bar control chart

How often should a simulated factory inspect its parts, and how many should it measure at once?

Shawn Lee

![Estimated daily cost of each inspection plan as the cost of a bad part rises](figures/cost_map.png)

Both lowest-cost plans measured eight parts per group. The preferred plan changed when a bad part cost about 4.73 times as much as inspecting one part.

## What this is

The Mouse Factory simulates production and records parts that fail inspection. An X-bar chart tracks the average measurement of a group of parts and signals when that average falls outside preset limits. This study compared group sizes, sampling schedules and alert limits across 55 runs covering 825 simulated working days. Each plan was priced using the same assumptions for inspection, alarms and defective parts.

## Results at a glance

| Question | Finding | Detail |
|---|---|---|
| Which plan cost least? | Random sampling in groups of eight averaged 82 inspections per working day and cost an estimated $795.65 per working day. | [Cost comparison](docs/FINDINGS.md) |
| How much did it save? | The estimate was $68.01 per working day below the reference plan. | [Reference plan](docs/FINDINGS.md) |
| How certain was the choice? | Taking eight consecutive parts with wider alert limits cost $10.64 more per working day on average. The 95% confidence interval ranged from $9.76 less to $31.04 more per working day. | [Uncertainty](docs/FINDINGS.md) |
| Did more inspection improve quality? | Increasing the target from 80 to 160 inspected parts per working day produced no consistent drop in bad parts. | [Inspection effort](docs/FINDINGS.md) |
| How quickly were problems detected? | None of the 52 alarms had enough evidence before the signal to estimate when a change began. | [Detection limits](docs/FINDINGS.md) |

## Quick start

From a full clone, create a Python 3.12 environment.

```sh
python -m venv .venv
```

Activate with `source .venv/bin/activate` on macOS or Linux, or `.\.venv\Scripts\Activate.ps1` in PowerShell.

```sh
python -m pip install -r requirements-tested.txt
python -m unittest discover -s tests
```

## Reproduce

Run from the repository root. Allow a few minutes after installation. The raw observations come from the original public Git commit and require no simulator credentials.

```sh
git restore --source=a1e31c7828b81ecd1dc962218af8429ab3c2d87b --worktree -- runs/
python -m control_chart_economic_design.analysis.analyze
python -m control_chart_economic_design.analysis.supplement
python -m control_chart_economic_design.validation.verify_deliverables
python -m control_chart_economic_design.reporting.build_report
```

The first command restores the observations locally. For a check using only the published summary tables, run the verification command on its own.

## Repository map

| Location | Contents |
|---|---|
| [Python package](control_chart_economic_design/) | Collection, data parsing, analysis, validation and reporting code |
| [Tests](tests/) | Checks for timestamps, data completeness and chart calculations |
| [Results](results/) and [figures](figures/) | Summary tables and charts |
| [Notebook](analysis.ipynb) and [two-page report](project_brief.pdf) | Executed analysis and decision brief |
| [Documentation](docs/) | Study design, findings, collection notes and original lab audit |

## Limitations

- The guest simulator produced a different defect profile from the registered course plant. [Methods](docs/METHODS.md)
- Each plan had three to five runs per experimental cell, leaving uncertainty between close alternatives. [Findings](docs/FINDINGS.md)
- The simulator records alarms without identifying which were false, so the cost calculation estimates the false-alarm charge. [Methods](docs/METHODS.md)
- Inspection and defect costs are assumptions, and the comparison covers only the plans tested. [Findings](docs/FINDINGS.md)

## Sources and attribution

The observations came from the University of Texas Rio Grande Valley Mouse Factory teaching simulator. The [methods](docs/METHODS.md) cite the simulator, the NIST statistical handbook and Montgomery’s work on control-chart costs. The [original lab audit](docs/original_lab_audit.md) uses the author’s course reports. This repository specifies no reuse license.
