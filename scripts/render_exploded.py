"""Render the released assembly as an exploded view, without changing any model.

Run with the CAD requirements plus Pillow, Numba and SciPy installed.
Purchased parts are schematic references; gear teeth and wiring are not modeled.
"""
from pathlib import Path
import json
import math
import os
import sys

ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault('XDG_CACHE_HOME', str(ROOT / '.cache'))
sys.path.insert(0, str(ROOT / 'cad'))
import cadquery as cq
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
import panels as v
import cad_render as renderer

OUT = ROOT / 'build/illustrations'
ASSETS = ROOT / 'site/solar-car-assets'
OUT.mkdir(parents=True, exist_ok=True)
shapes = cq.importers.importStep(str(ROOT / 'models/step/assembly-reference.step')).val().Solids()
assert len(shapes) == 13, 'Expected the released V2.10/BF5 assembly with reference panels.'
names = ['chassis', 'F-frame', 'F-panel', 'F1-left', 'F1-right', 'F2-left',
         'F2-right', 'R-frame', 'R-panel', 'R1-left', 'R1-right', 'R2-left', 'R2-right']
triangles, normals, colors, groups, parts = [], [], [], [], []
guides, post_labels = [], []
LIME, GRAY, BLUE = [223,236,73], [125,142,150], [29,63,117]


def add(shape, name, color, offset=(0, 0, 0)):
    vertices, faces = shape.translate(offset).tessellate(.04, .14)
    mesh = trimesh.Trimesh([[p.x,p.y,p.z] for p in vertices], faces, process=True)
    triangles.append(mesh.triangles.astype(np.float32))
    normals.append(mesh.face_normals.astype(np.float32))
    colors.append(np.tile(color, (len(faces), 1)).astype(np.float32))
    groups.append(np.full(len(faces), len(parts), dtype=np.int32))
    parts.append({'name': name, 'category': name})


for name, shape in zip(names, shapes):
    dz = 0 if name == 'chassis' else 137 if 'panel' in name else 98 if 'frame' in name else 32
    add(shape, name, BLUE if 'panel' in name else LIME if name == 'chassis' or 'frame' in name else GRAY, (0,0,dz))
    if 'left' in name or 'right' in name:
        b = shape.BoundingBox()
        x, y = (b.xmin+b.xmax)/2, (b.ymin+b.ymax)/2
        guides.append(((x,y,11.5), (x,y,b.zmin+32)))
        guides.append(((x,y,b.zmax+32), (x,y,b.zmax+93)))
        if 'left' in name:
            post_labels.append((name[:2], (x,y-3,(b.zmin+b.zmax)/2+32)))

for rear in [False, True]:
    p = v.pose(rear)
    for x in np.linspace(-24,24,9):
        add(v.assembled(v.block((x-.08,-26.5,6.805),(x+.08,26.5,6.82)),p), 'panel-grid', [105,131,157], (0,0,137))
    for y in [-13,13]:
        add(v.assembled(v.block((-26.5,y-.07,6.805),(26.5,y+.07,6.82)),p), 'panel-grid', [105,131,157], (0,0,137))
    guides.append(((p['cx'],0,p['z']+105), (p['cx'],0,p['z']+137)))

for x in [-31.5,31.5]:
    add(v.cylinder((x,-38.5,15),(x,38.5,15),1), 'axle', [135,145,150])
    for side in [-1,1]:
        off = (0,side*25,0)
        add(v.cylinder((x,side*28.5,15),(x,side*38.5,15),15),'wheel',[36,40,44],off)
        add(v.cylinder((x,side*38.5,15),(x,side*38.7,15),10),'hub',[160,172,179],off)
        add(v.cylinder((x,side*38.7,15),(x,side*39,15),3),'hub-center',[50,58,61],off)
        guides.append(((x,side*39,15), (x,side*53.5,15)))

# Explode the motor and pinion together towards the viewer, with one guide to its cradle.
mz = 12.3 + 12/math.cos(math.radians(20))
mx = -31.5 + math.sqrt(15**2 - (mz-15)**2)
motor_offset = (-35,-65,30)
add(v.cylinder((mx,-6,mz),(mx,6,mz),12),'motor',[165,177,184],motor_offset)
add(v.cylinder((mx,6,mz),(mx,18,mz),1),'motor-shaft',[105,116,123],motor_offset)
add(v.cylinder((mx,7,mz),(mx,17,mz),3),'pinion-reference',[239,174,69],motor_offset)
add(v.cylinder((-31.5,10.5,15),(-31.5,12.5,15),13),'axle-gear-reference',[239,174,69])
guides.append(((mx,-6,mz), (mx+motor_offset[0],-6+motor_offset[1],mz+motor_offset[2])))

renderer.scene = {'triangles':np.concatenate(triangles), 'normals':np.concatenate(normals),
                  'colors':np.concatenate(colors), 'groups':np.concatenate(groups)}
renderer.report = {'parts':parts}
renderer.render('exploded-base', [1.1,-1.8,.85], width=2200, height=2400, shadow=False)
p = json.loads((OUT/'exploded-base-projection.json').read_text())
im = Image.open(OUT/'exploded-base.png').convert('RGB')
draw = ImageDraw.Draw(im)
font = ImageFont.truetype('DejaVuSans.ttf', 35)
bold = ImageFont.truetype('DejaVuSans-Bold.ttf', 43)


def project(point):
    vec = np.array(point)-p['centre']
    return np.array([(vec@p['right']-p['projectedMid'][0])*p['scalePxPerMm']+p['width']/2,
                     -(vec@p['up']-p['projectedMid'][1])*p['scalePxPerMm']+p['height']/2])


for a,b in guides:
    a,b = project(a),project(b)
    length = np.linalg.norm(b-a)
    for start in np.arange(0,length,20):
        draw.line([tuple(a+(b-a)*start/length), tuple(a+(b-a)*min(start+9,length)/length)], fill='#a3ada8',width=3)

for code,point in post_labels:
    x,y = project(point)
    box = draw.textbbox((x-38,y),code,font=font)
    draw.rounded_rectangle((box[0]-9,box[1]-6,box[2]+9,box[3]+6),radius=6,fill='white')
    draw.text((x-38,y),code,fill='#202921',font=font)

# Numbers match the localized legend on the website; labels remain language-neutral.
callouts = [
    ('1',(54,-20,11),(1980,1900)),
    ('2',(31.5,-63.8,15),(1700,2280)),
    ('3',(mx-35,-71,mz+30),(230,1630)),
    ('4',(49.29,-20.5,48),(2000,1440)),
    ('5',(53,-26,126),(2000,980)),
    ('6',(40,-20,173),(1950,430)),
]
for number,point,label in callouts:
    target=project(point)
    draw.line([label,tuple(target)],fill='#626b66',width=3)
    draw.ellipse((target[0]-5,target[1]-5,target[0]+5,target[1]+5),fill='#626b66')
    x,y=label
    draw.ellipse((x-35,y-35,x+35,y+35),fill='#202921')
    draw.text((x,y-2),number,fill='white',font=bold,anchor='mm')

im.save(ASSETS/'assembly-exploded.webp',quality=94)
im.save(ROOT/'docs/assembly-exploded.png',optimize=True)
print('Exploded view generated from released STEP geometry.')
