# Analysis map

The parent `code/analysis/statistical_modeling` directory retains the original
analysis entry points and their historical dependencies. This subpackage adds the
current public-data assembly, final display renderer and privacy checks.

| Manuscript result | Existing analysis family in the parent code tree | Public input here |
|---|---|---|
| 26-sample direction scan | `reanalysis_20260916` and the programme-specific builders | `direction_reversal.csv`, `sample_flow.csv` |
| CHARLS kappa and paired contrast | CHARLS reconstruction plus the paired-state estimator | `charls_bridge.csv`, `charls_estimates.csv` |
| 12/400 denominator result | `analysis/allocation_simulation_20260920` | `simulation.csv`, `failures.csv` |
| CHARLS four-state support | `mechanism_followup_20260917` and state-support audit | `charls_states.csv`, `charls_heatmap_counts.csv` |
| HRS external application | `hrs` / HRS external-application entry points | `hrs_application.csv` |
| CVAI reconstruction | `analysis/published_paper_replication_20260920` | `cvai_or.csv`, `cvai_contrasts.csv` |

The public `scripts/reproduce.py` reads only the aggregate files in `data/derived`.
The parent raw-data entry points remain available for authorized reanalysis after
licensed data and private source artifacts have been supplied.
