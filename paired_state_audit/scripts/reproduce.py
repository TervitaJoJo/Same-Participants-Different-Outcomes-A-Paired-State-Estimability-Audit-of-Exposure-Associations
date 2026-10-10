"""Reproduce the public, aggregate-data part of the paired-state audit.

This entry point validates the privacy-reviewed aggregate CSVs, renders the
four main figures and six supplementary figures, and records the environment.
It does not claim to rerun analyses that require restricted participant data.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
SCRIPTS = PACKAGE / "scripts"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=PACKAGE / "outputs",
                        help="Output directory for figures and validation reports")
    parser.add_argument("--main-only", action="store_true",
                        help="Render only the four manuscript figures")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = output / "validation.json"
    subprocess.run([sys.executable, str(SCRIPTS / "validate_derived_data.py"),
                    "--report", str(report)], check=True)
    command = [sys.executable, str(SCRIPTS / "render_figures.py"), "--output", str(output)]
    if args.main_only:
        command.append("--main-only")
    subprocess.run(command, check=True)
    versions = {}
    for package in ("numpy", "pandas", "matplotlib"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = "unavailable"
    manifest = {
        "status": "passed",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": versions,
        "input_scope": "aggregate derived CSVs only",
        "participant_level_data_included": False,
        "raw_data_reanalysis": False,
        "figures": "main figures 1-4 and supplementary figures S1-S6"
        if not args.main_only else "main figures 1-4",
    }
    (output / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
