"""Retain a terminal operator record only on three consecutive indistinguishable blocked calls."""
from pathlib import Path
import json,os,signal,subprocess,time,datetime
v=Path(__file__).resolve().parents[1];r=v/'runs/followup-v7.2-mixed-711-enforced-01'
def read_events():return [json.loads(s) for s in (r/'events.jsonl').read_text().splitlines()]
def write(name,obj):(r/name).write_text(json.dumps(obj,indent=2)+'\n')
while not (r/'result.json').exists():
 es=read_events()
 turns=[]; current=None
 for e in es:
  if e['event']=='planner_observation':current={'card':e['observation'],'time':e['time']}
  if e['event']=='dependency_blocked': current['blocked']=e['id']
  if e['event']=='tool_result':turns.append(current)
 last=turns[-3:]
 if len(last)==3 and all(x.get('blocked') and x.get('blocked')==last[0].get('blocked') and x['card']==last[0]['card'] for x in last):break
 time.sleep(1)
else:raise SystemExit(0)
processes=subprocess.check_output(['ps','-Ao','pid=,command='],text=True).splitlines()
pids=[int(line.strip().split()[0]) for line in processes if 'followup-v7.2/cli.mjs episode' in line and ('--out '+str(r)) in line]
if len(pids)!=1:raise RuntimeError('Expected one matching active child')
now=datetime.datetime.now(datetime.timezone.utc);os.kill(pids[0],signal.SIGTERM);time.sleep(.5)
es=read_events();models=[e for e in es if e['event']=='model'];chest=[e['items'] for e in es if e['event']=='delivery'][-1]
reason='Three consecutive missing-receipt blocks for '+last[0]['blocked']+' produced the identical displayed observation; the frozen card omitted blocked/reason.'
meta=dict(time=now.isoformat(),event='operator_interruption',reason=reason,identicalBlockedCards=last,usageComplete=False,lastRetainedEvent=es[-1]['event'],lastRetainedTimestamp=es[-1]['time'],provenance='external operator record after SIGTERM; possible in-flight model request')
write('interruption.json',meta)
m=json.loads((r/'manifest.json').read_text())
res=dict(kind='agent_episode',status='operator_interrupted_stalled',error=reason,complete=False,delivered=chest,distinctTargets=len(chest),arm=m['arm'],seed=m['seed'],model=m['model'],promptTokens=sum(x['promptTokens'] for x in models),generatedTokens=sum(x['generatedTokens'] for x in models),usageComplete=False,modelTurns=len(models),wallSeconds=(now-datetime.datetime.fromisoformat(es[0]['time'].replace('Z','+00:00'))).total_seconds(),primitiveActions=sum(x['event']=='action' for x in es),verificationAttempts=sum(x['event']=='verification_started' for x in es),testKits=[e['snapshot']['inventory'] for e in es if e['event']=='verification_kit'],unverifiedMethodStarts=sum(e['event']=='dependency_started' and e['status']!='verified' for e in es),blockedMethodStarts=sum(e['event']=='dependency_blocked' for e in es),repairs=sum(e['event']=='method_revised' for e in es),provenance='external terminal accounting from retained events after explicit operator interruption',endTime=now.isoformat())
write('result.json',res);print(reason)
