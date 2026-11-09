"""Run each requested scheduled episode once, stop on instrumentation problems."""
import argparse, json, subprocess, sys, urllib.request
from pathlib import Path
from runpy import run_path
here=Path(__file__).resolve().parents[1]
audit=run_path(str(Path(__file__).with_name('audit-run.py')))['audit']
p=argparse.ArgumentParser();p.add_argument('--prepared',required=True,type=Path);p.add_argument('--calibration',required=True,type=Path);p.add_argument('--port',required=True,type=int);p.add_argument('--phase',required=True,choices=['mixed-pilot','remaining']);a=p.parse_args()
prep=a.prepared.resolve();runs=here/'runs';protocol=json.loads((prep/'protocol.json').read_text());schedule=json.loads((prep/'schedule.json').read_text())
pilot=[row for row in schedule if row['seed']==701 and row['library']=='mixed']
rows=pilot if a.phase=='mixed-pilot' else [row for row in schedule if row not in pilot]
model='sweaterdog/andy-4:micro-q8_0'
def evidence(name):return runs/(prep.name+'-'+name)
def qualifies(run,calibration=False):
    report=audit(run)
    if report['defects'] or report['status'] not in (['calibration_passed'] if calibration else ['success','agent_finished','budget_exhausted']):raise SystemExit(f'Inspect {run}: {report}')
    manifest=json.loads((run/'manifest.json').read_text())
    if manifest['sourceHashes']!=protocol['sourceHashes'] or manifest['server']['port']!=a.port:raise SystemExit('Run freeze/port does not match calibration')
    return report
qualifies(a.calibration,True)
if a.phase=='remaining':
    for row in pilot:qualifies(evidence(row['episode']))
fingerprint=json.loads((here/'setup-evidence/local-runtime-20261108.json').read_text())
for row in rows:
    run=evidence(row['episode'])
    if run.exists():raise SystemExit(f'Refusing to replace existing {run}')
    with urllib.request.urlopen('http://127.0.0.1:11434/api/tags',timeout=5) as response:
        models=json.load(response)['models']
    if not any(m['name']==model and m['digest']==fingerprint['tag']['digest'] for m in models):raise SystemExit('Frozen model missing or changed')
    args=[str(here/'mc.sh'),'episode','--port',str(a.port),'--prepared',str(prep),'--auto-arm','--arm',row['arm'],'--model',model,'--library',str(prep/('library-'+row['library']+'.json')),'--seed',str(row['seed']),'--out',str(run)]
    print('START',row['episode'],flush=True);subprocess.run(args,check=True)
    summary=qualifies(run)
    print('AUDIT',json.dumps(summary),flush=True)
