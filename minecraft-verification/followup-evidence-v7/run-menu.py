"""Launch the two fresh v7.2 menu episodes serially and audit every terminal."""
import pathlib,subprocess,json,time
v=pathlib.Path(__file__).resolve().parents[1];e=v/'followup-evidence-v7';prep=v/'prepared-followup-v7.2'
node=v.parent.parent/'minecraft-demo/.local/node22/bin/node'
for arm in ['prompt_only','enforced']:
 run=v/('runs/followup-v7.2-mixed-711-'+arm+'-01')
 if run.exists():raise RuntimeError('Run already exists: '+str(run))
 if arm=='prompt_only':
  for _ in range(90):
   p=e/'menu-preflight.json'
   if p.exists() and len(json.loads(p.read_text()))==3:break
   time.sleep(1)
  rows=json.loads(p.read_text())
  if len(rows)!=3 or not all(row['match'] for row in rows):raise RuntimeError('Menu preflight failed, inspect first.')
 print('Starting',run.name,flush=True)
 with (e/(run.name+'-console.log')).open('x') as out:
  subprocess.run([node,v/'followup-v7.2/cli.mjs','episode','--prepared',prep,'--port','61196','--auto-arm','--arm',arm,'--library',prep/'library-mixed.json','--seed','711','--out',run],stdout=out,stderr=subprocess.STDOUT,check=True)
 with (e/(run.name+'-audit.json')).open('x') as out:subprocess.run(['python3',e/'audit.py',run],stdout=out,check=True)
 result=json.loads((run/'result.json').read_text())
 print(arm,result['status'],result['distinctTargets'],flush=True)
 if result['status']=='infrastructure_error':raise RuntimeError(result['error'])
 time.sleep(4)
