"""Rebuild the published chassis and panel kit; no historical project files needed."""
from pathlib import Path
import argparse,os,json,math
os.environ.setdefault('XDG_CACHE_HOME',str(Path(__file__).resolve().parent.parent/'.cache'))
import cadquery as cq
import numpy as np
import trimesh
import chassis,frame,posts
v=frame.v

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path('build'))
    args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    checks=[];assembly=cq.Assembly(name='SolarCar');frames=[];stands=[]
    def save(shape,name,quantity):
        grounded=v.ground(shape)
        assert grounded.isValid() and len(grounded.Solids())==1,name
        cq.exporters.export(grounded,str(out/(name+'.stl')),tolerance=.01,angularTolerance=.08)
        cq.exporters.export(grounded,str(out/(name+'.step')))
        m=trimesh.load_mesh(out/(name+'.stl'))
        assert m.is_watertight and m.is_winding_consistent and len(m.split())==1,name
        checks.append({'file':name,'quantity':quantity,'volumeMm3':shape.Volume(),'sizeMm':m.extents.tolist(),'watertight':True})
        print('Built',name,flush=True)
        return grounded
    ch=chassis.build();save(ch,'solar-car-chassis-v2_10',1);assembly.add(ch.translate((0,0,7.5)),name='chassis')
    for rear in [False,True]:
        p=v.pose(rear);tag='R' if rear else 'F';f=frame.frame(p)
        fp=save(f,'solar-car-bf5-'+tag+'-frame',1);frames.append(fp.translate((35 if rear else -35,0,0)))
        assembly.add(v.assembled(f,p),name=tag+'-frame');assembly.add(v.panel(p),name=tag+'-panel-reference')
        for end in [-1,1]:
            code=tag+('1' if end<0 else '2');s=posts.lower_post(p,end);pr=save(s,'solar-car-bf5-'+code+'-post',2)
            col=['F1','F2','R1','R2'].index(code)
            for side in [-1,1]:
                stands.append(pr.translate((-30+20*col,side*10,0)))
                assembly.add(frame.to_world(s,p,end,side*20.5),name=code+('-left' if side<0 else '-right'))
    for name,shapes in [('frames',frames),('posts',stands)]:
        cq.exporters.export(cq.Compound.makeCompound(shapes),str(out/('solar-car-bf5-'+name+'.stl')),tolerance=.01,angularTolerance=.08)
    assembly.export(str(out/'assembly-reference.step'))
    (out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')

if __name__=='__main__':main()
