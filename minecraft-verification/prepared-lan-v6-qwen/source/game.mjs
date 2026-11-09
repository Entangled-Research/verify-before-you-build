import { once } from 'node:events';
import {NAMES,ARENA,TARGETS,VERSION,deltaSatisfied,receiptKey,permitted,validateMethod} from './protocol.mjs';

export const sleep = ms => new Promise(resolve=>setTimeout(resolve,ms));
export function guarded(bot,operation,milliseconds) {
  return new Promise((resolve,reject)=>{
    let settled=false;
    const done=(error,value)=>{if(settled)return;settled=true;clearTimeout(timer);bot.removeListener('end',ended);error?reject(error):resolve(value);};
    const ended=()=>{const e=Error('Minecraft connection ended during operation');e.infrastructure=true;done(e);};
    const timer=setTimeout(()=>{const e=Error('Minecraft operation timed out; connection closed to stop pending actions');e.infrastructure=true;done(e);bot.end();},Math.max(1,milliseconds));
    bot.once('end',ended);
    if(bot.experimentDisconnected){ended();return;}
    Promise.resolve().then(()=>settled?undefined:operation()).then(value=>done(null,value),error=>done(error));
  });
}
function counts(items){
  return items.reduce((a,i)=>{a[i.name]=(a[i.name]||0)+i.count;return a;},{});
}
export function inventory(bot){return counts(bot.inventory.items());}
// Mineflayer predicts inventory clicks. A newly opened chest window is emitted
// only after its server window_items packet is installed. These snapshots use
// the slots of that new window directly, before any transfer or local click.
async function readServerWindow(bot){
  const block=bot.findBlock({matching:b=>b.name==='chest',maxDistance:4});
  if(!block)throw Error('Missing readback chest');
  const frames=new Map();
  const record=packet=>{frames.set(packet.windowId,packet);};
  bot._client.on('window_items',record);
  let w;
  try{
    w=await bot.openContainer(block);
    const frame=frames.get(w.id);
    if(!frame||frame.items.length!==w.slots.length)throw Error('Missing fresh server window_items frame');
    const stacks=frame.items.flatMap((item,slot)=>item.itemCount>0?[{slot,name:bot.registry.items[item.itemId].name,count:item.itemCount}]:[]);
    return {source:'server:window_items',windowId:w.id,stateId:frame.stateId,slotCount:frame.items.length,stacks,
      inventory:counts(stacks.filter(s=>s.slot>=w.inventoryStart&&s.slot<w.inventoryEnd)),chest:counts(stacks.filter(s=>s.slot<w.inventoryStart))};
  }finally{bot._client.removeListener('window_items',record);w?.close();}
}
const slot = item => item ? {name:item.name,count:item.count} : null;
export const furnaceState = furnace => ({input:slot(furnace.inputItem()),fuelItem:slot(furnace.fuelItem()),output:slot(furnace.outputItem()),burnFraction:furnace.fuel});

export async function connect(mineflayer,port,role) {
  const bot=mineflayer.createBot({host:'127.0.0.1',port,username:NAMES[role],auth:'offline',version:VERSION,checkTimeoutInterval:30000});
  // Always attach an error listener, including after spawning.
  bot.on('error',()=>{});
  bot.on('end',()=>{bot.experimentDisconnected=true;});
  const timer=setTimeout(()=>bot.end(),30000);
  try { await Promise.race([once(bot,'spawn'),once(bot,'end').then(()=>{throw Error(`${role} disconnected before spawn`);})]); }
  finally {clearTimeout(timer);}
  // Vanilla 1.21.6 ignores block use while the client is still loading terrain.
  // This Mineflayer version does not send the vanilla ready acknowledgement.
  await bot.waitForChunksToLoad();
  bot._client.write('player_loaded',{});
  await sleep(500);
  return bot;
}

