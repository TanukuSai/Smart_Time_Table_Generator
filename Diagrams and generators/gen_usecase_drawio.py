"""Generate Use Case Diagram - optimized placement with zero overlaps."""
import xml.etree.ElementTree as ET, math

C = {'blue':('dae8fc','6c8ebf'),'green':('d5e8d4','82b366'),'orange':('fff2cc','d6b656'),
     'red':('f8cecc','b85450'),'purple':('e1d5e7','9673a6')}

EH = 46

# APPROACH: Place Admin's 10 use cases at distinct angles from Admin.
# Then place Faculty/Student use cases in clear corridors.
# Admin at (50, 440). Angles sorted, min 8deg separation.
# Faculty at bottom-left. Student at right, same height as View TT.

# Admin angles (sorted high to low): 
# uc1(Login)=62, uc3(Dept)=50, uc4(Faculty)=38, uc8(GenTT)=26, 
# uc5(Subjects)=14, uc9(Review)=2, uc6(Rooms)=-10, uc7(Constraints)=-22,
# uc12(SmartSub)=-34, uc11(Approve)=-48

AX, AY = 50, 460  # Admin center
R_NEAR = 380  # inner radius for left-column cases
R_FAR = 600   # outer radius for right-column cases

admin_cases = [
    # (uid, angle, radius, label, color, width)
    ('uc1',  74, 550, 'Login / Register', 'blue', 210),
    ('uc3',  52, R_NEAR, 'Manage Departments', 'green', 200),
    ('uc4',  39, R_NEAR, 'Manage Faculty', 'green', 200),
    ('uc8',  27, R_FAR, 'Generate Timetable', 'purple', 210),
    ('uc5',  15, R_NEAR, 'Manage Subjects', 'green', 200),
    ('uc9',   3, R_FAR, 'Review &amp; Publish TT', 'purple', 220),
    ('uc6', -10, R_NEAR, 'Manage Rooms', 'green', 200),
    ('uc7', -23, R_NEAR, 'Define Constraints', 'green', 210),
    ('uc12',-36, R_FAR, 'Smart Substitution', 'red', 210),
    ('uc11',-50, R_NEAR, 'Approve / Deny Leave', 'red', 220),
]

use_cases = []
for uid, ang, r, label, color, ew in admin_cases:
    rad = math.radians(ang)
    cx = AX + r * math.cos(rad)
    cy = AY - r * math.sin(rad)
    use_cases.append((uid, round(cx-ew/2), round(cy-EH/2), ew, EH, label, color))

# Non-admin use cases placed in CLEAR CORRIDORS
# View TT: top-right, Faculty line goes up-right, Student line goes left
use_cases.append(('uc2', 900, 0, 200, EH, 'View Timetable', 'blue'))
# Submit Leave: bottom-left, near Faculty
use_cases.append(('uc10', 200, 800, 220, EH, 'Submit Leave Request', 'orange'))
# View Sub TT: bottom-right
use_cases.append(('uc13', 700, 870, 220, 52, 'View Substitution TT', 'red'))

actors_data = [
    ('admin', 30, 430, 'Admin', 'd5e8d4', '82b366'),
    ('faculty', 10, 700, 'Faculty', 'fff2cc', 'd6b656'),
    ('student', 1200, 90, 'Student', 'f8cecc', 'b85450'),
]

STYLE = 'html=1;endArrow=none;strokeWidth=1.5;'
edges = [
    ('a1','admin','uc1',STYLE+'strokeColor=#82b366;'),
    ('a2','admin','uc3',STYLE+'strokeColor=#82b366;'),
    ('a3','admin','uc4',STYLE+'strokeColor=#82b366;'),
    ('a4','admin','uc5',STYLE+'strokeColor=#82b366;'),
    ('a5','admin','uc6',STYLE+'strokeColor=#82b366;'),
    ('a6','admin','uc7',STYLE+'strokeColor=#82b366;'),
    ('a7','admin','uc8',STYLE+'strokeColor=#82b366;'),
    ('a8','admin','uc9',STYLE+'strokeColor=#82b366;'),
    ('a9','admin','uc11',STYLE+'strokeColor=#82b366;'),
    ('a10','admin','uc12',STYLE+'strokeColor=#82b366;'),
    ('f1','faculty','uc1',STYLE+'strokeColor=#d6b656;'),
    ('f2','faculty','uc2',STYLE+'strokeColor=#d6b656;'),
    ('f3','faculty','uc10',STYLE+'strokeColor=#d6b656;'),
    ('s1','student','uc1',STYLE+'strokeColor=#b85450;'),
    ('s2','student','uc2',STYLE+'strokeColor=#b85450;'),
    ('s3','student','uc13',STYLE+'strokeColor=#b85450;'),
]
inc_edges = [('i1','uc11','uc12','&lt;&lt;include&gt;&gt;'),('i2','uc12','uc13','&lt;&lt;include&gt;&gt;')]

