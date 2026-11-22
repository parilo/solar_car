"""V2.10 chassis, one piece including the motor bed. Dimensions in mm."""
import math
import cadquery as cq

def box(a,b):return cq.Solid.makeBox(*[b[i]-a[i] for i in range(3)],cq.Vector(*a))

def round_vertical(shape,r):
 return shape.fillet(r,cq.Workplane(obj=shape).edges('|Z').vals())

def round_top(shape,z,r):
 edges=[e for e in shape.Edges() if abs(e.BoundingBox().zmin-z)<1e-6 and abs(e.BoundingBox().zmax-z)<1e-6]
 assert edges
 return shape.fillet(r,edges)

def xy(points,z,h):
 wire=cq.Wire.makePolygon([cq.Vector(x,y,z) for x,y in points],close=True)
 return cq.Solid.extrudeLinear(wire,[],cq.Vector(0,0,h))

def xz(points,y,h):
 wire=cq.Wire.makePolygon([cq.Vector(x,y,z) for x,z in points],close=True)
 return cq.Solid.extrudeLinear(wire,[],cq.Vector(0,h,0))

def build():
    hx=62;hy=25.5;deck=2.4;axle=7.5
    body=round_vertical(box((-hx,-hy,0),(hx,hy,deck)),10)
    body=body.cut(round_vertical(box((-50,-17.5,-1),(-6,17.5,3.4)),4),round_vertical(box((6,-17.5,-1),(50,17.5,3.4)),4)).clean()
    body=round_top(body,deck,.5)
    for side in [-1,1]:
     yc=side*(hy-.8)
     rib=round_vertical(box((-52,yc-.8,deck-.6),(52,yc+.8,deck+2.1)),.7)
     body=body.fuse(round_top(rib,deck+2.1,.5))
    for x in [-31.5,31.5]:
     for y in [-21.5,21.5]:
      bearing=round_vertical(box((x-4,y-4,deck-.6),(x+4,y+4,axle+3)),1.5)
      body=body.fuse(round_top(bearing,axle+3,1))
     drill=cq.Solid.makeCylinder(1.15,53,cq.Vector(x,-26.5,axle),cq.Vector(0,1,0))
     body=body.cut(drill)
    for cx,angle,local_xs in [(-30.5,10,[-20,22]),(30.5,20,[-20,20])]:
     for lx in local_xs:
      x=cx+lx*math.cos(math.radians(angle))
      for y in [-20.5,20.5]:body=body.cut(box((x-2.1,y-1.4,-1),(x+2.1,y+1.4,deck+1)))
    body=body.cut(box((-48,-23.5,deck-1),(48,-21.5,deck+.1)))
    mz=deck+2.4+12/math.cos(math.radians(20));mx=-31.5+math.sqrt(15**2-(mz-axle)**2)
    platform=box((-50.2,-11,0),(2,8.5,deck+2.4))
    front_edges=[e for e in cq.Workplane(obj=platform).edges('|Z').vals() if abs(e.Center().x-2)<1e-6]
    assert len(front_edges)==2
    platform=platform.fillet(2,front_edges)
    top_edges=[e for e in platform.Edges() if abs(e.BoundingBox().zmin-(deck+2.4))<1e-6 and abs(e.BoundingBox().zmax-(deck+2.4))<1e-6 and not (abs(e.BoundingBox().xmin+50.2)<1e-6 and abs(e.BoundingBox().xmax+50.2)<1e-6)]
    assert len(top_edges)==5
    platform=platform.fillet(.6,top_edges)
    platform=platform.fuse(box((mx-6,-17.6,0),(mx+6,-10.9,deck)))
    for side in [-1,1]:
     platform=platform.fuse(xz([(mx,deck+2.4),(mx+side*8,deck+2.4),(mx+side*8,deck+2.4+8*math.tan(math.radians(20)))],-5,10))
    body=body.fuse(platform)
    tie_voids=[]
    for side in [-1,1]:
     slot_x=mx+(-18 if side<0 else 14)
     void=box((slot_x-1.2,-2.3,-1),(slot_x+1.2,2.3,deck+4))
     body=body.cut(void);tie_voids.append(void)
    body=body.clean()
    return body
