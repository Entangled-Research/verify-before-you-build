import fs from 'node:fs';
import {prompt,mixedLibrary,STOCK} from '../../protocol.mjs';
import {MLX,interfacePrompt,decodeAction,mlxChat} from '../../model.mjs';
const dir=process.argv[2];fs.mkdirSync(dir);
const cases=[
 ['inventory','Before doing anything else inspect what I am carrying.',{tool:'inspect'}],
 ['recipe','Request the native recipe for a bookshelf. Do not craft it.',{tool:'recipe',item:'bookshelf'}],
 ['test','Run the reproduction test for the armor_stand publication in the test area; do not manufacture from it in production.',{tool:'verify_method',id:'armor_stand'}],
 ['rely','Run the existing daylight_detector publication in production now; a valid receipt for this revision is already available.',{tool:'use_method',id:'daylight_detector'}],
 ['craft','Carry out a direct craft of stick with one recipe application.',{tool:'craft',item:'stick',times:1}],
 ['smelt','Use the direct smelting tool to turn two raw_iron into two iron_ingot.',{tool:'smelt',input:'raw_iron',output:'iron_ingot',count:2}],
 ['finish','My delivery is complete. End the episode now.',{tool:'finish'}]];
const sys=prompt('no_gate')+interfacePrompt;
fs.writeFileSync(dir+'/spec.json',JSON.stringify({kind:'neutral offline interface preflight; zero Minecraft actions',criterion:'All seven independent requests must produce parseable JSON with the exact requested tool and arguments; ignore reason wording. No retries.',model:MLX,cases,system:sys},null,2));
for(const [name,instruction,expected] of cases){
 const messages=[{role:'system',content:sys},{role:'user',content:JSON.stringify({inventory:STOCK,methods:mixedLibrary(),instruction})}];
 const started=Date.now();try{const result=await mlxChat(messages,701,AbortSignal.timeout(150000));let action=null,parseError=null;
 try{action=decodeAction(result.content);}catch(e){parseError=e.message;}
 const pass=!!action&&Object.entries(expected).every(([k,v])=>action[k]===v);
 fs.writeFileSync(dir+'/'+name+'.json',JSON.stringify({name,expected,pass,action,parseError,elapsedMs:Date.now()-started,messages,raw:result.raw},null,2));console.log(name,pass,action?.tool,result.promptTokens,result.generatedTokens);
 }catch(e){fs.writeFileSync(dir+'/'+name+'.json',JSON.stringify({name,pass:false,messages,error:e.message},null,2));console.log(name,false,e.message);break;}
}
