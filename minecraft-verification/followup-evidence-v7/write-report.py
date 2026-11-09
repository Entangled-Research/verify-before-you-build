import json, pathlib, collections, csv
v=pathlib.Path(__file__).resolve().parents[1]
base=v/'followup-evidence-v7'
load=lambda p:json.loads(p.read_text())
lines=['# Minecraft verification follow-up','',
'The developmental completion criterion is delivery of one of each of the twelve items into the fresh production chest within a single episode. The original pilot delivered 2/12 with prompt-only verification and 0/12 with enforced verification. All subsequent attempts are kept here. [Original pilot](PILOT-RESULTS.md) · [v7.1 prospective protocol](prepared-followup-v7.1/development-protocol.md)','']
rows=[]
def first_event_time(run):
 f=run/'events.jsonl'
 return json.loads(f.open().readline())['time'] if f.exists() else ''
for path in sorted((v/'runs').glob('followup-v*-*'),key=first_event_time):
 if not (path/'result.json').exists(): continue
 result=load(path/'result.json')
 events=[json.loads(x) for x in (path/'events.jsonl').read_text().splitlines()]
 if result['kind']=='calibration':
  lines.append(f"Live calibration **{result['status']}**. [Result](runs/{path.name}/result.json)")
  if result['status']=='calibration_failed':
   lines.append('The first v7 calibration passed eleven clean recipes. Its furnace precheck rejected sand because the generated map omitted the vanilla ingredient tag for glass. Version 7.1 expanded ingredient tags from the installed game jar before the second calibration.')
  continue
 cnt=collections.Counter(x['event'] for x in events)
 rec=collections.Counter(x['status'] for x in events if x['event']=='receipt')
 kits=collections.Counter()
 for k in result['testKits']:kits.update(k)
 verifiedStarts=sum(x['event']=='dependency_started' and x['status']=='verified' for x in events)
 row=dict(attempt=path.name,arm=result['arm'],seed=result['seed'],status=result['status'],distinctTargets=result['distinctTargets'],complete=result['complete'],chest=json.dumps(result['delivered'],sort_keys=True),turns=result['modelTurns'],promptTokens=result['promptTokens'],generatedTokens=result['generatedTokens'],usageComplete=result['usageComplete'],seconds=result['wallSeconds'],actions=result['primitiveActions'],realTests=result['verificationAttempts'],positive=rec['verified'],negative=rec['failed'],cached=cnt['receipt_cache_hit'],verifiedStarts=verifiedStarts,unverifiedStarts=result['unverifiedMethodStarts'],blocked=result['blockedMethodStarts'],revisionRequests=result['repairs'],recipeBookEdits=sum(x.get('authorship')=='model selected recipe-book insertion' for x in events),noOpRevisionRequests=sum(x['before']==x['after'] for x in events if x['event']=='method_revised'),changedRevisionRequests=sum(x['before']!=x['after'] for x in events if x['event']=='method_revised'),kits=json.dumps(kits,sort_keys=True))
 rows.append(row)
completed=[row for row in rows if row['complete']]
if completed:
 sentences=[r["arm"].replace("_","-")+" delivered 12/12 in "+str(r["turns"])+" model turns ("+str(round(r["seconds"]/60,1))+" minutes)" for r in completed]
 lines.insert(2,'. '.join(sentence[:1].upper()+sentence[1:] for sentence in sentences)+'. The table retains every development agent attempt, including explicit operator interruptions.\n')
if rows:
 with (base/'followup-results.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
lines+=['','| Attempt | Chest | Turns | Tokens in + out | Wall min | Actual tests (passed/failed) | Cached | Verified production starts | Unverified starts | Model-selected recipe-book edits |','| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
for row in rows:
 lines.append(f"| [{row['attempt']}](runs/{row['attempt']}/result.json) | {row['distinctTargets']}/12 | {row['turns']} | {row['promptTokens']:,} + {row['generatedTokens']:,} | {row['seconds']/60:.1f} | {row['realTests']} ({row['positive']}/{row['negative']}) | {row['cached']} | {row['verifiedStarts']} | {row['unverifiedStarts']} | {row['recipeBookEdits']} |")
lines+=['','For each completed arm, the independent audit reconciles the raw Qwen choice with its displayed menu, the tool actually executed, each receipt and the final server chest. ' + ' · '.join('['+r['arm']+' menu audit](followup-evidence-v7/'+r['arm']+'-menu-audit.json)' for r in completed), '', 'Version 7.2 enforced delivered one hopper minecart before three identical chest-minecart production requests were blocked. Its displayed cards omitted the actual denial reason. The operator stopped that attempt and retained its partial usage. Version 7.3 changed only the previous-action feedback. A replay of the denied chest card and passing chest receipt selected test then produce before the fresh enforced attempt started. The successful prompt-only mode used v7.2, while this final enforced attempt used v7.3. [v7.3 prospective protocol](prepared-followup-v7.3/development-protocol.md)\n\nVersion 7.1 prompt-only was stopped after seven identical dispenser rewrite requests and six reads of its cached failure, leaving three chest deliveries. Its retained token counts exclude a possible in-flight request. In v7.2, a menu exposes the effect of each explicit choice and an unchanged rewrite reports its unchanged receipt. Both v7.2 arms use this same menu. [v7.2 prospective protocol](prepared-followup-v7.2/development-protocol.md)\n\nThe queue focuses on the first undelivered product. Qwen selects each action from the current method, exact revision receipt, stock and delivery state. After a failed reproduction, the recipe book can suggest a single prerequisite step from the failure inventory and vanilla recipes. Qwen selects the edit, test and production calls. Enforced requires a passing receipt for the chosen revision before admitting its production use. Existing exact receipts can be read again without starting a new test. These changes are shared across the two verification arms.','',
'After enforced ended, an independent client reopened the production chest without moving any items and confirmed exactly one of every target. [Fresh post-terminal chest frame](followup-evidence-v7/enforced-post-terminal-chest.json)\n\nThe [CSV](followup-evidence-v7/followup-results.csv) includes individual attempts, token use, kit allocations, starts, revisions and accounting. The previous pilot used a different interface and seed. Version 7.2 includes prompt-only and enforced arms. Its lack of a same-version no-gate baseline limits comparison with the previous pilot to description. These runs measure the tool-assisted controller on this order and cannot establish a causal benefit from verification.']
(v/'FOLLOWUP-RESULTS.md').write_text('\n'.join(lines)+'\n')
