#!/usr/bin/env python3
"""Produce three reviewable scientific-layout concepts and the selected figure.

Only Python stdlib is needed to produce SVG. Export each preview with:
rsvg-convert -z 2 -o preview.png preview.svg
Final vector PDF: rsvg-convert -f pdf -o figure1.pdf figure1.svg
"""
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parent
ITER=ROOT/'figure1-iterations';ITER.mkdir(exist_ok=True)
INK='#202a31';BLUE='#245e7a';GREY='#69747b';LIGHT='#b6c0c7';FAINT='#eff3f5'
class Drawing:
 def __init__(self,height=270):
  self.height=height
  self.p=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="468pt" height="{height*.72:g}pt" viewBox="0 0 650 {height}">
<title>Verify before build: declared foundations require local reproduction evidence.</title>
<desc>Run reproduction, compare observed and claimed output, record the verdict, and check a current local pass before downstream execution. Missing evidence triggers a test; failed evidence may require repair and retesting. Later failed evidence can revoke an earlier pass.</desc>
<defs><marker id="a" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L7 3.5 L0 7 z" fill="{BLUE}"/></marker><marker id="g" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L7 3.5 L0 7 z" fill="{GREY}"/></marker></defs>
<rect width="650" height="{height}" fill="white"/><g font-family="Arial, Helvetica, sans-serif">''']
 def text(self,x,y,s,size=11,color=INK,bold=False,anchor='middle',serif=False,italic=False):
  self.p.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{"bold" if bold else "normal"}" text-anchor="{anchor}"'+(' font-family="Georgia, serif"' if serif else '')+(' font-style="italic"' if italic else '')+'>'+escape(s)+'</text>')
 def path(self,d,color=BLUE,width=1.3,arrow=False,dash=None):
  self.p.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'+(f' marker-end="url(#{"g" if color==GREY else "a"})"' if arrow else '')+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def circle(self,x,y,r,fill='white',color=INK):self.p.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{color}" stroke-width="1.2"/>')
 def paper(self,x,y,w=38,h=48,receipt=False,blank=False):
  c=BLUE if receipt else INK
  self.path(f'M{x} {y} H{x+w-10} L{x+w} {y+10} V{y+h} H{x} Z',c,1.3)
  self.path(f'M{x+w-10} {y} V{y+10} H{x+w}',c,1.1)
  if receipt:self.path(f'M{x+9} {y+26} l6 6 l12 -15',BLUE,2)
  elif not blank:
   self.text(x+w/2,y+28,'f(x)',18,INK,serif=True,italic=True)
  self.path(f'M{x+9} {y+h-8} H{x+w-8}',LIGHT,.8)
 def run(self,x,y):
  self.path(f'M{x-26} {y-25} h-6 v50 h6 M{x+26} {y-25} h6 v50 h-6',LIGHT,1.1)
  self.text(x,y+7,'f(x)',24,INK,serif=True,italic=True)
 def compare(self,x,y,compact=True):
  self.text(x-5,y-5,'Claimed',9.3,GREY,anchor='end')
  self.text(x-5,y+14,'Observed',9.3,BLUE,anchor='end')
  self.path(f'M{x+3} {y-9} h30',INK,2.6)
  self.path(f'M{x+3} {y+10} h30',BLUE,2.6)
 def gate(self,x,y):
  self.path(f'M{x} {y-29} v18 M{x} {y+12} v18',INK,2.5)
 def network(self,x,y):
  self.path(f'M{x-20} {y} L{x} {y-22} L{x+20} {y} L{x} {y+22} Z',INK,1.1)
  self.path(f'M{x-20} {y} H{x+20}',INK,1.1)
  for xx,yy,r in [(x-20,y,5),(x,y-22,4),(x+20,y,5),(x,y+22,4)]:self.circle(xx,yy,r,color=BLUE if xx<x else INK)
 def save(self,path):path.write_text('\n'.join(self.p+['</g></svg>'])+'\n')

def concept_a():
 d=Drawing(270)
 d.text(15,17,"An external result becomes a foundation only when another lab declares reliance.",11,GREY,anchor='start',serif=True,italic=True)
 d.paper(31,62);d.text(50,137,'Claim + recipe',11.2,bold=True)
 d.text(50,152,'Inputs; expected result',9.3,GREY)
 d.path('M80 87 H179',arrow=True)
 d.text(131,55,'Declare',10.2,BLUE,bold=True);d.text(131,68,'foundation',10.2,BLUE,bold=True)
 d.run(219,87);d.text(219,137,'Reproduce',11.2,bold=True);d.text(219,152,'Fresh execution',9.3,GREY)
 d.path('M255 87 H282',arrow=True)
 d.compare(328,84);d.text(324,137,'Verify',11.2,bold=True);d.text(324,152,'Compare outputs',9.3,GREY)
 d.path('M365 87 H395',arrow=True);d.text(380,74,'pass',9.3,BLUE)
 d.paper(403,62,36,48,True);d.text(421,137,'Record receipt',11.2,bold=True);d.text(421,152,'Local ledger',9.3,GREY)
 d.path('M446 87 H488',arrow=True)
 d.gate(503,87);d.text(503,137,'Gate',11.2,bold=True);d.text(503,152,'Current pass',9.3,GREY)
 d.path('M490 87 H559',arrow=True)
 d.network(595,87);d.text(595,137,'New experiment',11.2,bold=True);d.text(595,152,'May start',9.3,GREY)
 # Returns are routed between captions, never through them.
 d.path('M365 108 H382 V185 H166 V111 H181',GREY,1.1,True)
 d.path('M503 119 H547 V185 H382',GREY,1.1)
 d.text(391,176,'failed test',9.5,GREY,anchor='start')
 d.text(556,176,'missing / failed',9.5,GREY,anchor='start')
 d.text(356,206,'Agent: test; revise and retest if needed.',11,GREY)
 d.text(15,239,'The executor checks every declared foundation before running downstream code.',10.4,INK,anchor='start')
 d.text(15,256,'A later failed reproduction revokes an earlier pass.',10.4,BLUE,anchor='start')
 return d

def concept_b():
 d=Drawing(270)
 d.text(17,18,'Publishing lab',11.1,GREY,bold=True,anchor='start')
 d.text(174,18,'Consuming lab',11.1,BLUE,bold=True,anchor='start')
 d.text(539,18,'Downstream work',11.1,GREY,bold=True,anchor='start')
 d.path('M160 31 V235',LIGHT,.7);d.path('M531 31 V235',LIGHT,.7)
 d.paper(45,64);d.text(64,130,'External claim',11.5,bold=True);d.text(64,146,'Recipe + claim',9.5,GREY)
 d.path('M92 88 H178',arrow=True);d.text(136,62,'declared',9.5,BLUE);d.text(136,75,'foundation',9.5,BLUE)
 d.run(216,88);d.text(216,132,'1  Reproduce',11,bold=True);d.text(216,147,'Fresh execution',9.3,GREY)
 d.path('M251 88 H275',arrow=True)
 d.compare(321,85);d.text(317,132,'2  Verify',11,bold=True);d.text(317,147,'Compare outputs',9.3,GREY)
 d.path('M360 88 H385',arrow=True);d.text(372,75,'pass',9,BLUE)
 d.paper(394,63,36,47,True);d.text(413,132,'Receipt',11,bold=True);d.text(413,147,'Latest local verdict',9.3,GREY)
 d.gate(492,88);d.text(492,132,'3  Gate',11,bold=True);d.text(492,147,'Before code runs',9.3,GREY)
 d.path('M437 88 H554',arrow=True);d.network(590,88);d.text(590,132,'Experiment',11,bold=True);d.text(590,147,'May start',9.3,GREY)
 d.path('M363 109 H374 V190 H180 V113 H181',GREY,1.1,True)
 d.path('M492 120 H519 V190 H374',GREY,1.1)
 d.text(346,211,'Missing evidence → test; failed evidence → respond and retest.',10.1,GREY)
 d.text(17,249,'Review may publish the claim. Only current reproduced evidence permits its declared use.',10.2,INK,anchor='start')
 return d

def concept_c():
 d=Drawing(270)
 d.text(15,17,'Verify before build',12.4,INK,bold=True,anchor='start')
 d.text(635,17,'A reproduction loop at the point of reliance',10.4,GREY,anchor='end',serif=True,italic=True)
 d.paper(34,62,41,51);d.text(55,137,'External claim',11.3,bold=True);d.text(55,152,'Recipe + expected result',9.2,GREY)
 d.path('M87 88 H177',arrow=True);d.text(132,57,'Agent declares',9.8,BLUE);d.text(132,70,'foundation',9.8,BLUE,bold=True)
 d.run(216,88);d.text(216,137,'Run reproduction',11.2,bold=True);d.text(216,152,'Fresh conditions',9.3,GREY)
 d.path('M253 88 H288',arrow=True)
 # A decision diamond makes comparison an explicit verifier function.
 d.path('M332 52 L371 88 L332 124 L293 88 Z',INK,1.1)
 d.text(332,85,'Outputs',10.7,bold=True);d.text(332,100,'match?',10.7,bold=True)
 d.text(332,145,'Verifier',11.2,bold=True)
 d.path('M374 88 H470',arrow=True);d.text(392,71,'pass',9.3,BLUE)
 d.paper(418,58,29,39,True)
 d.gate(489,88);d.text(489,137,'Executor gate',11.2,bold=True);d.text(489,152,'Current pass required',9.3,GREY)
 d.path('M473 88 H554',arrow=True);d.network(590,88)
 d.text(590,137,'New experiment',11.2,bold=True);d.text(590,152,'May start',9.3,GREY)
 d.path('M332 126 V189 H163 V112 H179',GREY,1.1,True)
 d.text(341,177,'fail',9.5,GREY,anchor='start')
 d.path('M489 120 H543 V189 H332',GREY,1.1)
 d.text(552,177,'no current pass',9.5,GREY,anchor='start')
 d.text(355,211,'Blocked: test; revise and retest if needed.',11,GREY)
 d.text(15,247,'A later failed reproduction revokes the earlier pass; publication alone never opens the gate.',10.2,INK,anchor='start')
 return d

for name,draw in [('concept-a-linear-evidence',concept_a()),('concept-b-lab-roles',concept_b()),('concept-c-comparison-loop',concept_c())]:draw.save(ITER/(name+'.svg'))
# Selection is deliberately left to explicit review; candidates never overwrite
# the stable manuscript figure until a reviewed concept is selected.

def concept_d():
 """Reviewed hybrid: role ownership, separate operations, two response paths."""
 d=Drawing(275)
 d.text(15,17,'Source lab',11.4,GREY,bold=True,anchor='start')
 d.text(184,17,'Consuming lab',11.4,BLUE,bold=True,anchor='start')
 # Source artifact and declaration trigger.
 d.paper(34,75,42,51)
 d.text(55,153,'Claim + recipe',12.2,bold=True)
 d.text(55,170,'Procedure + inputs',10.8,GREY)
 d.text(55,184,'Claimed output',10.8,GREY)
 d.path('M89 101 H184',arrow=True)
 d.text(137,72,'Declared',10.6,BLUE,bold=True)
 d.text(137,85,'foundation',10.6,BLUE,bold=True)
 # Run, comparison and recording are deliberately independent operations.
 d.run(223,101)
 d.text(223,153,'Reproduce',12.2,bold=True)
 d.text(223,170,'Fresh local run',10.8,GREY)
 d.path('M260 101 H291',arrow=True)
 d.compare(342,99)
 d.text(341,153,'Verify',12.2,bold=True)
 d.text(341,170,'Compare outputs',10.8,GREY)
 d.path('M380 101 H423',arrow=True)
 d.text(401,88,'verdict',10.2,BLUE)
 # A ledger, not an eternally valid checkmark badge. All outcomes are kept.
 d.paper(432,75,41,51,blank=True)
 # The ledger records positive and negative outcomes; no permanent checkmark.
 d.path('M441 91 H463 M441 101 H463 M441 111 H457',GREY,1.2)
 d.text(452,153,'Receipt ledger',12.2,bold=True)
 d.text(452,170,'Latest attempt',10.8,GREY)
 # Boundary is small but physically interrupts the only downstream path.
 d.path('M481 101 H565',arrow=True)
 d.gate(532,101)
 d.text(532,67,'Executor gate',10.5,GREY)
 d.text(506,88,'pass',10.5,BLUE)
 # A research plot replaces the generic network glyph.
 d.path('M580 76 V124 H625',INK,1.2)
 d.path('M585 115 L595 107 L605 111 L619 88',BLUE,1.2)
 for x,y in [(585,115),(595,107),(605,111),(619,88)]:d.circle(x,y,2.2,BLUE,BLUE)
 d.text(604,153,'Downstream',12.2,bold=True)
 d.text(604,169,'experiment',12.2,bold=True)
 d.text(604,184,'May start',10.8,GREY)
 # No evidence is not a faulty recipe: route directly to a fresh reproduction.
 d.path('M532 70 V47 H223 V70',GREY,1.1,True)
 d.text(373,35,'Missing receipt: reproduce',11,GREY)
 # Failed evidence has already entered the ledger. It blocks use and leaves
 # the choice to diagnose, revise/retest or stop with the agent.
 d.path('M532 133 H549 V213 H176 V121 H188',GREY,1.1,True)
 d.text(362,235,'Failed receipt: diagnose; revise and retest, or stop.',11,GREY)
 d.text(15,264,'A later failed reproduction revokes earlier authorization.',11,BLUE,anchor='start')
 return d
concept_d().save(ITER/'concept-d-reviewed-loop.svg')

def concept_e():
 """Final polish after independent review: agent actions are explicit."""
 d=concept_d()
 d.p=[s.replace('Missing receipt: reproduce','Missing receipt: agent requests reproduction')
       .replace('Failed receipt: diagnose; revise and retest, or stop.','Failed receipt: agent diagnoses, revises / retests, or stops.')
       .replace('Latest attempt','Latest verdict') for s in d.p]
 return d
concept_e().save(ITER/'concept-e-final-polish.svg')
# Reviewed selection: concept E is the stable manuscript figure.
concept_e().save(ROOT/'figure1.svg')
