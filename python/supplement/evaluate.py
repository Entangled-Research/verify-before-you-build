"""Run the anonymous verifier evaluation with no external dependencies."""
from __future__ import annotations

import json
import statistics
import tempfile
import time
from pathlib import Path

from verifier import (
    compare_metrics,
    dependency_violations,
    record_receipt,
    run_threshold_recipe,
)


HERE = Path(__file__).resolve().parent
TARGET = {"lab_id": "source-lab", "paper_id": "paper-1"}


def allowed(ledger: Path, proposal: dict) -> bool:
    return not dependency_violations(ledger, proposal)


def policy_cases(root: Path) -> list[dict]:
    cases = []

    def check(name: str, expected: bool, ledger: Path, proposal: dict):
        actual = allowed(ledger, proposal)
        cases.append({"case": name, "expected": expected, "actual": actual, "passed": expected == actual})

    check("no dependency", True, root / "a.jsonl", {})
    check("missing", False, root / "b.jsonl", {"foundational_external": [TARGET]})

    for status, expected in (("pending", False), ("failed", False), ("verified", True)):
        ledger = root / f"{status}.jsonl"
        record_receipt(ledger, lab_id="source-lab", paper_id="paper-1", status=status)
        check(status, expected, ledger, {"foundational_external": [TARGET]})

    ledger = root / "revoked.jsonl"
    for status in ("verified", "failed"):
        record_receipt(ledger, lab_id="source-lab", paper_id="paper-1", status=status)
    check("revoked", False, ledger, {"foundational_external": [TARGET]})

    ledger = root / "cleared.jsonl"
    for status in ("failed", "verified"):
        record_receipt(ledger, lab_id="source-lab", paper_id="paper-1", status=status)
    check("cleared", True, ledger, {"foundational_external": [TARGET]})

    second = {"lab_id": "source-lab", "paper_id": "paper-2"}
    ledger = root / "two.jsonl"
    for paper in ("paper-1", "paper-2"):
        record_receipt(ledger, lab_id="source-lab", paper_id=paper, status="verified")
    check("two verified", True, ledger, {"foundational_external": [TARGET, second]})

    ledger = root / "one.jsonl"
    record_receipt(ledger, lab_id="source-lab", paper_id="paper-1", status="verified")
    check("one of two", False, ledger, {"foundational_external": [TARGET, second]})

    reproduction = {"lab_id": "source-lab", "paper_id": "paper-1"}
    check("target exception", True, root / "target.jsonl", {
        "foundational_external": [TARGET], "reproduction_of": reproduction,
    })
    check("exception is narrow", False, root / "narrow.jsonl", {
        "foundational_external": [TARGET, second], "reproduction_of": reproduction,
    })
    check("malformed list", False, root / "malformed-a.jsonl", {
        "foundational_external": "source-lab/paper-1",
    })
    check("malformed object", False, root / "malformed-b.jsonl", {
        "foundational_external": [{"lab_id": "source-lab"}],
    })
    return cases


def latency(root: Path) -> list[dict]:
    results = []
    for size in (1, 10, 100, 1000):
        ledger = root / f"latency-{size}.jsonl"
        for index in range(size - 1):
            record_receipt(
                ledger,
                lab_id=f"other-{index % 7}",
                paper_id=f"paper-{index + 2}",
                status="failed",
            )
        record_receipt(ledger, lab_id="source-lab", paper_id="paper-1", status="verified")
        proposal = {"foundational_external": [TARGET]}
        samples = []
        for _ in range(1000):
            started = time.perf_counter_ns()
            if not allowed(ledger, proposal):
                raise AssertionError("verified proposal was blocked")
            samples.append((time.perf_counter_ns() - started) / 1_000_000)
        ordered = sorted(samples)
        results.append({
            "entries": size,
            "median_ms": round(statistics.median(samples), 4),
            "p95_ms": round(ordered[950], 4),
        })
    return results


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="verify-before-use-") as directory:
        root = Path(directory)
        policy = policy_cases(root)
        timing = latency(root)
        observed = run_threshold_recipe(HERE / "fixture_experiment.py")

    exact = {
        "run_00": 0.7273,
        "run_01": 0.8,
        "run_02": 0.8889,
        "run_03": 0.8571,
        "run_04": 0.6667,
    }
    exact_verdict, exact_rows = compare_metrics(exact, observed, 0.05)
    altered_verdict, altered_rows = compare_metrics({**exact, "run_02": 0.5}, observed, 0.05)
    result = {
        "policy": {
            "passed": sum(case["passed"] for case in policy),
            "total": len(policy),
            "cases": policy,
        },
        "reproductions": [
            {"name": "exact", "verdict": exact_verdict, "rows": exact_rows},
            {"name": "altered", "verdict": altered_verdict, "rows": altered_rows},
        ],
        "latency": timing,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
