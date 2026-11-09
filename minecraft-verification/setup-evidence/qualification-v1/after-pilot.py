"""Run the already frozen controls only after pilot terminal evidence reconciles."""
import json,pathlib,subprocess,sys,time
d=pathlib.Path(__file__).resolve().parent
v=d.parent.parent
e=d.parent/'mlx-qwen'
run=v/'runs/prepared-lan-v6-qwen-mixed-r1-enforced'
node=v.parent.parent/'minecraft-demo/.local/node22/bin/node'
deadline=time.time()+2400
targets=[run/'result.json',e/'post-terminal-enforced.json',e/'post-terminal-enforced-chest.json']
while not all(p.exists() for p in targets):
 if time.time()>deadline: sys.exit('Timed out waiting for post-arm observations; controls not launched.')
 time.sleep(2)
time.sleep(2)
for target,args in [
 ('enforced-audit.json',['python3',d.parent/'audit-run.py',run]),
 ('enforced-revisions.json',[node,d.parent/'revision-audit.cjs',run]),
 ('pilot-report.md',['python3',d.parent/'report-matched.py',v/'prepared-lan-v6-qwen',v/'runs','--pilot'])]:
 data=subprocess.check_output(args)
 (e/target).write_bytes(data)
result=json.loads(targets[0].read_text())
aud=json.loads((e/'enforced-audit.json').read_text())[0]
chest=json.loads(targets[2].read_text())
if aud['defects'] or aud['delivered']!=chest['delivered'] or result['status']!='budget_exhausted':
 sys.exit('Terminal evidence needs human review; controls not launched.')
print('Pilot audit and readbacks reconciled. Launching separately frozen scripted controls.',flush=True)
subprocess.run([node,d/'run.mjs',d/'result-01','61196'],check=True)
