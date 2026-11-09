"""Describe observed matched episodes, including missing slots, without replacing failures."""
import argparse, collections, json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('prepared',type=Path);p.add_argument('runs',type=Path);p.add_argument('--pilot',action='store_true');a=p.parse_args()
schedule=json.loads((a.prepared/'schedule.json').read_text());calibrations=[]
for f in sorted(a.runs.glob('calibration-*/result.json')):
    r=json.loads(f.read_text());calibrations.append((f.parent.name,r['status']))
print('Calibration records:')
for name,status in calibrations:print('- '+name+': '+status)
print()
print('| Library / seed | Arm | Status | Basket | Unverified starts | Blocked | Tests (passed/failed) | Revision requests | Actions (test/prod) | Model calls | Tokens (in/out) | Wall seconds |')
print('|---|---|---|---:|---:|---:|---|---:|---|---:|---|---:|')
details=[]
for row in schedule:
    if a.pilot and not (row['seed']==701 and row['library']=='mixed'):continue
    d=a.runs/(a.prepared.name+'-'+row['episode']);pre=f'| {row["library"]} / {row["seed"]} | {row["arm"]} | '
    if not (d/'result.json').is_file():
        print(pre+('running' if d.exists() else 'not run')+' | — | — | — | — | — | — | — | — | — |');continue
    r=json.loads((d/'result.json').read_text());events=[json.loads(l) for l in (d/'events.jsonl').read_text().splitlines()];act=collections.Counter(e['role'] for e in events if e['event']=='action');receipts=collections.Counter(e['status'] for e in events if e['event']=='receipt')
    print(pre+f"{r['status']} | {r['distinctTargets']}/12 | {r['unverifiedMethodStarts']} | {r['blockedMethodStarts']} | {r['verificationAttempts']} ({receipts['verified']}/{receipts['failed']}) | {r['repairs']} | {act['test']}/{act['production']} | {r['modelTurns']} | {r['promptTokens']:,}/{r['generatedTokens']:,} | {r['wallSeconds']:.1f} |")
    kits=collections.Counter()
    for kit in r['testKits']:kits.update(kit)
    fuel=collections.Counter(e['role'] for e in events if e['event']=='fuel_loaded')
    details.append((row['episode'],r['delivered'],dict(kits),dict(fuel),r.get('error')))
print()
for name,items,kits,fuel,error in details:
    print(f'- {name}: delivered {json.dumps(items,sort_keys=True)}; extra test materials allocated {json.dumps(kits,sort_keys=True)}; coal transferred {json.dumps(fuel,sort_keys=True)}.'+(f' Error: {error}.' if error else ''))
print('\nThese are exploratory episodes of one manufacturing task. Coal transferred is not a direct measure of fuel burned.')
