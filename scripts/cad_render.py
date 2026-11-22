"""Small orthographic CAD renderer used by render_exploded.py. Requires NumPy, Numba, Pillow and SciPy."""
from pathlib import Path
import os,json,math
ROOT=Path(__file__).resolve().parent.parent
os.environ['XDG_CACHE_HOME']=str(ROOT/'.cache')
os.environ['NUMBA_CACHE_DIR']=str(ROOT/'.cache/numba')
import numpy as np
from numba import njit
from PIL import Image,ImageDraw,ImageFilter,ImageFont
from scipy.spatial import ConvexHull

WORK=ROOT/'build/illustrations'
OUT=WORK
OUT.mkdir(parents=True,exist_ok=True)
scene=None
report=None

@njit(cache=True)
def draw_triangles(screen, intensities, colors, visible, width, height):
    pixels=np.full((height,width,4),255,dtype=np.uint8)
    pixels[:,:,3]=0
    depth=np.full((height,width),-1e30,dtype=np.float32)
    for i in range(len(screen)):
        if not visible[i]:continue
        a,b,c=screen[i]
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-9:continue
        x0=max(0,int(math.floor(min(a[0],b[0],c[0]))))
        x1=min(width,int(math.ceil(max(a[0],b[0],c[0]))))
        y0=max(0,int(math.floor(min(a[1],b[1],c[1]))))
        y1=min(height,int(math.ceil(max(a[1],b[1],c[1]))))
        for y in range(y0,y1):
            py=y+.5
            for x in range(x0,x1):
                px=x+.5
                wa=((b[1]-c[1])*(px-c[0])+(c[0]-b[0])*(py-c[1]))/den
                wb=((c[1]-a[1])*(px-c[0])+(a[0]-c[0])*(py-c[1]))/den
                wc=1-wa-wb
                if wa < -1e-7 or wb < -1e-7 or wc < -1e-7:continue
                z=wa*a[2]+wb*b[2]+wc*c[2]
                if z<=depth[y,x]:continue
                depth[y,x]=z
                for k in range(3):pixels[y,x,k]=min(255,max(0,int(colors[i,k]*intensities[i,0]+intensities[i,1])))
                pixels[y,x,3]=255
    return pixels

def render(name,eye,categories=None,width=2600,height=1700,shadow=True):
    mask=np.ones(len(scene['groups']),dtype=bool)
    if categories:
        ids=[i for i,p in enumerate(report['parts']) if p['category'] in categories]
        mask=np.isin(scene['groups'],ids)
    tris=scene['triangles'][mask].astype(np.float64)
    normals=scene['normals'][mask].astype(np.float64)
    colors=scene['colors'][mask]
    eye=np.array(eye,dtype=float);eye/=np.linalg.norm(eye)
    world_up=np.array([0,0,1] if abs(eye[2])<.999 else [0,1,0],dtype=float)
    right=np.cross(world_up,eye);right/=np.linalg.norm(right);up=np.cross(eye,right)
    xyz=tris.reshape(-1,3);centre=(xyz.min(axis=0)+xyz.max(axis=0))/2
    projected=np.stack([(xyz-centre)@right,(xyz-centre)@up,(xyz-centre)@eye],axis=-1)
    lo,hi=projected.min(axis=0),projected.max(axis=0)
    scale=min(width*.88/(hi[0]-lo[0]),height*.86/(hi[1]-lo[1]))
    mid=(lo+hi)/2
    projected[:,0]=(projected[:,0]-mid[0])*scale+width/2
    projected[:,1]=-(projected[:,1]-mid[1])*scale+height/2
    screen=projected.reshape(-1,3,3)
    light=np.array([-.4,-.7,1.3]);light/=np.linalg.norm(light)
    fill=np.array([.8,.6,1.0]);fill/=np.linalg.norm(fill)
    diffuse=.36+.5*np.maximum(0,normals@light)+.14*np.maximum(0,normals@fill)
    half=light+eye;half/=np.linalg.norm(half)
    spec=22*np.maximum(0,normals@half)**40
    intensity=np.column_stack([diffuse,spec]).astype(np.float32)
    visible=(normals@eye)>0
    overlay=Image.fromarray(draw_triangles(screen,intensity,colors,visible,width,height),'RGBA')
    bg=Image.new('RGBA',(width,height),(255,255,255,255))
    if shadow:
        ground=xyz[::6].copy();ground[:,2]=0
        gx=((ground-centre)@right-mid[0])*scale+width/2
        gy=-((ground-centre)@up-mid[1])*scale+height/2
        pts=np.column_stack([gx,gy]);hull=ConvexHull(pts)
        shadow_img=Image.new('RGBA',(width,height),(0,0,0,0));d=ImageDraw.Draw(shadow_img)
        d.polygon([tuple(x) for x in pts[hull.vertices]],fill=(70,103,94,22))
        bg.alpha_composite(shadow_img.filter(ImageFilter.GaussianBlur(width/75)))
    bg.alpha_composite(overlay)
    bg.convert('RGB').save(OUT/f'{name}.png',optimize=True)
    (WORK/f'{name}-projection.json').write_text(json.dumps({
        'eye':eye.tolist(),'right':right.tolist(),'up':up.tolist(),'centre':centre.tolist(),
        'projectedMid':mid.tolist(),'scalePxPerMm':scale,'width':width,'height':height,
        'partCategories':categories or 'all'},indent=2)+'\n')
    print(name,flush=True)

def load_scene(name):
    global scene,report
    scene=np.load(WORK/(name+'.npz'))
    report=json.loads((WORK/(name+'.json')).read_text())

