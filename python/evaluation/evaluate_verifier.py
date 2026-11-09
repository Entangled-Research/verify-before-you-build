"""Reproduce the verify-before-use evaluation reported in the paper."""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import tempfile
import time
from types import SimpleNamespace
from pathlib import Path

from efferents.agents.federation import (
    foundational_dependency_violations,
    record_reproduction,
)


TARGET = {"lab_id": "source-lab", "campaign_id": "paper-1", "why": "premise"}


def _proposal(*deps, reproduction_of=None):
    value = {"name": "downstream", "foundational_external": list(deps)}
    if reproduction_of is not None:
        value["reproduction_of"] = reproduction_of
    return value


def _allowed(paper_dir: Path, proposal: dict) -> bool:
    return foundational_dependency_violations(paper_dir, proposal) == []


def scenario_evaluation(root: Path) -> list[dict]:
    scenarios: list[tuple[str, bool, object]] = []

    def add(name: str, expected: bool, setup):
        scenarios.append((name, expected, setup))

    add("no external dependency", True, lambda p: _proposal())
    add("missing reproduction", False, lambda p: _proposal(TARGET))

    def status_case(status: str):
        def setup(paper: Path):
            record_reproduction(
                paper,
                lab_id="source-lab",
                campaign_id="paper-1",
                status=status,
            )
            return _proposal(TARGET)
        return setup

    add("pending reproduction", False, status_case("pending"))
    add("failed reproduction", False, status_case("failed"))
    add("verified reproduction", True, status_case("verified"))

    def verified_then_failed(paper: Path):
        for status in ("verified", "failed"):
            record_reproduction(
                paper, lab_id="source-lab", campaign_id="paper-1", status=status
            )
        return _proposal(TARGET)

    def failed_then_verified(paper: Path):
        for status in ("failed", "verified"):
            record_reproduction(
                paper, lab_id="source-lab", campaign_id="paper-1", status=status
            )
        return _proposal(TARGET)

    add("later failure revokes verification", False, verified_then_failed)
    add("later verification clears failure", True, failed_then_verified)

    second = {"lab_id": "source-lab", "campaign_id": "paper-2", "why": "premise"}

    def two_verified(paper: Path):
        for campaign in ("paper-1", "paper-2"):
            record_reproduction(
                paper, lab_id="source-lab", campaign_id=campaign, status="verified"
            )
        return _proposal(TARGET, second)

    def one_of_two_verified(paper: Path):
        record_reproduction(
            paper, lab_id="source-lab", campaign_id="paper-1", status="verified"
        )
        return _proposal(TARGET, second)

    add("all of two dependencies verified", True, two_verified)
    add("one of two dependencies unverified", False, one_of_two_verified)
    add(
        "reproduction may test its target",
        True,
        lambda p: _proposal(
            TARGET,
            reproduction_of={"lab_id": "source-lab", "campaign_id": "paper-1"},
        ),
    )
    add(
        "reproduction cannot waive another dependency",
        False,
        lambda p: _proposal(
            TARGET,
            second,
            reproduction_of={"lab_id": "source-lab", "campaign_id": "paper-1"},
        ),
    )
    add(
        "malformed dependency container",
        False,
        lambda p: {"foundational_external": "source-lab/paper-1"},
    )
    add(
        "malformed dependency object",
        False,
        lambda p: {"foundational_external": [{"lab_id": "source-lab"}]},
    )

    results = []
    for index, (name, expected, setup) in enumerate(scenarios):
        paper = root / f"scenario-{index}" / "paper"
        proposal = setup(paper)
        actual = _allowed(paper, proposal)
        results.append({
            "scenario": name,
            "expected_allowed": expected,
            "actual_allowed": actual,
            "passed": actual == expected,
        })
    return results


