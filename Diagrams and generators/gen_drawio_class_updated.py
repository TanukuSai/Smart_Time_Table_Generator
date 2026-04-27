"""
UML Class Diagram - draw.io aesthetic
Reflects actual PostgreSQL schema from database.py
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
GRAY_FILL   = '#f5f5f5'; GRAY_STROKE   = '#b3b3b3'
BG = '#ffffff'; TEXT = '#333333'; LINE = '#333333'; SHADOW = '#00000015'
FONT = 'Arial'

fig, ax = plt.subplots(figsize=(26, 20))
ax.set_xlim(0, 26)
ax.set_ylim(0, 20)
ax.set_aspect('equal')
ax.axis('off')
fig.patch.set_facecolor(BG)

LH = 0.30

def draw_class(ax, x, y, name, attrs, methods=None, w=4.2,
               hdr_fc=BLUE_FILL, hdr_ec=BLUE_STROKE, body_fc='#ffffff'):
    attr_h = len(attrs) * LH + 0.25
    meth_h = (len(methods) * LH + 0.25) if methods else 0
    total_h = 0.55 + attr_h + meth_h

    s = FancyBboxPatch((x + 0.06, y - total_h - 0.06), w, total_h,
                        boxstyle="round,pad=0.04", facecolor=SHADOW, edgecolor='none', zorder=0)
    ax.add_patch(s)

    body = FancyBboxPatch((x, y - total_h), w, total_h,
                           boxstyle="round,pad=0.04", facecolor=body_fc, edgecolor=hdr_ec,
                           linewidth=1.6, zorder=1)
    ax.add_patch(body)

    hdr = FancyBboxPatch((x, y - 0.55), w, 0.55,
                          boxstyle="round,pad=0.04", facecolor=hdr_fc, edgecolor=hdr_ec,
                          linewidth=1.6, zorder=2)
    ax.add_patch(hdr)
    ax.text(x + w/2, y - 0.275, name, fontsize=10, ha='center', va='center',
            fontweight='bold', color=TEXT, fontfamily=FONT, zorder=3)

    ax.plot([x, x + w], [y - 0.55, y - 0.55], '-', color=hdr_ec, linewidth=0.8, zorder=2)

    for i, attr in enumerate(attrs):
        ax.text(x + 0.12, y - 0.7 - i * LH, attr, fontsize=7.5, ha='left', va='top',
                color=TEXT, fontfamily='Consolas', zorder=3)

    if methods:
        my = y - 0.55 - attr_h
        ax.plot([x, x + w], [my, my], '-', color=hdr_ec, linewidth=0.6, zorder=2)
        for i, m in enumerate(methods):
            ax.text(x + 0.12, my - 0.12 - i * LH, m, fontsize=7.5, ha='left', va='top',
                    color='#006600', fontfamily='Consolas', fontstyle='italic', zorder=3)

    return (x, y, w, total_h)


def rel(ax, x1, y1, x2, y2, label='', c1='', c2='', color='#666666', lw=1.2, ls='-'):
    ax.plot([x1, x2], [y1, y2], ls, color=color, linewidth=lw, zorder=0)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my + 0.16, label, fontsize=7, ha='center', va='bottom',
                color=PURPLE_STROKE, fontstyle='italic', fontfamily=FONT, zorder=3)
    if c1:
        dx = 0.2 * np.sign(x2 - x1) if x1 != x2 else 0
        dy = 0.2 * np.sign(y2 - y1) if y1 != y2 else 0
        ax.text(x1 + dx, y1 + dy + 0.1, c1, fontsize=7.5, ha='center', va='bottom',
                color=RED_STROKE, fontweight='bold', fontfamily=FONT, zorder=3)
    if c2:
        dx = 0.2 * np.sign(x1 - x2) if x1 != x2 else 0
        dy = 0.2 * np.sign(y1 - y2) if y1 != y2 else 0
        ax.text(x2 + dx, y2 + dy + 0.1, c2, fontsize=7.5, ha='center', va='bottom',
                color=RED_STROKE, fontweight='bold', fontfamily=FONT, zorder=3)

def inheritance_arrow(ax, x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', facecolor='white', edgecolor=LINE,
                                lw=1.6), zorder=1)

# ROW 1: User hierarchy
draw_class(ax, 0.5, 19.5, '<<role>> Admin', [
    'inherits User (role = admin)',
], methods=[
    '+manageDepartments()',
    '+manageFaculty()',
    '+manageRooms()',
    '+setupDepartments()',
    '+viewTimetable()',
    '+publishTimetable()',
], w=4.0, hdr_fc=GREEN_FILL, hdr_ec=GREEN_STROKE)

draw_class(ax, 10.5, 19.5, 'User', [
    '+id : Serial PK',
    '+name : Text UNIQUE',
    '-password_hash : Text',
    '+role : Enum{admin|faculty|student}',
    '+admin_id : Integer FK',
    '+department_id : Integer FK',
    '+created_at : Timestamp',
], methods=[
    '+viewTimetable()',
], w=5.0, hdr_fc=BLUE_FILL, hdr_ec=BLUE_STROKE)

draw_class(ax, 21, 19.5, '<<role>> Student', [
    '+id : Serial PK',
    '+admin_id : Integer FK',
    '+name : Text',
    '+department_id : Integer FK',
    'inherits User (role = student)',
], methods=[
    '+viewTimetable()',
], w=4.5, hdr_fc=BLUE_FILL, hdr_ec=BLUE_STROKE)

# ROW 2: Core entities
draw_class(ax, 0.5, 14.0, 'Faculty', [
    '+id : Serial PK',
    '+user_id : Integer FK  UNIQUE',
    '+employee_code : Text',
    '+max_weekly_hours : Integer',
    '+is_present : Integer',
    '+admin_id : Integer FK',
], methods=[
    '+submitLeaveRequest()',
], w=4.2, hdr_fc=GREEN_FILL, hdr_ec=GREEN_STROKE)

draw_class(ax, 5.5, 14.0, 'Subject', [
    '+id : Serial PK',
    '+code : Text',
    '+name : Text',
    '+semester : Integer',
    '+classes_per_week : Integer',
    '+type : Enum{theory|lab}',
    '+admin_id : Integer FK',
], w=4.2, hdr_fc=ORANGE_FILL, hdr_ec=ORANGE_STROKE)

draw_class(ax, 10.5, 14.0, 'LeaveRequest', [
    '+id : Serial PK',
    '+admin_id : Integer FK',
    '+leave_type : Text{casual|medical}',
    '+status : Enum{pending|approved|denied}',
    '+admin_note : Text',
    '+start_date : Timestamp',
    '+end_date : Timestamp',
    '+approved_at : Timestamp',
], w=5.0, hdr_fc=RED_FILL, hdr_ec=RED_STROKE)

draw_class(ax, 16.5, 19.5, 'TimetableHistory', [
    '+id : Serial PK',
    '+admin_id : Integer FK',
    '+name : Text',
    '+department_ids : JSONB',
    '+snapshot : JSONB',
    '+log : Text',
    '+status : Enum{draft|published}',
    '+type : Text',
], methods=[
    '+viewTimetable()',
], w=4.2, hdr_fc=PURPLE_FILL, hdr_ec=PURPLE_STROKE)

draw_class(ax, 16.5, 14.0, 'TimetableSlot', [
    '+id : Serial PK',
    '+generation_id : Integer FK',
    '+day : Enum{Mon-Sun}',
    '+slot_index : Integer',
    '+slot_time : Text',
    '+subject_id : Integer FK',
    '+faculty_id : Integer FK',
    '+room_id : Integer FK',
    '+is_break : Integer',
    '+admin_id : Integer FK',
], w=4.5, hdr_fc=PURPLE_FILL, hdr_ec=PURPLE_STROKE)

# ROW 3: Supporting entities
draw_class(ax, 0.5, 8.2, 'Department', [
    '+id : Serial PK',
    '+name : Text',
    '+type : Enum{UG|PG}',
    '+semester : Integer',
    '+section : Text',
    '+strength : Integer',
    '+admin_id : Integer FK',
    '+room_id : Integer FK',
    '+lab_id : Integer FK',
], w=4.0, hdr_fc=ORANGE_FILL, hdr_ec=ORANGE_STROKE)

draw_class(ax, 5.5, 8.2, 'Room', [
    '+id : Serial PK',
    '+room_id : Text',
    '+type : Enum{classroom|lab|hall}',
    '+capacity : Integer',
    '+is_available : Integer',
    '+admin_id : Integer FK',
], w=4.2, hdr_fc=ORANGE_FILL, hdr_ec=ORANGE_STROKE)

draw_class(ax, 0.5, 3.5, 'Constraint', [
    '+id : Serial PK',
    '+is_builtin : Integer',
    '+config : JSONB',
    '+strength : Integer',
    '+is_enabled : Integer',
    '+category : Text',
    '+type : Enum{hard|soft}',
    '+admin_id : Integer FK',
    '+created_at : Timestamp',
], w=4.0, hdr_fc=GRAY_FILL, hdr_ec=GRAY_STROKE)

draw_class(ax, 16.5, 7.5, 'Substitution', [
    '+id : Serial PK',
    '+leave_request_id : Integer FK',
    '+timetable_slot_id : Integer FK',
    '+original_faculty_id : Integer FK',
    '+substitute_faculty_id : Integer FK',
    '+day : Text',
    '+slot_index : Integer',
    '+subject_id : Integer FK',
    '+status : Text',
    '+created_at : Timestamp',
    '+admin_id : Integer FK',
], w=4.8, hdr_fc=RED_FILL, hdr_ec=RED_STROKE)

# Junction tables
draw_class(ax, 5.5, 4.5, '<<junction>>\nfaculty_subjects', [
    '+faculty_id : Integer FK',
    '+subject_id : Integer FK',
], w=3.2, hdr_fc=GRAY_FILL, hdr_ec=GRAY_STROKE)

draw_class(ax, 9.5, 4.5, '<<junction>>\nfaculty_departments', [
    '+faculty_id : Integer FK',
    '+department_id : Integer FK',
], w=3.5, hdr_fc=GRAY_FILL, hdr_ec=GRAY_STROKE)

draw_class(ax, 9.5, 2.3, '<<junction>>\nsubject_departments', [
    '+subject_id : Integer FK',
    '+department_id : Integer FK',
], w=3.5, hdr_fc=GRAY_FILL, hdr_ec=GRAY_STROKE)

# RELATIONSHIPS
inheritance_arrow(ax, 4.5, 18.5, 10.5, 17.0)
inheritance_arrow(ax, 21, 18.5, 15.5, 17.0)

rel(ax, 2.5, 16.6, 2.5, 14.0, 'manages', '1', '*')
rel(ax, 2.5, 16.6, 2.5, 3.5, 'configures', '1', '*')
rel(ax, 4.7, 12.5, 10.5, 12.5, 'triggers', '1', '*')
rel(ax, 4.7, 12.0, 16.5, 12.0, 'assigns', '1', '*')
rel(ax, 9.7, 12.7, 16.5, 12.7, 'assigns', '1', '*')
rel(ax, 4.5, 7.0, 16.5, 10.8, 'allocates', '1', '*')
rel(ax, 9.7, 7.0, 16.5, 11.5, 'allocates', '1', '*')
rel(ax, 15.5, 11.0, 16.5, 7.5, 'requires', '1', '*')
rel(ax, 18.75, 10.5, 18.75, 7.5, 'modifies', '1', '*')
rel(ax, 4.5, 19.0, 16.5, 19.0, 'generates', '1', '*')
rel(ax, 2.5, 11.2, 5.5, 4.5, '', '1', '*')
rel(ax, 7.6, 11.8, 7.6, 4.5, '', '1', '*')
rel(ax, 4.7, 11.5, 9.5, 4.5, '', '1', '*')
rel(ax, 4.5, 6.5, 9.5, 3.7, '', '1', '*')
rel(ax, 7.6, 11.8, 11.0, 2.3, '', '1', '*')
rel(ax, 4.5, 6.0, 9.5, 1.8, '', '1', '*')

plt.tight_layout(pad=0.3)
plt.savefig('../STTG_Class_Diagram.svg', format='svg', dpi=300, bbox_inches='tight', facecolor=BG)
plt.savefig('../STTG_Class_Diagram.jpeg', format='jpeg', dpi=300, bbox_inches='tight', facecolor=BG)
print('[OK] Class Diagram saved as SVG and JPEG')
plt.close()
