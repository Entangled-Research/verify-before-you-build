import fs from 'node:fs';
import {prompt,mixedLibrary,STOCK,TARGETS} from '../../protocol.mjs';
import {MLX,interfacePrompt,decodeAction,mlxChat} from '../../model.mjs';
const dir=process.argv[2];fs.mkdirSync(dir);
const cases=[
 ['look','Report the contents of my inventory using the inventory inspection tool.',{tool:'inspect'}],
 ['lookup','Ask for the native recipe for an iron_trapdoor, without building one.',{tool:'recipe',item:'iron_trapdoor'}],
 ['reproduce','Before production, test the existing enchanting_table method in the isolated test arena.',{tool:'verify_method',id:'enchanting_table'}],
 ['execute','A valid receipt is already present for chest_minecart. Execute that published method in production now.',{tool:'use_method',id:'chest_minecart'}],
 ['make','Apply the oak_planks crafting recipe twice as a direct production action.',{tool:'craft',item:'oak_planks',times:2}],
 ['heat','Directly smelt 3 units of sand into glass in production.',{tool:'smelt',input:'sand',output:'glass',count:3}],
 ['replace','For a tool-serialization exercise only, revise the hopper_minecart procedure to exactly one step: direct craft of one application of oak_planks. Do not use or verify the edited procedure.',{tool:'revise_method',id:'hopper_minecart',steps:[{op:'craft',item:'oak_planks',times:1}]}],
 ['stop','All deliveries are done. Use the tool that ends this episode.',{tool:'finish'}]];
const sys=prompt('no_gate')+interfacePrompt;
fs.writeFileSync(dir+'/spec.json',JSON.stringify({kind:'neutral offline interface preflight; zero Minecraft actions',criterion:'All eight independent requests must produce parseable JSON with the exact requested tool and arguments; ignore reason wording. No retries.',model:MLX,cases,system:sys},null,2));
for(const [name,instruction,expected] of cases){
 const delivered=name==='stop'?Object.fromEntries(TARGETS.map(t=>[t,1])):{};
 const receipts=name==='execute'?[{id:'chest_minecart',status:'verified'}]:[];
 const messages=[{role:'system',content:sys},{role:'user',content:JSON.stringify({inventory:STOCK,delivered,methods:mixedLibrary(),receipts,instruction})}];
 const started=Date.now();try{const result=await mlxChat(messages,701,AbortSignal.timeout(150000));let action=null,parseError=null;
 try{action=decodeAction(result.content);}catch(e){parseError=e.message;}
 const pass=!!action&&Object.entries(expected).every(([k,v])=>k==='steps'?Array.isArray(action.steps)&&action.steps.length===v.length&&v.every((step,i)=>Object.entries(step).every(([field,val])=>action.steps[i][field]===val)):action[k]===v);
 fs.writeFileSync(dir+'/'+name+'.json',JSON.stringify({name,expected,pass,action,parseError,elapsedMs:Date.now()-started,messages,raw:result.raw},null,2));console.log(name,pass,action?.tool,result.promptTokens,result.generatedTokens);
 }catch(e){fs.writeFileSync(dir+'/'+name+'.json',JSON.stringify({name,pass:false,messages,error:e.message},null,2));console.log(name,false,e.message);break;}
}
