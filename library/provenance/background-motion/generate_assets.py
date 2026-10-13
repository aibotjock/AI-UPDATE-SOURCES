#!/usr/bin/env python3
"""Generate 200 original, reusable 16:9 cloud-AI-show graphics."""
from pathlib import Path
import math, random, json, hashlib, html

ROOT=Path(__file__).resolve().parent
W,H=1920,1080
NAVY='#061423'; NAVY2='#0c273d'; CYAN='#53d5ec'; GOLD='#e5bb69'; WHITE='#eaf7ff'; MUTED='#6d8ba5'
RNG=random.Random(241013)

def esc(s): return html.escape(str(s),quote=True)
def fmt(x): return f'{x:.2f}'
def path(d,c=CYAN,sw=2,op=.5,fill='none',extra=''):
 return f'<path d="{d}" fill="{fill}" stroke="{c}" stroke-width="{sw}" opacity="{op}" {extra}/>'
def line(x1,y1,x2,y2,c=CYAN,sw=2,op=.5,extra=''):
 return f'<line x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}" stroke="{c}" stroke-width="{sw}" opacity="{op}" {extra}/>'
def circle(x,y,r,c=CYAN,sw=2,op=.5,fill='none',extra=''):
 return f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}" fill="{fill}" stroke="{c}" stroke-width="{sw}" opacity="{op}" {extra}/>'
def rect(x,y,w,h,c=CYAN,sw=2,op=.5,fill='none',rx=0,extra=''):
 return f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="{rx}" fill="{fill}" stroke="{c}" stroke-width="{sw}" opacity="{op}" {extra}/>'
def poly(points,c=CYAN,sw=2,op=.5,fill='none'):
 return f'<polygon points="{" ".join(f"{fmt(x)},{fmt(y)}" for x,y in points)}" stroke="{c}" stroke-width="{sw}" fill="{fill}" opacity="{op}"/>'
def dots(points,r=3,c=CYAN,op=.65): return ''.join(circle(x,y,r,c,0,op,c) for x,y in points)
def wave(y,amp,period,start=0,end=1920,phase=0,step=18):
 pts=[(x,y+amp*math.sin(x/period+phase)) for x in range(start,end+1,step)]
 return 'M '+' L '.join(f'{fmt(x)} {fmt(y)}' for x,y in pts)
def title_markup(title,description,transparent=False):
 return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1920" height="1080" viewBox="0 0 1920 1080" role="img" aria-labelledby="title desc"><title id="title">{esc(title)}</title><desc id="desc">{esc(description)} Original artwork, CC BY 4.0. Attribution: AI Update Sources.</desc><defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="{NAVY}"/><stop offset="1" stop-color="{NAVY2}"/></linearGradient><radialGradient id="soft"><stop stop-color="{CYAN}" stop-opacity=".13"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient><radialGradient id="quiet"><stop stop-color="#061423" stop-opacity=".40"/><stop offset=".55" stop-color="#061423" stop-opacity=".25"/><stop offset="1" stop-color="#061423" stop-opacity="0"/></radialGradient><linearGradient id="ribbon"><stop stop-color="{CYAN}"/><stop offset=".6" stop-color="{WHITE}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient></defs>'''+('' if transparent else f'<rect width="1920" height="1080" fill="url(#bg)"/>')
def central_mask():
 # A dark, softly delimited writing field keeps foreground narration and figures legible.
 return '<ellipse cx="960" cy="540" rx="740" ry="410" fill="url(#quiet)"/>'
def cloud(x,y,s=1,op=.35):
 return f'<g transform="translate({x},{y}) scale({s})" opacity="{op}">'+path('M 0 90 C -28 90 -44 70 -40 50 C -36 27 -15 17 6 22 C 14 -13 60 -21 80 6 C 98 -6 127 2 135 22 C 162 13 183 34 180 57 C 180 78 160 91 137 90 Z',CYAN,2,1)+'</g>'

