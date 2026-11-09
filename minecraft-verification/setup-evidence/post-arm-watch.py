"""Pause only the outer process's between-arm transition. Never signal a research child."""
from datetime import datetime,timezone
from pathlib import Path
import os,sys,signal,subprocess,time,json
root=Path(__file__).resolve().parents[1];controller=int(sys.argv[1]);port=sys.argv[2];prep=sys.argv[3];node=root.parent.parent/'minecraft-demo/.local/node22/bin/node'
def now():return datetime.now(timezone.utc).isoformat()
def command(pid):
 r=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True);return r.stdout.strip()
def log(msg):print(now(),msg,flush=True)
for arm in ['no_gate','prompt_only','enforced']:
 run=root/'runs'/(prep+'-mixed-r1-'+arm)
 while not (run/'events.jsonl').is_file():
  if 'launch-mlx-pilot.py' not in command(controller):log('Launcher ended before '+arm);sys.exit()
  time.sleep(.4)
 if 'launch-mlx-pilot.py' not in command(controller):raise RuntimeError('Unrecognized launcher PID')
 os.kill(controller,signal.SIGSTOP);log('Holding launcher only, current research child continues: '+arm)
 try:
  while not (run/'result.json').is_file():
   time.sleep(.5)
  # CLI writes the result just before quitting, so wait for the server's
  # leave lines after this arm's join before reusing the persisted identity.
  limit=time.monotonic()+20;logpath=Path.home()/'Library/Application Support/minecraft/logs/latest.log'
  while time.monotonic()<limit:
   lines=logpath.read_text(errors='replace').splitlines()
   if all(max((i for i,l in enumerate(lines) if '[Server thread/INFO]' in l and n+' left the game' in l),default=-1)>max((i for i,l in enumerate(lines) if '[Server thread/INFO]' in l and n+' joined the game' in l),default=-1) for n in ['ProfessorPickaxe','InspectorIngot']):break
   time.sleep(.4)
  else:raise RuntimeError('Research clients have not both left; no readback attempted')
  out=root/'setup-evidence/mlx-qwen'/('post-terminal-'+arm+'.json')
  subprocess.run([str(node),str(root/'setup-evidence/post-arm-furnace.mjs'),port,str(out)],cwd=root.parent,timeout=40,check=True)
  time.sleep(1);log('Readback completed for '+arm)
 except Exception as exc:log('Separate readback unavailable: '+str(exc))
 finally:
  if arm!='enforced':
   release=root/'setup-evidence/mlx-qwen'/('transition-approved-'+arm)
   log('Waiting for coordinator evidence handoff before next arm: '+arm)
   while not release.exists():time.sleep(.5)
  os.kill(controller,signal.SIGCONT);log('Released launcher for normal audit/transition: '+arm)