export async function reset(bot,role,m) {
  const token=role==='production' ? 'production' : `test_${m.case}`;
  await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>{cleanup();reject(Error(`No ${token} reset acknowledgement. Is the datapack loaded and /function efferents:arm executed?`));},15000);
    const listener=text=>{if(text===`EV_READY:${token}`){cleanup();resolve();}};
    const cleanup=()=>{clearTimeout(timer);bot.removeListener('messagestr',listener);};
    bot.on('messagestr',listener);
    bot.chat(role==='production' ? '/trigger ev_prod set 1' : `/trigger ev_case set ${m.case}`);
  });
  await sleep(350);
  const x=role==='production'?0:32;
  if (Math.abs(bot.entity.position.x-(x+.5))>1 || Math.abs(bot.entity.position.y-100)>1) throw Error('Reset position mismatch');
  const expected=role==='production' ? (await import('./protocol.mjs')).STOCK : m.inputs;
  const snapshot=await guarded(bot,()=>readServerWindow(bot),15000);
  const point=bot.entity.position.floored();
  const checks=[[0,-2,0,ARENA.base],[0,-1,0,ARENA.floor],[0,9,0,ARENA.walls],[0,3,8,ARENA.walls],[0,3,-8,ARENA.walls],[8,3,0,ARENA.walls],[-8,3,0,ARENA.walls],[0,8,0,'air']];
  for(const dx of [-8,8])for(const dz of [-8,8])checks.push([dx,-2,dz,ARENA.base],[dx,-1,dz,ARENA.floor],[dx,0,dz,ARENA.cornerPillars],[dx,9,dz,ARENA.cornerPillars]);
  snapshot.geometry=checks.map(([dx,dy,dz,expected])=>{
    const pos=point.offset(dx,dy,dz),actual=bot.blockAt(pos)?.name;
    if(actual!==expected)throw Error(`Sandbox geometry mismatch at ${pos}: expected ${expected}, got ${actual}`);
    return {xyz:[pos.x,pos.y,pos.z],block:actual};
  });
  const actual=snapshot.inventory;
  if(Object.keys(snapshot.chest).length)throw Error('Reset chest is not empty');
  const ordered=v=>JSON.stringify(Object.fromEntries(Object.entries(v).sort()));
  if (ordered(actual)!==ordered(expected)) throw Error(`Reset inventory mismatch: ${JSON.stringify({expected,actual})}`);
  for (const name of ['crafting_table','furnace','chest']) if(!bot.findBlock({matching:b=>b.name===name,maxDistance:4})) throw Error(`Missing ${name}`);
  const furnaceBlock=bot.findBlock({matching:b=>b.name==='furnace',maxDistance:4});
  const f=await bot.openFurnace(furnaceBlock);
  try {if(f.inputItem()||f.fuelItem()||f.outputItem()||f.fuel>0||bot.blockAt(furnaceBlock.position).getProperties().lit) throw Error('Test/production furnace is not fresh');} finally {f.close();}
  return snapshot;
}