BACKGROUND_FAMILIES=[
 ('constellation','Perimeter constellation','Peripheral network; open center for talking points.'),
 ('cloud','Cloud topology','Cloud service silhouettes connected without depicting real infrastructure.'),
 ('tokenrails','Token routing rails','Routing paths for model-selection explanations; no factual architecture implied.'),
 ('matrix','Matrix wave','Abstract matrix waves for benchmark introductions.'),
 ('orbits','Offset orbital field','Peripheral halo composition for company or model introductions.'),
 ('contours','Signal contour map','Abstract contour lines; not real measurements.'),
 ('architecture','Architecture grid','Perspective grids for cloud platform and tool discussions.'),
 ('windows','Data window cluster','Empty window motifs framing screenshots or quotations.'),
 ('paths','Evidence pathways','Stylized citation and evidence pathways framing the canvas.'),
 ('ribbons','Neural ribbon study','Interwoven ribbons for reasoning and model-comparison segments.'),
 ('ports','Service port map','Abstract service node arrangement with no provider claims.'),
 ('pulses','Latency pulse field','Decorative pulse lines; never label as measured latency.'),
 ('attention','Attention particle field','Peripheral particle fields for focus and attention explanation.'),
 ('documents','Document horizon','Abstract page motifs for research and long-context sections.'),
 ('prisms','Multimodal prism field','Geometric mixed-media motifs for multimodal capabilities.'),
 ('landscape','Evaluation landscape','Abstract topographic frame; not benchmark data.'),
 ('ledger','Cost ledger framework','Empty bookkeeping motifs for price and task-cost sections.'),
 ('audio','Narration envelope','Decorative waveform framing; not a captured voice.'),
 ('layers','Reasoning layer stack','Empty layer stacks for tool, model, and system distinctions.'),
 ('lightpaths','Lightpath corridors','Soft luminous routes for announcements and chapter transitions.'),
]
VARIANTS=['Northwest balance','Eastward sweep','Southern horizon','Split perimeter','Diagonal counterweight']

