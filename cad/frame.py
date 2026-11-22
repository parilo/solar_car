"""BF4 panel frames and accepted SC1 upper joints. Dimensions in mm."""
import math
import cadquery as cq
import panels as v
SOCKET_HALF=4.0
HOOK_X=4.2
BOTTOM=-2.6
DIMS={'catchHeightConstructionDatumX':4.5}

def base_frame(p):
    o=v.OUTER;top=v.FRAME_FLOOR+2.4
    s=v.round_top(v.round_vertical(v.block((-o,-o,0),(o,o,top)),2.5),top,.4)
    opening=v.round_vertical(v.block((-23.5,-23.5,-1),(23.5,23.5,top+2)),4)
    s=s.cut(opening,v.block((-27.8,-27.8,v.FRAME_FLOOR),(27.8,27.8,top+3))).clean()
    for end in [-1,1]:
        x=v.mount_local_x(p,end)
        s=s.fuse(v.block((x-6,-o,0),(x+6,o,v.FRAME_FLOOR))).clean()
    for side in [-1,1]:
        for station in [-13,13]:
            x=station-12;ya,yb=sorted([side*(o-2.4),side*(o+4.3)])
            s=s.cut(v.block((x-.4,ya,-1),(x+25.8,yb,top+5))).clean()
            s=s.fuse(v.clip(x,side)).clean()
    return s.cut(v.block((-o-1,-3,v.FRAME_FLOOR),(-25.5,3,top+5))).clean()

def mount(p, end):
    a = math.radians(p['angle'])
    lx = v.mount_local_x(p, end)
    return p['cx']+lx*math.cos(a), p['z']-lx*math.sin(a)

def to_world(s, p, end, y):
    """Canonical +X is horizontal, toward the central opening. +Z is vertical."""
    x, z = mount(p, end)
    if end > 0:
        s = s.rotate((0, 0, 0), (0, 0, 1), 180)
    return s.translate((x, y, z))

def from_world(s, p, end, y):
    x, z = mount(p, end)
    s = s.translate((-x, -y, -z))
    if end > 0:
        s = s.rotate((0, 0, 0), (0, 0, 1), 180)
    return s

def plane_height(p, end, x, k):
    """Vertical height at horizontal x of the frame-local plane Z=k."""
    a = math.radians(p['angle'])
    return (k+end*x*math.sin(a))/math.cos(a)

def slab(p, end, kmin, kmax):
    pts = [(-40, plane_height(p, end, -40, kmin)),
           (40, plane_height(p, end, 40, kmin)),
           (40, plane_height(p, end, 40, kmax)),
           (-40, plane_height(p, end, -40, kmax))]
    return v.prism(pts, 'y', -60, 120)

def heights(p, end):
    # Put the retaining face at the old frame-relative level, but keep the
    # whole leaf and all guides vertical. Ramp length is vertical too.
    catch = plane_height(p, end, DIMS['catchHeightConstructionDatumX'], -.3)
    top = catch+2.1
    return catch, top, top-13.6

def tapered_shoulder(p, end):
    """Transfer the SC1 specimen's tapered underside, preserving the bearing face."""
    wires=[]
    for half,k in [(3.6,-5.6),(5.0,BOTTOM)]:
        pts=[cq.Vector(x,y,plane_height(p,end,x,k))
             for x,y in [(-half,-half),(half,-half),(half,half),(-half,half)]]
        wires.append(cq.Wire.makePolygon(pts,close=True))
    return cq.Solid.makeLoft(wires,ruled=True)

def frame(p):
    world = v.assembled(base_frame(p), p)
    for end in [-1, 1]:
        catch, top, root = heights(p, end)
        for y in [-20.5, 20.5]:
            # Carry the outer receiver all the way to the panel seating plane
            # so the vertical socket has a complete 2 mm inclined ceiling.
            receiver = v.block((-6, -6, -20), (6, 6, 20)).intersect(slab(p, end, BOTTOM, 4.8))
            socket = v.block((-SOCKET_HALF, -SOCKET_HALF, -60), (SOCKET_HALF, SOCKET_HALF, 20)).intersect(slab(p, end, -100, 2.8))
            window = v.block((SOCKET_HALF-.01, -2.6, catch-.3), (6.1, 2.6, top+.2))
            world = world.fuse(to_world(receiver,p,end,y)).cut(
                to_world(socket,p,end,y),to_world(window,p,end,y)).clean()
    return v.flat(world, p)

def local_post(p, end):
    _, z = mount(p, end)
    foot = 9.9-z
    catch, top, root = heights(p, end)
    # ONE vertical 7.2 x 7.2 body from the chassis datum up to the sloping cap.
    # There is no separately fused inclined upper shaft or thin transition.
    body = v.block((-3.6,-3.6,foot),(3.6,3.6,20)).intersect(slab(p,end,-100,2.4))
    shoulder = tapered_shoulder(p, end)
    slot = v.block((.4,-2.6,root),(2.0,2.6,20)).fuse(
        v.cylinder((1.2,-2.6,root),(1.2,2.6,root),.8)).clean()
    cuts = [slot, v.block((3.6,-2.6,root),(5.1,2.6,20)),
            v.block((1.99,-2.6,top),(5.1,2.6,20))]
    for ya,yb in [(-2.6,-2.2),(2.2,2.6)]:
        cuts.append(v.block((1.99,ya,root),(5.1,yb,20)))
    body = body.fuse(shoulder).cut(*cuts).clean()
    hook = v.prism([(3.5,catch),(HOOK_X,catch),(HOOK_X,catch+.5),
                    (3.6,top),(3.5,top)],'y',-2.2,4.4)
    return body.fuse(hook).clean()
