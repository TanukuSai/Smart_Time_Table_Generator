"""Generate clean STTG Class Diagram .drawio with routed edges."""
import xml.etree.ElementTree as ET

def cls_html(name, attrs, methods=None):
    h = f'<p style="margin:0;text-align:center;padding:4px"><b>{name}</b></p><hr/>'
    h += '<p style="margin:0;padding:4px;font-size:11px">' + '<br/>'.join(attrs) + '</p>'
    if methods:
        h += '<hr/><p style="margin:0;padding:4px;font-size:11px;color:#006600;font-style:italic">'
        h += '<br/>'.join(methods) + '</p>'
    return h

C = {'blue':('dae8fc','6c8ebf'),'green':('d5e8d4','82b366'),'orange':('fff2cc','d6b656'),
     'red':('f8cecc','b85450'),'purple':('e1d5e7','9673a6'),'gray':('f5f5f5','b3b3b3')}

# Layout: wide spacing, 4 rows x 5 columns
# Row1 y=30, Row2 y=430, Row3 y=880, Row4 y=1300
# Gaps: ~100px horizontal, ~70px vertical between boxes
classes = [
    # Row 1
    ('c1',80,30,260,230,'&laquo;role&raquo; Admin',['inherits User (role=admin)'],
     ['+manageDepartments()','+manageFaculty()','+manageRooms()','+setupConstraints()','+reviewLeaves()','+publishTimetable()'],'green'),
    ('c2',550,30,290,280,'User',
     ['+id : Serial PK','+name : Text','+email : Text UNIQUE','-password_hash : Text',
      '+role : Enum{admin|faculty|student}','+institution : Text','+admin_id : Integer FK',
      '+department_id : Integer FK','+created_at : Timestamp'],['+viewTimetable()'],'blue'),
    ('c4',960,30,280,280,'TimetableHistory',
     ['+id : Serial PK','+admin_id : Integer FK','+name : Text','+generated_at : Timestamp',
      '+department_ids : JSONB','+snapshot : JSONB','+log : Text','+status : Text{draft|published}',
      '+type : Text{regular|substitution}','+leave_request_id : Integer FK'],None,'purple'),
    ('c3',1400,30,260,150,'&laquo;role&raquo; Student',
     ['inherits User (role=student)','+department_id : Integer FK'],['+viewTimetable()'],'blue'),
    # Row 2
    ('c5',80,430,260,230,'Faculty',
     ['+id : Serial PK','+user_id : Integer FK UNIQUE','+employee_code : Text',
      '+max_weekly_hours : Integer','+is_present : Integer','+admin_id : Integer FK'],
     ['+submitLeaveRequest()'],'green'),
    ('c6',460,430,250,200,'Subject',
     ['+id : Serial PK','+name : Text','+code : Text','+semester : Integer',
      '+classes_per_week : Integer','+admin_id : Integer FK'],None,'orange'),
    ('c7',830,430,290,260,'LeaveRequest',
     ['+id : Serial PK','+faculty_id : Integer FK','+leave_date : Text','+reason : Text',
      '+leave_type : Text{casual|medical}','+status : Enum{pending|approved|denied}',
      '+admin_note : Text','+created_at : Timestamp','+reviewed_at : Timestamp'],None,'red'),
    ('c8',1250,430,270,280,'TimetableSlot',
     ['+id : Serial PK','+department_id : Integer FK','+day : Enum{Mon-Fri}','+slot_index : Integer',
      '+slot_time : Text','+subject_id : Integer FK','+faculty_id : Integer FK','+room_id : Integer FK',
      '+is_break : Integer','+admin_id : Integer FK'],None,'purple'),
    # Row 3
    ('c9',80,880,250,220,'Department',
     ['+id : Serial PK','+name : Text','+level : Text{UG|PG}','+semester : Integer',
      '+section : Text','+strength : Integer','+admin_id : Integer FK'],None,'orange'),
    ('c10',460,880,260,200,'Room',
     ['+id : Serial PK','+room_id : Text','+type : Enum{classroom|lab|hall}','+capacity : Integer',
      '+is_available : Integer','+admin_id : Integer FK'],None,'orange'),
    ('c11',1250,880,290,320,'Substitution',
     ['+id : Serial PK','+leave_request_id : Integer FK','+timetable_slot_id : Integer FK',
      '+original_faculty_id : Integer FK','+substitute_faculty_id : Integer FK','+department_id : Integer FK',
      '+day : Text','+slot_index : Integer','+subject_id : Integer FK','+status : Text',
      '+created_at : Timestamp','+admin_id : Integer FK'],None,'red'),
    # Row 4
    ('c12',80,1300,250,260,'Constraint',
     ['+id : Serial PK','+name : Text','+type : Enum{hard|soft}','+category : Text',
      '+is_enabled : Integer','+is_builtin : Integer','+config : JSONB',
      '+admin_id : Integer FK','+created_at : Timestamp'],None,'gray'),
    ('c13',460,1300,220,130,'&laquo;junction&raquo;\nfaculty_subjects',
     ['faculty_id : FK','subject_id : FK'],None,'gray'),
    ('c14',800,1300,230,150,'&laquo;junction&raquo;\nfaculty_departments',
     ['faculty_id : FK','department_id : FK','subject_id : FK'],None,'gray'),
    ('c15',800,1520,230,130,'&laquo;junction&raquo;\nsubject_departments',
     ['subject_id : FK','department_id : FK'],None,'gray'),
]

