"""Validate the public aggregate inputs used by the paired-state audit.

The checks deliberately operate on aggregate outputs only. They do not read,
discover, or infer participant-level records.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


PACKAGE = Path(__file__).resolve().parents[1]
DATA = PACKAGE / "data" / "derived"
REQUIRED = [
    "charls_bridge", "charls_estimates", "charls_heatmap_counts", "charls_states",
    "cvai_contrasts", "cvai_or", "direction_reversal", "failures", "hrs_application",
    "sample_flow", "simulation",
]
FORBIDDEN_COLUMN = re.compile(
    r"^(?:id|pid|participant_id|person_id|subject_id|uuid|name|address|dob|birth_date)$",
    flags=re.IGNORECASE,
)


def read(name: str) -> pd.DataFrame:
    path = DATA / f"{name}.csv"
    if not path.is_file():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def check_no_direct_identifiers(frames: dict[str, pd.DataFrame]) -> None:
    for name, frame in frames.items():
        bad = [column for column in frame.columns if FORBIDDEN_COLUMN.match(column)]
        if bad:
            raise AssertionError(f"{name}: direct identifier columns found: {bad}")
        if len(frame) > 100000:
            raise AssertionError(f"{name}: unexpectedly large aggregate table")


def validate(frames: dict[str, pd.DataFrame]) -> dict:
    check_no_direct_identifiers(frames)
    reversal = frames["direction_reversal"]
    assert len(reversal) == 26
    assert reversal["point_estimate_reversal"].astype(bool).sum() == 8
    assert (reversal["point_estimate_reversal"].astype(bool)
            & reversal["ci_excludes_zero"].astype(bool)).sum() == 6
    reversed_rows = reversal[reversal["point_estimate_reversal"].astype(bool)]
    assert np.all(np.log(reversed_rows["or_measured"].to_numpy())
                  * np.log(reversed_rows["or_selfreport"].to_numpy()) < 0)

    states = frames["charls_states"]
    all_states = states[states.scope.eq("all_smoking_statuses")]
    assert all_states.n.sum() == 10367
    current = states[states.scope.eq("current")]
    assert current.n.sum() == 3309
    noncurrent = states[states.scope.isin(["never", "former"])].groupby("state").n.sum()
    assert noncurrent.sum() == 7058
    heatmap = frames["charls_heatmap_counts"]
    assert heatmap.total_n.tolist() == [5781, 1134, 1824, 1628]
    assert heatmap.current_n.tolist() == [1967, 265, 633, 444]
    assert heatmap.noncurrent_n.tolist() == [3814, 869, 1191, 1184]
    assert np.all(heatmap.current_n + heatmap.noncurrent_n == heatmap.total_n)

    charls = frames["charls_estimates"]
    primary = charls[charls.contrast.eq("current_vs_noncurrent")].set_index("metric")
    assert abs(float(primary.loc["unreported_component", "estimate"])
               + float(primary.loc["history_normal_component", "estimate"])
               - float(primary.loc["delta", "estimate"])) < 1e-12
    assert np.isclose(float(primary.loc["delta", "estimate"]), -0.3408339356011121)

    failures = frames["failures"]
    sparse = failures[(failures.scenario.eq("very_sparse"))
                      & failures.n.eq(500) & failures.method.eq("primary")].iloc[0]
    assert tuple(int(sparse[column]) for column in
                 ["valid", "zero_required_state_cell", "fit_or_check_failure",
                  "ill_conditioned_hessian"]) == (12, 385, 3, 0)
    simulation = frames["simulation"]
    sparse_sim = simulation[(simulation.scenario.eq("very_sparse"))
                            & simulation.n.eq(500) & simulation.method.eq("primary")]
    assert set(sparse_sim.estimand) == {"delta", "CU", "CV"}
    assert np.allclose(sparse_sim.coverage_conditional, 1.0)
    assert np.allclose(sparse_sim.coverage_all, 0.03)

    cvai = frames["cvai_or"]
    assert len(cvai[cvai.scope.eq("common_definitions_plausible")]) == 4
    assert set(cvai.outcome) == {"S", "M", "MT", "SMT"}
    assert np.allclose(cvai.point, cvai.OR_per10_or_binary)
    hrs = frames["hrs_application"]
    assert list(hrs.term) == ["delta_m", "C_U", "C_V"]
    assert np.allclose(hrs.estimate, [-0.039, 0.055, -0.094])

    hashes = {}
    for name in REQUIRED:
        path = DATA / f"{name}.csv"
        hashes[f"{name}.csv"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "status": "passed",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "aggregate_files": len(REQUIRED),
        "row_counts": {name: int(len(frame)) for name, frame in frames.items()},
        "headline_checks": {
            "direction_reversals": "8 of 26; 6 paired intervals exclude zero",
            "charls_state_total": 10367,
            "charls_allocation_identity": "C_U + C_V = delta_m within 1e-12",
            "very_sparse_denominator": "12 valid and covering fits of 400 attempts",
            "very_sparse_coverage": "1.00 conditional; 0.03 all-attempts",
        },
        "sha256": hashes,
        "participant_level_data_included": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=PACKAGE / "outputs" / "validation.json")
    args = parser.parse_args()
    frames = {name: read(name) for name in REQUIRED}
    report = validate(frames)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