def latency_evaluation(root: Path, *, repetitions: int) -> list[dict]:
    results = []
    for ledger_entries in (1, 10, 100, 1000):
        paper = root / f"latency-{ledger_entries}" / "paper"
        record_reproduction(
            paper,
            lab_id="source-lab",
            campaign_id="paper-1",
            status="verified",
        )
        for i in range(ledger_entries - 1):
            record_reproduction(
                paper,
                lab_id=f"unrelated-{i % 7}",
                campaign_id=f"paper-{i + 2}",
                status=("verified" if i % 2 else "failed"),
            )
        proposal = _proposal(TARGET)
        samples_ms = []
        for _ in range(repetitions):
            started = time.perf_counter_ns()
            allowed = _allowed(paper, proposal)
            elapsed = time.perf_counter_ns() - started
            if not allowed:
                raise AssertionError("verified target was blocked during timing")
            samples_ms.append(elapsed / 1_000_000)
        ordered = sorted(samples_ms)
        p95_index = min(len(ordered) - 1, int(0.95 * len(ordered)))
        results.append({
            "ledger_entries": ledger_entries,
            "repetitions": repetitions,
            "median_ms": round(statistics.median(samples_ms), 4),
            "p95_ms": round(ordered[p95_index], 4),
            "max_ms": round(max(samples_ms), 4),
        })
    return results


def end_to_end_reproduction(root: Path) -> list[dict]:
    """Run the venue verifier against one exact and one altered claim."""
    from examples.challengescape.venue import venue

    venue.SUBMISSIONS = root / "venue" / "submissions"
    venue.PROCEEDINGS = root / "venue" / "proceedings"
    venue.REPRODUCTIONS = root / "venue" / "reproductions"
    venue.LEDGER = root / "venue" / "ledger.jsonl"
    for path in (venue.SUBMISSIONS, venue.PROCEEDINGS, venue.REPRODUCTIONS):
        path.mkdir(parents=True, exist_ok=True)

    expected = {
        "run_00": 0.7273,
        "run_01": 0.8,
        "run_02": 0.8889,
        "run_03": 0.8571,
        "run_04": 0.6667,
    }
    cases = [
        ("sub-001-exact", expected, "corroborated"),
        ("sub-002-altered", {**expected, "run_02": 0.5}, "challenged"),
    ]
    results = []
    for sub_id, claims, expected_verdict in cases:
        sub_dir = venue.SUBMISSIONS / sub_id
        sub_dir.mkdir(parents=True)
        status = {
            "submission_id": sub_id,
            "lab_id": "source-lab",
            "title": "Deterministic threshold study",
            "novelty_claim": "evaluation fixture",
            "state": "accepted",
            "round": 1,
            "below_gain_gate": False,
            "decisions": [],
            "post_publication": {"state": "none", "reproductions": []},
        }
        (sub_dir / "status.json").write_text(json.dumps(status, indent=2) + "\n")
        expected_yaml = "\n".join(f"    {key}: {value}" for key, value in claims.items())
        manuscript = (
            "# Reproduction fixture\n\n"
            "```yaml\n"
            "lab_dir: examples/repo-adapter\n"
            "metric: val_f1\n"
            "tolerance: 0.05\n"
            "expected:\n"
            f"{expected_yaml}\n"
            "```\n"
        )
        (sub_dir / "manuscript_v1.md").write_text(manuscript)
        started = time.perf_counter()
        venue.cmd_reproduce(SimpleNamespace(sub_id=sub_id, by="consumer-lab"))
        elapsed = time.perf_counter() - started
        updated = json.loads((sub_dir / "status.json").read_text())
        verdict = updated["post_publication"]["reproductions"][-1]["verdict"]
        report_path = venue.REPRODUCTIONS / f"{sub_id}_by_consumer-lab.md"
        report = report_path.read_text()
        results.append({
            "case": sub_id,
            "expected_verdict": expected_verdict,
            "actual_verdict": verdict,
            "passed": verdict == expected_verdict,
            "metric_rows": report.count("within margin") + report.count("OUT OF MARGIN"),
            "out_of_margin_rows": report.count("OUT OF MARGIN"),
            "elapsed_s": round(elapsed, 4),
        })
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    parser.add_argument("--repetitions", type=int, default=1000)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="verify-before-use-") as directory:
        root = Path(directory)
        scenarios = scenario_evaluation(root)
        latency = latency_evaluation(root, repetitions=args.repetitions)
        reproductions = end_to_end_reproduction(root)

    result = {
        "system": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "scenario_summary": {
            "passed": sum(row["passed"] for row in scenarios),
            "total": len(scenarios),
        },
        "scenarios": scenarios,
        "latency": latency,
        "end_to_end_reproductions": reproductions,
    }
    rendered = json.dumps(result, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
