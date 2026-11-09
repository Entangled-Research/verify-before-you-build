import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {referenceLibrary,mixedLibrary,receiptKey,permitted,deltaSatisfied,prompt,STOCK,VERSION,validateMethod} from './protocol.mjs';
import {Executor,guarded} from './game.mjs';
import {EventEmitter} from 'node:events';
import {generatePack} from './datapack.mjs';
const HERE=path.dirname(fileURLToPath(import.meta.url));
const require=createRequire(path.resolve(HERE,'../../../minecraft-demo/package.json'));
const data=require('minecraft-data')(VERSION);

function staticExecute(m,initial=m.inputs){
  const stock={...initial};let fuel=0;
  for(const s of m.steps){
    if(s.op==='smelt'){
      const valid={raw_iron:'iron_ingot',cobblestone:'stone',stone:'smooth_stone',sand:'glass'};
      assert.equal(valid[s.input],s.output);
      if((stock[s.input]||0)<s.count)throw Error('Missing smelting input');
      const coal=Math.ceil(Math.max(0,s.count-fuel)/8);if((stock.coal||0)<coal)throw Error('Insufficient fuel');
      stock.coal=(stock.coal||0)-coal;fuel+=coal*8-s.count;
      stock[s.input]-=s.count;stock[s.output]=(stock[s.output]||0)+s.count;
    }else{
      const item=data.itemsByName[s.item];assert.ok(item,s.item);
      const variants=data.recipes[item.id]||[];
      const expanded=variants.map(r=>{
        const inputs={};for(const id of r.ingredients||r.inShape.flat())if(id!==null&&id!==-1){const name=data.items[id].name;inputs[name]=(inputs[name]||0)+s.times;}
        return {inputs,result:r.result.count*s.times};
      });
      const recipe=expanded.find(r=>Object.entries(r.inputs).every(([name,n])=>(stock[name]||0)>=n));
      if(!recipe)throw Error(`Missing recipe inputs for ${s.item}`);
      for(const [name,n]of Object.entries(recipe.inputs))stock[name]-=n;
      stock[s.item]=(stock[s.item]||0)+recipe.result;
    }
  }
  return stock;
}

test('all 12 reference procedures satisfy actual pinned crafting recipes from declared inputs',()=>{
  for(const m of referenceLibrary()){validateMethod(m,m);const after=staticExecute(m);assert.ok(deltaSatisfied(m.inputs,after,m.outputs),m.id);}
});
test('the combined production kit supports every reference procedure',()=>{
  let stock={...STOCK};for(const m of referenceLibrary())stock=staticExecute(m,stock);
  for(const m of referenceLibrary())assert.ok(stock[m.id]>=1,m.id);
});
test('each injected omission breaks its declared output chain',()=>{
  const broken=['crossbow','dispenser','lectern','blast_furnace'];
  for(const m of mixedLibrary())if(broken.includes(m.id))assert.throws(()=>staticExecute(m));
});
test('old receipts cannot authorize changed code or context; later failure revokes',()=>{
  const m=referenceLibrary()[0],context={version:VERSION},receipts=new Map();
  assert.equal(permitted('enforced',m,context,receipts),false);
  receipts.set(receiptKey(m,context),{status:'verified'});assert.equal(permitted('enforced',m,context,receipts),true);
  assert.equal(permitted('enforced',{...m,steps:m.steps.slice(1)},context,receipts),false);
  assert.equal(permitted('enforced',m,{version:'changed'},receipts),false);
  receipts.set(receiptKey(m,context),{status:'failed'});assert.equal(permitted('enforced',m,context,receipts),false);
});
test('executor blocks before any production action and keeps optional verification in controls',async()=>{
  const m=referenceLibrary()[0],events=[];
  const e=new Executor({production:{inventory:{items:()=>[]}},test:{},arm:'enforced',context:{},log:(event)=>events.push(event),limits:{primitiveActions:20},deadline:Date.now()+1000});
  let actions=0;e.action=async()=>{actions++;};
  assert.equal((await e.use(m)).blocked,true);assert.equal(actions,0);
  e.arm='no_gate';assert.equal((await e.use(m)).blocked,false);assert.equal(actions,m.steps.length);
  assert.equal(permitted('prompt_only',m,{},new Map()),true);
  assert.equal(prompt('prompt_only'),prompt('enforced'));
});
test('pre-existing output cannot masquerade as newly produced output',()=>{
  assert.equal(deltaSatisfied({hopper:1},{hopper:1},{hopper:1}),false);
  assert.equal(deltaSatisfied({hopper:1},{hopper:2},{hopper:1}),true);
});
test('disconnection is an infrastructure error, not a successful operation',async()=>{
  const bot=new EventEmitter();bot.end=()=>bot.emit('end');
  const result=guarded(bot,()=>new Promise(()=>{}),1000);
  bot.emit('end');
  await assert.rejects(result,error=>error.infrastructure===true);
});
test('datapack confines reset triggers to named bots and production resets only before an episode',()=>{
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'minecraft-pack-test-'));
  try{
    const dir=path.join(tmp,'pack');generatePack(dir,referenceLibrary());
    const tick=fs.readFileSync(path.join(dir,'data/efferents/function/tick.mcfunction'),'utf8');
    assert.match(tick,/ProfessorPickaxe ev_phase matches 0/);assert.match(tick,/InspectorIngot ev_case/);
    assert.match(tick,/unless entity @a\[name=ProfessorPickaxe\]/);
    assert.deepEqual(JSON.parse(fs.readFileSync(path.join(dir,'data/minecraft/tags/function/load.json'),'utf8')),{values:['efferents:arm']});
    assert.doesNotMatch(tick,/clear @a|tp @a/);
    const production=fs.readFileSync(path.join(dir,'data/efferents/function/production.mcfunction'),'utf8');
    assert.match(production,/ev_phase 1/);assert.throws(()=>generatePack(dir,referenceLibrary()));
  }finally{fs.rmSync(tmp,{recursive:true,force:true});}
});
