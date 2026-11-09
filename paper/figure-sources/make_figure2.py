#!/usr/bin/env python3
"""Render the logged item workflow with native Minecraft 1.21.6 sprites.

Requires only Python standard library, ffmpeg for nearest-neighbor sprite
scaling, and rsvg-convert for SVG-to-PDF/PNG export. No game state is invented.
Sprites reconstruct the recorded workflow; this is not a gameplay screenshot.

python3 figures/make_figure2.py
rsvg-convert -f pdf -o figures/figure2.pdf figures/figure2.svg
rsvg-convert -z 2 -o figures/figure2.png figures/figure2.svg
"""
from pathlib import Path
from zipfile import ZipFile
from html import escape
import base64,hashlib,json,subprocess
OUT=Path(__file__).resolve().parent
JAR=Path.home()/'Library/Application Support/minecraft/versions/1.21.6/1.21.6.jar'
ASSETS=OUT/'minecraft-items';ASSETS.mkdir(exist_ok=True)
NAMES={'iron_ingot':'item/iron_ingot','stick':'item/stick','string':'item/string','tripwire_hook':'block/tripwire_hook','crossbow':'item/crossbow_standby','oak_planks':'block/oak_planks'}
records=[]
with ZipFile(JAR) as z:
 for name,loc in NAMES.items():
  source='assets/minecraft/textures/'+loc+'.png';data=z.read(source);raw=ASSETS/(name+'-native.png');raw.write_bytes(data)
  enlarged=ASSETS/(name+'.png')
  subprocess.run(['ffmpeg','-loglevel','error','-y','-i',str(raw),'-vf','format=rgba,scale=128:128:flags=neighbor','-frames:v','1',str(enlarged)],check=True)
  records.append({'item':name,'source':source,'sha256_native':hashlib.sha256(data).hexdigest(),'enlargement':'nearest-neighbor, 16 to 128 pixels'})
 recipe_sources={}
 for name in ['crossbow','tripwire_hook']:
  loc='data/minecraft/recipe/'+name+'.json';data=z.read(loc);(ASSETS/(name+'-recipe.json')).write_bytes(data)
  recipe_sources[name]={'path':loc,'sha256':hashlib.sha256(data).hexdigest(),'recipe':json.loads(data)}
 model_source='assets/minecraft/models/item/tripwire_hook.json'
 model=z.read(model_source);(ASSETS/'tripwire_hook-item-model.json').write_bytes(model)
INK='#222b32';BLUE='#28627c';GREY='#687178';PALE='#b7bfc4'
p=['''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="468pt" height="194.4pt" viewBox="0 0 650 270">
<title>Crossbow item workflows without and with enforced verification.</title>
<desc>Reconstruction of recorded workflows using native Minecraft item sprites. The crossbow recipe is missing its tripwire hook. Direct production fails and retries. In the assisted enforced run a fresh isolated test detects the fault, the agent selects the hook-crafting insertion, retests successfully, and produces a crossbow with its matching receipt. A branch shows the actual hook ingredients: iron ingot, stick and plank.</desc>
<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L7 3.5 L0 7 z" fill="#28627c"/></marker><marker id="greyarrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L7 3.5 L0 7 z" fill="#687178"/></marker></defs>
<rect width="650" height="270" fill="white"/>
<g font-family="Arial, Helvetica, sans-serif">''']
def text(x,y,s,size=11,color=INK,weight='normal',anchor='middle'):
 p.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{escape(s)}</text>')
def path(d,color=BLUE,width=1.2,arrow=False,dash=None):
 p.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'+(' marker-end="url(#greyarrow)"' if arrow and color==GREY else ' marker-end="url(#arrow)"' if arrow else '')+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
def icon(item,x,y,size=32,opacity=1):
 data=base64.b64encode((ASSETS/(item+'.png')).read_bytes()).decode()
 p.append(f'<image x="{x}" y="{y}" width="{size}" height="{size}" opacity="{opacity}" xlink:href="data:image/png;base64,{data}"/>')
def crossbow_grid(x,y):
 pattern=[['stick','iron_ingot','stick'],['string',None,'string'],[None,'stick',None]]
 for row in range(3):
  for col in range(3):
   xx=x+col*22;yy=y+row*22
   p.append(f'<rect x="{xx}" y="{yy}" width="21" height="21" fill="#f5f6f6" stroke="#b8c0c5" stroke-width="0.65"/>')
   item=pattern[row][col]
   if item:icon(item,xx+1.5,yy+1.5,18)
 # The omitted ingredient is explicitly a missing prerequisite, not an item.
 xx=x+22;yy=y+22
 p.append(f'<rect x="{xx}" y="{yy}" width="21" height="21" fill="white" stroke="{INK}" stroke-width="1" stroke-dasharray="2 2"/>')
 text(xx+10.5,yy+15,'?',15,INK,'bold')
