const {createRequire}=require('node:module');const libs=createRequire(process.cwd()+'/../minecraft-demo/package.json');const mf=libs('mineflayer');const timer=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
const bot=mf.createBot({host:'127.0.0.1',port:61196,username:'EfferentsLab',auth:'offline',version:'1.21.6'});
const write=bot._client.write.bind(bot._client);bot._client.write=(name,data)=>{if(['block_place','player_loaded','teleport_confirm'].includes(name)) console.log('out',name,data);return write(name,data);};
bot._client.on('packet',(d,m)=>{if(['open_window','acknowledge_player_digging'].includes(m.name))console.log('in',m.name,d);});
try{
await require('events').once(bot,'spawn');await timer(1000);
const block=bot.findBlock({matching:b=>b.name==='furnace',maxDistance:4});
console.log('position',bot.entity.position,'furnace',block?.position);
if(!block)throw Error('Furnace not in reach');
let window=null;bot.on('windowOpen',w=>window=w);
await bot.activateBlock(block);await timer(2000);console.log('before ready',window?.type);
if(!window){bot._client.write('player_loaded',{});await timer(150);await bot.activateBlock(block);await timer(1000);console.log('after ready',window?.type);}
if(window)window.close();
}finally{bot.quit();}
})().catch(e=>{console.error(e);process.exitCode=1});
