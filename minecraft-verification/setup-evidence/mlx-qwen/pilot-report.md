Calibration records:
- calibration-20261108-lan-v2-01: infrastructure_error
- calibration-20261108-lan-v3-01: calibration_failed
- calibration-20261108-lan-v5-01: calibration_passed

| Library / seed | Arm | Status | Basket | Unverified starts | Blocked | Tests (passed/failed) | Revision requests | Actions (test/prod) | Model calls | Tokens (in/out) | Wall seconds |
|---|---|---|---:|---:|---:|---|---:|---|---:|---|---:|
| mixed / 701 | no_gate | budget_exhausted | 2/12 | 61 | 0 | 0 (0/0) | 9 | 0/121 | 70 | 162,945/2,656 | 2343.6 |
| mixed / 701 | prompt_only | budget_exhausted | 2/12 | 29 | 0 | 1 (0/1) | 40 | 4/98 | 70 | 195,735/6,739 | 3231.5 |
| mixed / 701 | enforced | budget_exhausted | 0/12 | 0 | 45 | 11 (11/0) | 0 | 66/0 | 56 | 199,793/1,356 | 3161.7 |

- mixed-r1-no_gate: delivered {"chest_minecart": 1, "hopper_minecart": 1}; extra test materials allocated {}; coal transferred {"production": 13}.
- mixed-r1-prompt_only: delivered {"chest_minecart": 1, "hopper_minecart": 1}; extra test materials allocated {"coal": 1, "oak_log": 2, "raw_iron": 2, "string": 2}; coal transferred {"production": 22, "test": 1}.
- mixed-r1-enforced: delivered {}; extra test materials allocated {"coal": 22, "oak_log": 22, "raw_iron": 110}; coal transferred {"test": 22}.

These are exploratory episodes of one manufacturing task. Coal transferred is not a direct measure of fuel burned.
