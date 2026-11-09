"""Qualify a model-only protocol change against live v5 calibration and held-out transport checks."""
import argparse,json,hashlib,datetime
from pathlib import Path
from runpy import run_path
here=Path(__file__).resolve().parents[1];audit=run_path(str(here/'setup-evidence/audit-run.py'))['audit']
p=argparse.ArgumentParser();p.add_argument('prepared',type=Path);p.add_argument('neutral',type=Path);a=p.parse_args();base=here/'prepared-lan-v5';cal=here/'runs/calibration-20261108-lan-v5-01'
def joins(p):return {str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.rglob('*')) if f.is_file()}
def byte(path):return hashlib.sha256(path.read_bytes()).hexdigest()
report=audit(cal);assert not report['defects'] and report['status']=='calibration_passed'
files=['source/protocol.mjs','source/game.mjs','source/datapack.mjs','source/test.mjs','library-mixed.json','library-clean.json','observer-fixtures.json','schedule.json']
for rel in files:assert byte(a.prepared/rel)==byte(base/rel),rel
world=Path.home()/'Library/Application Support/minecraft/saves/verification benchmark/datapacks/efferents-verification';assert joins(base/'datapack')==joins(a.prepared/'datapack')==joins(world)
cases=json.loads((a.neutral/'spec.json').read_text())['cases'];assert len(cases)==len(set(c[0] for c in cases))==8
records=[json.loads((a.neutral/(c[0]+'.json')).read_text()) for c in cases]
assert all(r.get('action') and not r.get('parseError') for r in records)
assert sum(r['pass'] for r in records)==6 and {r['name'] for r in records if not r['pass']}=={'make','heat'}
assert all(r['pass'] for r in records if r['name'] in ['reproduce','execute'])
amendment=here/'setup-evidence/mlx-qwen/amendment-before-gameplay.md';assert amendment.is_file()
(a.prepared/'amendment-before-gameplay.md').write_bytes(amendment.read_bytes())
qual={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'calibration_run':cal.name,'calibration_status':'reused (not rerun): twelve server-readback controls and one delivery smoke test','reason':'Same live server, installed datapack, action executor, exact stock, target/fault fixtures, recipes, arm enforcement and schedule. Change is the planner transport, checkpoint and response decoding. Receipt context will be regenerated per episode.','prior_audit':report,'bitwise_unchanged':{rel:byte(a.prepared/rel) for rel in files},'live_datapack_sha256_by_file':joins(world),'neutral_interface_suite':str(a.neutral),'original_exact_gate':'failed: 6/8; not reclassified','new_exploratory_basis':'8/8 allowed parseable requests, both verify/use correctly selected; imperfect model choices retained as outcomes','prospective_amendment_sha256':byte(amendment),'neutral_evidence_sha256':joins(a.neutral),'model_provenance_sha256':byte(here/'setup-evidence/mlx-qwen/provenance.json')}
out=a.prepared/'qualification.json';assert not out.exists();out.write_text(json.dumps(qual,indent=2)+'\n');print(out)