O = 'edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;'
REL = f'{O}endArrow=none;strokeWidth=1.5;strokeColor=#666666;fontSize=10;fontStyle=2;fontColor=#9673a6;'
JN = f'{O}endArrow=none;strokeWidth=1.2;strokeColor=#999999;fontSize=10;fontStyle=1;fontColor=#b85450;'
INH = f'{O}endArrow=block;endFill=0;strokeWidth=2;strokeColor=#333333;'

# (id, src, tgt, label, style, waypoints or None)
edges = [
    # Inheritance: horizontal in Row 1
    ('r1','c1','c2','',f'{INH}exitX=1;exitY=0.3;entryX=0;entryY=0.3;',None),
    ('r2','c3','c2','',f'{INH}exitX=0;exitY=0.5;entryX=1;entryY=0.3;',None),
    # Admin -> TT History (across top, clear path)
    ('r4','c2','c4','generates',f'{REL}exitX=1;exitY=0.5;entryX=0;entryY=0.5;',None),
    # Admin -> Faculty (straight down left column)
    ('r3','c1','c5','manages',f'{REL}exitX=0.5;exitY=1;entryX=0.5;entryY=0;',None),
    # Admin -> Constraint (route down LEFT MARGIN to avoid crossing Dept)
    ('r5','c1','c12','configures',f'{REL}exitX=0;exitY=0.9;entryX=0;entryY=0.3;',
     [(40,240),(40,1375)]),
    # Faculty -> LeaveRequest (horizontal, clear path through gap)
    ('r6','c5','c7','submitted_by',f'{REL}exitX=1;exitY=0.6;entryX=0;entryY=0.3;',
     [(760,568),(760,508)]),
    # Faculty -> TimetableSlot (route through TOP GAP between Row1 and Row2)
    ('r7','c5','c8','assigned_faculty',f'{REL}exitX=1;exitY=0.1;entryX=0.3;entryY=0;',
     [(370,453),(370,390),(1331,390)]),
    # Subject -> TimetableSlot (route through gap above LeaveRequest)
    ('r8','c6','c8','allocated_subject',f'{REL}exitX=1;exitY=0.2;entryX=0.5;entryY=0;',
     [(740,470),(740,400),(1385,400)]),
    # Department -> TimetableSlot (route through BOTTOM GAP between Row2 and Row3)
    ('r9','c9','c8','scheduled_for',f'{REL}exitX=1;exitY=0.2;entryX=0;entryY=0.85;',
     [(370,924),(370,810),(1210,810),(1210,668)]),
    # Room -> TimetableSlot (route through gap)
    ('r10','c10','c8','allocated_room',f'{REL}exitX=1;exitY=0.2;entryX=0;entryY=0.95;',
     [(760,920),(760,790),(1200,790),(1200,696)]),
    # LeaveRequest -> Substitution (route right through gap)
    ('r11','c7','c11','triggers',f'{REL}exitX=1;exitY=0.7;entryX=0;entryY=0.2;',None),
    # TimetableSlot -> Substitution (straight down right column)
    ('r12','c8','c11','slot_ref',f'{REL}exitX=0.5;exitY=1;entryX=0.5;entryY=0;',None),
    # Junction edges (route down from Row2/Row3 to Row4)
    ('r13','c5','c13','1  *',f'{JN}exitX=0.7;exitY=1;entryX=0.5;entryY=0;',
     [(262,780),(570,780),(570,1300)]),
    ('r14','c6','c13','1  *',f'{JN}exitX=0.5;exitY=1;entryX=0.5;entryY=0;',
     [(585,780),(570,780),(570,1300)]),
    ('r15','c5','c14','1  *',f'{JN}exitX=1;exitY=0.9;entryX=0.5;entryY=0;',
     [(380,637),(380,760),(915,760),(915,1300)]),
    ('r16','c9','c14','1  *',f'{JN}exitX=1;exitY=0.8;entryX=0;entryY=0.5;',
     [(370,1056),(370,1375),(800,1375)]),
    ('r17','c6','c15','1  *',f'{JN}exitX=0.3;exitY=1;entryX=0.5;entryY=0;',
     [(535,760),(535,1200),(915,1200),(915,1520)]),
    ('r18','c9','c15','1  *',f'{JN}exitX=0.5;exitY=1;entryX=0;entryY=0.5;',
     [(205,1200),(205,1585),(800,1585)]),
]

