"""Copy the reviewed aggregate exports into a shareable package.

Use this script from the private author workspace after reviewing the source
directory. It copies named CSVs only and never recursively collects data files.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import pandas as pd


PACKAGE = Path(__file__).resolve().parents[1]
NAMES = [
    "charls_bridge", "charls_estimates", "charls_heatmap_counts", "charls_states",
    "cvai_contrasts", "cvai_or", "direction_reversal", "failures", "sample_flow",
    "simulation",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path,
                        help="Private directory containing the ten reviewed aggregate CSVs")
    parser.add_argument("--destination", type=Path, default=PACKAGE / "data" / "derived")
    parser.add_argument("--force", action="store_true",
                        help="Replace the destination files after explicit review")
    args = parser.parse_args()
    source = args.source.resolve()
    destination = args.destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    for name in NAMES:
        src = source / f"{name}.csv"
        dst = destination / src.name
        if not src.is_file():
            raise FileNotFoundError(src)
        if dst.exists() and not args.force:
            raise FileExistsError(f"{dst} exists; pass --force only after review")
        shutil.copyfile(src, dst)
    # The primary CHARLS bridge is current versus noncurrent. Correct the
    # historical label during export without changing any numeric result.
    bridge = destination / "charls_bridge.csv"
    frame = pd.read_csv(bridge)
    frame["estimand"] = frame["estimand"].str.replace(
        "current versus never", "current versus noncurrent", regex=False)
    frame.to_csv(bridge, index=False)
    print(f"Copied {len(NAMES)} reviewed aggregate CSVs to {destination}")
    print("HRS aggregate input is maintained separately as data/derived/hrs_application.csv.")


if __name__ == "__main__":
    main()