def background(fam,v):
 s=[]; seed=random.Random(1000+100*BACKGROUND_FAMILIES.index(next(z for z in BACKGROUND_FAMILIES if z[0]==fam))+v)
 if fam=='constellation':
  bands=[(0,0,700,260),(1450,50,400,860),(0,850,1920,210),(0,0,280,1080),(1350,0,570,380)]
  x,y,w,h=bands[v]
  pts=[(x+seed.random()*w,y+seed.random()*h) for _ in range(42+v*3)]
  for i,p in enumerate(pts):
   for q in sorted(pts,key=lambda q:(p[0]-q[0])**2+(p[1]-q[1])**2)[1:4]:
    if math.dist(p,q)<230: s.append(line(*p,*q,sw=1,op=.17))
  s.append(dots(pts,2.8,op=.65)); s.append(circle(x+w*.6,y+h*.5,90+15*v,GOLD,1,.18))
 elif fam=='cloud':
  configs=[[(100,55,1.1),(420,130,.8),(1650,850,1)],[(1550,80,1.3),(1620,440,.8),(70,880,.8)],[(70,865,.9),(570,940,.65),(1550,880,1.1)],[(80,100,1),(1600,100,1),(80,820,1),(1600,820,1)],[(30,30,1.2),(340,130,.6),(1530,780,1.4)]]
  cs=configs[v]
  for x,y,z in cs:s.append(cloud(x,y,z))
  for a,b in zip(cs,cs[1:]):
   s.append(path(f'M {a[0]+70} {a[1]+80} C {a[0]+350} {a[1]+80}, {b[0]-260} {b[1]+80}, {b[0]+70} {b[1]+80}',MUTED,1,.25))
  for x,y,z in cs:s.append(dots([(x+65*z,y+51*z)],5,GOLD,.75))
 elif fam=='tokenrails':
  for j in range(8):
   yy=(70+j*20 if v in [0,4] else 910+j*18)
   if v==1: d=f'M 1710 {j*130} H {1780-j*9} V 1080'
   elif v==3: d=f'M 0 {75+j*18} H {160+j*25} V {960-j*10} H 0 M 1920 {75+j*18} H {1760-j*25} V {960-j*10} H 1920'
   else:d=f'M 0 {yy} H {380+j*30} Q {480+j*30} {yy} {540+j*30} {yy+40} H 1920'
   s.append(path(d,CYAN if j%3 else GOLD,1.5,.2+.04*(j%3)))
  for j in range(18):
   x=50+j*104;y=(108+35*math.sin(j/3+v) if v in[0,4] else 972+15*math.sin(j))
   if v==1:x,y=1775+22*math.sin(j),j*62
   if v==3:x,y=(65 if j%2 else 1840),40+j*60
   s.append(rect(x,y,26,10,WHITE,0,.45,WHITE,2))
 elif fam=='matrix':
  for j in range(14):
   yy=44+j*12 if v!=2 else 858+j*12
   amp=12+2*j
   s.append(path(wave(yy,amp,125+v*38,phase=j*.12+v),CYAN,1,.18))
  for i in range(58):
   x=i*34;y=60+55*math.sin(i*.26+v) if v!=2 else 948+55*math.sin(i*.26+v)
   s.append(circle(x,y,2+(i%3),GOLD if i%9==0 else CYAN,0,.4,CYAN))
  if v in[1,3]:s.append('<g transform="translate(1920,1080) rotate(180)">'+path(wave(100,42,210),GOLD,2,.4)+'</g>')
 elif fam=='orbits':
  cx,cy=[(40,60),(1840,480),(800,1250),(-60,600),(1850,-30)][v]
  for j in range(12):
   s.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{120+j*32}" ry="{70+j*(18+v)}" fill="none" stroke="{CYAN if j%4 else GOLD}" stroke-width="{1 if j%4 else 2}" opacity="{.12+.02*(j%3)}" transform="rotate({-35+v*18} {cx} {cy})"/>')
  s.append(circle(cx,cy,510,CYAN,0,.4,'url(#soft)'))
 elif fam=='contours':
  for j in range(18):
   x=-90+j*18 if v in[0,3] else 1640+j*18
   pts=[(x+40*math.sin(y/(80+v*20)+j*.1)+j*4*math.sin(y/180),y) for y in range(-20,1101,20)]
   s.append(path('M '+' L '.join(f'{fmt(a)} {fmt(b)}' for a,b in pts),GOLD if j%6==0 else CYAN,1,.2))
  if v in[2,4]:s.append('<g transform="rotate(90 960 540)">'+path(wave(450,100,300),CYAN,1,.2)+'</g>')
 elif fam=='architecture':
  vanish=[(960,400),(600,520),(1250,300),(960,800),(1450,600)][v]
  vx,vy=vanish
  for x in range(-1200,3120,160):s.append(line(x,1080,vx,vy,MUTED,1,.15))
  for j in range(10):
   yy=vy+(1080-vy)*(j/10)**2
   s.append(line(0,yy,1920,yy,CYAN,1,.12))
  s.append(path(f'M 0 1050 H 320 V 1000 H 680 V 1018 H 1400 V 982 H 1920',GOLD,2,.5))
 elif fam=='windows':
  positions=[[(60,60),(360,110),(1540,865)],[(1530,85),(1640,355),(1600,800)],[(40,850),(510,880),(1310,900)],[(35,150),(55,700),(1600,150),(1620,680)],[(70,100),(250,240),(1500,790)]][v]
  for j,(x,y) in enumerate(positions):
   ww=210+30*(j%2);hh=110+15*j
   s.append(rect(x,y,ww,hh,CYAN,1,.28,rx=12));s.append(line(x,y+28,x+ww,y+28,MUTED,1,.25));s.append(dots([(x+16+k*13,y+15) for k in range(3)],2,GOLD,.7))
   for k in range(3):s.append(line(x+20,y+47+k*17,x+ww-30-k*22,y+47+k*17,MUTED,2,.27))
 elif fam=='paths':
  ytop=80+v*12; ybot=995-v*13
  routes=[f'M 60 {ytop} H {380+v*55} Q 530 {ytop} 530 {ytop+60} V 240',f'M 1860 {ybot} H {1500-v*65} Q 1350 {ybot} 1350 {ybot-60} V 840']
  if v==3:routes += ['M 60 480 H 160 V 620 H 80','M 1860 420 H 1780 V 600 H 1860']
  for j,d in enumerate(routes):s.append(path(d,GOLD if j else CYAN,3,.5,extra='stroke-linecap="round"'))
  for x,y in[(60,ytop),(530,240),(1860,ybot),(1350,840)]:s.append(circle(x,y,11,WHITE,1,.6));s.append(circle(x,y,4,CYAN,0,.7,CYAN))
 elif fam=='ribbons':
  for j in range(7):
   yy=110+j*9 if v!=2 else 925+j*10
   d=wave(yy,40+v*12,140+v*22,phase=j*.35+v)
   s.append(path(d,'url(#ribbon)',2,.25))
  if v in[1,3,4]:s.append('<g transform="translate(1920,1080) rotate(180)">'+path(wave(100,50,160),GOLD,2,.22)+'</g>')
 elif fam=='ports':
  for j in range(8+v):
   ang=(j/(8+v))*2*math.pi+v*.17
   x=960+850*math.cos(ang);y=540+450*math.sin(ang)
   s.append(rect(x-22,y-22,44,44,CYAN,1,.55,rx=9))
   s.append(circle(x,y,5,GOLD,0,.65,GOLD))
   if j:
    pa=(j-1)/(8+v)*2*math.pi+v*.17
    px=960+850*math.cos(pa);py=540+450*math.sin(pa)
    s.append(path(f'M {px} {py} Q {960+700*math.cos((pa+ang)/2)} {540+390*math.sin((pa+ang)/2)} {x} {y}',MUTED,1,.22))
 elif fam=='pulses':
  for j in range(5):
   y=(60+j*30 if v in[0,1] else 900+j*25)
   d=f'M 0 {y} H {130+v*90} l 18 -16 l 18 32 l 18 -64 l 18 96 l 18 -48 H {780+v*70} l 15 -28 l 18 55 l 16 -27 H 1920'
   s.append(path(d,GOLD if j==2 else CYAN,1.7,.3))
  if v in[1,4]:s.append('<g transform="translate(1900,0) rotate(90)">'+path('M 0 0 H 300 l 10 -20 l 10 40 l 10 -20 H 1080',CYAN,2,.4)+'</g>')
 elif fam=='attention':
  for j in range(210):
   angle=seed.random()*2*math.pi
   radius=1+seed.random()*.38
   x=960+800*radius*math.cos(angle+v*.5);y=540+415*radius*math.sin(angle+v*.5)
   s.append(circle(x,y,1+seed.random()*2.5,GOLD if j%13==0 else CYAN,0,.15+seed.random()*.35,CYAN))
  for j in range(5):s.append(f'<ellipse cx="960" cy="540" rx="{760+j*35}" ry="{400+j*18}" fill="none" stroke="{CYAN}" stroke-width="1" opacity=".1" transform="rotate({v*3} 960 540)"/>')
 elif fam=='documents':
  for j in range(7):
   xx=[50,1580,120,40,1530][v]+j*(50 if v in[0,2,3] else 24)
   yy=[60,90,910,780,760][v]+j*(-10 if v==2 else 16)
   s.append('<g transform="rotate('+str(-18+v*8+j*3)+f' {xx+55} {yy+65})">'+rect(xx,yy,100,130,CYAN,1,.22,rx=4)+''.join(line(xx+15,yy+25+k*15,xx+75,yy+25+k*15,MUTED,1,.22)for k in range(5))+'</g>')
 elif fam=='prisms':
  positions=[[(100,130),(1730,940)],[(1700,90),(1800,760)],[(100,950),(960,1040),(1650,930)],[(120,120),(1700,100),(110,950),(1800,980)],[(230,150),(1660,890)]][v]
  for j,(x,y)in enumerate(positions):
   r=70+15*j
   pts=[(x+r*math.cos(k*math.pi/3+v*.2),y+r*math.sin(k*math.pi/3+v*.2))for k in range(6)]
   s.append(poly(pts,CYAN,1,.35));s.append(poly(pts[::2],GOLD,1,.4));s.append(line(x,y,*pts[j%6],WHITE,1,.3))
 elif fam=='landscape':
  for j in range(14):
   y=940+j*7 if v!=0 else 80+j*8
   d='M '+ ' L '.join(f'{x} {fmt(y+35*math.sin(x/(140+v*20)+j*.17)+15*math.cos(x/71))}'for x in range(0,1921,16))
   s.append(path(d,GOLD if j%5==0 else CYAN,1,.25))
  if v in[1,4]:s.append('<g transform="translate(1920,1080) rotate(180)">'+path(wave(80,60,200),CYAN,2,.25)+'</g>')
 elif fam=='ledger':
  xx=80 if v in[0,3]else 1550; yy=90 if v in[0,1,4]else 850
  for j in range(4):
   x=xx+j*14;y=yy+j*12
   s.append(rect(x,y,250,150,CYAN,1,.2,rx=6))
  for j in range(5):s.append(line(xx+20,yy+30+j*22,xx+230,yy+30+j*22,MUTED,1,.4))
  for j in range(3):s.append(line(xx+80+j*60,yy+20,xx+80+j*60,yy+130,MUTED,1,.3))
  s.append(circle(1820 if xx<500 else 110,950 if yy<500 else 130,42,GOLD,1,.4))
 elif fam=='audio':
  for j in range(96):
   x=16+j*20
   amp=(14+42*abs(math.sin(j*.18+v)))*(1+.2*math.sin(j*.42))
   yy=970 if v in[0,2,4] else 90
   s.append(line(x,yy-amp,x,yy+amp,GOLD if j%9==0 else CYAN,2,.28))
  if v in[3,4]:s.append('<g transform="translate(1920,1080) rotate(180)">'+path(wave(65,18,83),CYAN,1,.23)+'</g>')
 elif fam=='layers':
  xx=[50,1530,100,20,1520][v];yy=[80,100,880,700,760][v]
  for j in range(6):
   x=xx+j*18;y=yy+j*11
   s.append(poly([(x,y),(x+210,y-40),(x+290,y+20),(x+80,y+60)],GOLD if j==5 else CYAN,1,.23))
  s.append(line(xx+80,yy+60,xx+180,yy+180,MUTED,1,.3))
 elif fam=='lightpaths':
  for j in range(12):
   if v==0:d=f'M -100 {90+j*12} C 500 {160+j*12} 1250 {-180+j*12} 2010 {50+j*12}'
   elif v==1:d=f'M 1730 -100 C {1690+j*12} 250 {1890+j*12} 700 1770 1180'
   elif v==2:d=f'M -100 {1010-j*14} C 560 {890-j*14} 1300 {1160-j*14} 2010 {940-j*14}'
   elif v==3:d=f'M -100 {90+j*8} C 180 40 260 180 180 1180 M 2010 {980-j*8} C 1740 960 1640 800 1760 -100'
   else:d=f'M -100 {60+j*10} C 780 -100 960 10 1920 {160-j*8} M -100 {1040-j*10} C 780 900 960 1080 1920 {940+j*8}'
   s.append(path(d,'url(#ribbon)',1.4,.22))
 return ''.join(s)+central_mask()

