# Paired-state estimability audit: reproducible public bundle

This subpackage contains the current analysis outputs and rendering code for the paired-state estimability audit. It is designed to run from a clean download without access to participant-level survey files.

The bundled CSVs are reviewed aggregate results: survey-wave estimates, CHARLS state counts and estimates, HRS application estimates, CVAI contrasts, and simulation summaries. They contain no participant identifiers and no row-level survey records. They support exact reconstruction of the manuscript figures and headline checks. The original CHARLS, HRS, CVAI and cross-survey analyses require the source releases and access conditions described in the manuscript; those restricted inputs are intentionally absent.

## Quick start

Python 3.11 or newer is recommended.

From this directory:

```bash
python -m pip install -r requirements.txt
python scripts/reproduce.py
```

The command writes `outputs/validation.json`, `outputs/run_manifest.json`, four main figures, and six supplementary figures. To render only the manuscript figures, use `python scripts/reproduce.py --main-only`.

The rendering code uses relative paths and never modifies files under `data/derived`. Each input table is checked for expected row counts, the 8/26 reversal result, the 6/8 supported reversals, CHARLS state totals, the allocation identity, CVAI definition consistency, and the 12/400 sparse-fit denominator result.

## Data boundary

This is a derived-data reproduction layer, not a substitute for a raw-data reanalysis. `scripts/export_derived_data.py` is an author-side helper for copying only the ten reviewed aggregate exports from a private workspace. It does not search recursively and does not copy `.dta`, `.sav`, `.pkl`, `.parquet`, compressed raw files or unidentified files.

The source CSVs preserve the values used for figure production. `data/derived/charls_bridge.csv` labels the primary CHARLS contrast as current versus noncurrent smoking; the separate current-versus-never sensitivity results remain identifiable in `charls_estimates.csv`.

## Layout

```text
paired_state_audit/
  data/derived/       aggregate CSVs only
  scripts/            validation, rendering and export entry points
  scripts/templates/  small independent Matplotlib drawing helpers
  docs/               data dictionary and reproducibility limits
  outputs/            generated figures and run reports
```

This directory was added to the existing project `code` folder. It is not a replacement for the historical source collection elsewhere under `code/analysis/statistical_modeling`.
