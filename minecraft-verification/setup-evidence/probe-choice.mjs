// Offline calibration of serialization/choice only. No Minecraft connection.
import fs from 'node:fs';import {TARGETS,prompt,mixedLibrary,STOCK} from '../protocol.mjs';
const dir=process.argv[2];fs.mkdirSync(dir);
const item={type:'string'},id={type:'string',enum:TARGETS},n={type:'integer',minimum:1,maximum:64};
const definition=(name,args={})=>({type:'object',properties:{tool:{type:'string',const:name},...args},required:['tool',...Object.keys(args)],additionalProperties:false});
const steps={type:'array',minItems:1,maxItems:40,items:{oneOf:[{type:'object',properties:{op:{const:'craft'},item,times:n},required:['op','item','times']},{type:'object',properties:{op:{const:'smelt'},input:item,output:item,count:n},required:['op','input','output','count']}]}};
const schema={oneOf:[definition('inspect'),definition('recipe',{item}),definition('verify_method',{id}),definition('use_method',{id}),definition('revise_method',{id,steps}),definition('craft',{item,times:n}),definition('smelt',{input:item,output:item,count:n}),definition('finish')]};
const system='You are ProfessorPickaxe. The experiment client accepts exactly one JSON tool request. Each tool has the same name as its JSON "tool" value. Use actual tools, never describe actions you did not take. Never use Mindcraft chat commands. Example request for a recipe: {"tool":"recipe","item":"book"}. Example request to test an existing procedure: {"tool":"verify_method","id":"chest_minecart"}. Example request to execute a procedure: {"tool":"use_method","id":"hopper_minecart"}. Select only the request specified in this turn.';
const cases=[['inventory','Inspect my inventory now. Do not finish.',{tool:'inspect'}],['verify','Test the published crossbow procedure in the verifier; do not run it in production.',{tool:'verify_method',id:'crossbow'}],['use','Use the published lectern procedure in production.',{tool:'use_method',id:'lectern'}],['recipe','Look up the native recipe for comparator.',{tool:'recipe',item:'comparator'}],['craft','Craft oak_planks from one oak_log in production, one recipe application.',{tool:'craft',item:'oak_planks',times:1}]];
fs.writeFileSync(dir+'/spec.json',JSON.stringify({system,schema,cases},null,2));
for(const [name,user,expected] of cases){
 const body={model:'sweaterdog/andy-4:micro-q8_0',stream:false,format:schema,messages:[{role:'system',content:system},{role:'user',content:user}],options:{seed:701,temperature:.2,num_ctx:16384,num_predict:256}};
 const start=Date.now();const r=await fetch('http://127.0.0.1:11434/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
 const data=await r.json();let action,pass=false;try{action=JSON.parse(data.message.content);pass=Object.entries(expected).every(([k,v])=>action[k]===v);}catch{}
 fs.writeFileSync(dir+'/'+name+'.json',JSON.stringify({expected,action,pass,data,elapsedMs:Date.now()-start},null,2));console.log(name,pass,JSON.stringify(action),data.error||'');
}
