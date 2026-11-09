"""Start only the two prospectively scheduled episodes after strong live calibration."""
import json, pathlib, subprocess, time, sys, hashlib
v=pathlib.Path(__file__).resolve().parents[1]
node=v.parent.parent/'minecraft-demo/.local/node22/bin/node'
source=v/'followup-v7.1/cli.mjs'
prep=v/'prepared-followup-v7.1'
evidence=v/'followup-evidence-v7'
def read(path): return json.loads(path.read_text())
def audit(run):
 output=subprocess.run(['python3',evidence/'audit.py',run],capture_output=True,check=False)
 (evidence/(run.name+'-audit.json')).write_bytes(output.stdout)
 if output.returncode:sys.exit('Audit failed: '+run.name+' '+output.stderr.decode())
cal=v/'runs/followup-v7.1-calibration-02'
stop=time.monotonic()+3600
while not (cal/'result.json').exists():
 if time.monotonic()>stop:sys.exit('Calibration did not terminate')
 time.sleep(2)
audit(cal)
qualification={'kind':'separate deterministic live calibration','path':str(cal),'sourceHashes':read(cal/'manifest.json')['sourceHashes'],'status':read(cal/'result.json')['status'],'controls':read(cal/'development-controls.json'),'positive':read(cal/'calibration.json')}
if qualification['status']!='calibration_passed':sys.exit('Calibration did not pass')
(prep/'qualification.json').write_text(json.dumps(qualification,indent=2)+'\n')
for arm in ['prompt_only','enforced']:
 run=v/('runs/followup-v7.1-mixed-711-'+arm+'-01')
 time.sleep(4)
 cmd=[node,source,'episode','--prepared',prep,'--port','61196','--auto-arm','--arm',arm,'--library',prep/'library-mixed.json','--seed','711','--out',run]
 print('Starting',run.name,flush=True)
 with (evidence/(run.name+'-console.log')).open('x') as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
 audit(run)
 r=read(run/'result.json')
 if r['status']=='infrastructure_error':sys.exit('Infrastructure failure, inspect before next arm: '+str(r['error']))
 print('Completed',arm,r['status'],r['distinctTargets'],flush=True)
