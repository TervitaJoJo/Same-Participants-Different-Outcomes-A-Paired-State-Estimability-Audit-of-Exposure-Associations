# Verification record

The public aggregate reproduction was run on 10 October 2026 with Python 3.14.5, NumPy 2.4.6, pandas 3.0.3 and Matplotlib 3.10.9.

- Aggregate validation passed for 11 CSV files.
- The 26-sample table contained 8 point-estimate reversals, of which 6 had paired intervals excluding zero.
- CHARLS state totals reconciled to 10,367 participants; current and noncurrent subtotals reconciled to 3,309 and 7,058.
- `C_U + C_V = Delta_m` passed within `1e-12` for the primary CHARLS contrast.
- The very-sparse simulation check recovered 12 valid covering fits among 400 attempts, with 1.00 conditional coverage and 0.03 all-attempts success plus coverage.
- The renderer produced four main figures and six supplementary figures in PNG, TIFF and PDF.
- No participant-level files or direct identifier columns were found in the bundled derived inputs.

The generated figures and JSON reports are intentionally not committed to this code subpackage. Run `python scripts/reproduce.py` to create them locally in `outputs/`.
