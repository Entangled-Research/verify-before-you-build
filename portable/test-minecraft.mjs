#!/usr/bin/env node
// Run unchanged archived tests in a disposable layout that satisfies their
// historical sibling dependency path. No server or model connection is made.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
if(!fs.existsSync(path.join(root,'dependencies/node_modules/minecraft-data')))throw Error('First run npm ci --prefix dependencies');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'verify-before-build-'));
try{
  const dest=path.join(tmp,'project/minecraft-verification');fs.mkdirSync(dest,{recursive:true});
  fs.symlinkSync(path.join(root,'dependencies'),path.join(tmp,'minecraft-demo'),'dir');
  for(const relative of ['', 'followup-v7.3']){
    const from=path.join(root,'minecraft-verification',relative),to=path.join(dest,relative);fs.mkdirSync(to,{recursive:true});
    for(const name of fs.readdirSync(from))if(name.endsWith('.mjs'))fs.copyFileSync(path.join(from,name),path.join(to,name));
  }
  const result=spawnSync(process.execPath,['--test',path.join(dest,'test.mjs'),path.join(dest,'followup-v7.3/test.mjs')],{stdio:'inherit'});
  if(result.error)throw result.error;
  process.exitCode=result.status??1;
}finally{fs.rmSync(tmp,{recursive:true,force:true});}
