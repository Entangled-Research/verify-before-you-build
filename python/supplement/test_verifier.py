from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from evaluate import policy_cases
from verifier import compare_metrics


class VerifierTests(unittest.TestCase):
    def test_all_policy_cases(self):
        with tempfile.TemporaryDirectory() as directory:
            cases = policy_cases(Path(directory))
        self.assertEqual(len(cases), 13)
        self.assertTrue(all(case["passed"] for case in cases))

    def test_exact_and_altered_claims(self):
        observed = {"score": 0.8889}
        exact, _ = compare_metrics({"score": 0.8889}, observed, 0.05)
        altered, rows = compare_metrics({"score": 0.5}, observed, 0.05)
        self.assertEqual(exact, "corroborated")
        self.assertEqual(altered, "challenged")
        self.assertFalse(rows[0]["within"])


if __name__ == "__main__":
    unittest.main()
