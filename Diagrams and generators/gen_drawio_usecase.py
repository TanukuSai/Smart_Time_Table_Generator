"""
UML Use Case Diagram â€“ draw.io aesthetic
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Ellipse
import matplotlib.patheffects as pe
import numpy as np

# â”€â”€ draw.io palette â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
BLUE_FILL, BLUE_STROKE   = '#dae8fc', '#6c8ebf'
GREEN_FILL, GREEN_STROKE  = '#d5e8d4', '#82b366'
ORANGE_FILL, ORANGE_STROKE = '#fff2cc', '#d6b656'
RED_FILL, RED_STROKE      = '#f8cecc', '#b85450'
PURPLE_FILL, PURPLE_STROKE = '#e1d5e7', '#9673a6'
GRAY_FILL, GRAY_STROKE    = '#f5f5f5', '#666666'
BG                        = '#ffffff'
TEXT_COLOR                = '#333333'
LINE_COLOR                = '#333333'
SHADOW_COLOR              = '#00000018'

FONT = 'Arial'

fig, ax = plt.subplots(figsize=(14, 11))
ax.set_xlim(0, 14)
ax.set_ylim(0, 11)
ax.set_aspect('equal')
ax.axis('off')
fig.patch.set_facecolor(BG)

# â”€â”€ helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def shadow_rect(ax, x, y, w, h, **kw):
    s = FancyBboxPatch((x+0.06, y-0.06), w, h, boxstyle="round,pad=0.15",
                        facecolor=SHADOW_COLOR, edgecolor='none', zorder=0)
    ax.add_patch(s)
    r = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15", zorder=1, **kw)
    ax.add_patch(r)
    return r

def shadow_ellipse(ax, cx, cy, w, h, fc, ec, lw=1.5):
    es = Ellipse((cx+0.05, cy-0.05), w, h, facecolor=SHADOW_COLOR, edgecolor='none', zorder=0)
    ax.add_patch(es)
    e = Ellipse((cx, cy), w, h, facecolor=fc, edgecolor=ec, linewidth=lw, zorder=1)
    ax.add_patch(e)

def draw_actor(ax, x, y, label):
    c = plt.Circle((x, y+0.38), 0.16, fill=False, edgecolor=LINE_COLOR, linewidth=1.8, zorder=2)
    ax.add_patch(c)
    ax.plot([x, x], [y+0.22, y-0.12], color=LINE_COLOR, linewidth=1.8, zorder=2)
    ax.plot([x-0.28, x+0.28], [y+0.08, y+0.08], color=LINE_COLOR, linewidth=1.8, zorder=2)
    ax.plot([x, x-0.22], [y-0.12, y-0.48], color=LINE_COLOR, linewidth=1.8, zorder=2)
    ax.plot([x, x+0.22], [y-0.12, y-0.48], color=LINE_COLOR, linewidth=1.8, zorder=2)
    ax.text(x, y-0.68, label, fontsize=12, ha='center', va='top',
            fontweight='bold', color=TEXT_COLOR, fontfamily=FONT, zorder=2)

def connect(ax, x1, y1, x2, y2):
    ax.plot([x1, x2], [y1, y2], '-', color='#999999', linewidth=1.0, zorder=0)

# â”€â”€ system boundary â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
shadow_rect(ax, 3.6, 0.4, 7.2, 9.8,
            facecolor='#f0f4fa', edgecolor=BLUE_STROKE, linewidth=2)
ax.text(7.2, 10.0, 'STTG System', fontsize=15, fontweight='bold',
        ha='center', va='center', color=BLUE_STROKE, fontfamily=FONT)

# â”€â”€ actors â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
draw_actor(ax, 1.6, 7.2, 'Admin')
draw_actor(ax, 1.6, 2.8, 'Faculty')
draw_actor(ax, 12.6, 4.8, 'Student')

# â”€â”€ use cases â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
cases = [
    (7.2, 9.2, 'Manage Departments',       BLUE_FILL,   BLUE_STROKE),
    (7.2, 8.2, 'Manage Faculty',           BLUE_FILL,   BLUE_STROKE),
    (7.2, 7.2, 'Manage Rooms',             BLUE_FILL,   BLUE_STROKE),
    (7.2, 6.2, 'Manage Subjects',          BLUE_FILL,   BLUE_STROKE),
    (7.2, 5.2, 'Set Constraints',          BLUE_FILL,   BLUE_STROKE),
    (7.2, 4.2, 'Generate Timetable',       GREEN_FILL,  GREEN_STROKE),
    (7.2, 3.2, 'Review / Publish Timetable', GREEN_FILL, GREEN_STROKE),
    (7.2, 2.2, 'Smart Substitution',       ORANGE_FILL, ORANGE_STROKE),
    (7.2, 1.2, 'Request Leave',            ORANGE_FILL, ORANGE_STROKE),
]
for cx, cy, label, fc, ec in cases:
    shadow_ellipse(ax, cx, cy, 3.6, 0.72, fc, ec)
    ax.text(cx, cy, label, fontsize=10, ha='center', va='center',
            color=TEXT_COLOR, fontfamily=FONT, fontweight='medium', zorder=2)

# â”€â”€ admin connections â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
for _, cy, *_ in cases[:8]:        # admin â†’ all except Request Leave
    connect(ax, 2.0, 7.2, 5.4, cy)

# â”€â”€ faculty connections â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
connect(ax, 2.0, 2.8, 5.4, 1.2)   # â†’ Request Leave
connect(ax, 2.0, 2.8, 5.4, 3.2)   # â†’ Review / Publish Timetable (view)

# â”€â”€ student connections â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
connect(ax, 12.3, 4.8, 9.0, 3.2)  # â†’ Review / Publish Timetable (view)

# â”€â”€ legend â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ly = 0.25
for i, (fc, ec, lab) in enumerate([
    (BLUE_FILL, BLUE_STROKE, 'Data Management'),
    (GREEN_FILL, GREEN_STROKE, 'Scheduling'),
    (ORANGE_FILL, ORANGE_STROKE, 'Leave / Substitution'),
]):
    r = FancyBboxPatch((0.3, ly + i*0.42 - 0.12), 0.35, 0.24,
                        boxstyle="round,pad=0.03", facecolor=fc, edgecolor=ec, linewidth=1.2)
    ax.add_patch(r)
    ax.text(0.78, ly + i*0.42, lab, fontsize=9, va='center', color=TEXT_COLOR, fontfamily=FONT)

plt.tight_layout(pad=0.3)
plt.savefig('STTG_UseCase_Diagram.png', dpi=200, bbox_inches='tight', facecolor=BG)
print('âœ“ Use Case Diagram saved')
plt.close()

