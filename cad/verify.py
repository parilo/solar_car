"""Compare a fresh build against the released STEP geometry."""
from pathlib import Path
import argparse
import cadquery as cq
import panels as v
parser=argparse.ArgumentParser();parser.add_argument('--build',type=Path,default=Path('build'));args=parser.parse_args()
root=Path(__file__).resolve().parent.parent
files={'solar-car-chassis-v2_10':'chassis-v2_10'}
files.update({'solar-car-bf5-'+n:n for n in ['F-frame','R-frame','F1-post','F2-post','R1-post','R2-post']})
for new,old in files.items():
 a=cq.importers.importStep(str(args.build/(new+'.step'))).val()
 b=v.ground(cq.importers.importStep(str(root/'models/step'/(old+'.step'))).val())
 difference=a.cut(b).Volume()+b.cut(a).Volume()
 assert difference<1e-4,(new,difference)
 print(new,'matches release',round(difference,8),'mm3')
