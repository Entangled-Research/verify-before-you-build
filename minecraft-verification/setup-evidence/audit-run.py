"""Read-only audits of frozen LAN-v5 calibration and episode evidence."""
import argparse, collections, json
from pathlib import Path

def audit(run):
    manifest=json.loads((run/'manifest.json').read_text())
    result=json.loads((run/'result.json').read_text())
    events=[json.loads(l) for l in (run/'events.jsonl').read_text().splitlines()]
    defects=[]
    def require(ok,message):
        if not ok:defects.append(message)
    def inspect_frame(frame,label):
        require(frame.get('source')=='server:window_items',label+' is not server-sourced')
        require(frame.get('slotCount')==63,label+' is not a chest frame')
        for subset,key in [(lambda n:n<27,'chest'),(lambda n:27<=n<63,'inventory')]:
            totals=collections.Counter()
            for item in frame.get('stacks',[]):
                if subset(item['slot']):totals[item['name']]+=item['count']
            require(dict(totals)==frame.get(key),label+' incorrect '+key)
    def inspect_kit(frame,label):
        inspect_frame(frame,label)
        require(len(frame.get('geometry',[]))==24,label+' incomplete live geometry')
        require(not frame.get('chest'),label+' nonempty initial chest')
    refs={m['id']:m for m in manifest['library']}
    last_receipt={};delivered={};unverified=blocked=attempts=0;token_counts=[0,0];model_calls=0
    starts=0;receipts=[]
    for e in events:
        typ=e['event']
        if typ=='episode_started':
            starts+=1;inspect_kit(e['initialSnapshot'],'producer start')
            require(e['initial']==manifest['protocol']['stock'],'wrong production stock')
        elif typ=='verification_started':
            attempts+=1;last_receipt[e['key']]='pending'
        elif typ=='verification_kit':
            inspect_kit(e['snapshot'],e['id']);require(e['snapshot']['inventory']==refs[e['id']]['inputs'],'wrong test kit')
        elif typ=='receipt':
            inspect_frame(e['endSnapshot'],e['id']+' end');inspect_kit(e['startSnapshot'],e['id']+' start')
            require(e['before']==e['startSnapshot']['inventory'] and e['after']==e['endSnapshot']['inventory'],'receipt count mismatch')
            delta=all(e['after'].get(item,0)-e['before'].get(item,0)>=qty for item,qty in e['outputs'].items())
            require((e['status']=='verified')==(not e.get('failure') and delta),'wrong receipt '+e['id'])
            last_receipt[e['key']]=e['status'];receipts.append({'id':e['id'],'status':e['status']})
        elif typ=='delivery':
            inspect_frame(e['snapshot'],'delivery');require(e['items']==e['snapshot']['chest'],'wrong delivery counts');delivered=e['items']
        elif typ=='craft_readback':
            inspect_frame(e['snapshot'],'craft '+e['item'])
        elif typ=='dependency_started':
            status=last_receipt.get(e['key'],'missing');require(status==e['status'],'dependency status mismatch')
            if status!='verified':
                unverified+=1;require(manifest['arm']!='enforced','unverified production in enforced')
        elif typ=='dependency_blocked':blocked+=1;require(manifest['arm']=='enforced','wrong-arm block')
        elif typ=='model':
            model_calls+=1;token_counts[0]+=e['promptTokens'];token_counts[1]+=e['generatedTokens']
    require(starts==1,'missing episode start')
    require(delivered==result['delivered'],'final delivery mismatch')
    require(attempts==result['verificationAttempts'] and unverified==result['unverifiedMethodStarts'] and blocked==result['blockedMethodStarts'],'event/result mismatch')
    require(model_calls==result['modelTurns'] and token_counts==[result['promptTokens'],result['generatedTokens']],'model accounting mismatch')
    if result['kind']=='calibration':
        require(len(receipts)==12 and all(r['status']=='verified' for r in receipts),'calibration not 12/12')
        require(result['status']=='calibration_passed' and delivered=={'dispenser':1},'delivery smoke check failed')
    return {'run':run.name,'status':result['status'],'receipts':receipts,'delivered':delivered,'modelCalls':model_calls,'verifiedTokenCounts':token_counts,'defects':defects}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('runs',nargs='+',type=Path);args=parser.parse_args()
    reports=[audit(run) for run in args.runs];print(json.dumps(reports,indent=2));raise SystemExit(any(r['defects'] for r in reports))
