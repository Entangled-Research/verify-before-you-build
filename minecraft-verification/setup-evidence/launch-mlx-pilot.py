"""Sequential irreversible-evidence pilot: never overwrite or retry an arm."""
import argparse,json,subprocess,urllib.request
from pathlib import Path
from runpy import run_path
here=Path(__file__).resolve().parents[1];audit=run_path(str(here/'setup-evidence/audit-run.py'))['audit']
p=argparse.ArgumentParser();p.add_argument('prepared',type=Path);p.add_argument('--port',type=int,required=True);a=p.parse_args();prep=a.prepared.resolve();q=json.loads((prep/'qualification.json').read_text());protocol=json.loads((prep/'protocol.json').read_text());assert not q['prior_audit']['defects']
schedule=[r for r in json.loads((prep/'schedule.json').read_text()) if r['seed']==701 and r['library']=='mixed']
assert [r['arm'] for r in schedule]==['no_gate','prompt_only','enforced']
checkpoint=json.loads((here/'setup-evidence/mlx-qwen/provenance.json').read_text());assert protocol['planner']['revision']==checkpoint['revision']
for row in schedule:
    run=here/'runs'/(prep.name+'-'+row['episode']);assert not run.exists(),run
    models=json.load(urllib.request.urlopen('http://127.0.0.1:18601/v1/models',timeout=5));assert checkpoint['path'] in [m['id'] for m in models['data']]
    args=[str(here/'mc.sh'),'episode','--port',str(a.port),'--prepared',str(prep),'--auto-arm','--arm',row['arm'],'--model',checkpoint['model'],'--library',str(prep/('library-'+row['library']+'.json')),'--seed',str(row['seed']),'--out',str(run)]
    print('START',row['episode'],flush=True);subprocess.run(args,check=True)
    report=audit(run);print('AUDIT',json.dumps(report),flush=True)
    if report['defects'] or report['status'] not in ['success','agent_finished','budget_exhausted']:raise SystemExit('Stop for inspection; no automatic retry or arm replacement')
