#!/usr/bin/env node
// Portability wrapper only. It does not modify a frozen experiment source.
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const [version,...args]=process.argv.slice(2);
const versions={v6:['','prepared-lan-v6-qwen'], 'v7.1':['followup-v7.1','prepared-followup-v7.1'], 'v7.2':['followup-v7.2','prepared-followup-v7.2'], 'v7.3':['followup-v7.3','prepared-followup-v7.3']};
if(!versions[version] || !args.length){
  console.error('Usage: node portable/minecraft.mjs v6|v7.1|v7.2|v7.3 COMMAND [args]');
  process.exit(2);
}
if(args.includes('--mindcraft') || args.includes('--prepared'))throw Error('This wrapper fixes dependency and prepared directories; invoke the archived CLI directly to override.');
const [source,prepared]=versions[version];
const cli=path.join(root,'minecraft-verification',source,'cli.mjs');
const result=spawnSync(process.execPath,[cli,...args,'--mindcraft',path.join(root,'dependencies'),'--prepared',path.join(root,'minecraft-verification',prepared)],{stdio:'inherit'});
if(result.error)throw result.error;
process.exit(result.status??1);
