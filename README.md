# Anonymous supplementary code

This is an anonymised code archive for peer review. It contains the paired-state estimator, audited simulation, selected empirical analysis modules, an independent aggregate-result renderer, and static checks. It intentionally omits author metadata, publication-history scripts, local provenance manifests, raw or derived participant data, credentials, and machine-specific user names.

The analysis source was copied from the private working package and path/project identifiers were replaced with neutral tokens. Scientific Python syntax and non-string AST structure were checked after this transformation; scientific values and estimands were not changed. The archive is suitable for blinded review, but it is not a complete raw-data reproduction package.

## Run the data-free check

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python checks/check_bundle.py
python runners/run_simulation.py --mode smoke --output outputs/simulation_smoke
```

The smoke run executes the historical numerical validator in a temporary directory and runs two replicates per scenario at n=500. It is a software check, not an inferential rerun. The full configuration remains available through `--mode full --workers 4`, but full empirical analyses require licensed survey inputs that are not included here.

## Contents

- `analysis/workspace`: anonymised analysis source with neutral historical folder names.
- `analysis/hrs`: HRS application source.
- `runners/run_simulation.py`: portable simulation and validation entry point.
- `visualization/render_figures.py`: independent Matplotlib renderer for external aggregate tables.
- `checks/check_bundle.py`: static syntax, hash and payload check.
- `manifests/source_manifest.*`: review-package hashes only; original private paths are withheld.

HRS is an application to a separate survey, not represented here as a preregistered or independent held-out validation. The package contains no author, affiliation, ORCID, email, repository, OSF, or local-account metadata. Please do not add identifying information before blinded review.

No public software licence is asserted in this blinded archive.
