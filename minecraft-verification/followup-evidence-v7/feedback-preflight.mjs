import fs from 'node:fs';
import {prompt} from '../followup-v7.3/protocol.mjs';
import {decodeAction,interfacePrompt,mlxChat} from '../followup-v7.3/model.mjs';
import {compactReceipt,workMenu,plannerFeedback} from '../followup-v7.3/planner.mjs';
const readEvents=file=>fs.readFileSync(new URL(file,import.meta.url),'utf8').trim().split('\n').map(JSON.parse);
const events=readEvents('../runs/followup-v7.2-mixed-711-enforced-01/events.jsonl');
const captured=events.find(e=>e.event==='planner_observation'&&e.observation.orderTarget==='chest_minecart').observation;
const block=events.find(e=>e.event==='tool_result'&&e.result?.blocked).result;
const receipt=compactReceipt(readEvents('../runs/followup-v7.1-calibration-02/events.jsonl').find(e=>e.event==='receipt'&&e.id==='chest_minecart'&&e.status==='verified'));
const rows=[];
for(const data of [{name:'denied chest use',last:block,receipt:null,expected:'test'},{name:'passed chest reproduction',last:receipt,receipt,expected:'produce'}]){
 const card=structuredClone(captured);
 card.last=plannerFeedback(data.last);card.receipt=data.receipt;
 const menu=workMenu({target:card.orderTarget,exactReceipt:data.receipt,recipeBookEdits:[]});
 card.menu=menu.map(({choice,effect})=>({choice,effect}));
 const r=await mlxChat([{role:'system',content:prompt('enforced')+interfacePrompt},{role:'user',content:JSON.stringify(card)}],711,AbortSignal.timeout(120000));
 let action;try{action=decodeAction(r.content);}catch{}
 rows.push({name:data.name,synthetic:true,card,raw:r.raw,action,expected:data.expected,pass:action?.tool==='choose'&&action.choice===data.expected});
 fs.writeFileSync(new URL('./feedback-preflight.json',import.meta.url),JSON.stringify(rows,null,2));
}
console.log(rows.map(x=>[x.name,x.action,x.pass]));
if(!rows.every(x=>x.pass))process.exitCode=1;
