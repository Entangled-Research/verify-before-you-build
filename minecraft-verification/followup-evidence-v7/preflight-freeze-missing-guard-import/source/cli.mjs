import fs from 'node:fs';
import {taskView,compactReceipt} from './planner.mjs';
import path from 'node:path';
import net from 'node:net';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { createInterface } from 'node:readline/promises';
import { execFileSync } from 'node:child_process';
import {ARMS,NAMES,ARENA,TARGETS,STOCK,LIMITS,VERSION,hash,prompt,referenceLibrary,mixedLibrary,validateMethod} from './protocol.mjs';
import {generatePack} from './datapack.mjs';
import {connect,reset,inventory,Executor} from './game.mjs';
import {MLX,modelPath,interfacePrompt,decodeAction,mlxChat} from './model.mjs';

const HERE=path.dirname(fileURLToPath(import.meta.url));
const args=process.argv.slice(2),command=args.shift();
function option(name,fallback){const i=args.indexOf(`--${name}`);return i<0?fallback:args[i+1];}
const has=name=>args.includes(`--${name}`);
const mindcraft=path.resolve(option('mindcraft',path.join(HERE,'../../../minecraft-demo')));
const require=createRequire(path.join(mindcraft,'package.json'));
const prepared=path.resolve(option('prepared',path.join(HERE,'prepared')));
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const save=(p,data)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(data,null,2)+'\n');};
function port(){const n=Number(option('port'));if(!Number.isInteger(n)||n<1||n>65535)throw Error('Supply --port with the Minecraft LAN port');return n;}
const model=option('model',MLX.name);
if(model!==MLX.name)throw Error('This protocol is frozen to '+MLX.name);
const sourceHashes=()=>Object.fromEntries(fs.readdirSync(HERE).filter(n=>n.endsWith('.mjs')).sort().map(n=>[n,hash(fs.readFileSync(path.join(HERE,n),'utf8'))]));

async function preflight(){
  const data=require('minecraft-data')(VERSION);require('mineflayer');require('vec3');
  for(const item of [...TARGETS,...Object.keys(STOCK)])if(!data.itemsByName[item])throw Error(`Unknown item: ${item}`);
  console.log(`Local dependencies and ${VERSION} item names: OK`);
  if(!fs.existsSync(path.join(prepared,'datapack/pack.mcmeta')))throw Error('Run prepare first');
  console.log('Prepared datapack: present');
  if(has('offline')){console.log('Offline check only: no server connection, model inference, or experiment.');return;}
  await new Promise((resolve,reject)=>{const s=net.createConnection({host:'127.0.0.1',port:port()});s.setTimeout(5000);s.once('connect',()=>{s.end();resolve();});s.once('error',reject);s.once('timeout',()=>{s.destroy();reject(Error('LAN TCP timeout'));});});
  const response=await fetch(MLX.base+'/models',{signal:AbortSignal.timeout(5000)});
  if(!response.ok)throw Error('Local MLX model list HTTP '+response.status);
  if(!(await response.json()).data.some(m=>m.id===modelPath()))throw Error('Frozen MLX snapshot is not served');
  console.log('LAN and dedicated local MLX endpoint with frozen Qwen snapshot: OK. No inference.');

}

