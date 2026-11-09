import fs from 'node:fs';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {mixedLibrary,VERSION} from '../followup-v7/protocol.mjs';
import {suggestions} from '../followup-v7/planner.mjs';
const require=createRequire(fileURLToPath(new URL('../../../minecraft-demo/package.json',import.meta.url)));
const registry=require('prismarine-registry')(VERSION);
const Recipe=require('prismarine-recipe')(registry).Recipe;
const bot={registry,findBlock:()=>true,recipesAll:(id)=>Recipe.find(id,null)};
const source=new URL('../setup-evidence/qualification-v1/result-01/events.jsonl',import.meta.url);
const events=fs.readFileSync(source,'utf8').trim().split('\n').map(JSON.parse);
const outputs=[];
for (const r of events.filter(e=>e.event==='receipt'&&e.status==='failed')) {
 const method=mixedLibrary().find(m=>m.id===r.id);
 const failed=events.filter(e=>e.event==='action'&&e.time<r.time&&!e.ok).at(-1);
 const index=method.steps.findIndex(s=>JSON.stringify(s)===JSON.stringify(failed.step));
 outputs.push({id:r.id,recipeBookEdits:suggestions(bot,method,{...r,failedStep:index})});
}
console.log(JSON.stringify(outputs,null,2));
