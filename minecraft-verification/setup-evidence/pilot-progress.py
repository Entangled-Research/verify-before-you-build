import pathlib, json, collections, sys
for p in sorted(pathlib.Path('minecraft-verification/runs').glob('prepared-lan-v6-qwen-mixed-r1-*/events.jsonl')):
 events=[json.loads(l) for l in p.read_text().splitlines() if l.strip()]
 kinds=collections.Counter(e['event'] for e in events);model=[e for e in events if e['event']=='model'];receipt=[(e['id'],e['status']) for e in events if e['event']=='receipt'];dep=[(e['id'],e['status']) for e in events if e['event']=='dependency_started'];dl=[e['items'] for e in events if e['event']=='delivery']
 print(p.parent.name,events[0]['time'],events[-1]['time'],events[-1]['event'],{'turns':len(model),'tokens':sum(e['promptTokens']+e['generatedTokens'] for e in model),'actions':kinds['action'],'unverified':sum(s!='verified' for _,s in dep),'blocked':kinds['dependency_blocked'],'receipts':receipt,'delivered':dl[-1] if dl else {},'toolErrors':kinds['tool_error'],'invalid':kinds['invalid_model_action']})
 if model:print('last request:',model[-1]['response'][:330].strip())
