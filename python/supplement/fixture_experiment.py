"""Deterministic experiment fixture used for end-to-end reproduction."""
from __future__ import annotations

import json
import sys


SCORES = {
    0.3: 0.7273,
    0.5: 0.8,
    0.65: 0.8889,
    0.8: 0.8571,
    0.9: 0.6667,
}


threshold = float(sys.argv[1])
print(json.dumps({"metrics": {"val_f1": SCORES[threshold]}}))
