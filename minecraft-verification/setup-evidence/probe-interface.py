"""Separate local model-interface diagnostics: no Minecraft connection, no execution."""
import argparse, datetime, json,time,urllib.request
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('out',type=Path);a=parser.parse_args();a.out.mkdir(parents=True,exist_ok=False)
model='sweaterdog/andy-4:micro-q8_0'
schema={'type':'object','properties':{'tool':{'type':'string','enum':['inspect','finish']}},'required':['tool'],'additionalProperties':False}
sys='Choose exactly one allowed tool. Output only a JSON object with key tool, for example {"tool":"inspect"}.'
user='The inventory is unknown. Inspect the inventory now. Reply with JSON.'
raw='<|im_start|>system\n'+sys+'<|im_end|>\n<|im_start|>user\n'+user+'<|im_end|>\n<|im_start|>assistant\n'
for name,path,payload in [
 ('chat-json','chat',{'messages':[{'role':'system','content':sys},{'role':'user','content':user}],'format':'json'}),
 ('chat-schema','chat',{'messages':[{'role':'system','content':sys},{'role':'user','content':user}],'format':schema}),
 ('raw-schema','generate',{'raw':True,'prompt':raw,'format':schema})]:
    p=dict(model=model,stream=False,options={'temperature':0.2,'seed':701,'num_predict':128,'num_ctx':16384},**payload)
    t=time.monotonic()
    try:
        req=urllib.request.Request('http://127.0.0.1:11434/api/'+path,data=json.dumps(p).encode(),headers={'Content-Type':'application/json'})
        r=json.load(urllib.request.urlopen(req,timeout=120));s=r.get('response',r.get('message',{}).get('content',''))
        try:obj=json.loads(s);valid=isinstance(obj,dict) and obj=={'tool':'inspect'}
        except ValueError:valid=False
        obs={'valid_expected_action':valid,'raw':r}
    except Exception as exc:obs={'error':str(exc)}
    result={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':'offline_interface_diagnostic','endpoint':path,'request':p,'elapsedSeconds':time.monotonic()-t,**obs}
    (a.out/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(name,obs.get('valid_expected_action'),obs.get('error'),round(result['elapsedSeconds'],2),flush=True)
