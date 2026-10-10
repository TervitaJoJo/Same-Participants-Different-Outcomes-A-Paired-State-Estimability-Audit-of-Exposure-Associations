# Aggregate data dictionary

All files in `data/derived` are aggregate tables. A row is a survey sample, outcome definition, observed joint state, simulation summary, or estimator summary; no row represents a person.

| File | Content | Primary use |
|---|---|---|
| `direction_reversal.csv` | 26 survey-wave OR pairs and paired intervals | Figure 1 and the 8/26 reversal check |
| `charls_bridge.csv` | CHARLS agreement, OR and paired-contrast bridge | Kappa-versus-association comparison |
| `charls_estimates.csv` | CHARLS standardized probabilities, log-ORs and allocations for two smoking contrasts | Figure 3 and allocation identity |
| `charls_states.csv` | CHARLS joint M/S state counts by smoking scope | Figure 3 and Supplementary Figure S5 |
| `charls_heatmap_counts.csv` | Four all-sample state cells with current/noncurrent subtotals | Figure 3 Panel A audit |
| `simulation.csv` | Simulation performance summaries by scenario, size, method and estimand | Figure 2 and Supplementary Figures S3-S4 |
| `failures.csv` | Attempted-fit failure counts | Figure 2 denominator audit |
| `hrs_application.csv` | HRS weighted paired contrast and two allocation components | Figure 4 Panel A |
| `cvai_or.csv` | Four adjusted CVAI odds ratios in a common CHARLS sample | Figure 4 Panel B |
| `cvai_contrasts.csv` | Paired CVAI definition contrasts and bootstrap intervals | Supplementary Figure S6 |
| `sample_flow.csv` | Aggregate inclusion counts for the 26 survey-wave samples | Supplementary Figure S2 |

The primary smoking contrast is current versus noncurrent. Current-versus-never results are retained as a separate sensitivity contrast in `charls_estimates.csv` and are not interchangeable with the primary rows.
