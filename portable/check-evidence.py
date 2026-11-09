"""Read-only, standard-library checks of the paper's seven archived episodes."""
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / 'minecraft-verification/runs'
expected = {
    'prepared-lan-v6-qwen-mixed-r1-no_gate': 2,
    'prepared-lan-v6-qwen-mixed-r1-prompt_only': 2,
    'prepared-lan-v6-qwen-mixed-r1-enforced': 0,
    'followup-v7.1-mixed-711-prompt_only-01': 3,
    'followup-v7.2-mixed-711-prompt_only-01': 12,
    'followup-v7.2-mixed-711-enforced-01': 1,
    'followup-v7.3-mixed-711-enforced-01': 12,
}
for name, count in expected.items():
    result = json.loads((RUNS / name / 'result.json').read_text())
    assert result['distinctTargets'] == count, name
    assert sum(n >= 1 for n in result['delivered'].values()) == count, name
    print(f'{name}: {count}/12 ({result["status"]})')
for arm in ['prompt_only', 'enforced']:
    version = 'v7.2' if arm == 'prompt_only' else 'v7.3'
    subprocess.run([sys.executable, str(ROOT / 'minecraft-verification/followup-evidence-v7/audit-menu.py'), str(RUNS / f'followup-{version}-mixed-711-{arm}-01')], check=True)
