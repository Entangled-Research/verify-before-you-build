import fs from 'node:fs';
import {prompt} from '../followup-v7/protocol.mjs';
import {decodeAction,interfacePrompt,mlxChat} from '../followup-v7/model.mjs';
const scenarios=[
  {name:'missing receipt for unrelated wooden tool',status:null,expected:'verify_method'},
  {name:'verified unrelated wooden tool',status:'verified',expected:'use_method'},
  {name:'missing ingredient in unrelated tool',status:'failed',expected:'insert_step'}
];
const outcomes=[];
for(const s of scenarios){
 const target='wooden_axe';
 const sample={target,undelivered:[target],deliveryChest:{},productionStock:{oak_planks:4,stick:2},procedure:{id:target,steps:[{op:'craft',item:target,times:1}]},exactReceipt:s.status?{id:target,key:'fixture',status:s.status,failure:s.status==='failed'?'missing stick':null}:null,recipeBookEdits:s.status==='failed'?[{item:'stick',step:{op:'craft',item:'stick',times:1},insertBefore:0}]:[],availableCommands:[{tool:'verify_method',id:target},{tool:'use_method',id:target},...(s.status==='failed'?[{tool:'insert_step',id:target,item:'stick'}]:[])],last:{ready:true}};
 const response=await mlxChat([{role:'system',content:prompt('enforced')+interfacePrompt},{role:'user',content:JSON.stringify(sample)}],711,AbortSignal.timeout(120000));
 let reply=null;
 try{reply=decodeAction(response.content);}catch{}
 outcomes.push({scenario:s.name,synthetic:true,expected:s.expected,raw:response.raw,parsed:reply,matched:reply?.tool===s.expected&&reply?.id===target});
 fs.writeFileSync(new URL('./planner-preflight.json',import.meta.url),JSON.stringify(outcomes,null,2));
}
console.log(outcomes.map(x=>[x.scenario,x.matched,x.parsed]));