# Build XML
root = ET.Element('mxfile', host='app.diagrams.net')
diag = ET.SubElement(root, 'diagram', name='Class Diagram', id='cd')
model = ET.SubElement(diag, 'mxGraphModel', dx='1800', dy='1800', grid='1',
    gridSize='10', guides='1', tooltips='1', connect='1', arrows='1',
    fold='1', page='0', pageScale='1', pageWidth='1800', pageHeight='1800',
    math='0', shadow='1')
rt = ET.SubElement(model, 'root')
ET.SubElement(rt, 'mxCell', id='0')
ET.SubElement(rt, 'mxCell', id='1', parent='0')

for cid,x,y,w,h,name,attrs,methods,color in classes:
    fc,sc = C[color]
    style = f'verticalAlign=top;align=left;overflow=fill;html=1;rounded=1;shadow=1;fillColor=#{fc};strokeColor=#{sc};strokeWidth=2;fontSize=12;'
    cell = ET.SubElement(rt, 'mxCell', id=cid, value=cls_html(name,attrs,methods),
                         style=style, vertex='1', parent='1')
    ET.SubElement(cell, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h)).set('as','geometry')

for eid,src,tgt,label,style,wps in edges:
    attrs = dict(id=eid, style=style, edge='1', source=src, target=tgt, parent='1')
    if label: attrs['value'] = label
    cell = ET.SubElement(rt, 'mxCell', **attrs)
    geo = ET.SubElement(cell, 'mxGeometry', relative='1')
    geo.set('as','geometry')
    if wps:
        arr = ET.SubElement(geo, 'Array')
        arr.set('as','points')
        for wx,wy in wps:
            ET.SubElement(arr, 'mxPoint', x=str(wx), y=str(wy))

tree = ET.ElementTree(root)
ET.indent(tree, space='  ')
tree.write('STTG_Class_Diagram.drawio', xml_declaration=True, encoding='UTF-8')
print('[OK] Class Diagram saved')