def check(x,y):path(f'M{x} {y} l4 4 l8 -10',BLUE,1.8)
text(15,16,'Without verification',12.4,INK,'bold','start')
text(15,32,'Original pilot v6 · seed 701',10.1,GREY,anchor='start')
text(280,16,'With enforced verification',12.4,BLUE,'bold','start')
text(280,32,'Assisted follow-up v7.3 · seed 711',10.1,GREY,anchor='start')
path('M260 6 V251',PALE,.8)
# Direct production applies the untested, incomplete procedure.
text(80,57,'Production craft',10.8,INK,'bold')
crossbow_grid(47,73)
path('M120 105 H175',GREY,1.3,True)
icon('crossbow',184,85,40,.23)
path('M185 86 L223 124',INK,1.3);path('M223 86 L185 124',INK,1.3)
text(81,157,'Hook step omitted',10.1,GREY)
text(203,157,'No crossbow',10.1,GREY)
path('M203 164 V186 H135 V125 H116',GREY,1.0,True)
text(141,203,'Retries in production',10.5,GREY)
text(15,235,'? = missing tripwire hook',10.2,GREY,anchor='start')
# Verification catches the same defect on an isolated kit; the model selects
# an offered edit rather than the executor silently repairing the procedure.
text(315,57,'Fresh test',10.8,INK,'bold')
crossbow_grid(282,73)
text(410,57,'Repair',10.8,INK,'bold')
icon('tripwire_hook',391,85,40)
text(500,57,'Retest',10.8,INK,'bold')
icon('crossbow',480,85,40);check(518,87)
text(594,57,'Production',10.8,INK,'bold')
icon('crossbow',574,85,40);check(612,87)
path('M353 105 H382',arrow=True);path('M437 105 H470',arrow=True)
path('M532 105 H564',arrow=True)
path('M548 84 V98',INK,1.8);path('M548 112 V132',INK,1.8)
text(315,157,'Fails',10.1,GREY)
text(410,157,'Selected edit',10.1,GREY)
text(500,157,'Passes',10.1,GREY)
text(594,157,'Receipt required',10.1,GREY)
# The actual intermediate recipe; output count is explicit.
text(280,183,'Insert the missing intermediate:',10.3,GREY,anchor='start')
icon('iron_ingot',291,193,24);text(326,211,'+',12,GREY)
icon('stick',338,193,24);text(373,211,'+',12,GREY)
icon('oak_planks',385,193,24);path('M421 205 H452',arrow=True)
icon('tripwire_hook',465,193,24);text(501,211,'×2',10.5,GREY,anchor='start')
text(393,235,'iron + stick + plank → tripwire hooks',10.1,GREY)
text(15,260,'Native item sprites reconstruct the logged workflow; this is not an in-game inventory screen.',9.5,GREY,anchor='start')
p.append('</g></svg>')
(OUT/'figure2.svg').write_text('\n'.join(p)+'\n')
manifest={'figure':'Figure 2, item workflow reconstruction','jar':str(JAR),'jar_sha256':hashlib.sha256(JAR.read_bytes()).hexdigest(),
'pixel_operations':'Native texture extraction and nearest-neighbor enlargement. Vector recipe grids, arrows, omission marks and checks are explanatory annotations.',
'interpretation':'Icons reconstruct logged procedures and outcomes; not game screenshots. Crossbow grids encode the vanilla shaped recipe with omitted hook. Hook recipe makes two; crossbow uses one.',
'comparison_scope':'Original no-gate v6 seed701 vs assisted enforced v7.3 seed711; differing interfaces, no causal performance comparison.',
'assets':records,'recipes':recipe_sources,'hook_item_model':{'path':model_source,'sha256':hashlib.sha256(model).hexdigest()},
'event_sources':['minecraft-verification/runs/prepared-lan-v6-qwen-mixed-r1-no_gate/events.jsonl','minecraft-verification/runs/followup-v7.3-mixed-711-enforced-01/events.jsonl'],
'event_accounts':['No-gate original crossbow fails and is retried in production.','Enforced original crossbow fails on isolated kit; Qwen selects tripwire-hook insertion; revised test passes; matching receipt admits crossbow delivery.']}
(OUT/'figure2-provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