# VERIFY
def crosses(ax,ay,bx,by,cx,cy,hw,hh):
    for i in range(1,300):
        t=i/300.0; px=ax+t*(bx-ax); py=ay+t*(by-ay)
        if ((px-cx)/hw)**2+((py-cy)/hh)**2<=1.0: return True
    return False

ac = {'admin':(50,460),'faculty':(30,730),'student':(1220,120)}
ud = {uid:(ux+uw/2,uy+uh/2,uw/2,uh/2) for uid,ux,uy,uw,uh,_,_ in use_cases}

bad = []
for eid,src,tgt,_ in edges:
    ax,ay=ac[src]; bx,by=ud[tgt][0],ud[tgt][1]
    for uid,(cx,cy,hw,hh) in ud.items():
        if uid==tgt: continue
        if crosses(ax,ay,bx,by,cx,cy,hw,hh): bad.append(f"  {src}->{tgt} crosses {uid}")
if bad:
    print(f"OVERLAPS ({len(bad)}):")
    for b in bad: print(b)
else:
    print("VERIFIED: zero overlaps!")

# GENERATE
root = ET.Element('mxfile', host='app.diagrams.net')
diag = ET.SubElement(root, 'diagram', name='Use Case Diagram', id='uc')
model = ET.SubElement(diag, 'mxGraphModel', dx='1200', dy='1000', grid='1',
    gridSize='10',guides='1',tooltips='1',connect='1',arrows='1',
    fold='1',page='0',pageScale='1',pageWidth='1200',pageHeight='1000',
    math='0',shadow='1')
rt = ET.SubElement(model, 'root')
ET.SubElement(rt, 'mxCell', id='0')
ET.SubElement(rt, 'mxCell', id='1', parent='0')
cell = ET.SubElement(rt, 'mxCell', id='bnd', value='',
    style='rounded=1;whiteSpace=wrap;html=1;arcSize=3;fillColor=none;dashed=1;strokeColor=#666666;strokeWidth=2;',
    vertex='1', parent='1')
ET.SubElement(cell, 'mxGeometry', x='140', y='0', width='1050', height='960').set('as','geometry')
for aid,ax,ay,lbl,fc,sc in actors_data:
    s = f'shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#{fc};strokeColor=#{sc};fontSize=13;fontStyle=1;'
    cell = ET.SubElement(rt, 'mxCell', id=aid, value=lbl, style=s, vertex='1', parent='1')
    ET.SubElement(cell, 'mxGeometry', x=str(ax), y=str(ay), width='40', height='60').set('as','geometry')
for uid,ux,uy,uw,uh,lbl,color in use_cases:
    fc,sc = C[color]
    s = f'ellipse;whiteSpace=wrap;html=1;shadow=1;fillColor=#{fc};strokeColor=#{sc};fontSize=12;strokeWidth=1.5;'
    cell = ET.SubElement(rt, 'mxCell', id=uid, value=lbl, style=s, vertex='1', parent='1')
    ET.SubElement(cell, 'mxGeometry', x=str(ux), y=str(uy), width=str(uw), height=str(uh)).set('as','geometry')
for eid,src,tgt,style in edges:
    cell = ET.SubElement(rt, 'mxCell', id=eid, style=style, edge='1', source=src, target=tgt, parent='1')
    ET.SubElement(cell, 'mxGeometry', relative='1').set('as','geometry')
for eid,src,tgt,lbl in inc_edges:
    s = 'html=1;endArrow=open;dashed=1;strokeWidth=1.5;fontSize=11;fontStyle=2;strokeColor=#666666;'
    cell = ET.SubElement(rt, 'mxCell', id=eid, value=lbl, style=s, edge='1', source=src, target=tgt, parent='1')
    ET.SubElement(cell, 'mxGeometry', relative='1').set('as','geometry')
tree = ET.ElementTree(root)
ET.indent(tree, space='  ')
tree.write('STTG_UseCase_Diagram.drawio', xml_declaration=True, encoding='UTF-8')
print('[OK] Diagram saved')
