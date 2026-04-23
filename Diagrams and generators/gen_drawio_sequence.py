"""
UML Sequence Diagram - draw.io aesthetic
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

BLUE_FILL   = '#dae8fc'; BLUE_STROKE   = '#6c8ebf'
GREEN_FILL  = '#d5e8d4'; GREEN_STROKE  = '#82b366'
ORANGE_FILL = '#fff2cc'; ORANGE_STROKE = '#d6b656'
RED_FILL    = '#f8cecc'; RED_STROKE    = '#b85450'
PURPLE_FILL = '#e1d5e7'; PURPLE_STROKE = '#9673a6'
GRAY_FILL   = '#f5f5f5'; GRAY_STROKE   = '#666666'
BG = '#ffffff'; TEXT = '#333333'; LINE = '#333333'; SHADOW = '#00000018'
FONT = 'Arial'

fig, ax = plt.subplots(figsize=(18, 17))
ax.set_xlim(0, 18)
ax.set_ylim(0, 17)
ax.set_aspect('equal')
ax.axis('off')
fig.patch.set_facecolor(BG)

def header_box(ax, x, w, label, fc=BLUE_FILL, ec=BLUE_STROKE):
    y_top = 16.3
    s = FancyBboxPatch((x - w/2 + 0.06, y_top - 0.06), w, 0.55,
                        boxstyle="round,pad=0.08", facecolor=SHADOW, edgecolor='none', zorder=0)
    ax.add_patch(s)
    r = FancyBboxPatch((x - w/2, y_top), w, 0.55,
                        boxstyle="round,pad=0.08", facecolor=fc, edgecolor=ec, linewidth=1.8, zorder=1)
    ax.add_patch(r)
    ax.text(x, y_top + 0.275, label, fontsize=11, ha='center', va='center',
            fontweight='bold', color=TEXT, fontfamily=FONT, zorder=2)
    ax.plot([x, x], [y_top, 0.3], '--', color='#b0b0b0', linewidth=0.9, zorder=0)

actors = [
    (2.5,  'Admin',       BLUE_FILL,   BLUE_STROKE),
    (6,    'Faculty',     GREEN_FILL,  GREEN_STROKE),
    (10,   'STTG System', ORANGE_FILL, ORANGE_STROKE),
    (14,   'Database',    PURPLE_FILL, PURPLE_STROKE),
    (17,   'Student',     RED_FILL,    RED_STROKE),
]
for x, label, fc, ec in actors:
    header_box(ax, x, 2.2, label, fc, ec)

def msg(ax, x1, x2, y, text, dashed=False, color=LINE, ret=False):
    ls = '--' if dashed else '-'
    fc = color
    dx1 = 0.15 * (1 if x2 > x1 else -1)
    ax.annotate('', xy=(x2 - dx1, y), xytext=(x1 + dx1, y),
                arrowprops=dict(arrowstyle='->', color=fc, lw=1.4,
                                linestyle='dashed' if dashed else 'solid'))
    mid = (x1 + x2) / 2
    ax.text(mid, y + 0.13, text, fontsize=8.5, ha='center', va='bottom',
            color=fc, fontfamily=FONT,
            fontstyle='italic' if dashed else 'normal', zorder=3)

def self_msg(ax, x, y, text):
    ax.annotate('', xy=(x + 0.15, y - 0.3), xytext=(x + 0.15, y),
                arrowprops=dict(arrowstyle='->', color=LINE, lw=1.3,
                                connectionstyle='arc3,rad=-0.5'))
    ax.text(x + 0.75, y - 0.12, text, fontsize=8.5, ha='left', va='center',
            color=TEXT, fontfamily=FONT, zorder=3)

def section(ax, y, label, fc=BLUE_FILL, ec=BLUE_STROKE):
    r = FancyBboxPatch((0.3, y - 0.15), 3.5, 0.32,
                        boxstyle="round,pad=0.06", facecolor=fc, edgecolor=ec, linewidth=1.2)
    ax.add_patch(r)
    ax.text(0.5, y, label, fontsize=9, ha='left', va='center',
            fontweight='bold', color=TEXT, fontfamily=FONT, zorder=2)
    ax.plot([0.3, 17.7], [y - 0.18, y - 0.18], '-', color=ec, linewidth=0.5, alpha=0.3)

# 1 - Setup & Data Entry
section(ax, 15.8, '1. Setup & Data Entry', BLUE_FILL, BLUE_STROKE)

msg(ax, 2.5, 10, 15.2, 'Login / Register')
msg(ax, 2.5, 10, 14.6, 'Create Departments, Subjects, Faculty, Rooms')
msg(ax, 10, 14, 14.0, 'Save Entities')
msg(ax, 14, 10, 13.5, 'Confirm Saved', dashed=True, color=GREEN_STROKE)
msg(ax, 2.5, 10, 12.9, 'Define Scheduling Constraints')
msg(ax, 10, 14, 12.3, 'Store Constraints')

# 2 - Timetable Generation
section(ax, 11.7, '2. Timetable Generation', GREEN_FILL, GREEN_STROKE)

msg(ax, 2.5, 10, 11.1, 'Request Generate Timetable')
msg(ax, 10, 14, 10.5, 'Fetch Entities & Constraints')
msg(ax, 14, 10, 10.0, 'Return Data', dashed=True, color=GREEN_STROKE)
self_msg(ax, 10, 9.4, 'Execute CSP + Backtracking')
msg(ax, 10, 14, 8.6, 'Save Timetable (status = draft)')
msg(ax, 10, 2.5, 8.1, 'Return Draft Timetable', dashed=True, color=GREEN_STROKE)
msg(ax, 2.5, 10, 7.6, 'Review & Publish Timetable')
msg(ax, 10, 14, 7.1, 'UPDATE status -> published')

# 3 - Leave & Smart Substitution
section(ax, 6.5, '3. Leave & Smart Substitution', ORANGE_FILL, ORANGE_STROKE)

msg(ax, 6, 10, 5.9, 'Submit Leave Request')
msg(ax, 10, 14, 5.4, 'Store Leave Request')
msg(ax, 10, 2.5, 4.9, 'Notify Admin: New Leave', dashed=True, color=ORANGE_STROKE)
msg(ax, 2.5, 10, 4.4, 'Approve Leave')
msg(ax, 10, 14, 3.9, 'Update Faculty is_present = 0')
self_msg(ax, 10, 3.3, 'Smart Substitution Algorithm')
msg(ax, 10, 14, 2.5, 'Save Substitution Timetable (draft)')
msg(ax, 10, 2.5, 2.0, 'Return Substitution Draft', dashed=True, color=GREEN_STROKE)
msg(ax, 2.5, 10, 1.5, 'Review & Publish Substitution')

# 4 - View Timetable
section(ax, 1.0, '4. View Timetable', RED_FILL, RED_STROKE)

msg(ax, 17, 10, 0.5, 'View Published Timetable')

plt.tight_layout(pad=0.3)
plt.savefig('STTG_Sequence_Diagram.png', dpi=200, bbox_inches='tight', facecolor=BG)
print('[OK] Sequence Diagram saved')
plt.close()
