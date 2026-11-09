import fs from 'node:fs';
import {prompt} from '../followup-v7.2/protocol.mjs';
import {decodeAction,interfacePrompt,mlxChat} from '../followup-v7.2/model.mjs';
import {workMenu} from '../followup-v7.2/planner.mjs';
const cases=[['new',null,'test'],['passed','verified','produce'],['failed','failed','insert_1']];
const output=[];
for(const [name,status,expected] of cases) {
 const target='wooden_axe';
 const view={target,exactReceipt:status?{id:target,status}:null,recipeBookEdits:status==='failed'?[{item:'stick',step:{op:'craft',item:'stick',times:1}}]:[]};
 const menu=workMenu(view);
 const card={orderTarget:target,delivered:{},unfinished:[target],currentProcedure:[{op:'craft',item:target,times:1}],stock:{oak_planks:4},receipt:view.exactReceipt,menu:menu.map(({choice,effect})=>({choice,effect})),last:null};
 const r=await mlxChat([{role:'system',content:prompt('enforced')+interfacePrompt},{role:'user',content:JSON.stringify(card)}],711,AbortSignal.timeout(120000));
 let action;try{action=decodeAction(r.content);}catch{}
 const match=action?.tool==='choose'&&action.choice===expected;
 output.push({synthetic:true,name,card,r,action,match});
 fs.writeFileSync(new URL('./menu-preflight.json',import.meta.url),JSON.stringify(output,null,2));
}
console.log(output.map(o=>[o.name,o.match,o.action]));
