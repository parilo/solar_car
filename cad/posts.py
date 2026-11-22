"""BF5 straight posts: integral upper and lower snap joints. Dimensions in mm."""
import frame as b
v=b.v

def lower_post(p,end):
    """Canonical upper end retained. Lower fork uses earlier V2.11 pin envelope.
    Isolate the two flexible tines from the surrounding post up to Z=15.5 world.
    Remaining outer walls carry load to the chassis at Z=9.9.
    """
    _,z=b.mount(p,end)
    old=b.local_post(p,end)
    pocket=v.block((-2.6,-1.8,9.8-z),(2.6,1.8,15.5-z))
    body=old.cut(pocket)
    # BF4's 7.2 mm square foot grazes the chassis edge rib by 0.2 mm.
    # Narrow only Y at the foot (6.4 mm), then blend back to 7.2 above the rib.
    for side in [-1,1]:
        trim=[(side*y,zz-z) for y,zz in [(3.2,9.8),(4,9.8),(4,13),(3.6,13),(3.2,12.1)]]
        body=body.cut(v.prism(trim,'x',-4,8))
    # Original pin lower envelope: 3.6 x 2.4 shaft, 4.8 catch, 0.2 axial play.
    pts=[(-1.8,16-z),(-1.8,7.3-z),(-2.4,7.3-z),(-2.4,6.8-z),
         (-1.6,5.1-z),(1.6,5.1-z),(2.4,6.8-z),(2.4,7.3-z),(1.8,7.3-z),(1.8,16-z)]
    fork=v.prism(pts,'y',-1.2,2.4)
    # Rounded end to the 1.2 mm split; top of the relief stays at Z=15.5.
    split=v.block((-.6,-1.3,4.9-z),(.6,1.3,14.9-z)).fuse(v.cylinder((0,-1.3,14.9-z),(0,1.3,14.9-z),.6))
    fork=fork.cut(split).clean()
    result=body.fuse(fork).clean()
    assert result.isValid() and len(result.Solids())==1
    upper_region=v.block((-10,-10,16.1-z),(10,10,100))
    diff=result.intersect(upper_region).cut(old).Volume()+old.intersect(upper_region).cut(result).Volume()
    assert diff<1e-6,('upper changed',diff)
    # Both pockets beside the narrow fork must stay empty for its full free length.
    for ya,yb in [(-1.79,-1.21),(1.21,1.79)]:
        assert result.intersect(v.block((-2.59,ya,9.91-z),(2.59,yb,15.49-z))).Volume()<1e-7
    # 1 mm lateral and 1.4 mm fore/aft solid walls remain around the relief.
    for xa,xb,ya,yb in [(-3.6,-2.6,-3.2,3.2),(2.6,3.6,-3.2,3.2),(-2.6,2.6,-3.2,-1.8),(-2.6,2.6,1.8,3.2)]:
        wall=v.block((xa,ya,9.9-z),(xb,yb,15.5-z))
        assert wall.cut(result).Volume()<1e-6
    return result
