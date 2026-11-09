// Observer-only, no game or inference access. Use the same JSON encoding as
// protocol.hash to distinguish requested revisions from changed procedures.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const digest=x=>crypto.createHash('sha256').update(JSON.stringify(x)).digest('hex');
for(const dir of process.argv.slice(2)){
 const manifest=JSON.parse(fs.readFileSync(path.join(dir,'manifest.json'))),events=fs.readFileSync(path.join(dir,'events.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
 const ctx={episodeId:path.basename(dir),minecraft:manifest.server.version,serverPort:manifest.server.port,initialStock:manifest.protocol.stock,workstations:['crafting_table','empty_furnace'],testArena:[32,100,0],arena:manifest.protocol.arena,adapterSourceSha256:manifest.sourceHashes};
 const methods=new Map(manifest.library.map(m=>[m.id,m])),versions=new Map(),rows=[];let turn=null,active=null,delivered={};
 for(const e of events){if(e.event==='model')turn=e.turn;
  if(e.event==='method_revised'){
   const before=digest(e.before),after=digest(e.after),id=e.after.id,changed=before!==after;
   if(before!==digest(methods.get(id)))throw Error('Revision predecessor hash mismatch');
   const key=digest({method:e.after,context:ctx}),row={turn,id,before,after,key,changed,testReceipts:[],productionStarts:[],newlyDelivered:0};
   methods.set(id,e.after);rows.push(row);if(changed)versions.set(key,row);
  }else if(e.event==='receipt'){const row=versions.get(e.key);if(row)row.testReceipts.push(e.status);}
  else if(e.event==='dependency_started'){
   if(e.key!==digest({method:methods.get(e.id),context:ctx}))throw Error('Start hash mismatch');
   active={key:e.key,id:e.id,startCount:delivered[e.id]||0};const row=versions.get(e.key);if(row)row.productionStarts.push({turn,receipt:e.status});
  }else if(e.event==='delivery'){delivered=e.items;}
  else if(e.event==='tool_result'){
   if(active&&e.tool.tool==='use_method'&&!e.result?.error){const row=versions.get(active.key);if(row)row.newlyDelivered+=Math.max(0,(delivered[active.id]||0)-active.startCount);}
   active=null;
  }
 }
 console.log(JSON.stringify({run:path.basename(dir),rows,requests:rows.length,distinctChanges:rows.filter(r=>r.changed).length,noopRequests:rows.filter(r=>!r.changed).length,changedRevisionsProducingTarget:rows.filter(r=>r.changed&&r.newlyDelivered>0).length},null,2));
}