MOTION_FAMILIES=[
 ('focus-ring','Focus-ring pulse','Focus attention on a highlighted screenshot region.',3.0),
 ('brackets','Evidence brackets','Reveal brackets around cited source material.',2.0),
 ('panel-wipe','Source-panel wipe','Transition or reveal a source panel without fabricated content.',2.4),
 ('scan','Evidence scanline','Brief scanning gesture over an existing source screenshot.',3.0),
 ('token-trail','Token trail','Decorative cloud-request movement between interface regions.',4.0),
 ('divider','Comparison divider','Introduce a side-by-side comparison area.',2.0),
 ('curtain','Transition curtain','Brief transition between chapters or models.',1.5),
 ('constellation-build','Network connections','Reveal abstract connection structure.',4.0),
 ('pointer','Annotation path','Animated pointer path to support a factual callout.',2.5),
 ('focus-frame','Focus frame','Expand or settle a focus boundary around content.',2.4),
 ('pin','Source pin','Source annotation cue; supply text separately.',2.0),
 ('timeline','Timeline sweep','Indicate chronological progression without invented dates.',3.5),
 ('underline','Emphasis underline','Animated emphasis below a statement.',1.5),
 ('connection','Connection trace','Trace a relationship between two actual labeled elements.',3.5),
 ('orbit','Orbital transition','Abstract orbital motion for a company/topic transition.',4.0),
 ('waveform','Narration ambience','Decorative audio ambience; not an actual audio waveform.',5.0),
 ('grid','Grid drift','Subtle peripheral grid motion behind content.',6.0),
 ('corner','Corner attention cue','Subtle chapter-boundary attention pulse.',3.0),
 ('completion','Completion marker','Animate a neutral completion indicator; requires actual supporting context.',2.0),
 ('ribbon','Evidence ribbon','Animate a perimeter ribbon around cited content.',4.5),
]
MOTION_VARIANTS=['Center focus','Left evidence','Right evidence','Lower detail','Wide comparison']
EXPORT='Animate in a modern browser. To use in PowerPoint/video, render frames or record a timed browser playback; SVG import may be static. Transparent source canvas; export alpha as WebM/ProRes 4444 when needed. Preserve animation duration and 1920x1080 aspect ratio.'

