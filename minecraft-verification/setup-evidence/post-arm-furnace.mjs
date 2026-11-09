// Separate, read-only post-terminal connection. Intentionally does not reset,
// insert/extract, trigger the datapack, or perform any manufacturing actions.
import fs from 'node:fs';import {createRequire} from 'node:module';import {connect,sleep} from '../game.mjs';
const require=createRequire(process.cwd()+'/../minecraft-demo/package.json');const [port,out]=process.argv.slice(2);let bot;
try{
 bot=await connect(require('mineflayer'),Number(port),'production');
 const block=bot.findBlock({matching:b=>b.name==='furnace',maxDistance:4});if(!block||block.position.x!==-1||block.position.y!==100||block.position.z!==0)throw Error('Not at the production furnace');
 const frames=new Map(),props=[];bot._client.on('window_items',p=>frames.set(p.windowId,p));bot._client.on('craft_progress_bar',p=>props.push(p));
 const w=await bot.openFurnace(block);try{
  const packet=frames.get(w.id);if(!packet)throw Error('No fresh furnace window_items');
  await sleep(250);const slots=packet.items.flatMap((item,slot)=>item.itemCount?[{slot,item:bot.registry.items[item.itemId].name,count:item.itemCount}]:[]);
  fs.writeFileSync(out,JSON.stringify({time:new Date().toISOString(),kind:'post-terminal read-only furnace audit',player:bot.username,position:block.position,source:'server:window_items',windowId:w.id,stateId:packet.stateId,lit:bot.blockAt(block.position).getProperties().lit,furnaceSlots:slots.filter(s=>s.slot<3),playerInventorySlots:slots.filter(s=>s.slot>=3),rawFrame:packet,properties:props.filter(p=>p.windowId===w.id),note:'Opened after the terminal result, outside episode time; no items moved, no commands issued and no reset. Burning may advance between terminal and readback.'},null,2)+'\n',{flag:'wx'});console.log('Post-terminal readback',out);
 }finally{w.close();}
 const chestBlock=bot.findBlock({matching:b=>b.name==='chest',maxDistance:4});
 if(!chestBlock||chestBlock.position.x!==0||chestBlock.position.y!==100||chestBlock.position.z!==2)throw Error('Missing production delivery chest');
 frames.clear();const chest=await bot.openContainer(chestBlock);
 try{
  const packet=frames.get(chest.id);if(!packet)throw Error('No fresh post-terminal chest window_items');
  const stacks=packet.items.flatMap((item,slot)=>item.itemCount?[{slot,item:bot.registry.items[item.itemId].name,count:item.itemCount}]:[]);
  const delivered=stacks.filter(s=>s.slot<chest.inventoryStart).reduce((m,s)=>(m[s.item]=(m[s.item]||0)+s.count,m),{});
  fs.writeFileSync(out.replace(/\.json$/,'-chest.json'),JSON.stringify({time:new Date().toISOString(),kind:'post-terminal read-only delivery chest audit',player:bot.username,position:chestBlock.position,windowId:chest.id,stateId:packet.stateId,source:'server:window_items',delivered,stacks,rawFrame:packet},null,2)+'\n',{flag:'wx'});
 }finally{chest.close();}
}finally{bot?.quit();}