export class Executor {
  constructor({production,test,arm,context,log,limits,deadline}) {
    Object.assign(this,{production,test,arm,context,log,limits,deadline});
    this.receipts=new Map();this.actions=0;this.testAttempts=0;this.delivered={};this.kits=[];
  }
  checkBudget() {
    if(Date.now()>this.deadline) throw Error('Episode time budget exhausted');
    if(this.actions>=this.limits.primitiveActions) throw Error('Primitive-action budget exhausted');
  }
  async action(bot,step,role) {
    this.checkBudget();
    const dummy={id:'action',case:1,inputs:{},outputs:{},steps:[step]};validateMethod(dummy,dummy);
    this.actions++;
    const before=inventory(bot),started=Date.now();
    try {
      if(step.op==='craft') {
        const item=bot.registry.itemsByName[step.item];if(!item)throw Error('Unknown item');
        const table=bot.findBlock({matching:b=>b.name==='crafting_table',maxDistance:4});
        const recipes=bot.recipesFor(item.id,null,1,table);
        if(!recipes.length)throw Error(`No executable recipe for ${step.item} from current inventory`);
        // Mineflayer reuses predicted crafting slots for a batched craft; on
        // vanilla 1.21.6 this can corrupt repeated applications (e.g. torches).
        // Open a new table for each application and check its actual result
        // from a fresh server window before selecting the next recipe.
        let stock=before;
        for(let i=0;i<step.times;i++){
          const recipe=bot.recipesFor(item.id,null,1,table)[0];
          if(!recipe)throw Error(`No executable recipe for ${step.item} from current inventory`);
          await guarded(bot,()=>bot.craft(recipe,1,table),Math.min(30000,this.deadline-Date.now()));
          const snap=await guarded(bot,()=>readServerWindow(bot),15000);
          this.log('craft_readback',{role,item:step.item,application:i+1,snapshot:snap});
          if((snap.inventory[step.item]||0)-(stock[step.item]||0)<recipe.result.count){
            const error=Error(`Server did not confirm craft of ${step.item}`);error.infrastructure=true;throw error;
          }
          stock=snap.inventory;
        }
      } else await guarded(bot,()=>this.smelt(bot,step),this.deadline-Date.now());
      this.log('action',{role,step,before,after:inventory(bot),elapsedMs:Date.now()-started,ok:true});
    } catch(error) {
      this.log('action',{role,step,before,after:inventory(bot),elapsedMs:Date.now()-started,ok:false,error:error.message});throw error;
    }
    if(role==='production')await this.deliver();
    return inventory(bot);
  }
  async smelt(bot,step) {
    const block=bot.findBlock({matching:b=>b.name==='furnace',maxDistance:4});if(!block)throw Error('Missing furnace');
    const f=await bot.openFurnace(block);
    await sleep(200); // Allow the server's initial furnace-property packets to arrive.
    const before={...furnaceState(f),lit:bot.blockAt(block.position).getProperties().lit};
    let produced=0;
    try {
      if(f.inputItem()||f.outputItem())throw Error('Furnace has uncollected input/output; cannot attribute this operation');
      const input=bot.registry.itemsByName[step.input];if(!input)throw Error('Unknown smelting input');
      await f.putInput(input.id,null,step.count);
      const stop=Math.min(this.deadline,Date.now()+(step.count*12000)+15000);
      while(produced<step.count) {
        if(Date.now()>stop)throw Error('Smelting deadline exceeded');
        // Current-burn window properties can be null when reopening a burning
        // furnace. Its server block state remains lit for the residual burn.
        const lit=bot.blockAt(block.position).getProperties().lit;
        if(!lit && !f.fuelItem() && f.inputItem()) {
          const coal=bot.registry.itemsByName.coal;
          if(!(inventory(bot).coal>0))throw Error('No coal available');
          await f.putFuel(coal.id,null,1);
          this.log('fuel_loaded',{role:bot===this.test?'test':'production',item:'coal',count:1,input:step.input});
        }
        if(f.outputItem()) {
          if(f.outputItem().name!==step.output)throw Error(`Unexpected smelting output: ${f.outputItem().name}`);
          const taken=await f.takeOutput();produced+=taken.count;
        }
        if(produced<step.count)await sleep(250);
      }
      this.log('furnace',{before,after:{...furnaceState(f),lit:bot.blockAt(block.position).getProperties().lit},produced,input:step.input,output:step.output});
    } finally {f.close();}
  }
  async deliver() {
    const block=this.production.findBlock({matching:b=>b.name==='chest',maxDistance:4});if(!block)throw Error('Missing delivery chest');
    const chest=await guarded(this.production,()=>this.production.openContainer(block),15000);
    try {
      for(const item of chest.items())if(TARGETS.includes(item.name))await chest.deposit(item.type,item.metadata,item.count);

    } finally {chest.close();}
    const snapshot=await guarded(this.production,()=>readServerWindow(this.production),15000);
    this.delivered=snapshot.chest;
    this.log('delivery',{items:this.delivered,snapshot});
  }
  async verify(m) {
    this.checkBudget();if(this.testAttempts>=this.limits.verifications)throw Error('Verification-attempt budget exhausted');
    this.testAttempts++;
    const started=Date.now();let startSnapshot;let failure=null;
    this.receipts.set(receiptKey(m,this.context),{status:'pending'});
    this.log('verification_started',{id:m.id,key:receiptKey(m,this.context)});
    try {
      startSnapshot=await guarded(this.test,()=>reset(this.test,'test',m),30000);
    } catch(error) {
      // Infrastructure failure is not evidence against the scientific claim.
      this.log('verification_infrastructure_error',{id:m.id,error:error.message});
      error.infrastructure=true;
      throw error;
    }
    const before=startSnapshot.inventory;
    this.kits.push(before);
    this.log('verification_kit',{id:m.id,snapshot:startSnapshot});
    try {for(const step of m.steps)await this.action(this.test,step,'test');}
    catch(error){if(error.infrastructure)throw error;failure=error.message;}
    let endSnapshot;
    try{endSnapshot=await guarded(this.test,()=>readServerWindow(this.test),15000);}
    catch(error){this.log('verification_infrastructure_error',{id:m.id,error:error.message});error.infrastructure=true;throw error;}
    const after=endSnapshot.inventory;
    const receipt={id:m.id,key:receiptKey(m,this.context),status:!failure&&deltaSatisfied(before,after,m.outputs)?'verified':'failed',before,after,startSnapshot,endSnapshot,outputs:m.outputs,failure,elapsedMs:Date.now()-started,context:this.context};
    this.receipts.set(receipt.key,receipt);this.log('receipt',receipt);return receipt;
  }
  async use(m) {
    this.checkBudget();
    const key=receiptKey(m,this.context),status=this.receipts.get(key)?.status??'missing';
    if(!permitted(this.arm,m,this.context,this.receipts)){
      this.log('dependency_blocked',{id:m.id,key,status});return {blocked:true,reason:`Current receipt is ${status}; verify this revision or replace the method.`};
    }
    this.log('dependency_started',{id:m.id,key,status});
    for(const step of m.steps)await this.action(this.production,step,'production');
    return {blocked:false,inventory:inventory(this.production),delivered:this.delivered};
  }
}
