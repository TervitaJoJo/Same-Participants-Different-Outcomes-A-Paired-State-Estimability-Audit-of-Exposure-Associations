"""Check source hashes, Python syntax and accidental non-code/credential inclusion.

This does not execute archived analysis or manuscript-production modules.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

REPO = Path(__file__).resolve().parents[1]
FORBIDDEN = {'.dta', '.sav', '.sas7bdat', '.xpt', '.pkl', '.pickle', '.parquet',
             '.feather', '.rds', '.rdata', '.gz', '.zip', '.png', '.tif', '.pdf', '.doc', '.docx'}
ALLOWED = {'.py', '.vbs', '.ps1', '.sh', '.r', '.do', '.md', '.txt', '.json', '.csv'}
SECRET = re.compile(r'(?:sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)')


def decode(raw):
    return raw.decode('utf-16') if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else raw.decode('utf-8-sig')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report', type=Path, help='Optional JSON report path')
    args = p.parse_args()
    rows = json.loads((REPO / 'manifests/source_manifest.json').read_text(encoding='utf-8'))
    problems = []; syntax = 0; inspected = 0
    for row in rows:
        src = REPO / row['packaged_path']
        if not src.is_file():
            problems.append({'file': row['packaged_path'], 'issue': 'missing source'})
        elif hashlib.sha256(src.read_bytes()).hexdigest() != row['source_sha256']:
            problems.append({'file': row['packaged_path'], 'issue': 'source hash differs'})
    for path in REPO.rglob('*'):
        if not path.is_file(): continue
        rel = path.relative_to(REPO)
        if any(x in rel.parts for x in ['.git', '.venv', 'venv', '__pycache__', 'outputs']): continue
        inspected += 1
        suffix = path.suffix.lower()
        if suffix in FORBIDDEN or (suffix not in ALLOWED and path.name not in ['.gitignore', '.gitattributes']):
            problems.append({'file': rel.as_posix(), 'issue': 'unexpected file type for code-only release'})
            continue
        if suffix == '.csv' and rel.as_posix() != 'manifests/source_manifest.csv':
            problems.append({'file': rel.as_posix(), 'issue': 'data-like CSV outside source manifest'})
        try:
            text = decode(path.read_bytes())
        except UnicodeDecodeError:
            problems.append({'file': rel.as_posix(), 'issue': 'unreadable source encoding'})
            continue
        if SECRET.search(text):
            problems.append({'file': rel.as_posix(), 'issue': 'potential credential pattern; inspect privately'})
        if suffix == '.py':
            try:
                ast.parse(text, filename=rel.as_posix())
                syntax += 1
            except SyntaxError as exc:
                problems.append({'file': rel.as_posix(), 'issue': f'Python syntax error at line {exc.lineno}'})
    summary = {'status': 'passed' if not problems else 'failed', 'preserved_source_files': len(rows),
               'python_files_parsed': syntax, 'files_inspected': inspected, 'issues': problems,
               'scope': 'Static source/data-type checks; credential pattern scan is not a general security guarantee'}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    if problems: sys.exit(1)


if __name__ == '__main__':
    main()
