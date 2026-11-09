import {connect,reset,Executor} from '../game.mjs';
import {LIMITS,referenceLibrary} from '../protocol.mjs';
import {createRequire} from 'node:module';
const require=createRequire(process.cwd()+'/../minecraft-demo/package.json');
let bot;
try{
  bot=await connect(require('mineflayer'),Number(process.argv[2]),'test');
  const log=(event,data)=>console.log(JSON.stringify({time:new Date().toISOString(),event,...data}));
  const executor=new Executor({production:null,test:bot,arm:'enforced',context:{diagnostic:true},log,limits:LIMITS,deadline:Date.now()+120000});
  for(const [id,steps] of [['comparator',3],['repeater',3],['lectern',3]]){
    const m=referenceLibrary().find(m=>m.id===id);
    const snapshot=await reset(bot,'test',m);log('diagnostic_kit',{id,snapshot});
    for(const s of m.steps.slice(0,steps)) await executor.action(bot,s,'test');
  }
  log('diagnostic_complete',{});
}catch(error){console.error(error);process.exitCode=1;}finally{bot?.quit();}
