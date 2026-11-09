# Standalone Python verifier fixture

Run the policy cases, exact and altered claims, and ledger timing with the Python standard library.

    python3 evaluate.py
    python3 -m unittest -v test_verifier.py

The fixture emits five predetermined F1 values. It exercises command execution, metric comparison and gate decisions. The separate framework evaluator invokes a real logistic-regression training and scoring recipe. Its original archived outputs are in framework_evaluation_results.json and the sibling evaluation directory. Timings vary by host.
