import pathlib, subprocess, time, json, re
v=pathlib.Path(__file__).resolve().parents[1]
e=v/'followup-evidence-v7'
run=v/'runs/followup-v7.3-mixed-711-enforced-01'
while not (run/'result.json').exists():time.sleep(1)
for cmd,path in [
 (['python3',e/'audit.py',run],e/(run.name+'-audit.json')),
 (['python3',e/'audit-menu.py',run],e/'enforced-menu-audit.json')]:
 out=subprocess.check_output(cmd)
 path.write_bytes(out)
subprocess.run(['python3',e/'write-report.py'],check=True)
r=json.loads((run/'result.json').read_text())
assert r['complete'] and r['distinctTargets']==12 and r['unverifiedMethodStarts']==0
report=v/'FOLLOWUP-RESULTS.md'
for dest in re.findall(r'\]\(([^)]+)\)',report.read_text()):
 assert (v/dest).exists(),dest
readme=v/'README.md';s=readme.read_text()
tag='- [Developmental follow-up results]'
if tag not in s:readme.write_text(s.replace('## Evidence boundaries\n\n','## Evidence boundaries\n\n'+tag+'(FOLLOWUP-RESULTS.md): all four follow-up agent attempts, audited manufacturing deliveries, interface changes and separate calibration records.\n'))
print('Terminal result and independent menu/packet audits complete:',r['status'],r['distinctTargets'],r['modelTurns'],r['promptTokens'],r['generatedTokens'],r['wallSeconds'],flush=True)
