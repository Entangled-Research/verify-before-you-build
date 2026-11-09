"""Write the one-seed pilot handoff from retained results, only after scripted controls are terminal."""
from pathlib import Path
import json,csv,collections
v=Path(__file__).resolve().parent.parent
def load(path):return json.loads((v/path).read_text())
prefix='runs/prepared-lan-v6-qwen-mixed-r1-'
arms=['no_gate','prompt_only','enforced']
results=[load(prefix+a+'/result.json') for a in arms]
audpath='setup-evidence/mlx-qwen/'
audits=[load(audpath+a.replace('_','-')+'-audit.json')[0] for a in arms]
revs=[load(audpath+a.replace('_','-')+'-revisions.json') for a in arms]
qualpath='setup-evidence/qualification-v1/result-01/result.json'
qual=load(qualpath)
csvpath=v/audpath/'pilot-comparison.csv'
rows=[]
for r,a,rev in zip(results,arms,revs):
 ev=[json.loads(x) for x in (v/(prefix+a)/'events.jsonl').read_text().splitlines()]
 ac=collections.Counter(x['role'] for x in ev if x['event']=='action')
 kits=collections.Counter()
 for k in r['testKits']: kits.update(k)
 total=r['promptTokens']+r['generatedTokens']
 rows.append(dict(arm=a,library='mixed',seed=701,status=r['status'],basketComplete=r['complete'],distinctTargets=r['distinctTargets'],delivered=json.dumps(r['delivered'],sort_keys=True),modelTurns=r['modelTurns'],promptTokens=r['promptTokens'],generatedTokens=r['generatedTokens'],tokensOverThreshold=max(0,total-200000),usageComplete=r['usageComplete'],wallSeconds=r['wallSeconds'],testPrimitiveAttempts=ac['test'],productionPrimitiveAttempts=ac['production'],tests=r['verificationAttempts'],testKitAllocations=json.dumps(dict(kits),sort_keys=True),unverifiedStarts=r['unverifiedMethodStarts'],blockedStarts=r['blockedMethodStarts'],revisionRequests=rev['requests'],changedRevisions=rev['distinctChanges'],unchangedRevisionRequests=rev['noopRequests'],targetProducingChangedRevisions=rev['changedRevisionsProducingTarget']))
with csvpath.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
lines=['# Minecraft verification pilot: mixed library, seed 701','',
'All three agents left the same twelve-item order incomplete. Enforcing verification prevented unverified production starts but did not improve completion on this order and seed. One local Qwen model ran independently under each rule. The outcomes below use the server delivery chest. Real verifier reproductions, calibration deliveries and scripted tests earn no delivery credit for the agent.','',
'| Arm | Delivered / 12 | Model turns | Prompt + output tokens | Time (min) | Primitive attempts | Test attempts | Unverified starts | Blocked starts |',
'| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |']
for r,a in zip(results,arms):
 lines.append(f"| [{a}]({prefix+a}/result.json) | {r['distinctTargets']} | {r['modelTurns']} | {r['promptTokens']:,} + {r['generatedTokens']:,} | {r['wallSeconds']/60:.1f} | {r['primitiveActions']} | {r['verificationAttempts']} | {r['unverifiedMethodStarts']} | {r['blockedMethodStarts']} |")
lines+=['',
'Each arm started with fresh production stock, isolated verifier kits, a fresh conversation and an empty receipt table. The no-gate and prompt-only arms delivered one hopper minecart and one chest minecart each. Both exhausted the 70-turn limit; the prompt-only arm also crossed the 200,000-token start-of-turn check on its final request by 2,474 tokens. Enforced exceeded that threshold by 1,149 tokens. Token totals include all reported prompt and generated units; they do not estimate compute. Wall time includes setup. The two permissive arms each left one raw iron in an unlit production furnace, as established by separate post-terminal server reads. The fixed toolset cannot clear and recover that furnace, which can amplify a planning mistake after resources run short.','',
'| Arm | Revision requests | Changed method identity | No change | New versions yielding their intended target |',
'| --- | ---: | ---: | ---: | ---: |']
for a,rev in zip(arms,revs):
 lines.append(f"| [{a}]({audpath+a.replace('_','-')}-revisions.json) | {rev['requests']} | {rev['distinctChanges']} | {rev['noopRequests']} | {rev['changedRevisionsProducingTarget']} |")
lines+=['','No-gate allocated no verifier kits and attempted the supplied faulty crossbow and dispenser in production. Prompt-only allocated two logs, two raw iron, one coal and two string for its only isolated test; the supplied faulty crossbow procedure failed. It also started 18 crossbow and 9 dispenser procedures in production across their supplied and revised versions. Its revisions yielded no repaired target. In the enforced arm, the first attempt to reuse the hopper procedure without a receipt was blocked. The agent obtained a valid receipt for it, then repeatedly requested other unverified production methods. All 11 passing tests were repeats of that one method. Of 45 blocked requests, one was the initial hopper request and 44 were for the correct, untested chest minecart. None detected a defective procedure. There were zero production starts and no receipt bypass. The post-terminal production furnace and delivery chest were both empty. This arm exhausted the token budget on its 56th request; it did not hit the wall limit. Its 11 verifier kits allocated 110 raw iron, 22 logs and 22 coal in addition to its untouched production stock.','',
'**Scripted controls, outside the agent episodes.** The [prospective specification](setup-evidence/qualification-v1/spec.json) was frozen before the controls began. The [control result]('+qualpath+') has status **'+qual['status']+'**, '+str(sum(bool(x['ok']) for x in qual['assertions']))+'/'+str(len(qual['assertions']))+' assertions true, '+str(qual['verificationAttempts'])+' test attempts and zero model calls. Assertions and server observations are retained individually.','']
for row in qual['assertions']:
 lines.append('- '+('PASS' if row['ok'] else 'FAIL')+': '+row['name'])
if qual.get('error'):lines.append('Control error: '+qual['error'])
lines+=['','**Interpretation.** These are descriptive outcomes for one fixed order, mixed hand-authored library and seed. A valid test does not ensure the planner will use its receipt. Do not treat repeated tests of one procedure as independent replications, a correct untested method being blocked as a detected fault, or a scripted delivery as agent success. Primitive attempts include separate test materials and time. Neither this pilot nor its controls establish a general improvement in completion, compute cost or throughput.',
'','The [frozen amendment](prepared-lan-v6-qwen/amendment-before-gameplay.md) records why the Qwen interface was used despite imperfect tool selection. [Calibration and rejected interface diagnostics](setup-evidence/LAN-RESULTS.md) are distinct from the matched comparisons. The [detailed pilot report]('+audpath+'pilot-report.md) includes individual test kits, resources, accounting and receipt evidence. See the [operator guide](OPERATOR.md) for reproduction. The [comparison CSV](setup-evidence/mlx-qwen/pilot-comparison.csv) contains one row per agent arm; independent packet/token audits are [no-gate](setup-evidence/mlx-qwen/no-gate-audit.json), [prompt-only](setup-evidence/mlx-qwen/prompt-only-audit.json) and [enforced](setup-evidence/mlx-qwen/enforced-audit.json). Further seeds and the clean-library matrix were not run; review the recovery tools and how results are exposed to the planner before expanding.']
(v/'PILOT-RESULTS.md').write_text('\n'.join(lines)+'\n')
