"""Portable entry point for the unchanged, audited simulation implementation.

Only filesystem/provenance handling differs from the historical entry point.
Smoke output is a software check, not a replacement for the 400-replicate study.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / 'analysis/workspace'
SIM_REL = Path('analysis/allocation_simulation')
CORE_REL = Path('paired_state_core/code/common.py')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numerical_validation(output):
    """Run the original validator in isolation so archived files are never changed."""
    with tempfile.TemporaryDirectory(prefix='paired_state_validation_') as tmp:
        root = Path(tmp)
        for rel in [CORE_REL, SIM_REL / 'run_audited.py', SIM_REL / 'validate_audited.py']:
            dest = root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / rel, dest)
        proc = subprocess.run([sys.executable, '-B', str(root / SIM_REL / 'validate_audited.py')],
                              cwd=root, capture_output=True, text=True, encoding='utf-8')
        (output / 'validation_stdout.txt').write_text(proc.stdout, encoding='utf-8')
        (output / 'validation_stderr.txt').write_text(proc.stderr, encoding='utf-8')
        if proc.returncode:
            raise RuntimeError('Numerical validation failed; inspect validation_stderr.txt')
        report = json.loads((root / SIM_REL / 'pre_run_validation.json').read_text(encoding='utf-8'))
        if report['status'] != 'passed' or not all(c['passed'] for c in report['checks']):
            raise RuntimeError('Validator did not pass every recorded check')
        (output / 'validation.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['validate', 'smoke', 'full'], default='smoke')
    parser.add_argument('--output', type=Path, help='New/empty output directory')
    parser.add_argument('--workers', type=int, default=1, help='Parallel batches for full run')
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('--workers must be positive')
    output = (args.output or REPO / 'outputs' / ('simulation_' + args.mode)).resolve()
    if output.exists() and any(output.iterdir()):
        parser.error('Output directory is not empty; use a new path to preserve prior results')
    output.mkdir(parents=True, exist_ok=True)
    before = {rel.as_posix(): sha(SOURCE / rel) for rel in
              [CORE_REL, SIM_REL / 'run_audited.py', SIM_REL / 'validate_audited.py']}
    report = numerical_validation(output)
    metadata = {
        'mode': args.mode, 'started_utc': datetime.now(timezone.utc).isoformat(),
        'python': platform.python_version(), 'source_sha256': before,
        'versions': {p: importlib.metadata.version(p) for p in
                     ['numpy', 'pandas', 'scipy', 'statsmodels', 'patsy']},
        'validation_checks_passed': len(report['checks']),
        'adaptation': 'Output/provenance handling only; historical manuscript-file hash dependency omitted',
        'registration_claim': 'None; this is a re-run of previously developed analysis code',
    }
    if args.mode != 'validate':
        sys.path.insert(0, str(SOURCE / SIM_REL))
        import run_audited as r
        import pandas as pd
        reps = r.REPS if args.mode == 'full' else 2
        sizes = r.SIZES if args.mode == 'full' else [500]
        truths = [r.scenario_truth(s) for s in r.SCENARIOS]
        (output / 'truth.json').write_text(json.dumps(truths, indent=2) + '\n', encoding='utf-8')
        jobs = [(si, n, start, min(start + 40, reps))
                for si in range(len(r.SCENARIOS)) for n in sizes for start in range(0, reps, 40)]
        rows = []
        if args.workers == 1:
            for i, job in enumerate(jobs):
                rows.extend(r.run_batch(*job))
                print(f'Completed batch {i + 1}/{len(jobs)}', flush=True)
        else:
            with ProcessPoolExecutor(max_workers=args.workers) as pool:
                futures = [pool.submit(r.run_batch, *job) for job in jobs]
                for i, future in enumerate(as_completed(futures)):
                    rows.extend(future.result())
                    print(f'Completed batch {i + 1}/{len(jobs)}', flush=True)
        df = pd.DataFrame(rows).sort_values(['scenario', 'n', 'replicate', 'method'])
        df.to_csv(output / 'replicate_results.csv', index=False)
        r.summarize(df).to_csv(output / 'summary.csv', index=False)
        df[df.status != 'ok'].groupby(['scenario', 'n', 'method', 'status']).size().rename(
            'count').reset_index().to_csv(output / 'failures.csv', index=False)
        metadata.update(seed=r.SEED, repetitions=reps, sizes=sizes,
                        generated_datasets=len(r.SCENARIOS) * len(sizes) * reps,
                        estimator_rows=len(df), successful_rows=int((df.status == 'ok').sum()),
                        statuses=df.status.value_counts().to_dict(),
                        max_identity_error=float(df.identity_error.max()),
                        inference_status='Full historical configuration' if args.mode == 'full'
                        else 'Smoke only: too few replicates for performance inference')
    metadata['source_unchanged'] = all(sha(SOURCE / k) == v for k, v in before.items())
    if not metadata['source_unchanged']:
        raise RuntimeError('Archived scientific source changed during validation')
    metadata['completed_utc'] = datetime.now(timezone.utc).isoformat()
    (output / 'run_manifest.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(metadata, indent=2))


if __name__ == '__main__':
    main()