function prepare(){
  if(fs.existsSync(prepared))throw Error('Prepared directory already exists; choose --prepared NEW_DIRECTORY to preserve it');
  fs.mkdirSync(prepared,{recursive:true});
  const sourceDir=path.join(prepared,'source');fs.mkdirSync(sourceDir);
  for(const name of Object.keys(sourceHashes()))fs.copyFileSync(path.join(HERE,name),path.join(sourceDir,name));
  const methods=referenceLibrary();
  for(const m of methods)validateMethod(m,m);
  save(path.join(prepared,'library-clean.json'),methods);
  save(path.join(prepared,'library-mixed.json'),mixedLibrary());
  save(path.join(prepared,'observer-fixtures.json'),{origin:'hand-authored reference procedures; explicitly injected faults, not observed agent failures',mixedFaults:{crossbow:'omitted tripwire_hook step',dispenser:'omitted bow step',lectern:'omitted book step',blast_furnace:'omitted smooth_stone step'}});
  save(path.join(prepared,'protocol.json'),{version:7,planner:{...MLX,consecutiveInvalidStop:5},minecraft:VERSION,arena:ARENA,players:NAMES,arms:ARMS,targets:TARGETS,stock:STOCK,limits:LIMITS,sourceHashes:sourceHashes(),
    verification:'Real execution from exact method inputs in separate reset arena; inventory output delta required; no item transfer from tests to production.',
    scope:'Standalone Minecraft verifier adapter; not yet the Efferents journal executor. Known Minecraft crafting is a controlled systems test, not unknown science.',
    outcomes:['complete basket','delivered distinct targets','unverified method starts','blocked method starts','repairs','tokens','wall seconds','primitive actions','test kits consumed'],
    initialMatrix:{libraries:['mixed'],arms:['prompt_only','enforced'],seeds:[711],episodes:2},
    notes:['No experiment is launched by prepare.','Same direct actions, inventory observation, and optional verification in every arm.','Prompt-only and enforced prompts are identical.','Separate test materials are reported, not free production resources.','Injected-fault frequencies are not estimates of natural error prevalence.','Three repetitions of one task are exploratory, not three independent scientific domains.']});
  for(const arm of ARMS)fs.writeFileSync(path.join(prepared,`prompt-${arm}.txt`),prompt(arm)+interfacePrompt+'\n');
  const rows=['prompt_only','enforced'].map(arm=>({episode:'mixed-seed711-'+arm,library:'mixed',arm,seed:711}));
  save(path.join(prepared,'schedule.json'),rows);
  generatePack(path.join(prepared,'datapack'),methods);
  console.log(`Prepared ${prepared}; no game, model, or experiment started.`);
}

function install(){
  if(!option('world'))throw Error('Supply --world PATH_TO_YOUR_DEDICATED_MINECRAFT_WORLD');
  const world=path.resolve(option('world'));
  if(!fs.existsSync(path.join(world,'level.dat')))throw Error('This is not a Minecraft world directory (level.dat missing)');
  const destination=path.join(world,'datapacks','efferents-verification');
  if(fs.existsSync(destination))throw Error('Datapack already exists; remove/archive it explicitly before installing a replacement');
  fs.mkdirSync(path.dirname(destination),{recursive:true});
  fs.cpSync(path.join(prepared,'datapack'),destination,{recursive:true,errorOnExist:true,force:false});
  console.log(`Installed ${destination}. Nothing connected or launched. In Minecraft use /reload.`);
}

