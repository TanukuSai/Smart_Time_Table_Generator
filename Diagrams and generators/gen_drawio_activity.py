"""
UML Activity Diagram - draw.io aesthetic
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import numpy as np

BLUE_FILL   = '#dae8fc'; BLUE_STROKE   = '#6c8ebf'
GREEN_FILL  = '#d5e8d4'; GREEN_STROKE  = '#82b366'
ORANGE_FILL = '#fff2cc'; ORANGE_STROKE = '#d6b656'
RED_FILL    = '#f8cecc'; RED_STROKE    = '#b85450'
PURPLE_FILL = '#e1d5e7'; PURPLE_STROKE = '#9673a6'
GRAY_FILL   = '#f5f5f5'; GRAY_STROKE   = '#666666'
BG = '#ffffff'; TEXT = '#333333'; LINE = '#333333'; SHADOW = '#00000018'
FONT = 'Arial'

fig, ax = plt.subplots(figsize=(13, 20))
ax.set_xlim(0, 13)
ax.set_ylim(0, 20)
ax.set_aspect('equal')
ax.axis('off')
fig.patch.set_facecolor(BG)

def start_node(ax, x, y):
    s = Circle((x+0.04, y-0.04), 0.22, facecolor=SHADOW, edgecolor='none', zorder=0)
    ax.add_patch(s)
    c = Circle((x, y), 0.22, facecolor='#333333', edgecolor='#333333', linewidth=2, zorder=1)
    ax.add_patch(c)

def end_node(ax, x, y):
    s = Circle((x+0.04, y-0.04), 0.22, facecolor=SHADOW, edgecolor='none', zorder=0)
    ax.add_patch(s)
    outer = Circle((x, y), 0.22, facecolor='white', edgecolor='#333333', linewidth=2.5, zorder=1)
    ax.add_patch(outer)
    inner = Circle((x, y), 0.14, facecolor='#333333', edgecolor='#333333', linewidth=1, zorder=2)
    ax.add_patch(inner)

def activity(ax, x, y, text, w=4, h=0.65, fc=BLUE_FILL, ec=BLUE_STROKE):
    s = FancyBboxPatch((x - w/2 + 0.05, y - h/2 - 0.05), w, h,
                        boxstyle="round,pad=0.12", facecolor=SHADOW, edgecolor='none', zorder=0)
    ax.add_patch(s)
    r = FancyBboxPatch((x - w/2, y - h/2), w, h,
                        boxstyle="round,pad=0.12", facecolor=fc, edgecolor=ec, linewidth=1.8, zorder=1)
    ax.add_patch(r)
    ax.text(x, y, text, fontsize=10, ha='center', va='center',
            color=TEXT, fontfamily=FONT, fontweight='medium', zorder=2)

def decision(ax, x, y, text, s=0.55):
    pts = np.array([(x, y+s), (x+s*1.6, y), (x, y-s), (x-s*1.6, y)])
    ax.fill(pts[:,0]+0.04, pts[:,1]-0.04, color=SHADOW, zorder=0)
    ax.fill(pts[:,0], pts[:,1], facecolor=ORANGE_FILL, edgecolor=ORANGE_STROKE, linewidth=1.8, zorder=1)
    ax.text(x, y, text, fontsize=9, ha='center', va='center',
            color=TEXT, fontfamily=FONT, fontweight='bold', zorder=2)

def arrow(ax, x1, y1, x2, y2, label='', side='right'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=LINE, lw=1.6), zorder=1)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        off = 0.18 if side == 'right' else -0.18
        ha = 'left' if side == 'right' else 'right'
        ax.text(mx + off, my, label, fontsize=9, ha=ha, va='center',
                color=RED_STROKE, fontweight='bold', fontfamily=FONT, zorder=3)

def curved_arrow(ax, x1, y1, x2, y2, rad=-0.3):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=LINE, lw=1.4,
                                connectionstyle=f'arc3,rad={rad}'), zorder=1)

CX = 6.5

# MAIN FLOW
start_node(ax, CX, 19.5)
arrow(ax, CX, 19.28, CX, 18.9)

activity(ax, CX, 18.6, 'Admin Logs In')
arrow(ax, CX, 18.28, CX, 17.85)

activity(ax, CX, 17.55, 'Setup: Departments, Faculty,\nSubjects, Rooms', h=0.8)
arrow(ax, CX, 17.15, CX, 16.75)

activity(ax, CX, 16.45, 'Define Hard / Soft Constraints')
arrow(ax, CX, 16.13, CX, 15.7)

activity(ax, CX, 15.4, 'Trigger Timetable Generation', fc=GREEN_FILL, ec=GREEN_STROKE)
arrow(ax, CX, 15.08, CX, 14.65)

activity(ax, CX, 14.35, 'Execute CSP + Backtracking\nAlgorithm', h=0.8, fc=GREEN_FILL, ec=GREEN_STROKE)
arrow(ax, CX, 13.95, CX, 13.45)

decision(ax, CX, 13.0, 'Conflicts\nFound?')

arrow(ax, CX - 0.88, 13.0, 2.8, 13.0, 'Yes', side='left')
activity(ax, 2.8, 12.2, 'Backtrack &\nReassign Slot', w=3.0, h=0.75, fc=RED_FILL, ec=RED_STROKE)
curved_arrow(ax, 2.8, 11.83, CX - 2.0, 14.35, rad=-0.4)

arrow(ax, CX + 0.88, 13.0, 10.2, 13.0, 'No')
arrow(ax, 10.2, 13.0, 10.2, 12.55)
activity(ax, 10.2, 12.25, 'Save as Draft', w=2.8, fc=GREEN_FILL, ec=GREEN_STROKE)
arrow(ax, 10.2, 11.93, CX, 11.45)

activity(ax, CX, 11.15, 'Admin Reviews Draft Timetable')
arrow(ax, CX, 10.83, CX, 10.35)

decision(ax, CX, 9.9, 'Approve?')

arrow(ax, CX - 0.88, 9.9, 2.8, 9.9, 'No', side='left')
activity(ax, 2.8, 9.1, 'Edit Slots\nManually', w=2.8, h=0.75, fc=ORANGE_FILL, ec=ORANGE_STROKE)
curved_arrow(ax, 2.8, 8.73, CX - 2.0, 11.15, rad=-0.4)

arrow(ax, CX + 0.88, 9.9, 10.2, 9.9, 'Yes')
arrow(ax, 10.2, 9.9, 10.2, 9.45)
activity(ax, 10.2, 9.15, 'Publish Timetable', w=3.0, fc=GREEN_FILL, ec=GREEN_STROKE)
arrow(ax, 10.2, 8.83, CX, 8.35)

# Separator
ax.plot([1.2, 11.8], [7.95, 7.95], '--', color=ORANGE_STROKE, linewidth=1.2, alpha=0.6)
r = FancyBboxPatch((CX - 2.5, 7.78), 5.0, 0.34,
                    boxstyle="round,pad=0.06", facecolor='white', edgecolor=ORANGE_STROKE, linewidth=1.2, zorder=2)
ax.add_patch(r)
ax.text(CX, 7.95, '-- Smart Substitution Flow --', fontsize=10, ha='center', va='center',
        color=ORANGE_STROKE, fontweight='bold', fontfamily=FONT, zorder=3)

# SUBSTITUTION FLOW
arrow(ax, CX, 7.78, CX, 7.35)

activity(ax, CX, 7.05, 'Faculty Submits Leave Request', fc=ORANGE_FILL, ec=ORANGE_STROKE)
arrow(ax, CX, 6.73, CX, 6.3)

activity(ax, CX, 6.0, 'Admin Reviews Leave Request')
arrow(ax, CX, 5.68, CX, 5.2)

decision(ax, CX, 4.75, 'Approved?')

arrow(ax, CX - 0.88, 4.75, 2.8, 4.75, 'No', side='left')
activity(ax, 2.8, 3.95, 'Leave Denied', w=2.5, fc=RED_FILL, ec=RED_STROKE)
arrow(ax, 2.8, 3.63, 2.8, 3.2)
end_node(ax, 2.8, 2.95)

arrow(ax, CX + 0.88, 4.75, 10.2, 4.75, 'Yes')
arrow(ax, 10.2, 4.75, 10.2, 4.3)
activity(ax, 10.2, 4.0, 'Run Smart\nSubstitution', w=3.0, h=0.75, fc=ORANGE_FILL, ec=ORANGE_STROKE)
arrow(ax, 10.2, 3.63, CX, 3.15)

activity(ax, CX, 2.85, 'Save Substitution Timetable (Draft)', w=5.0, fc=GREEN_FILL, ec=GREEN_STROKE)
arrow(ax, CX, 2.53, CX, 2.1)

activity(ax, CX, 1.8, 'Admin Reviews & Publishes')
arrow(ax, CX, 1.48, CX, 1.05)

end_node(ax, CX, 0.8)

plt.tight_layout(pad=0.3)
plt.savefig('STTG_Activity_Diagram.png', dpi=200, bbox_inches='tight', facecolor=BG)
print('[OK] Activity Diagram saved')
plt.close()
