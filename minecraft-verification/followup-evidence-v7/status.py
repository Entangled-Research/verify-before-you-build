import json,pathlib,collections
v=pathlib.Path(__file__).resolve().parents[1]
for run in sorted((v/'runs').glob('followup-v*-*')):
 file=run/'events.jsonl'
 if not file.exists():continue
 ev=[json.loads(s) for s in file.read_text().splitlines() if s.strip()]
 count=collections.Counter(x['event'] for x in ev)
 targets=[(x['id'],x['status']) for x in ev if x['event']=='receipt']
 d=next((x['items'] for x in reversed(ev) if x['event']=='delivery'),{})
 model=[x for x in ev if x['event']=='model']
 recent=next((x for x in reversed(ev) if x['event']=='tool_result'),{})
 print(run.name,ev[-1]['time'],ev[-1]['event'],'receipts',len(targets),targets[-2:],'chest',len(d),'turns',len(model),'tokens',sum(x['promptTokens']+x['generatedTokens'] for x in model),'cached',count['receipt_cache_hit'],'last_tool',recent.get('tool'))
