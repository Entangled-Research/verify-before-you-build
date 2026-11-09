"""Reconcile the offered options, raw model decisions, executed tools and chest."""
from pathlib import Path
import argparse,json,collections
parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);a=parser.parse_args();run=a.run
ev=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()]
result=json.loads((run/'result.json').read_text())
manifest=json.loads((run/'manifest.json').read_text())
errors=[];resolved=[];choices=collections.Counter();last_chest={};card=None;pending=None;started=collections.Counter()
def check(condition,note):
 if not condition:errors.append(note)
for e in ev:
 tag=e['event']
 if tag=='delivery':
  check(e['snapshot']['source']=='server:window_items','unconfirmed delivery');last_chest=e['items']
 elif tag=='planner_observation':
  check(pending is None,'previous model action unresolved')
  card=e
  expected=next((id for id in manifest['protocol']['targets'] if last_chest.get(id,0)<1),None)
  check(card['observation']['orderTarget']==expected,'focus differs from live chest');pending=None
 elif tag=='model':
  check(card['turn']==e['turn'],'model has wrong observation turn')
  pending=json.loads(e['response'])
 elif tag=='menu_selected':
  check(pending and pending.get('tool')=='choose' and pending['choice']==e['choice'],'menu choice differs from raw response')
  option=next((entry for entry in card['menuMapping'] if entry['choice']==e['choice']),None)
  check(option and option['action']==e['resolvedAction'],'selected action absent/different in offer')
  pending=e['resolvedAction'];choices[e['choice']]+=1
 elif tag=='dependency_started':
  check(pending=={'tool':'use_method','id':e['id']},'production use without corresponding planner decision')
  started[e['status']]+=1
 elif tag=='verification_started':
  check(pending=={'tool':'verify_method','id':e['id']},'test without corresponding planner decision')
 elif tag=='method_revised':
  check(pending and pending.get('tool') in ('revise_method','insert_step') and pending['id']==e['after']['id'],'revision without corresponding decision')
 elif tag=='tool_result':
  check(pending==e['tool'],'tool returned differs from selected action')
  resolved.append(e['tool']);pending=None
check(pending is None,'unfinished model action')
check(last_chest==result['delivered'],'terminal chest mismatch')
check(len(resolved)==result['modelTurns'],'unresolved or unaccounted model turn')
print(json.dumps(dict(run=run.name,resolvedModelTurns=len(resolved),menuChoices=choices,productionStartsByReceipt=started,terminalChest=last_chest,errors=errors),indent=2))
raise SystemExit(bool(errors))