def anim(attr,values,dur,repeat=True,extra=''):
 return f'<animate attributeName="{attr}" values="{values}" dur="{dur}s" repeatCount="{"indefinite" if repeat else "1"}" {extra}/>'
def atype(kind,values,dur,extra=''):
 return f'<animateTransform attributeName="transform" type="{kind}" values="{values}" dur="{dur}s" repeatCount="indefinite" {extra}/>'
def group(s,animation,extra=''):return f'<g {extra}>{animation}{s}</g>'
def motion(fam,v,d):
 cx,cy=[(960,540),(470,500),(1450,500),(960,810),(960,540)][v]
 bw=[550,650,650,850,1380][v];bh=[340,480,480,220,640][v]
 x=cx-bw/2;y=cy-bh/2
 s=[]
 if fam=='focus-ring':
  for j in range(3 if v<4 else 2):
   rr=95+v*12+j*24
   s.append(f'<circle cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="{CYAN if j else GOLD}" stroke-width="{3 if j else 4}" opacity=".65">'+anim('r',f'{rr};{rr+35};{rr}',d)+anim('opacity','.2;.75;.2',d)+'</circle>')
  if v==4:s.append(rect(x,y,bw,bh,CYAN,1,.35,rx=24))
 elif fam=='brackets':
  for px,py,sx,sy in[(x,y,1,1),(x+bw,y,-1,1),(x,y+bh,1,-1),(x+bw,y+bh,-1,-1)]:
   pp=path(f'M {px+sx*58} {py} H {px} V {py+sy*58}',CYAN,4,.85,extra='stroke-linecap="round" stroke-dasharray="116" stroke-dashoffset="0"')
   s.append(group(pp,anim('opacity','.15;1;1;.15',d)))
  if v in[1,3]:s.append(line(x,y+bh+18,x+bw,y+bh+18,GOLD,1,.4))
 elif fam=='panel-wipe':
  # Low-opacity fill deliberately reveals underlying genuine media.
  pp=rect(x,y,bw,bh,CYAN,1,.12,CYAN,10)
  s.append(group(pp,anim('opacity','0;1;1;0',d)+atype('translate',f'{-bw} 0;0 0;0 0;{bw} 0',d)))
  s.append(group(line(x,y,x,y+bh,GOLD,3,.8),atype('translate',f'0 0;{bw} 0;{bw} 0;0 0',d)))
 elif fam=='scan':
  s.append(rect(x,y,bw,bh,CYAN,1,.25,rx=8))
  pp=line(x,y,x+bw,y,CYAN,3,.8)+rect(x,y,bw,22,CYAN,0,.09,CYAN)
  s.append(group(pp,atype('translate',f'0 0;0 {bh};0 {bh};0 0',d)))
  s.append(dots([(x,y),(x+bw,y+bh)],4,GOLD,.6))
 elif fam=='token-trail':
  routes=[f'M 240 540 C 600 280 1200 800 1680 540',f'M 220 220 C 650 220 640 850 1700 850',f'M 250 880 C 900 880 980 160 1650 160',f'M 120 920 H 560 Q 650 920 650 820 V 180 H 1720',f'M 180 540 H 760 Q 960 200 1160 540 H 1740']
  s.append(path(routes[v],CYAN,1,.22))
  for j in range(7):
   s.append(f'<circle r="{4+(j%3)}" fill="{GOLD if j%3==0 else CYAN}" opacity=".8"><animateMotion dur="{d}s" begin="{-j*d/7}s" repeatCount="indefinite" path="{routes[v]}"/></circle>')
 elif fam=='divider':
  if v in[0,1,2,4]:
   xx=[960,680,1240,960,960][v]
   s.append(f'<line x1="{xx}" y1="120" x2="{xx}" y2="960" stroke="{CYAN}" stroke-width="2" opacity=".6">'+anim('y2','120;960;960',d)+'</line>')
   s.append(group(circle(xx,540,16,GOLD,2,.7),anim('opacity','0;.8;.8;0',d)))
   if v==4:s.append(line(160,280,1760,280,WHITE,1,.3))
  else:s.append(f'<line x1="200" y1="650" x2="1720" y2="650" stroke="{CYAN}" stroke-width="2">'+anim('x2','200;1720;1720',d)+'</line>')
 elif fam=='curtain':
  if v<3:
   ww=320+v*160
   pp=rect(-ww,0,ww,1080,NAVY,0,.94,NAVY)+line(-4,0,-4,1080,GOLD,4,.8)
   s.append(group(pp,atype('translate',f'0 0;{1920+ww} 0',d)))
  elif v==3:
   s.append(group(rect(0,-260,1920,260,NAVY,0,.95,NAVY),atype('translate','0 0;0 1340',d)))
  else:
   for j in range(4):
    s.append(group(rect(j*480,-1080,480,1080,NAVY,0,.95,NAVY),atype('translate','0 0;0 2160',d,extra=f'begin="{j*.12}s"')))
 elif fam=='constellation-build':
  pts=[(220+j*190,130+60*math.sin(j+v))for j in range(9)] if v%2==0 else[(1700+40*math.sin(j+v),90+j*110)for j in range(9)]
  for i,(a,b)in enumerate(zip(pts,pts[1:])):
   s.append(group(line(*a,*b,CYAN,2,.65),anim('opacity','0;0;1;1;0',d,extra=f'begin="{i*.12}s"')))
  s.append(group(dots(pts,5,GOLD,.8),anim('opacity','.25;.9;.9;.25',d)))
 elif fam=='pointer':
  end=(cx,cy);start=(cx-180-v*35,cy+150)
  s.append(path(f'M {start[0]} {start[1]} Q {cx-160} {cy} {cx} {cy}',GOLD,3,.8,extra='stroke-dasharray="420"'))
  s.append(group(poly([(cx-16,cy-10),(cx,cy),(cx-19,cy+6)],GOLD,0,1,GOLD),anim('opacity','.3;1;1;.3',d)))
  s.append(group(circle(cx,cy,24,CYAN,2,.6),anim('opacity','0;.8;0',d)))
 elif fam=='focus-frame':
  frame=rect(-bw/2,-bh/2,bw,bh,CYAN,3,.75,rx=18)+rect(-bw/2-9,-bh/2-9,bw+18,bh+18,GOLD,1,.3,rx=24)
  s.append(f'<g transform="translate({cx},{cy})">'+group(frame,atype('scale','1.12 1.12;1 1;1 1;1.12 1.12',d))+'</g>')
 elif fam=='pin':
  pp=circle(cx,cy,14,GOLD,3,.9)+line(cx,cy+14,cx,cy+70,CYAN,2,.7)+rect(cx-50,cy+80,100,8,CYAN,0,.4,CYAN,4)
  s.append(group(pp,atype('translate','0 -20;0 0;0 0;0 -20',d)+anim('opacity','.1;1;1;.1',d)))
  if v==4:s.append(f'<circle cx="{cx}" cy="{cy}" r="36" fill="none" stroke="{CYAN}" stroke-width="1" opacity=".3">'+anim('r','18;48;18',d)+'</circle>')
 elif fam=='timeline':
  yy=[880,230,540,950,820][v]
  s.append(line(220,yy,1700,yy,CYAN,2,.3))
  for j in range(5+v):s.append(circle(220+j*1480/(4+v),yy,5,GOLD,1,.7))
  s.append(group(circle(220,yy,10,CYAN,0,.9,CYAN),atype('translate','0 0;1480 0',d)))
 elif fam=='underline':
  yy=cy+bh*.4
  s.append(f'<path d="M {x} {yy} Q {cx} {yy+12+v*3} {x+bw} {yy}" fill="none" stroke="{GOLD}" stroke-width="{4+v}" stroke-linecap="round" stroke-dasharray="{bw*1.05}" stroke-dashoffset="0">'+anim('stroke-dashoffset',f'{bw*1.05};0;0',d)+'</path>')
 elif fam=='connection':
  a=(260,200+v*135);b=(1660,850-v*140)
  dd=f'M {a[0]} {a[1]} C 600 {a[1]} 1320 {b[1]} {b[0]} {b[1]}'
  s.append(path(dd,CYAN,2,.45,extra='stroke-dasharray="8 12"'))
  s.append(circle(*a,12,GOLD,2,.8));s.append(circle(*b,12,GOLD,2,.8))
  s.append(f'<circle r="7" fill="{WHITE}"><animateMotion path="{dd}" dur="{d}s" repeatCount="indefinite"/></circle>')
 elif fam=='orbit':
  r=100+v*45
  s.append(f'<g transform="translate({cx},{cy})">'+group(path(f'M {-r} 0 A {r} {r*.6} 0 1 1 {r} 0 A {r} {r*.6} 0 1 1 {-r} 0',CYAN,2,.5)+circle(r,0,7,GOLD,0,.85,GOLD),atype('rotate','0;360',d))+'</g>')
  if v==4:s.append(circle(cx,cy,r+38,GOLD,1,.2))
 elif fam=='waveform':
  yy=[980,100,920,1040,80][v]
  for j in range(64):
   xx=300+j*21;hh=10+22*abs(math.sin(j*.27+v))
   s.append(f'<rect x="{xx}" y="{yy-hh}" width="3" height="{hh*2}" rx="1.5" fill="{CYAN if j%8 else GOLD}" opacity=".35">'+anim('opacity','.18;.6;.18',d,extra=f'begin="{-j*.09}s"')+anim('height',f'{hh};{hh*2};{hh}',d,extra=f'begin="{-j*.09}s"')+'</rect>')
 elif fam=='grid':
  pp=''.join(line(90+j*36,0,90+j*36,1080,CYAN,1,.12)for j in range(7))+''.join(line(70,60+j*48,350,60+j*48,CYAN,1,.12)for j in range(21))
  if v==0:s.append(group(pp,atype('translate','0 0;0 48',d)))
  elif v==1:s.append(group(pp,atype('translate','1500 0;1500 -48',d)))
  elif v==2:s.append('<g transform="rotate(90 960 540)">'+group(pp,atype('translate','0 0;0 48',d))+'</g>')
  elif v==3:s.append(group(pp,atype('translate','0 0;36 0',d)));s.append(group(pp,atype('translate','1500 0;1464 0',d)))
  else:s.append('<g transform="rotate(14 960 540)">'+group(pp,atype('translate','0 0;36 48',d))+'</g>')
 elif fam=='corner':
  coords=[(70,70,1,1),(1850,70,-1,1),(1850,1010,-1,-1),(70,1010,1,-1),(70,70,1,1)][v]
  xx,yy,sx,sy=coords
  for j in range(3):
   dd=f'M {xx} {yy+sy*(70+j*15)} V {yy} H {xx+sx*(70+j*15)}'
   s.append(group(path(dd,CYAN if j else GOLD,3,.7),anim('opacity','.15;.8;.15',d,extra=f'begin="{-j*.25}s"')))
  if v==4:s.append(group(path('M 1850 940 V 1010 H 1780',CYAN,3,.6),anim('opacity','.8;.15;.8',d)))
 elif fam=='completion':
  if v in[0,1,2]:
   pp=circle(cx,cy,46,CYAN,2,.55)+path(f'M {cx-20} {cy} l 15 15 l 29 -34',GOLD,5,.95,extra='stroke-linecap="round" stroke-linejoin="round"')
  elif v==3:pp=rect(cx-100,cy-25,200,50,CYAN,2,.5,rx=25)+circle(cx+65,cy,10,GOLD,0,.8,GOLD)
  else:pp=path(f'M {cx-180} {cy} H {cx+180}',CYAN,4,.6)+circle(cx+180,cy,15,GOLD,2,.8)
  s.append(group(pp,anim('opacity','0;1;1;0',d)))
 elif fam=='ribbon':
  routes=[wave(75,23,180),wave(1000,24,240),f'M 75 0 C 140 350 5 650 85 1080',f'M 1830 0 C 1780 350 1900 650 1840 1080',f'M 30 160 Q 30 30 160 30 H 1760 Q 1890 30 1890 160 V 920 Q 1890 1050 1760 1050 H 160 Q 30 1050 30 920 Z']
  dd=routes[v];s.append(path(dd,CYAN,1,.35));s.append(path(dd,GOLD,3,.7,extra='stroke-dasharray="85 2400"'))
  # Moving highlight along perimeter; content remains untouched.
  s.append(f'<circle r="5" fill="{WHITE}"><animateMotion path="{dd}" dur="{d}s" repeatCount="indefinite"/></circle>')
 return ''.join(s)

