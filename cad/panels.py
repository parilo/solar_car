"""Shared panel geometry, clips and assembly poses. All dimensions in mm."""
import math
import cadquery as cq
FRAME_FLOOR=4.8
PANEL_THICKNESS=2
OUTER=29.4
CLIP_RISE=FRAME_FLOOR-2

def block(a, b):
    return cq.Solid.makeBox(*[b[i] - a[i] for i in range(3)], cq.Vector(*a))

def cylinder(a, b, radius):
    delta = cq.Vector(*b) - cq.Vector(*a)
    return cq.Solid.makeCylinder(radius, delta.Length, cq.Vector(*a), delta.normalized())

def prism(points, axis, start, depth):
    if axis == 'x':
        vertices = [cq.Vector(start, a, b) for a, b in points]
        direction = cq.Vector(depth, 0, 0)
    elif axis == 'y':
        vertices = [cq.Vector(a, start, b) for a, b in points]
        direction = cq.Vector(0, depth, 0)
    else:
        vertices = [cq.Vector(a, b, start) for a, b in points]
        direction = cq.Vector(0, 0, depth)
    return cq.Solid.extrudeLinear(cq.Wire.makePolygon(vertices, close=True), [], direction)

def round_vertical(shape, radius):
    return shape.fillet(radius, cq.Workplane(obj=shape).edges('|Z').vals())

def round_top(shape, z, radius):
    edges = [e for e in shape.Edges() if abs(e.BoundingBox().zmin-z) < 1e-6
             and abs(e.BoundingBox().zmax-z) < 1e-6]
    return shape.fillet(radius, edges)

def pose(rear):
    front_base = 15 + 18/math.cos(math.radians(20)) + math.tan(math.radians(20))
    # Actual PANEL centres, rather than frame datum planes, differ by exactly 15.
    offset = FRAME_FLOOR + PANEL_THICKNESS/2
    rear_base = front_base + 15 + offset*(math.cos(math.radians(20))-math.cos(math.radians(10)))
    return {'rear': rear, 'cx': -30.5 if rear else 30.5,
            'angle': 10 if rear else 20, 'z': rear_base if rear else front_base}

def mount_local_x(p, end):
    return 22 if p['rear'] and end > 0 else end*20

def assembled(shape, p):
    return shape.rotate((0, 0, 0), (0, 1, 0), p['angle']).translate((p['cx'], 0, p['z']))

def flat(shape, p):
    return shape.translate((-p['cx'], 0, -p['z'])).rotate((0, 0, 0), (0, 1, 0), -p['angle'])

def clip(x, side):
    outer = OUTER
    inner = outer - 1.6
    def by(xa, xb, ya, yb, za, zb):
        lo, hi = sorted([side*ya, side*yb])
        return block((xa, lo, za), (xb, hi, zb))
    foot = by(x-1, x+4, outer-3.4, outer+4.2, 0, 2)
    points = [(x, side*inner), (x+24, side*inner),
              (x+24, side*(outer+.4)), (x+10, side*(outer+.4))]
    for i in range(7, -1, -1):
        t = i/8
        smooth = 3*t*t-2*t*t*t
        points.append((x+4+6*t, side*(outer+.4+2*(1-smooth))))
    points.append((x, side*(outer+2.4)))
    arm = prism(points, 'z', 0, 4+CLIP_RISE)
    lower = FRAME_FLOOR+2+.25-.3
    top = lower+2.7
    nose = by(x+21, x+24, inner, outer+.4, 0, top)
    hook = prism([(side*(outer-2.5), lower+.9), (side*inner, lower),
                  (side*(outer+.4), lower), (side*(outer+.4), top),
                  (side*(outer-2.5), lower+2.1)], 'x', x+21, 3)
    guard = by(x+3.8, x+25.8, outer+1.8, outer+4.2, 0, 4+CLIP_RISE)
    end = by(x+24.8, x+25.8, outer-3.4, outer+4.2, 0, 2)
    return foot.fuse(arm, nose, hook, guard, end).clean()

def panel(p):
    return assembled(block((-27.5, -27.5, FRAME_FLOOR),
                           (27.5, 27.5, FRAME_FLOOR+2)), p)

def ground(shape):
    b = shape.BoundingBox()
    return shape.translate((-(b.xmin+b.xmax)/2, -(b.ymin+b.ymax)/2, -b.zmin))
