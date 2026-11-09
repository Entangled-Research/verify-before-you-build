import fs from 'node:fs';
import path from 'node:path';
import {NAMES,STOCK,ARENA} from './protocol.mjs';

export function generatePack(directory,methods) {
  if (fs.existsSync(directory)) throw Error('Refusing to overwrite datapack directory');
  const put = (file,text) => { const p=path.join(directory,file); fs.mkdirSync(path.dirname(p),{recursive:true}); fs.writeFileSync(p,text+'\n'); };
  // Pinned Java 1.21.6 datapack. Only named experiment players and two small arenas.
  put('pack.mcmeta',JSON.stringify({pack:{pack_format:80,description:'Efferents manufacturing verification — Java 1.21.6'}},null,2));
  put('data/minecraft/tags/function/tick.json',JSON.stringify({values:['efferents:tick']}));
  put('data/minecraft/tags/function/load.json',JSON.stringify({values:['efferents:arm']}));
  const arena = x => {
    const r=(ARENA.width-1)/2,z=(ARENA.length-1)/2;
    const {baseY,floorY,wallBottomY,roofY}=ARENA;
    return [
      `fill ${x-r} ${baseY} ${-z} ${x+r} ${baseY} ${z} ${ARENA.base}`,
      `fill ${x-r} ${floorY} ${-z} ${x+r} ${floorY} ${z} ${ARENA.floor}`,
      `fill ${x-r} ${wallBottomY} ${-z} ${x+r} ${roofY} ${z} ${ARENA.walls}`,
      `fill ${x-r+1} ${wallBottomY} ${-z+1} ${x+r-1} ${roofY-1} ${z-1} air`,
      ...[-r,r].flatMap(dx=>[-z,z].map(dz=>`fill ${x+dx} ${wallBottomY} ${dz} ${x+dx} ${roofY} ${dz} ${ARENA.cornerPillars}`)),
      `setblock ${x+1} 100 0 crafting_table`,`setblock ${x-1} 100 0 furnace[facing=east]`,`setblock ${x} 100 2 chest[facing=north]`
    ];
  };
  const give = (name,stock) => Object.entries(stock).map(([item,n])=>`give ${name} minecraft:${item} ${n}`);
  put('data/efferents/function/arm.mcfunction',[
    'scoreboard objectives add ev_prod trigger','scoreboard objectives add ev_case trigger','scoreboard objectives add ev_phase dummy',
    'forceload add -16 -16 47 15',
    `scoreboard players set ${NAMES.production} ev_phase 0`,
    `scoreboard players set ${NAMES.production} ev_prod 0`,`scoreboard players set ${NAMES.test} ev_case 0`,
    `tellraw @a {"text":"Efferents episode armed. Two 17x17 sand work areas near 0/100/0 and 32/100/0 will be reset when requested."}`].join('\n'));
  put('data/efferents/function/production.mcfunction',[
    ...arena(0),`clear ${NAMES.production}`,`gamemode survival ${NAMES.production}`,`effect give ${NAMES.production} minecraft:resistance 100000 4 true`,
    `tp ${NAMES.production} 0.5 100 0.5`,...give(NAMES.production,STOCK),
    `scoreboard players set ${NAMES.production} ev_prod 0`,`scoreboard players set ${NAMES.production} ev_phase 1`,
    `tellraw ${NAMES.production} {"text":"EV_READY:production"}`].join('\n'));
  const tick = [
    // A new episode reconnects the producer; never reset it while it is present.
    `execute unless entity @a[name=${NAMES.production}] run scoreboard players set ${NAMES.production} ev_phase 0`,
    `execute if score ${NAMES.production} ev_phase matches 0 run scoreboard players enable ${NAMES.production} ev_prod`,
    `execute if score ${NAMES.production} ev_phase matches 0 if score ${NAMES.production} ev_prod matches 1 run function efferents:production`,
    `scoreboard players enable ${NAMES.test} ev_case`,
  ];
  for (const m of methods) {
    put(`data/efferents/function/test_${m.case}.mcfunction`,[
      ...arena(32),`clear ${NAMES.test}`,`gamemode survival ${NAMES.test}`,`effect give ${NAMES.test} minecraft:resistance 100000 4 true`,
      `tp ${NAMES.test} 32.5 100 0.5`,...give(NAMES.test,m.inputs),
      `scoreboard players set ${NAMES.test} ev_case 0`,`tellraw ${NAMES.test} {"text":"EV_READY:test_${m.case}"}`].join('\n'));
    tick.push(`execute if score ${NAMES.test} ev_case matches ${m.case} run function efferents:test_${m.case}`);
  }
  put('data/efferents/function/tick.mcfunction',tick.join('\n'));
  put('data/efferents/function/disarm.mcfunction',[
    `scoreboard players set ${NAMES.production} ev_phase 1`,
    `scoreboard players reset ${NAMES.production} ev_prod`,`scoreboard players reset ${NAMES.test} ev_case`,
    'forceload remove -16 -16 47 15'].join('\n'));
}