async function episode(){
  const calibration=command==='calibrate';
  if(!calibration&&!ARMS.includes(option('arm')))throw Error(`Choose --arm ${ARMS.join('|')}`);
  const arm=calibration?'enforced':option('arm'),seed=Number(option('seed','701'));
  const libraryPath=path.resolve(option('library',path.join(prepared,'library-clean.json')));
  const methods=read(libraryPath),contracts=referenceLibrary();
  if(methods.length!==contracts.length || new Set(methods.map(m=>m.id)).size!==contracts.length)throw Error('Expected one method for each target');
  for(const m of methods)validateMethod(m,contracts.find(c=>c.id===m.id));
  const run=path.resolve(option('out',path.join(HERE,'runs',`${new Date().toISOString().replaceAll(':','-')}-${arm}`)));
  if(fs.existsSync(run))throw Error('Refusing to overwrite run');fs.mkdirSync(run,{recursive:true});
  const started=Date.now();let production,test,executor,terminal='infrastructure_error',error=null;let promptTokens=0,generatedTokens=0,turns=0,modelCalls=0;
  const events=[];
  const log=(event,fields={})=>{const record={time:new Date().toISOString(),event,...fields};events.push(record);fs.appendFileSync(path.join(run,'events.jsonl'),JSON.stringify(record)+'\n');};
  const protocol=read(path.join(prepared,'protocol.json'));
  if(hash(protocol.sourceHashes)!==hash(sourceHashes()))throw Error('Source changed since prepare; prepare a new frozen directory before running');
  const limits={...LIMITS};
  const qualification=calibration?null:read(path.join(prepared,'qualification.json'));
  save(path.join(run,'manifest.json'),{kind:calibration?'calibration':'agent_episode',arm,seed,model:calibration?null:model,server:{host:'127.0.0.1',port:port(),version:VERSION},librarySha256:hash(methods),library:methods,sourceHashes:sourceHashes(),protocol,qualification,limits,node:process.version});
  let hardStop,activeDeadline=null;
  try{
    const mineflayer=require('mineflayer');
    production=await connect(mineflayer,port(),'production');test=await connect(mineflayer,port(),'test');
    console.log(`Bots ${NAMES.production} and ${NAMES.test} joined.`);
    if(has('auto-arm')){
      console.log('Using datapack automatic episode arming.');
    }else{
      console.log('In Minecraft run /function efferents:arm .');
      const rl=createInterface({input:process.stdin,output:process.stdout});
      try{await rl.question('Press Enter after arming the episode: ');}finally{rl.close();}
    }
    const initialSnapshot=await reset(production,'production');
    const initial=initialSnapshot.inventory;
    const context={episodeId:path.basename(run),minecraft:VERSION,serverPort:port(),initialStock:STOCK,workstations:['crafting_table','empty_furnace'],testArena:[32,100,0],arena:ARENA,adapterSourceSha256:sourceHashes()};
    const deadline=Date.now()+limits.episodeSeconds*1000;activeDeadline=deadline;
    hardStop=setTimeout(()=>{production.end();test.end();},limits.episodeSeconds*1000);
    executor=new Executor({production,test,arm,context,log,limits,deadline});
    log('episode_started',{initial,initialSnapshot});
    if(calibration){
      const checks=[];
      for(const m of methods){
        const receipt=await executor.verify(m);checks.push({id:m.id,status:receipt.status,failure:receipt.failure});
        console.log(`${m.id}: ${receipt.status}${receipt.failure?' — '+receipt.failure:''}`);
      }
      save(path.join(run,'calibration.json'),checks);
      if(checks.every(c=>c.status==='verified')){
        // Exercise the production write path separately from the twelve verifier
        // controls. The next agent episode receives an entirely new stock.
        const m=methods.find(method=>method.id==='dispenser');
        for(const step of m.steps)await executor.action(production,step,'production');
        const ok=executor.delivered.dispenser===1;
        log('calibration_delivery',{id:m.id,serverChest:executor.delivered,ok});
        const controls=[];
        const positive=await executor.verify(methods[0]);
        controls.push({name:'real passing receipt cached without another kit',ok:positive.status==='verified'&&executor.testAttempts===12});
        for(const id of ['crossbow','dispenser','lectern','blast_furnace']){
          const bad=mixedLibrary().find(method=>method.id===id);
          const r=await executor.verify(bad);
          controls.push({name:'original faulty '+id+' fails without automatic edits',ok:r.status==='failed'&&r.endSnapshot.source==='server:window_items',error:r.failure});
        }
        const before=inventory(production);
        let rejected=false;
        try{await executor.action(production,{op:'smelt',input:'raw_iron',output:'iron_ingot',count:64},'production');}
        catch(error){rejected=error.message==='Insufficient raw_iron before furnace transfer';}
        const block=production.findBlock({matching:b=>b.name==='furnace',maxDistance:4});
        const f=await production.openFurnace(block);
        try{
          controls.push({name:'insufficient smelt rejected before moving inputs',ok:rejected&&!f.inputItem()&&inventory(production).raw_iron===before.raw_iron});
          await f.putInput(production.registry.itemsByName.raw_iron.id,null,1);
        }finally{f.close();}
        const recovered=await guarded(production,()=>executor.recoverFurnace(production),20000);
        controls.push({name:'staged abandoned input physically recovered',ok:recovered.recovered.input?.name==='raw_iron'&&recovered.inventory.raw_iron===before.raw_iron});
        save(path.join(run,'development-controls.json'),controls);
        terminal=ok&&controls.every(c=>c.ok)?'calibration_passed':'calibration_failed';
      }else terminal='calibration_failed';
      return;
    }
    const system={role:'system',content:prompt(arm)+interfacePrompt};let last={ready:true},invalid=0;
    terminal='budget_exhausted';
    for(turns=0;turns<limits.modelTurns;turns++){
      if(Date.now()>deadline || promptTokens+generatedTokens>=limits.modelTokens || executor.actions>=limits.primitiveActions)break;
      const observation=taskView(methods,executor,production,inventory(production),last);
      const request=[system,{role:'user',content:JSON.stringify(observation)}];
      log('planner_observation',{turn:turns,observation});
      const t=Date.now();
      const result=await mlxChat(request,seed,AbortSignal.timeout(Math.max(1,Math.min(limits.requestSeconds*1000,deadline-Date.now()))));
      modelCalls++;promptTokens+=result.promptTokens;generatedTokens+=result.generatedTokens;
      log('model',{turn:turns,promptTokens:result.promptTokens,generatedTokens:result.generatedTokens,elapsedMs:Date.now()-t,response:result.content,raw:result.raw});
      let tool;
      try{tool=decodeAction(result.content);invalid=0;}catch(e){
        invalid++;last={error:e.message};log('invalid_model_action',{turn:turns,consecutive:invalid,error:e.message});
        if(invalid>=5){terminal='interface_failure';break;}
        continue;
      }

      const method=methods.find(m=>m.id===tool.id);
      try{
        if(tool.id && tool.id!==observation.target)throw Error('Current work order is '+observation.target+'. Select its exact method ID.');
        switch(tool.tool){
          case 'inspect':last={inventory:inventory(production),delivered:executor.delivered};break;
          case 'recipe':{
            const item=production.registry.itemsByName[tool.item];if(!item)throw Error('Unknown item');
            const table=production.findBlock({matching:b=>b.name==='crafting_table',maxDistance:4});
            last=production.recipesAll(item.id,null,table).map(r=>({result:r.result,delta:r.delta.map(d=>({item:production.registry.items[d.id]?.name,count:d.count}))}));break;
          }
          case 'verify_method':if(!method)throw Error('Unknown method');last=compactReceipt(await executor.verify(method));break;
          case 'use_method':if(!method)throw Error('Unknown method');last=await executor.use(method);break;
          case 'recover_furnace':last=await guarded(production,()=>executor.recoverFurnace(production),20000);break;
          case 'insert_step':{
            const edit=observation.recipeBookEdits.find(e=>e.item===tool.item);
            if(!edit)throw Error('Select an offered recipe-book insert or write your own revise_method.');
            const revised=structuredClone(method);
            revised.steps.splice(edit.insertBefore,0,edit.step);
            validateMethod(revised,contracts.find(c=>c.id===method.id));
            log('method_revised',{before:method,after:revised,authorship:'model selected recipe-book insertion',edit});
            methods[methods.indexOf(method)]=revised;last={revised:revised.id};break;
          }
          case 'revise_method':{
            if(!method)throw Error('Unknown method');const revised={...method,steps:tool.steps};validateMethod(revised,contracts.find(c=>c.id===method.id));
            log('method_revised',{before:method,after:revised});methods[methods.indexOf(method)]=revised;last={revised:revised.id,receipt:'New steps require a new receipt.'};break;
          }
          case 'craft':last=await executor.action(production,{op:'craft',item:tool.item,times:tool.times},'production');break;
          case 'smelt':last=await executor.action(production,{op:'smelt',input:tool.input,output:tool.output,count:tool.count},'production');break;
          case 'finish':await executor.deliver();terminal='agent_finished';break;
          default:throw Error('Unknown tool');
        }
      }catch(e){last={error:e.message};log('tool_error',{tool,error:e.message});if(e.infrastructure)throw e;}
      log('tool_result',{tool,result:last});
      if(TARGETS.every(t=>(executor.delivered[t]||0)>=1)){terminal='success';break;}
      if(tool.tool==='finish')break;
    }
    await executor.deliver();
  }catch(e){error=e.message;const expired=!calibration&&activeDeadline!==null&&Date.now()>=activeDeadline;terminal=expired?'budget_exhausted':'infrastructure_error';log(expired?'deadline_stop':'fatal',{error});}
  finally{
    clearTimeout(hardStop);
    const delivered=executor?.delivered||{};
    const result={kind:calibration?'calibration':'agent_episode',status:terminal,error,complete:TARGETS.every(t=>(delivered[t]||0)>=1),delivered,distinctTargets:TARGETS.filter(t=>(delivered[t]||0)>=1).length,
      arm,seed,model:calibration?null:model,promptTokens,generatedTokens,usageComplete:true,modelTurns:modelCalls,wallSeconds:(Date.now()-started)/1000,
      primitiveActions:executor?.actions||0,verificationAttempts:executor?.testAttempts||0,testKits:executor?.kits||[],
      productionInventory:production?.inventory?inventory(production):null,
      unverifiedMethodStarts:events.filter(e=>e.event==='dependency_started'&&e.status!=='verified').length,
      blockedMethodStarts:events.filter(e=>e.event==='dependency_blocked').length,repairs:events.filter(e=>e.event==='method_revised').length,
      limitations:['Local MLX endpoint token counts; no provider inference-compute measurement.','Method dependency declarations only; direct reimplementation is allowed.','Test resources are separate and logged; equal production supplies do not mean equal total materials consumed.','LAN live correctness must be established by preflight and calibration.']};
    if(error)result.usageComplete=false;
    save(path.join(run,'result.json'),result);production?.quit();test?.quit();console.log(JSON.stringify(result,null,2));console.log(`Evidence: ${run}`);
  }
}