def main():
 entries=[]
 for category,families in [('backgrounds',BACKGROUND_FAMILIES),('motion-overlays',MOTION_FAMILIES)]:
  (ROOT/category).mkdir(parents=True,exist_ok=True)
  for family in families:
   fam,label,use=family[:3]
   for v in range(5):
    variant=VARIANTS[v] if category=='backgrounds' else MOTION_VARIANTS[v]
    title=f'{label} — {variant}'
    aid=f'bm-{category[:2]}-{fam}-{v+1:02d}'
    rel=f'{category}/{fam}-{v+1:02d}.svg'
    duration=family[3]+(.2*v if category=='motion-overlays' else 0) if category=='motion-overlays' else None
    desc=use+(f' Loop duration {duration:.1f} seconds. {EXPORT}' if duration else ' Use beneath foreground content; the center is intentionally quiet.')
    body=background(fam,v) if category=='backgrounds' else motion(fam,v,duration)
    data=title_markup(title,desc,category=='motion-overlays')+body+'</svg>\n'
    (ROOT/rel).write_text(data)
    entries.append({'id':aid,'title':title,'path':rel,'category':category,'tags':['cloud-ai','youtube','16:9','original',fam,'navy-cyan-gold',('transparent' if category=='motion-overlays' else 'negative-space')],'intended_use':use,'dimensions':{'width':W,'height':H,'unit':'px'},'duration_seconds':duration,'origin':'original','license':'CC-BY-4.0','attribution':'AI Update Sources','transparent':category=='motion-overlays','export_guidance':EXPORT if duration else 'Import SVG directly into presentation software, or rasterize at 1920x1080 or larger.','reuse_limits':['Decorative graphics are not source evidence, actual measurements, provider logos, or factual infrastructure diagrams.','Supply verified text, data and source attribution separately.']+(['SVG SMIL animation requires browser playback; PowerPoint SVG imports may display a static frame.']if duration else []),'sha256':hashlib.sha256(data.encode()).hexdigest(),'bytes':len(data.encode())})
 (ROOT/'manifest.json').write_text(json.dumps({'collection':'Original backgrounds and motion overlays','version':'1.0.0','count':len(entries),'assets':entries},indent=2)+'\n')
 (ROOT/'README.md').write_text('''# Original backgrounds and motion overlays

200 original assets for the cloud-model AI update show: **100 static SVG backgrounds** and **100 SVG SMIL motion overlays**. All use a 1920 × 1080 viewBox. Backgrounds have quiet central space; overlays have transparent canvases. Each family has five distinct geometric compositions rather than simple color replacements.

## Reuse

- Static backgrounds can sit below benchmark charts, screenshots, model outputs, and narration cards.
- Overlays can emphasize, introduce or transition genuine source content. Keep motion away from text while it is being read.
- Artwork is illustrative only. Pulse/waveform/landscape graphics do not encode measurements. The completion animation does not establish that an evaluation passed.
- No logo, benchmark result, model output, or screenshot in this collection purports to come from a provider.
- Licensing: CC BY 4.0, attribution **AI Update Sources**. License link: https://creativecommons.org/licenses/by/4.0/

## Formats and animation

`backgrounds/*.svg`: static editable vectors. `motion-overlays/*.svg`: self-contained browser-playable SVG SMIL animations. Exact loop durations and purposes appear in `manifest.json` and each SVG description. The motion examples are intentionally cyclic and can be trimmed to a single loop; transitions should be used once, not continuously.

PowerPoint importing an SVG may show only a static frame: **native PowerPoint animation is not claimed**. Import the static graphic and apply PowerPoint-native motion, or render browser animation to a video clip. For faithful export, play the SVG at 1920 × 1080 in a compatible browser and record/capture frames at a fixed rate (e.g. 30 fps); encode the intended loop with FFmpeg. Use WebM with alpha or ProRes 4444 for transparency, or composite onto the actual slide before creating an H.264 MP4. A screen recorder may flatten alpha. Browser automation and recording tools may be unavailable in a restricted environment.

## Manifest

`manifest.json` contains IDs, titles, relative paths, dimensions, duration, category, origin, license, intended uses, reuse limits, byte sizes, and SHA-256 hashes. It is the machine-readable catalog. `generate_assets.py` reproduces all 200 SVGs deterministically. The generator and QA contact sheet are supporting files, not counted as assets.

## Verification

The collection is checked for valid XML, 200 unique file hashes, 1920 × 1080 dimensions, and animation presence in all 100 motion files. The contact sheet samples every static family and every motion family at its initial SVG frame. Initial-frame raster verification does not verify browser animation or PowerPoint export playback.
''')
 print(json.dumps({'assets':len(entries),'backgrounds':100,'motion_overlays':100,'path':str(ROOT)}))

if __name__=='__main__': main()
