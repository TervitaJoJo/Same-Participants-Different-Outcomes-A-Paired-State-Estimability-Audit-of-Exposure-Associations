# Reproducibility scope

Running `scripts/reproduce.py` performs a deterministic aggregate-data reproduction:

1. Validate the reviewed CSV schemas, privacy boundary and headline identities.
2. Render Figures 1-4 and Supplementary Figures S1-S6 from those CSVs.
3. Write software-version and input-hash records to `outputs/`.

The script does not rerun participant-level regression, survey-weighted fitting, bootstrap resampling or the full 10,800-dataset simulation. Those analyses require restricted survey releases and private preparation metadata. The historical raw-data entry points remain in the parent project code collection and should only be run in a separate private workspace with the relevant data-use permissions.

The aggregate files are sufficient to reproduce the manuscript's reported display values and the following checks: 8 of 26 direction reversals, 6 supported reversals, CHARLS n=10,367 state totals, `C_U + C_V = Delta_m`, and 12 successful covering fits among 400 very-sparse attempts.