function summarize(){
  const root=path.resolve(option('runs',path.join(HERE,'runs')));const results=[];
  if(fs.existsSync(root))for(const name of fs.readdirSync(root))if(fs.existsSync(path.join(root,name,'result.json')))results.push({episode:name,...read(path.join(root,name,'result.json'))});
  console.log('| Episode | Kind | Arm | Status | Targets / 12 | Unverified starts | Verification attempts | Tokens | Seconds |');
  console.log('|---|---|---|---|---:|---:|---:|---:|---:|');
  for(const r of results)console.log(`| ${r.episode} | ${r.kind} | ${r.arm} | ${r.status} | ${r.distinctTargets} | ${r.unverifiedMethodStarts} | ${r.verificationAttempts} | ${r.promptTokens+r.generatedTokens} | ${r.wallSeconds.toFixed(1)} |`);
  if(!results.length)console.log('No episodes have been run.');
}

try{
  if(command==='prepare')prepare();
  else if(command==='install')install();
  else if(command==='preflight')await preflight();
  else if(command==='episode')await episode();
  else if(command==='calibrate')await episode();
  else if(command==='summarize')summarize();
  else console.log('Commands: prepare [--prepared DIR]; install --world WORLD_DIRECTORY; preflight [--offline | --port PORT] [--model MODEL]; calibrate --port PORT [--out NEW_DIR]; episode --port PORT --arm no_gate|prompt_only|enforced [--library FILE] [--seed 701] [--out NEW_DIR]; summarize [--runs DIR]. All use the same --prepared DIR.');
}catch(e){console.error(e.message);process.exitCode=1;}
