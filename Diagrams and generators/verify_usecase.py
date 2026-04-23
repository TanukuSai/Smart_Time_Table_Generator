"""Verify no straight lines from actors cross through use case ellipses."""
import math

actors = {
    'admin': (70, 330),    # center of actor (50+20, 300+30)
    'faculty': (70, 730),
    'student': (1100, 350),
}

# Use case centers and dimensions (x,y = top-left corner, then center)
ucs = {
    'uc1':  (350, 77, 110, 27.5),   # center_x, center_y, half_w, half_h
    'uc2':  (710, 77, 110, 27.5),
    'uc3':  (350, 177, 110, 27.5),
    'uc4':  (350, 277, 110, 27.5),
    'uc5':  (350, 377, 110, 27.5),
    'uc6':  (350, 477, 110, 27.5),
    'uc7':  (350, 577, 110, 27.5),
    'uc8':  (710, 227, 110, 27.5),
    'uc9':  (710, 350, 110, 30),
    'uc10': (350, 727, 110, 27.5),
    'uc11': (350, 827, 110, 27.5),
    'uc12': (710, 727, 110, 27.5),
    'uc13': (710, 830, 110, 30),
}

edges = [
    ('admin','uc1'),('admin','uc3'),('admin','uc4'),('admin','uc5'),
    ('admin','uc6'),('admin','uc7'),('admin','uc8'),('admin','uc9'),
    ('admin','uc11'),('admin','uc12'),
    ('faculty','uc1'),('faculty','uc2'),('faculty','uc10'),
    ('student','uc1'),('student','uc2'),('student','uc13'),
]

def line_crosses_ellipse(ax, ay, bx, by, cx, cy, hw, hh):
    """Check if line segment from (ax,ay) to (bx,by) passes through ellipse centered at (cx,cy) with half-widths hw,hh."""
    # Sample 100 points along the line and check if any are inside the ellipse
    for i in range(1, 100):
        t = i / 100.0
        px = ax + t * (bx - ax)
        py = ay + t * (by - ay)
        # Check if point is inside ellipse
        if ((px - cx) / hw) ** 2 + ((py - cy) / hh) ** 2 <= 1.0:
            return True
    return False

problems = []
for actor_id, target_id in edges:
    ax, ay = actors[actor_id]
    bx, by = ucs[target_id][0], ucs[target_id][1]
    # Check against ALL other use cases
    for uc_id, (cx, cy, hw, hh) in ucs.items():
        if uc_id == target_id:
            continue
        if line_crosses_ellipse(ax, ay, bx, by, cx, cy, hw, hh):
            problems.append(f"  {actor_id} -> {target_id} crosses through {uc_id}")

if problems:
    print(f"OVERLAPS FOUND ({len(problems)}):")
    for p in problems:
        print(p)
else:
    print("NO OVERLAPS - all clear!")
