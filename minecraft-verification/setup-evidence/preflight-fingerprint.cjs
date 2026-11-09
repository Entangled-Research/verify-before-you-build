const fs=require('node:fs'),crypto=require('node:crypto'),path=require('node:path');
const {createRequire}=require('node:module');
const libs=createRequire(process.cwd()+'/../minecraft-demo/package.json');
const sum=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
(async()=>{
const model='sweaterdog/andy-4:micro-q8_0',models=await(await fetch('http://127.0.0.1:11434/api/tags')).json();
const tag=models.models.find(m=>m.name===model);if(!tag)throw Error('Missing frozen model');
const files=['mineflayer/lib/plugins/inventory.js','mineflayer/lib/plugins/craft.js','mineflayer/lib/plugins/furnace.js','mineflayer/lib/plugins/physics.js','minecraft-data/minecraft-data/data/pc/1.21.6/protocol.json'];
const versions=Object.fromEntries(['mineflayer','minecraft-protocol','prismarine-item','prismarine-windows','minecraft-data'].map(name=>[name,libs(name+'/package.json').version]));
console.log(JSON.stringify({time:new Date().toISOString(),node:process.version,ollama:await(await fetch('http://127.0.0.1:11434/api/version')).json(),tag,versions,sha256:Object.fromEntries(files.map(name=>[name,sum(libs.resolve(name))]))},null,2));
})().catch(e=>{console.error(e);process.exitCode=1});
