import fs from 'node:fs';import path from 'node:path';import {createRequire} from 'node:module';import {fileURLToPath} from 'node:url';import crypto from 'node:crypto';
import {connect,reset,Executor,guarded} from '../../game.mjs';
import {referenceLibrary,mixedLibrary,receiptKey,validateMethod,VERSION,STOCK,ARENA,LIMITS} from '../../protocol.mjs';
const dir=path.dirname(fileURLToPath(import.meta.url)),here=path.resolve(dir,'../..'),prep=path.join(here,'prepared-lan-v6-qwen');
const [outArg,portArg]=process.argv.slice(2),out=path.resolve(outArg),port=Number(portArg);if(!Number.isInteger(port))throw Error('Missing LAN port');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const freeze=JSON.parse(fs.readFileSync(path.join(dir,'freeze.json'),'utf8'));
for(const [name,digest] of Object.entries(freeze.sources))if(sha(path.join(dir,name))!==digest)throw Error('Qualification source mismatch: '+name);
for(const f of ['game.mjs','protocol.mjs','datapack.mjs'])if(sha(path.join(here,f))!==sha(path.join(prep,'source',f)))throw Error('Gameplay source changed: '+f);
for(const arm of ['no_gate','prompt_only','enforced']){
 const run=path.join(here,'runs','prepared-lan-v6-qwen-mixed-r1-'+arm),r=JSON.parse(fs.readFileSync(path.join(run,'result.json')));
 if(!['budget_exhausted','agent_finished','success'].includes(r.status))throw Error('Pilot run not normally terminal: '+arm);
 if(!fs.existsSync(path.join(here,'setup-evidence/mlx-qwen','post-terminal-'+arm+'.json')))throw Error('Missing post-terminal furnace observation: '+arm);
}
const require=createRequire(path.resolve(here,'../../minecraft-demo/package.json'));
if(fs.existsSync(out))throw Error('Refusing to overwrite qualification evidence');fs.mkdirSync(out);
const save=(file,data)=>fs.writeFileSync(path.join(out,file),JSON.stringify(data,null,2)+'\n');
const protocol=JSON.parse(fs.readFileSync(path.join(prep,'protocol.json'))),spec=JSON.parse(fs.readFileSync(path.join(dir,'spec.json')));
save('manifest.json',{kind:spec.kind,authorship:spec.authorship,startedAt:new Date().toISOString(),server:{port,version:VERSION},spec,freeze,executorSourceHashes:protocol.sourceHashes,model:null});
let prod,test,e,status='infrastructure_error',error=null;const assertions=[],events=[];
const log=(event,details={})=>{const obj={time:new Date().toISOString(),event,...details};events.push(obj);fs.appendFileSync(path.join(out,'events.jsonl'),JSON.stringify(obj)+'\n');};
const check=(name,ok,fields={})=>{assertions.push({name,ok:!!ok,...fields});log('assertion',{name,ok:!!ok,...fields});};
const eq=(v,w)=>JSON.stringify(Object.entries(v).sort())===JSON.stringify(Object.entries(w).sort());
const same=(a,b)=>eq(a.inventory,b.inventory)&&eq(a.chest,b.chest);
async function observe(bot){
 const block=bot.findBlock({matching:b=>b.name==='chest',maxDistance:4}),frames=new Map(),capture=p=>frames.set(p.windowId,p);bot._client.on('window_items',capture);let w;
 try{w=await bot.openContainer(block);const frame=frames.get(w.id);if(!frame)throw Error('No fresh server frame');const inv={},chest={};
 const stacks=frame.items.flatMap((item,slot)=>item.itemCount?[{slot,name:bot.registry.items[item.itemId].name,count:item.itemCount}]:[]);
 for(const s of stacks){const into=s.slot<w.inventoryStart?chest:inv;into[s.name]=(into[s.name]||0)+s.count;}
 const snapshot={source:'server:window_items',windowId:w.id,stateId:frame.stateId,stacks,inventory:inv,chest};log('production_observation',{snapshot});return snapshot;
 }finally{bot._client.removeListener('window_items',capture);w?.close();}
}
try{
 prod=await connect(require('mineflayer'),port,'production');test=await connect(require('mineflayer'),port,'test');const initial=await reset(prod,'production');log('initial',{snapshot:initial});
 const ctx={episodeId:path.basename(out),minecraft:VERSION,serverPort:port,initialStock:STOCK,workstations:['crafting_table','empty_furnace'],testArena:[32,100,0],arena:ARENA,adapterSourceSha256:protocol.sourceHashes};
 e=new Executor({production:prod,test,arm:'enforced',context:ctx,log,limits:{...LIMITS},deadline:Date.now()+spec.budget.wallSeconds*1000});
 const clean=referenceLibrary(),mixed=mixedLibrary(),hopper=clean.find(m=>m.id==='hopper_minecart'),current=()=>guarded(prod,()=>observe(prod),15000);
 const pre=await current(),blocked=await e.use(hopper),afterBlock=await current();
 check('unverified clean use blocks without production action or state change',blocked.blocked&&e.actions===0&&same(pre,afterBlock));
 const receipt=await e.verify(hopper);check('clean hopper reproduction verified with observed output delta',receipt.status==='verified'&&receipt.endSnapshot.source==='server:window_items'&&(receipt.after.hopper_minecart||0)-(receipt.before.hopper_minecart||0)>=1);
 const use=await e.use(hopper),afterUse=await current(),starts=events.filter(x=>x.event==='dependency_started'&&x.id===hopper.id);
 check('authorized matching receipt produces one actual delivery',!use.blocked&&starts.length===1&&starts[0].status==='verified'&&starts[0].key===receipt.key&&eq(afterUse.chest,{hopper_minecart:1}),{receiptKey:receipt.key,startKey:starts[0]?.key||null});
 const revised=structuredClone(hopper);revised.steps.find(s=>s.item==='oak_planks').times=1;validateMethod(revised,hopper);
 for(const [label,m] of [['changed hopper revision',revised],['different chest minecart method',clean.find(m=>m.id==='chest_minecart')]]){
  const before=await current(),act=e.actions,result=await e.use(m),after=await current();
  check(label+' cannot reuse hopper receipt',receiptKey(m,ctx)!==receipt.key&&result.blocked&&e.actions===act&&same(before,after),{candidateKey:receiptKey(m,ctx),originalKey:receipt.key});
 }
 const beforeFaults=await current();
 for(const id of ['crossbow','dispenser','lectern','blast_furnace']){
  const m=mixed.find(m=>m.id===id),r=await e.verify(m);
  check('mixed '+id+' fails from exact fresh test kit',r.status==='failed'&&eq(r.before,m.inputs)&&r.endSnapshot.source==='server:window_items'&&(r.after[id]||0)-(r.before[id]||0)<1,{receipt:r.key,failure:r.failure});
 }
 const afterFaults=await current();check('fault tests preserve production state',same(beforeFaults,afterFaults));
 status=assertions.every(a=>a.ok)?'qualification_passed':'qualification_failed';
}catch(exc){error=String(exc.message||exc);log('infrastructure_error',{error});}
finally{save('result.json',{kind:spec.kind,authorship:spec.authorship,status,error,finishedAt:new Date().toISOString(),assertions,modelCalls:0,primitiveActions:e?.actions||0,verificationAttempts:e?.testAttempts||0,testKits:e?.kits||[]});prod?.quit();test?.quit();console.log('Qualification:',status,error||'');}
