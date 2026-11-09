"""Standalone verify-before-use gate used by the anonymous artifact."""
from __future__ import annotations

import json
import math
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID_STATUS = {"verified", "failed", "pending"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def record_receipt(
    ledger: Path,
    *,
    lab_id: str,
    paper_id: str,
    status: str,
    claimed: float | None = None,
    observed: float | None = None,
) -> None:
    if status not in VALID_STATUS:
        raise ValueError(f"invalid status: {status}")
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a") as stream:
        stream.write(json.dumps({
            "ts": _now(),
            "lab_id": lab_id,
            "paper_id": paper_id,
            "status": status,
            "claimed": claimed,
            "observed": observed,
        }) + "\n")


def latest_status(ledger: Path, *, lab_id: str, paper_id: str) -> str | None:
    if not ledger.exists():
        return None
    result = None
    for line in ledger.read_text().splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("lab_id") == lab_id and item.get("paper_id") == paper_id:
            result = item.get("status")
    return result


def dependency_violations(ledger: Path, proposal: dict[str, Any]) -> list[dict[str, Any]]:
    deps = proposal.get("foundational_external")
    if deps is None:
        return []
    if not isinstance(deps, list):
        return [{"reason": "foundational_external must be a list"}]

    reproduction = proposal.get("reproduction_of")
    reproduction_key = None
    if isinstance(reproduction, dict):
        lab = reproduction.get("lab_id")
        paper = reproduction.get("paper_id")
        if isinstance(lab, str) and isinstance(paper, str):
            reproduction_key = (lab, paper)

    violations = []
    for index, dep in enumerate(deps):
        if not isinstance(dep, dict):
            violations.append({"index": index, "reason": "dependency must be an object"})
            continue
        lab = dep.get("lab_id")
        paper = dep.get("paper_id")
        if not isinstance(lab, str) or not lab or not isinstance(paper, str) or not paper:
            violations.append({"index": index, "reason": "dependency identity is incomplete"})
            continue
        if reproduction_key == (lab, paper):
            continue
        status = latest_status(ledger, lab_id=lab, paper_id=paper)
        if status != "verified":
            violations.append({
                "index": index,
                "lab_id": lab,
                "paper_id": paper,
                "status": status,
                "reason": "latest reproduction is not verified",
            })
    return violations


def compare_metrics(
    claimed: dict[str, float],
    observed: dict[str, float],
    tolerance: float,
) -> tuple[str, list[dict[str, Any]]]:
    rows = []
    all_within = True
    for metric, expected in claimed.items():
        actual = observed.get(metric)
        within = False
        if actual is not None:
            values = (float(expected), float(actual), float(tolerance))
            if all(math.isfinite(value) for value in values) and tolerance >= 0:
                within = abs(actual - expected) <= tolerance * max(abs(expected), 1e-9)
        all_within = all_within and within
        rows.append({
            "metric": metric,
            "claimed": expected,
            "observed": actual,
            "within": within,
        })
    return ("corroborated" if all_within else "challenged"), rows


def run_threshold_recipe(fixture: Path) -> dict[str, float]:
    observed = {}
    with tempfile.TemporaryDirectory(prefix="paper-reproduction-") as directory:
        work = Path(directory)
        for index, threshold in enumerate((0.3, 0.5, 0.65, 0.8, 0.9)):
            process = subprocess.run(
                ["python3", str(fixture), str(threshold)],
                cwd=work,
                text=True,
                capture_output=True,
                timeout=30,
                check=True,
            )
            payload = json.loads(process.stdout)
            observed[f"run_{index:02d}"] = float(payload["metrics"]["val_f1"])
    return observed
